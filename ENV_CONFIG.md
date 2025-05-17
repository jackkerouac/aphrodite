# Environment Variable Configuration

Aphrodite-Python Docker supports configuration via environment variables, allowing you to set up your instance without directly editing the YAML files. This is particularly useful for container deployments and automated setups.

## Using Environment Variables

There are two ways to provide environment variables:

1. **In the `.env` file** - Copy the `.env.template` file to `.env` and edit the values
2. **In the `docker-compose.yml` file** - Add environment variables directly under the `environment:` section
3. **When running Docker directly** - Use the `-e` flag (e.g., `docker run -e APHRODITE_JELLYFIN_URL=https://jellyfin.example.com ...`)

## Available Configuration Variables

### Jellyfin Configuration
- `APHRODITE_JELLYFIN_URL` - Your Jellyfin server URL
- `APHRODITE_JELLYFIN_API_KEY` - Your Jellyfin API key
- `APHRODITE_JELLYFIN_USER_ID` - Your Jellyfin user ID

### OMDB API Configuration
- `APHRODITE_OMDB_API_KEY` - Your OMDB API key
- `APHRODITE_OMDB_CACHE_EXPIRATION` - Cache expiration in days

### TMDB API Configuration
- `APHRODITE_TMDB_API_KEY` - Your TMDB API key
- `APHRODITE_TMDB_CACHE_EXPIRATION` - Cache expiration in days
- `APHRODITE_TMDB_LANGUAGE` - Preferred language code (e.g., `en`)
- `APHRODITE_TMDB_REGION` - Preferred region code (e.g., `US`)

### aniDB Configuration
- `APHRODITE_ANIDB_USERNAME` - Your aniDB username
- `APHRODITE_ANIDB_PASSWORD` - Your aniDB password
- `APHRODITE_ANIDB_VERSION` - API version
- `APHRODITE_ANIDB_CLIENT_NAME` - Your client name
- `APHRODITE_ANIDB_LANGUAGE` - Preferred language code
- `APHRODITE_ANIDB_CACHE_EXPIRATION` - Cache expiration in days

### Audio Badge Settings
- `APHRODITE_AUDIO_BADGE_POSITION` - Badge position (`top-left`, `top-right`, `bottom-left`, `bottom-right`)
- `APHRODITE_AUDIO_BADGE_SIZE` - Badge size in pixels
- `APHRODITE_AUDIO_EDGE_PADDING` - Padding from edge in pixels
- `APHRODITE_AUDIO_TEXT_PADDING` - Text padding in pixels
- `APHRODITE_AUDIO_DYNAMIC_SIZING` - Enable dynamic sizing (`true` or `false`)
- `APHRODITE_AUDIO_FONT` - Font file name
- `APHRODITE_AUDIO_TEXT_COLOR` - Text color (hex code)
- `APHRODITE_AUDIO_BG_COLOR` - Background color (hex code)
- `APHRODITE_AUDIO_BG_OPACITY` - Background opacity (0-100)

### Resolution Badge Settings
- `APHRODITE_RESOLUTION_BADGE_POSITION` - Badge position
- `APHRODITE_RESOLUTION_BADGE_SIZE` - Badge size in pixels
- `APHRODITE_RESOLUTION_EDGE_PADDING` - Padding from edge in pixels
- `APHRODITE_RESOLUTION_TEXT_PADDING` - Text padding in pixels
- `APHRODITE_RESOLUTION_DYNAMIC_SIZING` - Enable dynamic sizing
- `APHRODITE_RESOLUTION_FONT` - Font file name
- `APHRODITE_RESOLUTION_TEXT_COLOR` - Text color (hex code)
- `APHRODITE_RESOLUTION_BG_COLOR` - Background color (hex code)
- `APHRODITE_RESOLUTION_BG_OPACITY` - Background opacity (0-100)

### Review Badge Settings
- `APHRODITE_REVIEW_BADGE_POSITION` - Badge position
- `APHRODITE_REVIEW_BADGE_SIZE` - Badge size in pixels
- `APHRODITE_REVIEW_EDGE_PADDING` - Padding from edge in pixels
- `APHRODITE_REVIEW_TEXT_PADDING` - Text padding in pixels
- `APHRODITE_REVIEW_BADGE_ORIENTATION` - Badge orientation (`vertical` or `horizontal`)
- `APHRODITE_REVIEW_BADGE_SPACING` - Spacing between badges in pixels
- `APHRODITE_REVIEW_MAX_BADGES` - Maximum number of badges to display
- `APHRODITE_REVIEW_DYNAMIC_SIZING` - Enable dynamic sizing
- `APHRODITE_REVIEW_FONT` - Font file name
- `APHRODITE_REVIEW_TEXT_COLOR` - Text color (hex code)
- `APHRODITE_REVIEW_BG_COLOR` - Background color (hex code)
- `APHRODITE_REVIEW_BG_OPACITY` - Background opacity (0-100)

## Priority Order

Configuration values are applied in the following order (later values override earlier ones):

1. Default values in the YAML files
2. Values from mounted configuration files
3. Environment variables

This means environment variables will always take precedence over values in the configuration files.
