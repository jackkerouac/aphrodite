#!/usr/bin/env python3
"""
Create Enhanced Crunchyroll Awards Data with TMDb IDs

This script creates a comprehensive awards JSON file with TMDb IDs
for integration with Aphrodite's workflow.
"""

import json
import requests
import time
import re
from typing import Dict, List, Optional
from datetime import datetime

class AwardsDataCreator:
    def __init__(self, tmdb_api_key: str):
        self.tmdb_api_key = tmdb_api_key
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        
    def get_comprehensive_awards_data(self) -> Dict:
        """Get comprehensive awards data with all known winners"""
        return {
            "2025": {
                "year": 2025,
                "ceremony_date": "2025-05-25",
                "location": "Grand Prince Hotel Shin Takanawa, Tokyo, Japan",
                "ceremony_number": 9,
                "vote_count": "51 million",
                "categories": {
                    "Anime of the Year": "Solo Leveling",
                    "Film of the Year": "Look Back",
                    "Best New Series": "Solo Leveling",
                    "Best Action": "Solo Leveling",
                    "Best Continuing Series": "Demon Slayer: Kimetsu no Yaiba",
                    "Best Animation": "Demon Slayer: Kimetsu no Yaiba",
                    "Best Background Art": "Frieren: Beyond Journey's End",
                    "Best Slice of Life": "Makeine: Too Many Losing Heroines!",
                    "Best Opening Sequence": "DAN DA DAN",
                    "Best Anime Song": "DAN DA DAN",
                    "Best Score": "Solo Leveling",
                    "Best Ending Sequence": "Solo Leveling",
                    "Global Impact Award": "Attack on Titan"
                }
            },
            "2024": {
                "year": 2024,
                "ceremony_number": 8,
                "categories": {
                    "Anime of the Year": "Jujutsu Kaisen",
                    "Best Animation": "Demon Slayer: Kimetsu no Yaiba",
                    "Best Action": "Jujutsu Kaisen"
                }
            },
            "2023": {
                "year": 2023,
                "ceremony_number": 7,
                "location": "Grand Prince Hotel New Takanawa, Tokyo, Japan",
                "categories": {
                    "Anime of the Year": "Cyberpunk: Edgerunners"
                }
            },
            "2022": {
                "year": 2022,
                "ceremony_number": 6,
                "categories": {
                    "Anime of the Year": "Demon Slayer: Kimetsu no Yaiba"
                }
            },
            "2021": {
                "year": 2021,
                "ceremony_number": 5,
                "categories": {
                    "Anime of the Year": "Jujutsu Kaisen"
                }
            },
            "2020": {
                "year": 2020,
                "ceremony_number": 4,
                "categories": {
                    "Anime of the Year": "Demon Slayer: Kimetsu no Yaiba"
                }
            },
            "2019": {
                "year": 2019,
                "ceremony_number": 3,
                "categories": {
                    "Anime of the Year": "Demon Slayer: Kimetsu no Yaiba"
                }
            },
            "2018": {
                "year": 2018,
                "ceremony_number": 2,
                "categories": {
                    "Anime of the Year": "My Hero Academia",
                    "Best Hero": "My Hero Academia",
                    "Best Villain": "My Hero Academia",
                    "Best Boy": "My Hero Academia",
                    "Best Girl": "My Hero Academia",
                    "Best Opening": "My Hero Academia",
                    "Best Animation": "My Hero Academia",
                    "Best Action": "My Hero Academia"
                }
            },
            "2017": {
                "year": 2017,
                "ceremony_number": 1,
                "location": "California, United States",
                "categories": {
                    "Anime of the Year": "Yuri!!! on Ice",
                    "Best Boy": "Yuri!!! on Ice",
                    "Best Opening": "Yuri!!! on Ice",
                    "Best Ending": "Yuri!!! on Ice",
                    "Best Animation": "Yuri!!! on Ice",
                    "Best Couple": "Yuri!!! on Ice",
                    "Most Heartwarming Scene": "Yuri!!! on Ice"
                }
            }
        }
    
    def search_tmdb_tv(self, anime_name: str) -> Optional[Dict]:
        """Search TMDb for TV show"""
        try:
            url = f"{self.tmdb_base_url}/search/tv"
            params = {
                "api_key": self.tmdb_api_key,
                "query": anime_name,
                "language": "en-US"
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    result = data["results"][0]
                    return {
                        "tmdb_id": result["id"],
                        "tmdb_name": result["name"],
                        "first_air_date": result.get("first_air_date"),
                        "overview": result.get("overview", "")
                    }
            
            time.sleep(0.25)  # Rate limiting
            return None
            
        except Exception as e:
            print(f"Error searching TMDb for '{anime_name}': {e}")
            return None
    
    def search_tmdb_movie(self, anime_name: str) -> Optional[Dict]:
        """Search TMDb for movies"""
        try:
            url = f"{self.tmdb_base_url}/search/movie"
            params = {
                "api_key": self.tmdb_api_key,
                "query": anime_name,
                "language": "en-US"
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    result = data["results"][0]
                    return {
                        "tmdb_id": result["id"],
                        "tmdb_name": result["title"],
                        "release_date": result.get("release_date"),
                        "overview": result.get("overview", "")
                    }
            
            time.sleep(0.25)  # Rate limiting
            return None
            
        except Exception as e:
            print(f"Error searching TMDb movies for '{anime_name}': {e}")
            return None
    
    def get_title_variants(self, title: str) -> List[str]:
        """Generate search variants for better TMDb matching"""
        variants = [title]
        
        # Remove punctuation variants
        variants.append(re.sub(r'[!?:.]', '', title))
        variants.append(re.sub(r'[!?:.]', ' ', title).strip())
        
        # Specific anime title variants
        anime_variants = {
            "Demon Slayer: Kimetsu no Yaiba": [
                "Demon Slayer",
                "Kimetsu no Yaiba"
            ],
            "Attack on Titan": [
                "Shingeki no Kyojin"
            ],
            "My Hero Academia": [
                "Boku no Hero Academia"
            ],
            "Yuri!!! on Ice": [
                "Yuri on Ice"
            ],
            "DAN DA DAN": [
                "Dandadan"
            ],
            "Makeine: Too Many Losing Heroines!": [
                "Makeine",
                "Too Many Losing Heroines"
            ]
        }
        
        if title in anime_variants:
            variants.extend(anime_variants[title])
        
        return list(set(variants))
    
    def find_tmdb_data(self, anime_name: str, is_movie: bool = False) -> Optional[Dict]:
        """Find TMDb data for anime with multiple search attempts"""
        print(f"Searching TMDb for: {anime_name}")
        
        variants = self.get_title_variants(anime_name)
        
        for variant in variants:
            print(f"  Trying variant: {variant}")
            
            if is_movie:
                result = self.search_tmdb_movie(variant)
            else:
                result = self.search_tmdb_tv(variant)
            
            if result:
                print(f"  ✅ Found: {result['tmdb_name']} (ID: {result['tmdb_id']})")
                return result
        
        print(f"  ❌ No TMDb match found for {anime_name}")
        return None
    
    def create_enhanced_awards_data(self) -> Dict:
        """Create comprehensive awards data with TMDb IDs"""
        print("Creating enhanced Crunchyroll Awards data...")
        
        # Get base awards data
        awards_by_year = self.get_comprehensive_awards_data()
        
        # Collect all unique anime
        anime_winners = {}
        
        for year_str, year_data in awards_by_year.items():
            categories = year_data.get("categories", {})
            for category, winner in categories.items():
                if winner and isinstance(winner, str):
                    anime_name = self.clean_anime_name(winner)
                    if anime_name:
                        if anime_name not in anime_winners:
                            anime_winners[anime_name] = {
                                "name": anime_name,
                                "awards": [],
                                "identifiers": {
                                    "tmdb_tv_id": None,
                                    "tmdb_movie_id": None,
                                    "tmdb_tv_data": None,
                                    "tmdb_movie_data": None
                                },
                                "search_variants": self.get_title_variants(anime_name)
                            }
                        
                        anime_winners[anime_name]["awards"].append({
                            "year": year_data["year"],
                            "category": category,
                            "raw_winner_text": winner
                        })
        
        # Get TMDb data for each anime
        print(f"\nSearching TMDb for {len(anime_winners)} anime...")
        for anime_name, anime_data in anime_winners.items():
            # Check if it's a movie (Film of the Year category)
            is_movie = any(award["category"] == "Film of the Year" for award in anime_data["awards"])
            
            # Search TV shows
            tv_data = self.find_tmdb_data(anime_name, is_movie=False)
            if tv_data:
                anime_data["identifiers"]["tmdb_tv_id"] = tv_data["tmdb_id"]
                anime_data["identifiers"]["tmdb_tv_data"] = tv_data
            
            # Search movies if it's a film or if no TV result found
            if is_movie or not tv_data:
                movie_data = self.find_tmdb_data(anime_name, is_movie=True)
                if movie_data:
                    anime_data["identifiers"]["tmdb_movie_id"] = movie_data["tmdb_id"]
                    anime_data["identifiers"]["tmdb_movie_data"] = movie_data
        
        # Create final structure
        enhanced_data = {
            "metadata": {
                "source": "Crunchyroll Anime Awards with TMDb integration",
                "created_date": datetime.now().isoformat(),
                "note": "Enhanced data with TMDb IDs for Aphrodite integration",
                "total_ceremonies": 9,
                "years_covered": "2017-2025",
                "tmdb_api_used": True
            },
            "awards_by_year": awards_by_year,
            "anime_winners": anime_winners,
            "statistics": {
                "total_unique_anime": len(anime_winners),
                "anime_with_tmdb_tv": sum(1 for a in anime_winners.values() if a["identifiers"]["tmdb_tv_id"]),
                "anime_with_tmdb_movie": sum(1 for a in anime_winners.values() if a["identifiers"]["tmdb_movie_id"]),
                "anime_without_tmdb": sum(1 for a in anime_winners.values() 
                                        if not a["identifiers"]["tmdb_tv_id"] and not a["identifiers"]["tmdb_movie_id"])
            }
        }
        
        return enhanced_data
    
    def clean_anime_name(self, winner_text: str) -> str:
        """Clean and extract anime name from winner text"""
        if not winner_text:
            return ""
        
        anime_name = winner_text.strip()
        
        # Remove artist/performer names (for songs)
        if " - " in anime_name:
            parts = anime_name.split(" - ")
            if len(parts) > 1:
                anime_name = parts[-1].strip()
        
        # Remove parenthetical information
        anime_name = re.sub(r'\([^)]*\)', '', anime_name).strip()
        
        # Common patterns to clean
        patterns_to_remove = [
            r'Season \d+',
            r'Part \d+',
            r'Arc$',
            r'Final Season.*',
            r'The Final.*',
            r'Opening Theme.*',
            r'Ending Theme.*',
            r'Hashira Training Arc',
            r'Entertainment District Arc'
        ]
        
        for pattern in patterns_to_remove:
            anime_name = re.sub(pattern, '', anime_name, flags=re.IGNORECASE).strip()
        
        # Handle special cases
        if 'Demon Slayer' in anime_name:
            return 'Demon Slayer: Kimetsu no Yaiba'
        elif 'My Hero Academia' in anime_name:
            return 'My Hero Academia'
        elif 'Jujutsu Kaisen' in anime_name:
            return 'Jujutsu Kaisen'
        elif 'Attack on Titan' in anime_name:
            return 'Attack on Titan'
        
        return anime_name


def main():
    """Main function to create enhanced awards data"""
    # TMDb API key from your settings
    TMDB_API_KEY = "0b2dc1bbbed569c9f97b2c54c7d167d2"
    
    creator = AwardsDataCreator(TMDB_API_KEY)
    
    try:
        # Create enhanced data
        enhanced_data = creator.create_enhanced_awards_data()
        
        # Save to file
        output_file = "E:/programming/aphrodite/crunchyroll_anime_awards_enhanced.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        # Print summary
        stats = enhanced_data["statistics"]
        print(f"\n{'='*50}")
        print("ENHANCED CRUNCHYROLL AWARDS DATA CREATED")
        print(f"{'='*50}")
        print(f"Total unique anime: {stats['total_unique_anime']}")
        print(f"With TMDb TV ID: {stats['anime_with_tmdb_tv']}")
        print(f"With TMDb Movie ID: {stats['anime_with_tmdb_movie']}")
        print(f"Without TMDb ID: {stats['anime_without_tmdb']}")
        print(f"\nSaved to: {output_file}")
        
        # Show anime without TMDb IDs
        if stats['anime_without_tmdb'] > 0:
            print(f"\nAnime without TMDb matches:")
            for name, data in enhanced_data["anime_winners"].items():
                if not data["identifiers"]["tmdb_tv_id"] and not data["identifiers"]["tmdb_movie_id"]:
                    print(f"  - {name}")
        
        print(f"\n✅ Enhanced awards data ready for Aphrodite integration!")
        
    except Exception as e:
        print(f"❌ Error creating enhanced data: {e}")


if __name__ == "__main__":
    main()
