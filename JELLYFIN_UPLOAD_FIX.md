# Jellyfin Poster Upload Fix

## Overview
The Jellyfin poster upload is failing with a 500 Internal Server Error. This document outlines the fixes we've implemented and next steps.

## Changes Made

1. **Enhanced Error Logging**
   - Added detailed response logging to capture full error messages from Jellyfin
   - Added authentication checks to verify API token permissions
   - Added user info checks before upload attempts

2. **Multiple Upload Approaches**
   The updated posterProcessor.js now tries multiple methods in sequence:
   - Method 1: Direct buffer upload with POST
   - Method 2: FormData multipart upload
   - Method 3: Index-based URL (`/Images/Primary/0`)
   - Method 4: PUT method instead of POST

3. **Added Test Script**
   Created `test-jellyfin-upload.js` to isolate and test the upload functionality

## Required Steps

1. **Install Dependencies**
   ```bash
   cd backend
   npm install form-data
   ```

2. **Run Test Script**
   ```bash
   cd backend
   node test-jellyfin-upload.js
   ```
   This will help identify if the issue is with:
   - API token permissions
   - Incorrect URL format
   - Server configuration

3. **Check Jellyfin Server Logs**
   The 500 error means something is wrong on the server side. Check:
   - `/var/log/jellyfin/` (Linux)
   - `%PROGRAMDATA%\Jellyfin\Server\log\` (Windows)
   Look for errors around the time of upload attempts.

## Common Issues & Solutions

1. **API Token Permissions**
   - Ensure the API token has administrative rights
   - Try regenerating the API token in Jellyfin dashboard

2. **Image Format**
   - Jellyfin might expect specific image formats
   - We're sending PNG, but JPEG might be required

3. **File Size**
   - Large posters might exceed server limits
   - Check Jellyfin's maximum upload size settings

4. **URL Format**
   - Some Jellyfin versions use different endpoints
   - The test script will try various formats

## Next Steps

1. Run the test script to see which upload method works
2. Check Jellyfin server logs for specific error messages
3. If still failing, consider:
   - Using Jellyfin's SDK/library instead of direct API calls
   - Checking if the image needs to be resized before upload
   - Verifying the media item exists and is accessible

## Debug Output Expected

After running the changes, you should see detailed logs like:
```
Deleting existing poster (if any): { url: '...', token: '***abcd' }
User info check: { status: 200, userId: '...', name: '...' }
Attempting method 1: Direct buffer upload...
Upload response: { status: 500, body: '...' }
Attempting method 2: FormData upload...
```

This will help pinpoint exactly which step fails and why.
