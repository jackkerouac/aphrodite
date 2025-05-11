# Jellyfin Authentication Debug Guide

## Problem Summary
The Jellyfin poster upload is failing with a 500 Internal Server Error. Initial testing shows that authentication is failing with a 400 Bad Request, suggesting the API token format or headers are incorrect.

## Test Scripts Created

### 1. API Key Analysis (`test-api-key.js`)
```bash
cd backend
node test-api-key.js
```
This script analyzes the API key format stored in the database to check for:
- Extra spaces or characters
- Correct format (hex, alphanumeric, base64)
- Length and type

### 2. Authentication Test (`test-jellyfin-auth.js`)
```bash
cd backend
node test-jellyfin-auth.js
```
This script tests multiple authentication header formats:
- `X-Emby-Token`
- `X-MediaBrowser-Token`
- `Authorization: MediaBrowser Token="..."`
- `Authorization: Bearer ...`
- `Authorization: Emby Token="..."`
- `X-Emby-Authorization`

### 3. Upload Test (`test-jellyfin-upload.js`)
```bash
cd backend
node test-jellyfin-upload.js
```
This script tests the actual upload process with different methods.

## Common Issues & Solutions

### 1. API Token Format Issues

**Symptoms:**
- Authentication returns 400 Bad Request
- Token appears valid but doesn't work

**Solutions:**
- Check if the token has extra spaces: `token.trim()`
- Verify the token is the API key, not a user password
- Regenerate the API key in Jellyfin dashboard

### 2. Wrong Header Format

**Symptoms:**
- Authentication fails with all header formats
- Server expects different authentication method

**Solutions:**
- Run `test-jellyfin-auth.js` to find working format
- Check Jellyfin version (10.10.7 in your case)
- Try device authentication if API key fails

### 3. Permission Issues

**Symptoms:**
- Authentication works but upload fails
- 500 error on image operations

**Solutions:**
- Ensure API key has administrative permissions
- Check if the user has media management rights
- Verify the item exists and is accessible

## Step-by-Step Debugging Process

1. **Verify API Key Format**
   ```bash
   node test-api-key.js
   ```
   - Check for extra spaces or invalid characters
   - Confirm it's the correct type of key

2. **Find Working Authentication**
   ```bash
   node test-jellyfin-auth.js
   ```
   - This will try all authentication methods
   - Note which one works

3. **Update Code with Working Auth**
   - Once you find the working auth format, update `posterProcessor.js`
   - Use the exact header format that worked

4. **Test Upload Again**
   ```bash
   node test-jellyfin-upload.js
   ```
   - Should now authenticate properly
   - If still failing, check server logs

## Server Log Locations

Check Jellyfin server logs for detailed error messages:

**Linux:**
```bash
tail -f /var/log/jellyfin/log_*.log
```

**Windows:**
```
C:\ProgramData\Jellyfin\Server\log\log_*.log
```

**Docker:**
```bash
docker logs jellyfin
```

## Alternative Solutions

If API key authentication continues to fail:

1. **Generate New API Key**
   - Jellyfin Dashboard → API Keys → Add API Key
   - Update database with new key

2. **Use Device Authentication**
   - Some Jellyfin setups require device-based auth
   - This involves registering a device first

3. **Check Reverse Proxy**
   - Your server is behind Cloudflare
   - Ensure headers aren't being stripped

4. **Try Direct Server Connection**
   - Bypass Cloudflare if possible
   - Test with local/direct server URL

## Expected Working Flow

1. Find correct authentication header format
2. Successfully authenticate to `/Users/Me`
3. Delete existing poster (if any)
4. Upload new poster with correct headers
5. Verify upload success

## Next Steps After Running Tests

1. Share the output of all test scripts
2. Check Jellyfin server logs
3. Implement the working authentication format
4. Retry the poster upload process

The test scripts will provide detailed information about what's failing and help identify the correct authentication method for your Jellyfin server.
