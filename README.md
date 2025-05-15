# Aphrodite - Jellyfin Poster Processing System

Aphrodite is a Python-based utility for enhancing Jellyfin media posters by adding informational badges (such as audio codec information) to them.

## Features

- Connects to a Jellyfin server to retrieve media information
- Downloads original media posters
- Creates customizable badges with audio codec information
- Applies badges to posters in configurable positions
- Uploads modified posters back to Jellyfin
- Includes a robust state management system for tracking processing status
- Built-in retry mechanism for handling transient failures

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aphrodite-python.git
   cd aphrodite-python
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

4. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Configure your settings (see Configuration section)

## Configuration

1. Copy the example settings file:
   ```
   cp settings.example.yaml settings.yaml
   ```

2. Edit `settings.yaml` with your Jellyfin server details:
   ```yaml
   api_keys:
     Jellyfin:
       - url: "https://your-jellyfin-server.com"
         api_key: "your-api-key-here"
         user_id: "your-user-id-here"
   ```

3. Customize badge appearance in `badge_settings_audio.yml`

## Usage

Aphrodite provides several command-line interfaces for different operations:

### Check System Settings and Jellyfin Connection

```
python aphrodite.py check
```

This command verifies your settings and connection to Jellyfin, displaying all available libraries and their item counts.

### Show Processing Status

```
python aphrodite.py status
```

Displays the current status of all items being processed, including counts for each state and details about failed items.

### Process a Single Item

```
python aphrodite.py item ITEM_ID [--retries MAX_RETRIES]
```

Processes a single Jellyfin item, creating and applying a badge with its audio codec information.

### Process an Entire Library

```
python aphrodite.py library LIBRARY_ID [--limit NUM_ITEMS] [--retries MAX_RETRIES]
```

Processes all items in a specific Jellyfin library. Use `--limit` to restrict the number of items processed.

### Process Items in a Specific State

```
python aphrodite.py state STATE_NAME [--limit NUM_ITEMS] [--retries MAX_RETRIES]
```

Processes items in a specific state (pending, downloaded, resized, badged, uploaded, or failed).

### Retry Failed Items

```
python aphrodite.py retry [--limit NUM_ITEMS] [--retries MAX_RETRIES]
```

Retries processing for all items that previously failed.

## Individual Module Usage

Aphrodite's components can also be used independently:

### Get Media Information

```
python -m aphrodite_helpers.get_media_info --itemid ITEM_ID [--info-only] [--output OUTPUT_DIR]
```

Retrieves media information from Jellyfin and optionally creates a badge with the audio codec.

### Download Poster

```
python -m aphrodite_helpers.poster_fetcher --itemid ITEM_ID [--output OUTPUT_DIR]
```

Downloads a poster for a specific Jellyfin item.

### Apply Badge

```
python -m aphrodite_helpers.apply_badge [--input INPUT_DIR] [--output OUTPUT_DIR] [--text TEXT]
```

Applies badges to all posters in the input directory. Use `--test` to create a test badge without processing posters.

### Upload Poster

```
python -m aphrodite_helpers.poster_uploader --itemid ITEM_ID --poster POSTER_PATH [--retries MAX_RETRIES]
```

Uploads a modified poster back to Jellyfin.

### State Management

```
python -m aphrodite_helpers.state_manager [--list STATE] [--count] [--info ITEM_ID] [--retry ITEM_ID] [--cleanup]
```

Manage the state of items being processed.

## Directory Structure

- `aphrodite.py` - Main entry point
- `settings.yaml` - Global configuration
- `badge_settings_audio.yml` - Badge styling configuration
- `aphrodite_helpers/` - Helper modules
  - `__init__.py`
  - `check_jellyfin_connection.py` - Jellyfin API connection utilities
  - `settings_validator.py` - Validates configuration files
  - `poster_fetcher.py` - Downloads posters from Jellyfin
  - `get_media_info.py` - Retrieves media metadata
  - `apply_badge.py` - Creates and applies badges
  - `poster_uploader.py` - Uploads modified posters back to Jellyfin
  - `state_manager.py` - Manages processing state
- `posters/` - Directory for posters
  - `original/` - Original downloaded posters
  - `working/` - Temporary working directory
  - `modified/` - Final output with badges
- `workflow_state/` - State tracking directories
  - `pending/` - Items identified but not yet processed
  - `downloaded/` - Items with successfully downloaded posters
  - `resized/` - Items with resized posters
  - `badged/` - Items with badges applied
  - `uploaded/` - Items with posters successfully uploaded
  - `failed/` - Items that failed during processing

## State Management System

Aphrodite includes a robust state management system to track the progress of items through the processing pipeline:

1. Each item is represented by a state file (JSON) containing metadata about the item.
2. As the item progresses through the workflow, its state file moves between different state directories.
3. A state transition updates both the state file contents and moves it to the appropriate directory.
4. Failure handling includes retry logic and detailed error tracking.

Items can be in one of the following states:
- `pending` - Item identified but processing not started
- `downloaded` - Poster successfully downloaded
- `resized` - Poster resized if needed
- `badged` - Badge successfully applied to poster
- `uploaded` - Modified poster uploaded to Jellyfin
- `failed` - Processing failed at some point

## Badge Customization

Badges can be customized by editing the `badge_settings_audio.yml` file. Available options include:

- **Background**: Color, opacity
- **Border**: Color, width, radius
- **Shadow**: Enable/disable, blur, offset
- **Text**: Font, color, size
- **Position**: Top-left, top-right, bottom-left, bottom-right
- **Size**: Fixed or dynamic sizing based on text

## Requirements

- Python 3.7+
- Pillow (for image processing)
- requests (for API communication)
- PyYAML (for configuration)

## License

[MIT License](LICENSE)
