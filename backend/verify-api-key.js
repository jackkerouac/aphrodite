import fetch from 'node-fetch';
import { pool as db } from './db.js';
import crypto from 'crypto';

async function verifyApiKey() {
  try {
    const userId = 1;
    const settingsQuery = `
      SELECT jellyfin_url as url, jellyfin_api_key as token, jellyfin_user_id 
      FROM jellyfin_settings 
      WHERE user_id = $1
    `;
    
    const settingsResult = await db.query(settingsQuery, [userId]);
    const settings = settingsResult.rows[0];

    if (!settings) {
      throw new Error('Jellyfin settings not found');
    }

    const baseUrl = settings.url.replace(/\/$/, '');
    
    console.log('API Key Verification for Jellyfin 10.10.7');
    console.log('========================================');
    console.log('URL:', baseUrl);
    console.log('Stored Token:', settings.token);
    console.log('Stored User ID:', settings.jellyfin_user_id);
    
    // Step 1: Check if this might be a user password instead of API key
    console.log('\n1. Checking if token might be a password...');
    
    // Try to authenticate with the token as a password
    const authPayload = {
      Username: settings.jellyfin_user_id,
      Pw: settings.token // Try token as password
    };
    
    const authResponse = await fetch(`${baseUrl}/Users/AuthenticateByName`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Emby-Authorization': `MediaBrowser Client="Aphrodite", Device="Server", DeviceId="${crypto.randomUUID()}", Version="1.0.0"`
      },
      body: JSON.stringify(authPayload)
    });
    
    console.log('Password auth status:', authResponse.status);
    
    if (authResponse.ok) {
      const authData = await authResponse.json();
      console.log('✅ Success! This appears to be a password, not an API key');
      console.log('User:', authData.User.Name);
      console.log('New Access Token:', authData.AccessToken);
      console.log('\nYou should update the database with this access token instead of the password.');
      
      // Test if the new token works
      console.log('\nTesting the new access token...');
      const testResponse = await fetch(`${baseUrl}/Users/Me`, {
        headers: { 'X-Emby-Token': authData.AccessToken }
      });
      console.log('New token test status:', testResponse.status);
      
      if (testResponse.ok) {
        console.log('✅ New token works! Update your database with:', authData.AccessToken);
      }
    } else {
      console.log('❌ Not a password');
    }
    
    // Step 2: Try different API key validation approaches
    console.log('\n2. Testing API key validation endpoints...');
    
    // Method 1: Check sessions
    const sessionsResponse = await fetch(`${baseUrl}/Sessions`, {
      headers: { 'X-Emby-Token': settings.token }
    });
    console.log('Sessions endpoint status:', sessionsResponse.status);
    
    // Method 2: Create a new API key with device info
    console.log('\n3. Trying to create a proper API key...');
    
    // First, we need to authenticate properly
    console.log('Enter the Jellyfin admin password to create a new API key');
    console.log('(Or press Ctrl+C to skip this step)');
    
    // Provide instructions for manual API key creation
    console.log('\n📝 Manual API Key Creation Instructions:');
    console.log('1. Go to Jellyfin Dashboard');
    console.log('2. Navigate to: Advanced > API Keys');
    console.log('3. Click "+" to add new API key');
    console.log('4. Name it "Aphrodite"');
    console.log('5. Copy the generated key');
    console.log('6. Update your database with the new key');
    
    // Step 3: Test various endpoints to understand the error
    console.log('\n4. Detailed error analysis...');
    
    const testRequests = [
      {
        name: 'Users endpoint with token',
        url: `${baseUrl}/Users`,
        headers: { 'X-Emby-Token': settings.token }
      },
      {
        name: 'Users endpoint with authorization header',
        url: `${baseUrl}/Users`,
        headers: { 
          'X-Emby-Authorization': `MediaBrowser Client="Aphrodite", Token="${settings.token}"`
        }
      },
      {
        name: 'API key in URL',
        url: `${baseUrl}/Users?ApiKey=${settings.token}`,
        headers: {}
      }
    ];
    
    for (const test of testRequests) {
      console.log(`\nTesting: ${test.name}`);
      const response = await fetch(test.url, { headers: test.headers });
      console.log('Status:', response.status);
      
      if (!response.ok) {
        const text = await response.text();
        console.log('Error:', text.substring(0, 200));
        
        // Try to parse error details
        try {
          const error = JSON.parse(text);
          console.log('Error details:', error);
        } catch (e) {
          // Not JSON
        }
      }
    }
    
    // Step 4: Check if server requires device authentication
    console.log('\n5. Testing device authentication...');
    
    const deviceAuth = {
      url: `${baseUrl}/QuickConnect/Initiate`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Emby-Authorization': `MediaBrowser Client="Aphrodite", Device="Server", DeviceId="${crypto.randomUUID()}", Version="1.0.0"`
      }
    };
    
    const deviceResponse = await fetch(deviceAuth.url, {
      method: deviceAuth.method,
      headers: deviceAuth.headers
    });
    
    console.log('Device auth status:', deviceResponse.status);
    
    if (deviceResponse.ok) {
      const deviceData = await deviceResponse.json();
      console.log('Device auth response:', deviceData);
    }

  } catch (error) {
    console.error('Error:', error);
  } finally {
    process.exit(0);
  }
}

verifyApiKey();
