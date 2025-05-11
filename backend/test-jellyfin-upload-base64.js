import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Your Jellyfin server details
const jellyfinUrl = 'https://jellyfin.okaymedia.ca';
const apiKey = '9a5b0cf1c2be45edba0b8e0e582e3be9';
const itemId = '0039f9b10d1131e253a381b1b2067639';

async function testBase64Upload() {
  try {
    // Read the test image
    const testImagePath = join(__dirname, 'temp', `poster-modified-${itemId}.png`);
    console.log(`\nReading test image from: ${testImagePath}`);
    
    const imageBuffer = await readFile(testImagePath);
    console.log(`Image size: ${imageBuffer.length} bytes`);
    
    // Convert to base64
    const base64Data = imageBuffer.toString('base64');
    console.log(`Base64 size: ${base64Data.length} characters`);
    
    // Method 1: Query parameter authentication with base64 encoding
    console.log('\n--- Method 1: Query Param Auth with Base64 ---');
    const uploadUrl = `${jellyfinUrl}/Items/${itemId}/Images/Primary?api_key=${apiKey}`;
    
    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'image/png',
        'Content-Encoding': 'base64',
        'Content-Length': base64Data.length.toString()
      },
      body: base64Data
    });
    
    console.log(`Status: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.log(`Response body: ${errorText}`);
    } else {
      console.log('Upload successful!');
    }
    
    // Method 2: Header authentication with base64 encoding
    console.log('\n--- Method 2: Header Auth with Base64 ---');
    const uploadUrl2 = `${jellyfinUrl}/Items/${itemId}/Images/Primary`;
    
    const response2 = await fetch(uploadUrl2, {
      method: 'POST',
      headers: {
        'X-Emby-Token': apiKey,
        'Content-Type': 'image/png',
        'Content-Encoding': 'base64',
        'Content-Length': base64Data.length.toString()
      },
      body: base64Data
    });
    
    console.log(`Status: ${response2.status} ${response2.statusText}`);
    
    if (!response2.ok) {
      const errorText = await response2.text();
      console.log(`Response body: ${errorText}`);
    } else {
      console.log('Upload successful!');
    }
    
  } catch (error) {
    console.error('Error during test:', error.message);
  }
}

// Run the test
testBase64Upload();
