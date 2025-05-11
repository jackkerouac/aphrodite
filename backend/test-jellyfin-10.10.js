import fetch from 'node-fetch';
import { pool as db } from './db.js';

async function testJellyfin10_10() {
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
    
    console.log('Testing Jellyfin 10.10.7 Specific Endpoints');
    console.log('==========================================');
    console.log('URL:', baseUrl);
    console.log('Token:', settings.token);
    console.log('User ID:', settings.jellyfin_user_id);
    
    // Test 1: System Info (should work)
    console.log('\n1. System Info (Public)');
    try {
      const systemResponse = await fetch(`${baseUrl}/System/Info`);
      const systemText = await systemResponse.text();
      console.log('System response status:', systemResponse.status);
      console.log('System response text:', systemText.substring(0, 100));
      
      if (systemResponse.ok && systemText) {
        try {
          const systemInfo = JSON.parse(systemText);
          console.log('Version:', systemInfo.Version);
          console.log('Server Name:', systemInfo.ServerName);
        } catch (e) {
          console.log('Could not parse system info as JSON');
        }
      }
    } catch (e) {
      console.log('Error getting system info:', e.message);
    }
    
    // Test 2: Try API key with specific format for Jellyfin 10.10
    console.log('\n2. Testing API Key formats for Jellyfin 10.10');
    
    // Format 1: Query parameter (some versions prefer this)
    console.log('\nTrying API key as query parameter...');
    const queryUrl = `${baseUrl}/Users?api_key=${settings.token}`;
    const queryResponse = await fetch(queryUrl);
    console.log('Query param status:', queryResponse.status);
    if (queryResponse.ok) {
      const users = await queryResponse.json();
      console.log('✅ Success with query parameter!');
      console.log('Users found:', users.length);
    }
    
    // Format 2: Custom header format for 10.10
    console.log('\nTrying X-Emby-Token with specific user endpoint...');
    const userUrl = `${baseUrl}/Users/${settings.jellyfin_user_id}`;
    const userResponse = await fetch(userUrl, {
      headers: {
        'X-Emby-Token': settings.token
      }
    });
    console.log('User endpoint status:', userResponse.status);
    if (userResponse.ok) {
      const user = await userResponse.json();
      console.log('✅ Success! User:', user.Name);
    }
    
    // Test 3: Check if API key is valid by accessing simple endpoints
    console.log('\n3. Testing simple authenticated endpoints');
    
    const testEndpoints = [
      '/System/Info',
      '/System/Configuration',
      '/Users',
      '/Library/MediaFolders',
      '/Items'
    ];
    
    for (const endpoint of testEndpoints) {
      console.log(`\nTesting ${endpoint}`);
      
      // Try with header
      const headerResponse = await fetch(`${baseUrl}${endpoint}`, {
        headers: { 'X-Emby-Token': settings.token }
      });
      console.log('With header:', headerResponse.status);
      
      // Try with query param
      const queryResponse = await fetch(`${baseUrl}${endpoint}?api_key=${settings.token}`);
      console.log('With query:', queryResponse.status);
    }
    
    // Test 4: Test image endpoints specifically
    console.log('\n4. Testing image endpoints');
    const itemId = '0039f9b10d1131e253a381b1b2067639';
    
    // Try to get item info first
    const itemResponse = await fetch(`${baseUrl}/Items/${itemId}`, {
      headers: { 'X-Emby-Token': settings.token }
    });
    console.log('Item info status:', itemResponse.status);
    
    if (itemResponse.ok) {
      const item = await itemResponse.json();
      console.log('Item found:', item.Name, item.Type);
    }
    
    // Try image endpoints with both auth methods
    const imageEndpoints = [
      `/Items/${itemId}/Images`,
      `/Items/${itemId}/Images/Primary`,
      `/Items/${itemId}/Images/Primary/0`
    ];
    
    for (const endpoint of imageEndpoints) {
      console.log(`\nTesting ${endpoint}`);
      
      // With header
      const headerResponse = await fetch(`${baseUrl}${endpoint}`, {
        headers: { 'X-Emby-Token': settings.token }
      });
      console.log('With header:', headerResponse.status);
      
      // With query param
      const queryResponse = await fetch(`${baseUrl}${endpoint}?api_key=${settings.token}`);
      console.log('With query:', queryResponse.status);
    }
    
    // Test 5: Check API Keys endpoint (if we have admin access)
    console.log('\n5. Checking API Keys management endpoint');
    const apiKeysResponse = await fetch(`${baseUrl}/Auth/Keys`, {
      headers: { 'X-Emby-Token': settings.token }
    });
    console.log('API Keys endpoint status:', apiKeysResponse.status);
    
    if (apiKeysResponse.ok) {
      const apiKeys = await apiKeysResponse.json();
      console.log('Number of API keys:', apiKeys.Items?.length);
      
      // Check if our key is in the list
      const ourKey = apiKeys.Items?.find(key => key.AccessToken === settings.token);
      if (ourKey) {
        console.log('Our API key found:', {
          appName: ourKey.AppName,
          isActive: ourKey.IsActive,
          dateCreated: ourKey.DateCreated
        });
      } else {
        console.log('⚠️  Our API key not found in the list!');
      }
    }

  } catch (error) {
    console.error('Error:', error);
  } finally {
    process.exit(0);
  }
}

testJellyfin10_10();
