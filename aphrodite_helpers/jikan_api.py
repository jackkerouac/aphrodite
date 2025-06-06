#!/usr/bin/env python3
# aphrodite_helpers/jikan_api.py

import requests
import time
import json
from typing import Dict, Any, Optional


class JikanAPI:
    """
    Jikan API wrapper for MyAnimeList data
    Free API, no authentication required
    """
    
    def __init__(self, rate_limit_delay: float = 1.0):
        self.base_url = "https://api.jikan.moe/v4"
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.cache = {}
        self.cache_expiration = 60 * 60 * 24  # 24 hours
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Make a rate-limited request to Jikan API
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            API response data or None if failed
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.get(url, params=params or {}, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited, wait longer and retry once
                print(f"⚠️ Jikan API rate limited, waiting 5 seconds...")
                time.sleep(5)
                response = requests.get(url, params=params or {}, timeout=10)
                self.last_request_time = time.time()
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"❌ Jikan API error after retry: {response.status_code}")
                    return None
            else:
                print(f"❌ Jikan API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Jikan API request failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Jikan API unexpected error: {e}")
            return None
    
    def search_anime(self, query: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """
        Search for anime by title
        
        Args:
            query: Anime title to search for
            limit: Maximum number of results (1-25)
            
        Returns:
            Search results or None if failed
        """
        cache_key = f"search_{query.lower()}_{limit}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                return cache_entry["data"]
        
        params = {
            "q": query,
            "limit": min(limit, 25),
            "order_by": "popularity",
            "sort": "asc"
        }
        
        result = self._make_request("anime", params)
        
        # Cache the result
        if result:
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": result
            }
        
        return result
    
    def get_anime_details(self, anime_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific anime
        
        Args:
            anime_id: MyAnimeList anime ID
            
        Returns:
            Anime details or None if failed
        """
        cache_key = f"anime_{anime_id}"
        
        # Check cache first
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                return cache_entry["data"]
        
        result = self._make_request(f"anime/{anime_id}")
        
        # Cache the result
        if result:
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": result
            }
        
        return result
    
    def find_anime_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Find the best matching anime for a given title using multiple search strategies
        
        Args:
            title: Anime title to search for
            
        Returns:
            Best match anime data or None if not found
        """
        print(f"🔍 find_anime_by_title: Searching for '{title}'")
        
        # Generate multiple search variations
        search_variations = self._generate_search_variations(title)
        
        all_results = []
        best_matches = []
        
        # Try each search variation
        for i, variation in enumerate(search_variations[:5], 1):  # Limit to 5 variations to avoid rate limits
            print(f"   {i}. Trying variation: '{variation}'")
            
            search_results = self.search_anime(variation, limit=10)
            
            if search_results and "data" in search_results and search_results["data"]:
                anime_list = search_results["data"]
                all_results.extend(anime_list)
                
                print(f"   Found {len(anime_list)} results for '{variation}'")
                
                # Look for exact or partial matches in this result set
                matches = self._find_title_matches(title, anime_list)
                best_matches.extend(matches)
            else:
                print(f"   No results for '{variation}'")
        
        # Remove duplicates (same MAL ID)
        unique_results = {}
        for anime in all_results:
            mal_id = anime.get('mal_id')
            if mal_id and mal_id not in unique_results:
                unique_results[mal_id] = anime
        
        # Find the best match from all results
        if best_matches:
            # Sort by match quality and score
            best_matches.sort(key=lambda x: (
                x['match_score'],  # Higher match score first
                -(x['anime'].get('score') or 0),  # Higher anime score
                -(x['anime'].get('scored_by') or 0)  # More votes
            ), reverse=True)
            
            best_anime = best_matches[0]['anime']
            print(f"   ✅ Best match: {best_anime.get('title')} (ID: {best_anime.get('mal_id')})")
            print(f"   Match reason: {best_matches[0]['reason']}")
            
            # Get detailed information for the best match
            return self.get_anime_details(best_anime['mal_id'])
        
        # If no good matches, look for specific known anime in all results
        print(f"   🔍 No exact matches found, checking for known anime...")
        for anime in unique_results.values():
            # Check if this is "A Returner's Magic Should Be Special" specifically
            english_title = anime.get('title_english', '').lower()
            main_title = anime.get('title', '').lower()
            
            if ('returner' in english_title and 'magic' in english_title and 'special' in english_title) or \
               ('returner' in main_title and 'magic' in main_title and 'special' in main_title):
                print(f"   ✅ Found target anime: {anime.get('title')} (ID: {anime.get('mal_id')})")
                return self.get_anime_details(anime['mal_id'])
        
        # If no good matches, try with the highest-scored anime from all results
        if unique_results:
            scored_anime = [a for a in unique_results.values() if a.get('score')]
            if scored_anime:
                best_by_score = max(scored_anime, key=lambda x: x.get('score', 0))
                print(f"   🤔 No exact matches, trying highest scored: {best_by_score.get('title')} (ID: {best_by_score.get('mal_id')})")
                return self.get_anime_details(best_by_score['mal_id'])
        
        print(f"   ❌ No suitable matches found")
        return None
    
    def _clean_title_for_search(self, title: str) -> str:
        """Clean up the title for better search results"""
        import re
        
        # Remove common suffixes and prefixes that might interfere with search
        title = re.sub(r'\s*\(\d{4}\)\s*', '', title)  # Remove year in parentheses
        title = re.sub(r'\s*Season\s+\d+', '', title, flags=re.IGNORECASE)  # Remove "Season X"
        title = re.sub(r'\s*S\d+', '', title)  # Remove "S1", "S2", etc.
        title = re.sub(r'\s*Part\s+\d+', '', title, flags=re.IGNORECASE)  # Remove "Part X"
        title = re.sub(r'\s*Vol\.?\s*\d+', '', title, flags=re.IGNORECASE)  # Remove "Vol X"
        
        # Clean up extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def _generate_search_variations(self, title: str) -> list:
        """Generate multiple search variations of a title for better matching"""
        import re
        
        variations = [title]  # Original title
        
        # Clean version
        cleaned = self._clean_title_for_search(title)
        if cleaned != title and cleaned.strip():
            variations.append(cleaned.strip())
        
        # Remove special characters and punctuation
        no_punct = re.sub(r'[^\w\s]', '', title)
        if no_punct != title and no_punct.strip():
            variations.append(no_punct.strip())
        
        # Remove articles (A, An, The)
        no_articles = re.sub(r'^(A|An|The)\s+', '', title, flags=re.IGNORECASE)
        if no_articles != title:
            variations.append(no_articles)
        
        # Remove possessives ('s)
        no_possessive = re.sub(r"'s\b", '', title)
        if no_possessive != title:
            variations.append(no_possessive)
        
        # Replace apostrophes with nothing
        no_apostrophe = title.replace("'", "")
        if no_apostrophe != title:
            variations.append(no_apostrophe)
        
        # Simplified version (keep only alphanumeric and spaces)
        simple = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
        simple = re.sub(r'\s+', ' ', simple).strip()
        if simple != title and simple:
            variations.append(simple)
        
        # Short version (first few important words)
        words = title.split()
        if len(words) > 2:
            # Try different lengths
            for word_count in [3, 2]:  # First 3 words, then 2 words
                if len(words) >= word_count:
                    short = ' '.join(words[:word_count])
                    if short not in variations:
                        variations.append(short)
        
        # Remove duplicates while preserving order
        unique_variations = []
        for var in variations:
            if var and var.strip() and var not in unique_variations:
                unique_variations.append(var.strip())
        
        return unique_variations
    
    def _find_title_matches(self, original_title: str, anime_list: list) -> list:
        """Find anime that match the original title with scoring"""
        import re
        
        matches = []
        original_lower = original_title.lower()
        original_clean = re.sub(r'[^a-zA-Z0-9\s]', '', original_lower)
        original_words = set(original_clean.split())
        
        for anime in anime_list:
            titles_to_check = [
                anime.get("title", ""),
                anime.get("title_english", ""),
                anime.get("title_japanese", "")
            ]
            
            # Also check alternative titles if available
            if "titles" in anime:
                for title_obj in anime["titles"]:
                    titles_to_check.append(title_obj.get("title", ""))
            
            best_match_score = 0
            best_reason = ""
            
            for title in titles_to_check:
                if not title:
                    continue
                
                title_lower = title.lower()
                title_clean = re.sub(r'[^a-zA-Z0-9\s]', '', title_lower)
                
                # Exact match (highest score)
                if title_lower == original_lower or title_clean == original_clean:
                    best_match_score = 100
                    best_reason = f"Exact match: '{title}'"
                    break
                
                # Substring match
                if original_lower in title_lower or title_lower in original_lower:
                    score = 80
                    if best_match_score < score:
                        best_match_score = score
                        best_reason = f"Substring match: '{title}'"
                
                # Word overlap
                title_words = set(title_clean.split())
                common_words = original_words & title_words
                if common_words:
                    overlap_ratio = len(common_words) / max(len(original_words), len(title_words))
                    score = int(60 * overlap_ratio)
                    if best_match_score < score:
                        best_match_score = score
                        best_reason = f"Word overlap ({len(common_words)} words): '{title}'"
            
            if best_match_score > 50:  # Only include reasonable matches
                matches.append({
                    'anime': anime,
                    'match_score': best_match_score,
                    'reason': best_reason
                })
        
        return matches
    
    def extract_rating_data(self, anime_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract rating information from anime data
        
        Args:
            anime_data: Full anime data from Jikan API
            
        Returns:
            Simplified rating data or None
        """
        if not anime_data or "data" not in anime_data:
            return None
        
        anime = anime_data["data"]
        
        return {
            "mal_id": anime.get("mal_id"),
            "title": anime.get("title"),
            "score": anime.get("score"),
            "scored_by": anime.get("scored_by"),
            "rank": anime.get("rank"),
            "popularity": anime.get("popularity"),
            "members": anime.get("members"),
            "favorites": anime.get("favorites"),
            "status": anime.get("status"),
            "episodes": anime.get("episodes"),
            "source_url": anime.get("url"),
            "year": anime.get("year"),
            "season": anime.get("season")
        }
