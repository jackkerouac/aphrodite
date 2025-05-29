#!/usr/bin/env python3
# aphrodite_helpers/get_review_info.py

import os
import sys
import argparse
import requests
import json
import time
from requests.exceptions import RequestException

# Add parent directory to sys.path to allow importing from other modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aphrodite_helpers.settings_validator import load_settings
from aphrodite_helpers.get_media_info import get_jellyfin_item_details

class ReviewFetcher:
    def __init__(self, settings):
        self.settings = settings
        self.jellyfin_settings = settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
        self.omdb_settings = settings.get("api_keys", {}).get("OMDB", [{}])[0]
        self.tmdb_settings = settings.get("api_keys", {}).get("TMDB", [{}])[0]
        anidb_list = settings.get("api_keys", {}).get("aniDB", [{}])
        self.anidb_settings = anidb_list[0] if anidb_list else {}
        
        # Setup headers for Jellyfin API calls
        self.jellyfin_headers = {"X-Emby-Token": self.jellyfin_settings.get("api_key", "")}
        
        # Initialize cache
        self.cache = {}
        self.cache_expiration = 60 * 60  # Default 1 hour
        
        # Load badge settings to get image mappings
        self.badge_settings = self.load_badge_settings()
    
    def load_badge_settings(self, settings_file="badge_settings_review.yml"):
        """Load badge settings to get image mappings"""
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(root_dir, settings_file)
            
            with open(full_path, 'r') as f:
                import yaml
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load badge settings: {e}")
            return {}
        
    def get_jellyfin_item_metadata(self, item_id):
        """Retrieve item metadata from Jellyfin"""
        return get_jellyfin_item_details(
            self.jellyfin_settings.get('url'),
            self.jellyfin_settings.get('api_key'),
            self.jellyfin_settings.get('user_id'),
            item_id
        )
    
    def get_imdb_id(self, item_data):
        """Extract IMDb ID from Jellyfin item data"""
        if not item_data:
            return None
        
        # Try to get IMDB ID from provider IDs
        provider_ids = item_data.get("ProviderIds", {})
        imdb_id = provider_ids.get("Imdb")
        
        return imdb_id
    
    def get_tmdb_id(self, item_data):
        """Extract TMDb ID from Jellyfin item data"""
        if not item_data:
            return None
        
        # Try to get TMDb ID from provider IDs
        provider_ids = item_data.get("ProviderIds", {})
        tmdb_id = provider_ids.get("Tmdb")
        
        return tmdb_id
    
    def get_anidb_id(self, item_data):
        """Extract AniDB ID from Jellyfin item data"""
        if not item_data:
            print(f"🔍 No item data provided to get_anidb_id")
            return None
        
        # Try to get AniDB ID from provider IDs
        provider_ids = item_data.get("ProviderIds", {})
        print(f"🔍 Provider IDs available: {list(provider_ids.keys())}")
        anidb_id = provider_ids.get("AniDb")
        print(f"🔍 AniDB ID found: {anidb_id}")
        
        return anidb_id
    
    def fetch_omdb_ratings(self, imdb_id):
        """Fetch ratings from OMDB API"""
        if not imdb_id or not self.omdb_settings.get("api_key"):
            return None
        
        # Check cache first
        cache_key = f"omdb_{imdb_id}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                return cache_entry["data"]
        
        # Fetch from OMDB API
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={self.omdb_settings.get('api_key')}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": data
            }
            
            return data
        except RequestException as e:
            print(f"❌ Error fetching OMDB data: {e}")
            return None
    
    def fetch_tmdb_ratings(self, tmdb_id, media_type="movie"):
        """Fetch ratings from TMDB API"""
        if not tmdb_id or not self.tmdb_settings.get("api_key"):
            return None
        
        # Check cache first
        cache_key = f"tmdb_{tmdb_id}_{media_type}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                return cache_entry["data"]
        
        # Fetch from TMDB API
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
        params = {
            "api_key": self.tmdb_settings.get("api_key"),
            "language": self.tmdb_settings.get("language", "en")
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": data
            }
            
            return data
        except RequestException as e:
            print(f"❌ Error fetching TMDB data: {e}")
            return None
    
    def fetch_anidb_ratings(self, anidb_id=None, item_name=None):
        """Fetch ratings from AniDB
        
        This implementation searches AniDB by title if no ID is provided,
        then fetches the rating information.
        """
        print(f"🔍 fetch_anidb_ratings called with anidb_id: {anidb_id}, item_name: {item_name}")
        print(f"🔍 anidb_settings available: {bool(self.anidb_settings)}")
        
        if not self.anidb_settings:
            print(f"❌ No AniDB settings found")
            return None
            
        # If we don't have an AniDB ID, try to search by title
        if not anidb_id and item_name:
            print(f"🔍 No AniDB ID provided, searching by title: {item_name}")
            anidb_id = self.search_anidb_by_title(item_name)
            if not anidb_id:
                print(f"❌ Could not find AniDB ID for title: {item_name}")
                return None
        elif not anidb_id:
            print(f"❌ No AniDB ID or title provided")
            return None
            
        print(f"🔍 Fetching AniDB rating for ID: {anidb_id}")
        
        # Check cache first
        cache_key = f"anidb_{anidb_id}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                print(f"✅ Using cached AniDB data for ID: {anidb_id}")
                return cache_entry["data"]
        
        # Fetch rating from AniDB
        rating_data = self.fetch_anidb_anime_info(anidb_id)
        
        if rating_data:
            # Store in cache
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": rating_data
            }
            print(f"✅ Successfully fetched AniDB rating: {rating_data.get('rating', 'N/A')}")
            return rating_data
        else:
            print(f"❌ Failed to fetch AniDB rating for ID: {anidb_id}")
            return None
    
    def search_anidb_by_title(self, title):
        """Search AniDB for an anime by title and return the AniDB ID"""
        if not title:
            return None
            
        print(f"🔍 Searching AniDB for title: {title}")
        
        # Clean up the title for search
        search_title = self.clean_title_for_search(title)
        print(f"🔍 Cleaned search title: {search_title}")
        
        # Check cache first
        cache_key = f"anidb_search_{search_title.lower()}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_expiration:
                print(f"✅ Using cached AniDB search result for: {search_title}")
                return cache_entry["data"]
        
        try:
            # AniDB HTTP API for search
            # Note: This uses the unofficial HTTP API, not the UDP API
            # Add rate limiting to be respectful to AniDB
            time.sleep(1)  # Wait 1 second between requests
            
            search_url = "https://anidb.net/perl-bin/animedb.pl"
            params = {
                "show": "animelist",
                "adb.search": search_title,
                "do.search": "Search"
            }
            
            headers = {
                "User-Agent": f"{self.anidb_settings.get('client_name', 'aphrodite')}/{self.anidb_settings.get('version', '1')}"
            }
            
            print(f"🌐 Making AniDB search request...")
            response = requests.get(search_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse the HTML response to extract anime ID
            anidb_id = self.parse_anidb_search_response(response.text, search_title)
            
            # Cache the result (even if None to avoid repeated failed searches)
            self.cache[cache_key] = {
                "timestamp": time.time(),
                "data": anidb_id
            }
            
            if anidb_id:
                print(f"✅ Found AniDB ID: {anidb_id} for title: {search_title}")
            else:
                print(f"❌ No AniDB ID found for title: {search_title}")
                
            return anidb_id
            
        except Exception as e:
            print(f"❌ Error searching AniDB: {e}")
            return None
    
    def clean_title_for_search(self, title):
        """Clean up the title for better AniDB search results"""
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
    
    def parse_anidb_search_response(self, html_content, search_title):
        """Parse AniDB search response HTML to extract the anime ID"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for anime links in the search results
            # AniDB anime links have the pattern: /anime/[id]
            import re
            anime_links = soup.find_all('a', href=re.compile(r'/anime/\d+'))
            
            if not anime_links:
                print(f"❌ No anime links found in search results")
                return None
            
            # Get the first result (most likely match)
            first_link = anime_links[0]
            href = first_link.get('href')
            
            # Extract ID from href like "/anime/12345"
            match = re.search(r'/anime/(\d+)', href)
            if match:
                anidb_id = match.group(1)
                print(f"✅ Extracted AniDB ID: {anidb_id} from search results")
                return anidb_id
            else:
                print(f"❌ Could not extract ID from href: {href}")
                return None
                
        except Exception as e:
            print(f"❌ Error parsing AniDB search response: {e}")
            return None
    
    def fetch_anidb_anime_info(self, anidb_id):
        """Fetch anime information including rating from AniDB"""
        try:
            # Add rate limiting to be respectful to AniDB
            time.sleep(1)  # Wait 1 second between requests
            
            # Fetch the anime page
            anime_url = f"https://anidb.net/anime/{anidb_id}"
            headers = {
                "User-Agent": f"{self.anidb_settings.get('client_name', 'aphrodite')}/{self.anidb_settings.get('version', '1')}"
            }
            
            print(f"🌐 Fetching AniDB anime info from: {anime_url}")
            response = requests.get(anime_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse the rating from the HTML
            rating = self.parse_anidb_rating(response.text)
            
            if rating:
                return {
                    "anidb_id": anidb_id,
                    "rating": rating,
                    "source_url": anime_url
                }
            else:
                print(f"❌ Could not extract rating from AniDB page")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching AniDB anime info: {e}")
            return None
    
    def parse_anidb_rating(self, html_content):
        """Parse the rating from AniDB anime page HTML"""
        import re
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for rating information - AniDB typically shows ratings in specific elements
            # Try multiple selectors as AniDB's HTML structure can vary
            
            # Method 1: Look for rating in data tables
            rating_element = soup.find('span', class_='rating')
            if rating_element:
                rating_text = rating_element.get_text().strip()
                rating_match = re.search(r'(\d+\.\d+)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
                    print(f"✅ Found rating (method 1): {rating}")
                    return rating
            
            # Method 2: Look for rating in stats section
            rating_pattern = r'Rating:\s*(\d+\.\d+)'
            rating_match = re.search(rating_pattern, html_content, re.IGNORECASE)
            if rating_match:
                rating = float(rating_match.group(1))
                print(f"✅ Found rating (method 2): {rating}")
                return rating
            
            # Method 3: Look for average rating in any context
            avg_pattern = r'Average:\s*(\d+\.\d+)'
            avg_match = re.search(avg_pattern, html_content, re.IGNORECASE)
            if avg_match:
                rating = float(avg_match.group(1))
                print(f"✅ Found rating (method 3): {rating}")
                return rating
            
            print(f"❌ Could not find rating in AniDB page HTML")
            return None
            
        except Exception as e:
            print(f"❌ Error parsing AniDB rating: {e}")
            return None
    
    def format_review_data(self, review_data, show_details=False):
        """Format the review data from various sources into a structured format"""
        formatted_reviews = []
        
        # Get image mappings from settings
        image_mappings = self.badge_settings.get("ImageBadges", {}).get("image_mapping", {})
        
        # Process OMDB data
        if review_data.get("omdb"):
            omdb_data = review_data["omdb"]
            
            # IMDB Rating - Convert to percentage
            if "imdbRating" in omdb_data and omdb_data["imdbRating"] != "N/A":
                try:
                    # Convert rating from 0-10 scale to percentage
                    imdb_rating = float(omdb_data["imdbRating"])
                    percentage_rating = int(round(imdb_rating * 10))
                    
                    formatted_reviews.append({
                        "source": "IMDb",
                        "rating": f"{percentage_rating}%",  # Display as percentage
                        "original_rating": omdb_data["imdbRating"],  # Keep original for reference
                        "max_rating": "100%",  # Standardize max rating
                        "votes": omdb_data.get("imdbVotes", "N/A"),
                        "image_key": "IMDb"
                    })
                    
                    # Check if in top listings based on rating and votes
                    imdb_votes_str = omdb_data.get("imdbVotes", "0").replace(",", "")
                    imdb_votes = int(imdb_votes_str) if imdb_votes_str.isdigit() else 0
                    
                    if imdb_rating >= 8.0 and imdb_votes >= 100000:
                        # Add top badge based on rating
                        if imdb_rating >= 8.5 and imdb_votes >= 250000:
                            formatted_reviews.append({
                                "source": "IMDb Top 250",
                                "rating": f"{percentage_rating}%",
                                "image_key": "IMDbTop250"
                            })
                        elif imdb_rating >= 8.0 and imdb_votes >= 100000:
                            formatted_reviews.append({
                                "source": "IMDb Top 1000",
                                "rating": f"{percentage_rating}%",
                                "image_key": "IMDbTop1000"
                            })
                except (ValueError, TypeError):
                    pass
                
            # Rotten Tomatoes
            if "Ratings" in omdb_data:
                for rating in omdb_data["Ratings"]:
                    if rating["Source"] == "Rotten Tomatoes":
                        rt_value = rating["Value"].rstrip("%")
                        try:
                            rt_score = int(rt_value)
                            
                            # Determine RT image based on score
                            if rt_score >= 90:
                                image_key = "RT-Crit-Top"
                            elif rt_score >= 60:
                                image_key = "RT-Crit-Fresh"
                            else:
                                image_key = "RT-Crit-Rotten"
                                
                            formatted_reviews.append({
                                "source": "Rotten Tomatoes",
                                "rating": f"{rt_score}%",  # Already a percentage
                                "max_rating": "100%",
                                "image_key": image_key
                            })
                        except ValueError:
                            pass
                    
                    elif rating["Source"] == "Metacritic":
                        mc_value = rating["Value"].split("/")[0]
                        try:
                            mc_score = int(mc_value)
                            
                            # Determine Metacritic image based on score
                            image_key = "Metacritic"
                            if mc_score >= 90:
                                image_key = "MetacriticTop"
                                
                            formatted_reviews.append({
                                "source": "Metacritic",
                                "rating": f"{mc_score}%",  # Convert to percentage format
                                "max_rating": "100%",
                                "image_key": image_key
                            })
                        except ValueError:
                            pass
        
        # Process TMDB data
        if review_data.get("tmdb"):
            tmdb_data = review_data["tmdb"]
            
            if "vote_average" in tmdb_data and tmdb_data["vote_average"]:
                vote_average = tmdb_data["vote_average"]
                vote_count = tmdb_data.get("vote_count", 0)
                
                # Only include if there are enough votes to be meaningful
                if vote_count >= 10:
                    try:
                        # Convert from 0-10 scale to percentage
                        percentage_rating = int(round(float(vote_average) * 10))
                        
                        formatted_reviews.append({
                            "source": "TMDb",
                            "rating": f"{percentage_rating}%",  # Display as percentage
                            "original_rating": f"{vote_average:.1f}",  # Keep original for reference
                            "max_rating": "100%",  # Standardize max rating
                            "votes": vote_count,
                            "image_key": "TMDb"
                        })
                    except (ValueError, TypeError):
                        # Fallback in case of parsing errors
                        formatted_reviews.append({
                            "source": "TMDb",
                            "rating": f"{vote_average:.1f}",
                            "max_rating": "10",
                            "votes": vote_count,
                            "image_key": "TMDb"
                        })
        
        # Process AniDB data (placeholder)
        if review_data.get("anidb"):
            anidb_data = review_data["anidb"]
            
            if "rating" in anidb_data:
                try:
                    # Convert from 0-10 scale to percentage
                    anidb_rating = float(anidb_data["rating"])
                    percentage_rating = int(round(anidb_rating * 10))
                    
                    formatted_reviews.append({
                        "source": "AniDB",
                        "rating": f"{percentage_rating}%",  # Display as percentage
                        "original_rating": anidb_data["rating"],  # Keep original for reference
                        "max_rating": "100%",  # Standardize max rating
                        "image_key": "AniDB"
                    })
                except (ValueError, TypeError):
                    # Fallback to original format if conversion fails
                    formatted_reviews.append({
                        "source": "AniDB",
                        "rating": anidb_data["rating"],
                        "max_rating": "10",
                        "image_key": "AniDB"
                    })
        
        # If show_details is True, return detailed review information
        if show_details:
            return formatted_reviews
        else:
            # Return simplified data for badge creation
            simplified_reviews = []
            for review in formatted_reviews:
                # For badge creation, we use image_key for loading the image
                # and provide the rating as additional text for display if needed
                simplified_reviews.append({
                    "source": review["source"],
                    "image_key": review["image_key"],
                    "text": review.get("rating", "")
                })
            return simplified_reviews
    
    def get_reviews(self, item_id, show_details=False):
        """Get reviews for a media item from all available sources"""
        # Get item data from Jellyfin
        item_data = self.get_jellyfin_item_metadata(item_id)
        if not item_data:
            print("❌ Could not retrieve item data from Jellyfin")
            return []
        
        # Get IDs from different sources
        imdb_id = self.get_imdb_id(item_data)
        tmdb_id = self.get_tmdb_id(item_data)
        anidb_id = self.get_anidb_id(item_data)
        
        # Item type - movie or tv series
        media_type = "tv" if item_data.get("Type") == "Series" else "movie"
        
        # Collect review data from different sources
        review_data = {}
        
        # OMDB (includes IMDb, Rotten Tomatoes, Metacritic)
        if imdb_id and self.omdb_settings.get("api_key"):
            review_data["omdb"] = self.fetch_omdb_ratings(imdb_id)
        
        # TMDB
        if tmdb_id and self.tmdb_settings.get("api_key"):
            review_data["tmdb"] = self.fetch_tmdb_ratings(tmdb_id, media_type)
        
        # AniDB (with title search fallback)
        print(f"🔍 Checking AniDB: anidb_id={anidb_id}, settings_available={bool(self.anidb_settings)}")
        if self.anidb_settings:
            # Try with AniDB ID first, fall back to title search
            item_name = item_data.get('Name') if not anidb_id else None
            print(f"🔍 Fetching AniDB ratings (ID: {anidb_id}, Name: {item_name})")
            review_data["anidb"] = self.fetch_anidb_ratings(anidb_id, item_name)
        else:
            print(f"🔍 Skipping AniDB - no settings available")
        
        # Format the collected review data
        return self.format_review_data(review_data, show_details)

def display_reviews(reviews, item_title):
    """Display reviews in a human-readable format"""
    print(f"\n📊 Reviews for: {item_title}\n")
    print("-" * 50)
    
    if not reviews:
        print("No reviews found.")
        return
    
    for review in reviews:
        source = review.get("source", "Unknown")
        rating = review.get("rating", "N/A")
        max_rating = review.get("max_rating", "")
        votes = review.get("votes", "")
        
        print(f"🏆 {source}: {rating}" + (f"/{max_rating}" if max_rating else ""))
        if votes:
            print(f"   Votes: {votes}")
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Get reviews for a Jellyfin media item")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--show-reviews", action="store_true", help="Display reviews in human-readable format")
    parser.add_argument("--settings", default="settings.yaml", help="Settings file path")
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings(args.settings)
    
    # Create review fetcher
    review_fetcher = ReviewFetcher(settings)
    
    try:
        # Get item details for title
        jellyfin_settings = settings.get("api_keys", {}).get("Jellyfin", [{}])[0]
        item_details = get_jellyfin_item_details(
            jellyfin_settings.get("url", ""),
            jellyfin_settings.get("api_key", ""),
            jellyfin_settings.get("user_id", ""),
            args.itemid
        )
        
        if not item_details:
            print(f"❌ Could not retrieve item details for ID: {args.itemid}")
            return 1
        
        item_title = item_details.get("Name", "Unknown Title")
        
        # Get reviews with detailed information for display
        reviews = review_fetcher.get_reviews(args.itemid, show_details=True)
        
        # Display reviews if requested
        if args.show_reviews:
            display_reviews(reviews, item_title)
        else:
            # Just return the number of reviews found
            print(f"✅ Found {len(reviews)} reviews for '{item_title}'")
            
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
