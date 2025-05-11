# Jellyfin Authentication Solution

## Problem Analysis

Based on the test results:
1. API key format is correct (32 characters, hexadecimal)
2. All authentication methods return 400 Bad Request
3. Public endpoints work fine
4. The API key appears to be invalid or not properly configured

## Most Likely Causes

1. **Invalid API Key**: The stored API key might be:
   - Revoked or expired
   - Not actually an API key (might be a user password)
   - Created with insufficient permissions

2. **Wrong Authentication Method**: Jellyfin 10.10.7 might require:
   - Different header format
   - Query parameter instead of header
   - Device registration first

## Solution Steps

### Step 1: Run the Jellyfin 10.10 Specific Test
```bash
cd backend
node test-jellyfin-10.10.js
```
This will test various endpoints and authentication methods specific to your version.

### Step 2: Verify the API Key
```bash
cd backend
node verify-api-key.js
```
This will check if:
- The token is actually a password
- The API key is valid
- Device authentication is required

### Step 3: Create a New API Key (Recommended)

1. **Access Jellyfin Dashboard**
   - Go to: https://jellyfin.okaymedia.ca
   - Login as administrator

2. **Navigate to API Keys**
   - Go to: Dashboard → Advanced → API Keys
   - Or direct URL: https://jellyfin.okaymedia.ca/web/index.html#!/apikeys.html

3. **Create New API Key**
   - Click the "+" button
   - Name it: "Aphrodite"
   - Click "Save"
   - Copy the generated API key

4. **Update Database**
   ```sql
   UPDATE jellyfin_settings 
   SET jellyfin_api_key = 'YOUR_NEW_API_KEY_HERE'
   WHERE user_id = 1;
   ```

### Step 4: Test the New API Key

Edit `manual-api-test.js` with your new API key:
```javascript
const API_KEY = 'YOUR_NEW_API_KEY_HERE';
```

Then run:
```bash
node manual-api-test.js
```

### Step 5: Update the Code

Once you find the working authentication method, update `posterProcessor.js`:

```javascript
// If query parameter works:
const uploadUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary?api_key=${settings.token}`;

// Or if a specific header works:
const headers = {
  'X-Emby-Token': settings.token
};
```

## Quick Test Sequence

1. **First, check if your current token is valid:**
   ```bash
   cd backend
   node test-jellyfin-10.10.js
   ```

2. **If that fails, verify what type of token you have:**
   ```bash
   node verify-api-key.js
   ```

3. **If you need a new API key:**
   - Create one in Jellyfin dashboard
   - Update your database
   - Test with `manual-api-test.js`

4. **Once working, update the poster processor code**

## Expected Success Output

When authentication works, you should see:
```
✅ Success! Found X users
User info: { id: '...', name: '...' }
Item info status: 200
```

## Common Issues

1. **400 Bad Request**: Invalid API key or wrong format
2. **401 Unauthorized**: Valid format but no permissions
3. **500 Internal Server Error**: Server-side issue, check logs

## Next Steps After Fix

1. The poster upload should work
2. Test with the original upload script
3. Monitor for any new errors

The key is finding which authentication method works with your Jellyfin 10.10.7 server, then updating the code to use that method consistently.