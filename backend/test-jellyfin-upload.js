import fetch from 'node-fetch';
import { promises as fs } from 'fs';
import dotenv from 'dotenv';
import { pool as db } from './db.js';

dotenv.config();

async function testJellyfinUpload() {
  try {
    // Get Jellyfin settings from database for user ID 1
    const userId = 1; // Adjust this if needed
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

    console.log('Jellyfin settings:', {
      url: settings.url,
      hasToken: !!settings.token,
      userId: settings.jellyfin_user_id
    });

    // Test basic connection
    const baseUrl = settings.url.replace(/\/$/, '');
    const systemInfoUrl = `${baseUrl}/System/Info/Public`;
    
    // Test different authentication formats
    console.log('\nTesting authentication formats...');
    
    // Format 1: X-Emby-Token
    const headers1 = { 'X-Emby-Token': settings.token };
    
    // Format 2: X-MediaBrowser-Token
    const headers2 = { 'X-MediaBrowser-Token': settings.token };
    
    // Format 3: Authorization header
    const headers3 = { 'Authorization': `MediaBrowser Token="${settings.token}"` };
    
    // Format 4: All headers combined
    const headers4 = {
      'X-Emby-Token': settings.token,
      'X-MediaBrowser-Token': settings.token,
      'Authorization': `MediaBrowser Token="${settings.token}"`
    };
    
    // Format 5: Api-Key header
    const headers5 = { 'Api-Key': settings.token };
    
    const authFormats = [
      { name: 'X-Emby-Token', headers: headers1 },
      { name: 'X-MediaBrowser-Token', headers: headers2 },
      { name: 'Authorization MediaBrowser', headers: headers3 },
      { name: 'All headers', headers: headers4 },
      { name: 'Api-Key', headers: headers5 }
    ];
    
    let workingHeaders = null;
    
    for (const format of authFormats) {
      console.log(`\nTrying auth format: ${format.name}`);
      const userUrl = `${baseUrl}/Users/Me`;
      const userResponse = await fetch(userUrl, { headers: format.headers });
      
      if (userResponse.ok) {
        const userInfo = await userResponse.json();
        console.log(`✅ ${format.name} worked!`);
        console.log('User info:', {
          id: userInfo.Id,
          name: userInfo.Name,
          serverId: userInfo.ServerId
        });
        workingHeaders = format.headers;
        break;
      } else {
        console.log(`❌ ${format.name} failed:`, userResponse.status, userResponse.statusText);
      }
    }
    
    if (!workingHeaders) {
      console.error('\n❌ No authentication format worked!');
      console.log('Token format debug:');
      console.log('Token length:', settings.token?.length);
      console.log('Token starts with:', settings.token?.substring(0, 8) + '...');
      console.log('Token ends with:', '...' + settings.token?.slice(-8));
      
      // Try to get system info without auth to see if it's public
      const publicUrl = `${baseUrl}/System/Info/Public`;
      const publicResponse = await fetch(publicUrl);
      console.log('\nPublic endpoint access:', publicResponse.status);
      
      throw new Error('Authentication failed with all formats');
    }
    
    const headers = workingHeaders;

    console.log('\nTesting basic connection...');
    const systemResponse = await fetch(systemInfoUrl, { headers });
    const systemInfo = await systemResponse.json();
    console.log('System info:', systemInfo);

    // Test authentication
    console.log('\nTesting authentication...');
    const userUrl = `${baseUrl}/Users/Me`;
    const userResponse = await fetch(userUrl, { headers });
    
    if (userResponse.ok) {
      const userInfo = await userResponse.json();
      console.log('User info:', {
        id: userInfo.Id,
        name: userInfo.Name,
        serverId: userInfo.ServerId
      });
    } else {
      console.error('Authentication failed:', userResponse.status, userResponse.statusText);
    }

    // Test a simple image upload with a small test image
    console.log('\nTesting image upload with a small test image...');
    const testItemId = '0039f9b10d1131e253a381b1b2067639'; // Your test item ID
    
    // Create a simple 10x10 pixel red image
    const sharp = (await import('sharp')).default;
    const testImageBuffer = await sharp({
      create: {
        width: 10,
        height: 10,
        channels: 4,
        background: { r: 255, g: 0, b: 0, alpha: 1 }
      }
    }).png().toBuffer();

    console.log('Test image created, size:', testImageBuffer.length, 'bytes');

    // Try to upload the test image
    const uploadUrl = `${baseUrl}/Items/${testItemId}/Images/Primary`;
    
    console.log('Upload URL:', uploadUrl);
    
    // Method 1: Simple POST with image/png
    const uploadHeaders = {
      ...headers,
      'Content-Type': 'image/png',
      'Content-Length': testImageBuffer.length.toString()
    };

    const uploadResponse = await fetch(uploadUrl, {
      method: 'POST',
      headers: uploadHeaders,
      body: testImageBuffer
    });

    const responseText = await uploadResponse.text();
    
    console.log('\nUpload response:', {
      status: uploadResponse.status,
      statusText: uploadResponse.statusText,
      headers: Object.fromEntries(uploadResponse.headers.entries()),
      body: responseText.substring(0, 500)
    });

    // If that fails, try the index-based approach
    if (!uploadResponse.ok) {
      console.log('\nTrying index-based upload...');
      const indexUrl = `${baseUrl}/Items/${testItemId}/Images/Primary/0`;
      
      const indexResponse = await fetch(indexUrl, {
        method: 'POST',
        headers: uploadHeaders,
        body: testImageBuffer
      });

      const indexResponseText = await indexResponse.text();
      
      console.log('Index-based upload response:', {
        status: indexResponse.status,
        statusText: indexResponse.statusText,
        body: indexResponseText.substring(0, 500)
      });
    }

  } catch (error) {
    console.error('Error in test:', error);
  } finally {
    process.exit(0);
  }
}

testJellyfinUpload();
