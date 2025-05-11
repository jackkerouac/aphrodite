# Test Scripts Guide

This guide explains how to use the test scripts to diagnose and fix the Jellyfin authentication issue.

## Prerequisites

1. Navigate to the backend directory:
   ```bash
   cd E:\programming\aphrodite\backend
   ```

2. Ensure you have all dependencies installed:
   ```bash
   npm install
   ```

## Test Scripts Overview

### 1. `test-api-key.js` - API Key Analysis
Analyzes the format and structure of your stored API key.

**What it checks:**
- API key length and format
- Extra spaces or invalid characters  
- Whether it's hexadecimal, alphanumeric, or base64

**Usage:**
```bash
node test-api-key.js
```

**Expected output:**
```
API Key Analysis:
----------------
Length: 32
Type: string
Is alphanumeric? true
Has hex format: true
...
```

### 2. `test-jellyfin-auth.js` - Authentication Methods Test
Tests multiple authentication header formats to find which one works.

**What it tests:**
- X-Emby-Token header
- X-MediaBrowser-Token header
- Authorization header (various formats)
- API key in query parameters

**Usage:**
```bash
node test-jellyfin-auth.js
```

**Expected output if working:**
```
✅ X-Emby-Token worked!
User info: { id: '...', name: '...' }
```

### 3. `test-jellyfin-10.10.js` - Version-Specific Testing
Tests endpoints and authentication methods specific to Jellyfin 10.10.7.

**What it tests:**
- API key as query parameter
- Various authenticated endpoints
- Image-specific endpoints
- API Keys management endpoint

**Usage:**
```bash
node test-jellyfin-10.10.js
```

**Expected output:**
```
Testing Jellyfin 10.10.7 Specific Endpoints
==========================================
System Info: Version: 10.10.7
...
```

### 4. `verify-api-key.js` - API Key Verification
Checks if your token is actually a password or if the API key is valid.

**What it tests:**
- If the token is a user password
- Device authentication requirements
- Detailed error analysis

**Usage:**
```bash
node verify-api-key.js
```

**Expected output if password:**
```
✅ Success! This appears to be a password, not an API key
New Access Token: [actual API token]
```

### 5. `manual-api-test.js` - Manual API Testing
A simple test script where you manually enter your API key to test.

**Usage:**
1. Edit the file and replace the API key:
   ```javascript
   const API_KEY = 'YOUR_ACTUAL_API_KEY