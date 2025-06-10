# Data formatting and main review aggregation methods
from aphrodite_helpers.minimal_logger import log_error, log_warning, log_milestone, LoggedOperation

class ReviewFormatterMixin:
    def format_review_data(self, review_data, show_details=False):
        """Format the review data from various sources into a structured format"""
        formatted_reviews = []
        
        # Get image mappings from settings
        image_mappings = self.badge_settings.get("ImageBadges", {}).get("image_mapping", {})
        
        # Process OMDB data
        if review_data.get("omdb"):
            omdb_data = review_data["omdb"]
            
            # IMDB Rating - Convert to percentage (FIXED: Priority-based selection)
            if "imdbRating" in omdb_data and omdb_data["imdbRating"] != "N/A":
                try:
                    # Convert rating from 0-10 scale to percentage
                    imdb_rating = float(omdb_data["imdbRating"])
                    percentage_rating = int(round(imdb_rating * 10))
                    
                    # Get vote count for Top badge qualification
                    imdb_votes_str = omdb_data.get("imdbVotes", "0").replace(",", "")
                    imdb_votes = int(imdb_votes_str) if imdb_votes_str.isdigit() else 0
                    
                    # PRIORITY-BASED SELECTION: Only one IMDb badge per movie
                    # Priority: Top 250 > Top 1000 > Regular IMDb
                    if imdb_rating >= 8.5 and imdb_votes >= 250000:
                        # Top 250 takes priority
                        formatted_reviews.append({
                            "source": "IMDb Top 250",
                            "rating": f"{percentage_rating}%",
                            "original_rating": omdb_data["imdbRating"],
                            "max_rating": "100%",
                            "votes": omdb_data.get("imdbVotes", "N/A"),
                            "image_key": "IMDbTop250"
                        })
                    elif imdb_rating >= 8.0 and imdb_votes >= 100000:
                        # Top 1000 takes priority over regular
                        formatted_reviews.append({
                            "source": "IMDb Top 1000",
                            "rating": f"{percentage_rating}%",
                            "original_rating": omdb_data["imdbRating"],
                            "max_rating": "100%",
                            "votes": omdb_data.get("imdbVotes", "N/A"),
                            "image_key": "IMDbTop1000"
                        })
                    else:
                        # Regular IMDb badge
                        formatted_reviews.append({
                            "source": "IMDb",
                            "rating": f"{percentage_rating}%",
                            "original_rating": omdb_data["imdbRating"],
                            "max_rating": "100%",
                            "votes": omdb_data.get("imdbVotes", "N/A"),
                            "image_key": "IMDb"
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
        
        # Process AniDB data
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
        
        # Process MyAnimeList data (via Jikan API)
        if review_data.get("myanimelist"):
            mal_data = review_data["myanimelist"]
            
            if "rating" in mal_data and mal_data["rating"]:
                try:
                    # Convert from 0-10 scale to percentage
                    mal_rating = float(mal_data["rating"])
                    percentage_rating = int(round(mal_rating * 10))
                    
                    formatted_reviews.append({
                        "source": "MyAnimeList",
                        "rating": f"{percentage_rating}%",  # Display as percentage
                        "original_rating": f"{mal_rating:.2f}",  # Keep original for reference
                        "max_rating": "100%",  # Standardize max rating
                        "votes": mal_data.get("scored_by", "N/A"),
                        "rank": mal_data.get("rank", "N/A"),
                        "popularity": mal_data.get("popularity", "N/A"),
                        "image_key": "MAL"  # Use MAL image key from badge settings
                    })
                except (ValueError, TypeError):
                    # Fallback to original format if conversion fails
                    formatted_reviews.append({
                        "source": "MyAnimeList",
                        "rating": f"{mal_data['rating']:.2f}",
                        "max_rating": "10",
                        "votes": mal_data.get("scored_by", "N/A"),
                        "image_key": "MAL"
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
            log_error("Could not retrieve item data from Jellyfin", "review_formatter")
            return []
        
        # Get IDs from different sources
        imdb_id = self.get_imdb_id(item_data)
        tmdb_id = self.get_tmdb_id(item_data)
        anidb_id = self.get_anidb_id(item_data)
        mal_id = self.get_mal_id(item_data)
        
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
        
        # AniDB (with auto-discovery fallback)
        if self.anidb_settings:
            # Try with AniDB ID first, fall back to auto-discovery
            item_name = item_data.get('Name')
            review_data["anidb"] = self.fetch_anidb_ratings(anidb_id, item_name, item_data)
        
        # MyAnimeList (via Jikan API - check if enabled in preferences)
        from aphrodite_helpers.review_preferences import ReviewPreferences
        try:
            review_prefs = ReviewPreferences()
            should_include = review_prefs.should_include_source('MyAnimeList', item_data)
            
            if should_include:
                item_name = item_data.get('Name')
                review_data["myanimelist"] = self.fetch_myanimelist_ratings(mal_id, item_name, item_data)
        except Exception as e:
            log_warning(f"Error checking MyAnimeList preferences: {e}", "review_formatter")
            # Fallback: fetch anyway if we can't check preferences
            item_name = item_data.get('Name')
            review_data["myanimelist"] = self.fetch_myanimelist_ratings(mal_id, item_name, item_data)
        
        # Format the collected review data
        formatted_reviews = self.format_review_data(review_data, show_details)
        
        # Apply user preferences to filter and order reviews
        from aphrodite_helpers.review_preferences import filter_reviews_by_preferences
        filtered_reviews = filter_reviews_by_preferences(formatted_reviews, item_data)
        
        return filtered_reviews
