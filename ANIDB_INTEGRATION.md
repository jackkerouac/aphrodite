# AniDB Integration Guide

## Overview

Aphrodite now supports fetching anime ratings from AniDB! Unlike other services that require explicit IDs in Jellyfin metadata, AniDB integration works by searching for anime titles automatically.

## How It Works

1. **Check for AniDB ID**: First, Aphrodite checks if the anime already has an AniDB ID in its Jellyfin metadata
2. **Title Search Fallback**: If no AniDB ID is found, it automatically searches AniDB using the anime's title
3. **Rating Extraction**: Once an anime is found, Aphrodite fetches the rating from the AniDB page
4. **Caching**: Results are cached to avoid repeated API calls

## Configuration

Make sure your `settings.yaml` includes AniDB credentials:

```yaml
api_keys:
  aniDB:
  - username: your_anidb_username
    password: your_anidb_password
    version: 1
    client_name: your_client_name
    language: en
    cache_expiration: 60
```

## Features

### Smart Title Cleaning
The system automatically cleans anime titles for better search results by removing:
- Year suffixes like "(2022)"
- Season indicators like "Season 2" or "S2"
- Part indicators like "Part 1"
- Volume indicators like "Vol. 1"

### Rate Limiting
Built-in rate limiting (1 second between requests) to be respectful to AniDB's servers.

### Caching
Search results and ratings are cached to minimize API calls and improve performance.

### Multiple Rating Extraction Methods
The system tries multiple methods to extract ratings from AniDB pages to handle different page layouts.

## Usage

AniDB ratings will automatically be included when processing anime with review badges enabled. No additional configuration needed beyond the API credentials.

### Example Log Output

```
🔍 Checking AniDB: anidb_id=None, settings_available=True
🔍 Fetching AniDB ratings (ID: None, Name: Aharen-san wa Hakarenai)
🔍 No AniDB ID provided, searching by title: Aharen-san wa Hakarenai
🔍 Cleaned search title: Aharen-san wa Hakarenai
🌐 Making AniDB search request...
✅ Found AniDB ID: 16201 for title: Aharen-san wa Hakarenai
🔍 Fetching AniDB rating for ID: 16201
🌐 Fetching AniDB anime info from: https://anidb.net/anime/16201
✅ Found rating (method 2): 7.2
✅ Successfully fetched AniDB rating: 7.2
```

## Troubleshooting

### No Rating Found
- The anime might not exist on AniDB
- The title might be too different from AniDB's title
- AniDB's page structure might have changed

### Search Failures
- Check your AniDB credentials
- Verify network connectivity
- AniDB might be temporarily unavailable

### Rate Limiting
- The system includes built-in delays to respect AniDB's servers
- If processing many anime, expect longer processing times

## Dependencies

The AniDB integration requires:
- `beautifulsoup4>=4.11.0` for HTML parsing
- `requests>=2.27.1` for HTTP requests

These are automatically included in the updated `requirements.txt`.
