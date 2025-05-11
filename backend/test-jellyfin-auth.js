import fetch from 'node-fetch';
import { pool as db } from './db.js';

async function testJellyfinAuth() {
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
    
    console.log('Testing Jellyfin Authentication');
    console.log('==============================');
    console.log('URL:', baseUrl);
    console.log('Token length:', settings.token?.length);
    console.log('User ID in settings:', settings.jellyfin_user_id);
    
    // Test 1: Public endpoint (should work without auth)
    console.log('\n1. Testing public endpoint...');
    const publicResponse = await fetch(`${baseUrl}/System/Info/Public`);
    console.log('Public endpoint status:', publicResponse.status);
    
    // Test 2: Get available users (might work without auth)
    console.log('\n2. Testing user list endpoint...');
    const usersResponse = await fetch(`${baseUrl}/Users/Public`);
    console.log('Users list status:', usersResponse.status);
    if (usersResponse.ok) {
      const users = await usersResponse.json();
      console.log('Available users:', users.map(u => ({ id: u.Id, name: u.Name })));
    }
    
    // Test 3: Different auth header formats
    console.log('\n3. Testing authentication headers...');
    
    const authTests = [
      {
        name: 'X-Emby-Token',
        headers: { 'X-Emby-Token': settings.token }
      },
      {
        name: 'X-MediaBrowser-Token',
        headers: { 'X-MediaBrowser-Token': settings.token }
      },
      {
        name: 'Authorization (MediaBrowser Token)',
        headers: { 'Authorization': `MediaBrowser Token="${settings.token}"` }
      },
      {
        name: 'Authorization (Bearer)',
        headers: { 'Authorization': `Bearer ${settings.token}` }
      },
      {
        name: 'Authorization (Emby Token)',
        headers: { 'Authorization': `Emby Token="${settings.token}"` }
      },
      {
        name: 'X-Emby-Authorization',
        headers: { 'X-Emby-Authorization': `MediaBrowser Token="${settings.token}"` }
      }
    ];
    
    for (const test of authTests) {
      console.log(`\nTrying: ${test.name}`);
      const response = await fetch(`${baseUrl}/Users/Me`, { headers: test.headers });
      console.log(`Status: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Success! User:', data.Name, 'ID:', data.Id);
        
        // If successful, test image access with this auth
        console.log('\nTesting image access with working auth...');
        const itemId = '0039f9b10d1131e253a381b1b2067639';
        
        // Test getting current image
        const getImageResponse = await fetch(`${baseUrl}/Items/${itemId}/Images/Primary`, {
          headers: test.headers
        });
        console.log('Get image status:', getImageResponse.status);
        
        // Test getting image info
        const imageInfoResponse = await fetch(`${baseUrl}/Items/${itemId}/Images`, {
          headers: test.headers
        });
        console.log('Image info status:', imageInfoResponse.status);
        if (imageInfoResponse.ok) {
          const imageInfo = await imageInfoResponse.json();
          console.log('Current images:', imageInfo);
        }
        
        break;
      } else {
        const errorText = await response.text();
        console.log('❌ Failed:', errorText.substring(0, 100));
      }
    }
    
    // Test 4: Check if maybe we need to authenticate first
    console.log('\n4. Testing authentication endpoint...');
    const authPayload = {
      Username: settings.jellyfin_user_id || 'admin',
      Password: '', // We don't have password, so trying empty
      RememberMe: false
    };
    
    const authResponse = await fetch(`${baseUrl}/Users/AuthenticateByName`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(authPayload)
    });
    
    console.log('Auth endpoint status:', authResponse.status);
    if (authResponse.ok) {
      const authData = await authResponse.json();
      console.log('Auth response:', {
        user: authData.User?.Name,
        token: authData.AccessToken?.substring(0, 10) + '...'
      });
    } else {
      const errorText = await authResponse.text();
      console.log('Auth error:', errorText);
    }

  } catch (error) {
    console.error('Error:', error);
  } finally {
    process.exit(0);
  }
}

testJellyfinAuth();
