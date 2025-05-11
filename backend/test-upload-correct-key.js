import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Correct Jellyfin server details
const jellyfinUrl = 'https://jellyfin.okaymedia.ca';
const apiKey = 'd66524acc5d544d591e0cbbabff6053c';  // Correct API key
const itemId = '00ba4e022c0ef5f7849ac1119fd58f0d';

async function testUploadMethods() {
  try {
    // Read the test image
    const testImagePath = join(__dirname, 'temp', `poster-modified-${itemId}.png`);
    console.log(`\nReading test image from: ${testImagePath}`);
    
    const imageBuffer = await readFile(testImagePath);
    console.log(`Image size: ${imageBuffer.length} bytes`);
    
    // Test 1: Upload as base64 with Content-Encoding header (like Python code)
    console.log('\n--- Test 1: Base64 with Content-Encoding ---');
    const base64Data = imageBuffer.toString('base64');
    console.log(`Base64 size: ${base64Data.length} characters`);
    
    const uploadUrl = `${jellyfinUrl}/Items/${itemId}/Images/Primary?api_key=${apiKey}`;
    
    const response1 = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'image/png',
        'Content-Encoding': 'base64'
      },
      body: base64Data
    });
    
    console.log(`Status: ${response1.status} ${response1.statusText}`);
    
    if (!response1.ok) {
      const errorText = await response1.text();
      console.log(`Response body: ${errorText}`);
    } else {
      console.log('Upload successful!');
      return; // Success, no need to try other methods
    }
    
    // Test 2: Upload as binary buffer
    console.log('\n--- Test 2: Binary upload ---');
    
    const response2 = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'image/png',
        'Content-Length': imageBuffer.length.toString()
      },
      body: imageBuffer
    });
    
    console.log(`Status: ${response2.status} ${response2.statusText}`);
    
    if (!response2.ok) {
      const errorText = await response2.text();
      console.log(`Response body: ${errorText}`);
    } else {
      console.log('Upload successful!');
      return;
    }
    
    // Test 3: Upload as base64 without Content-Encoding header
    console.log('\n--- Test 3: Base64 without Content-Encoding ---');
    
    const response3 = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'image/png'
      },
      body: base64Data
    });
    
    console.log(`Status: ${response3.status} ${response3.statusText}`);
    
    if (!response3.ok) {
      const errorText = await response3.text();
      console.log(`Response body: ${errorText}`);
    } else {
      console.log('Upload successful!');
      return;
    }
    
    // Test 4: X-Emby-Token header with base64
    console.log('\n--- Test 4: X-Emby-Token header with base64 ---');
    
    const uploadUrl2 = `${jellyfinUrl}/Items/${itemId}/Images/Primary`;
    
    const response4 = await fetch(uploadUrl2, {
      method: 'POST',
      headers: {
        'X-Emby-Token': apiKey,
        'Content-Type': 'image/png',
        'Content-Encoding': 'base64'
      },
      body: base64Data
    });
    
    console.log(`Status: ${response4.status} ${response4.statusText}`);
    
    if (!response4.ok) {
      const errorText = await response4.text();
      console.log(`Response body: ${errorText}`);
    } else {
      console.log('Upload successful!');
      return;
    }
    
  } catch (error) {
    console.error('Error during test:', error.message);
  }
}

// Run the test
testUploadMethods();
