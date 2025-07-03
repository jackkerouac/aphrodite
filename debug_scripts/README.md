# Debug Scripts for Aphrodite

This directory contains debug scripts to help troubleshoot issues with the Aphrodite poster processing system.

## Available Scripts

### 1. `test_jellyfin_connection.py`
Tests the basic Jellyfin connection and poster download functionality.

**Usage:**
```bash
cd /path/to/aphrodite
python debug_scripts/test_jellyfin_connection.py
```

**What it tests:**
- Jellyfin server connection
- Library retrieval
- Library items retrieval
- Poster URL generation
- Poster download

### 2. `test_poster_processing.py`
Tests the poster processing workflow that the worker uses.

**Usage:**
```bash
cd /path/to/aphrodite
python debug_scripts/test_poster_processing.py
```

**What it tests:**
- Jellyfin connection
- Test item retrieval
- Poster processor initialization
- Poster download workflow

## Running the Scripts

1. **Make sure you're in the Aphrodite root directory**
2. **Ensure your Jellyfin configuration is set up** (either in database or environment variables)
3. **Run the scripts using Python 3:**
   ```bash
   python debug_scripts/test_jellyfin_connection.py
   python debug_scripts/test_poster_processing.py
   ```

## Common Issues and Solutions

### "No Jellyfin settings available"
- Check that your Jellyfin URL and API key are properly configured
- Verify environment variables: `JELLYFIN_URL`, `JELLYFIN_API_KEY`
- Check the database settings in the web interface

### "No poster found for item"
- Verify the item IDs are valid in Jellyfin
- Check that the items actually have poster images
- Confirm API authentication is working

### HTTP 401 or 403 errors
- Verify your Jellyfin API key is correct
- Check that the API key has the necessary permissions
- Ensure the Jellyfin server is accessible from your environment

## Debugging Output

The scripts will output detailed information about:
- Connection status
- Authentication results
- Item discovery
- Poster URL generation
- Download success/failure

Use this information to identify where the poster processing pipeline is failing.

## Next Steps

If these scripts identify issues:
1. Fix the Jellyfin configuration
2. Rebuild the Docker container
3. Test the batch processing again
4. Check the worker logs for the same error patterns
