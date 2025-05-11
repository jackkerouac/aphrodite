import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Your Jellyfin server details
const jellyfinUrl = 'https://jellyfin.okaymedia.ca';
const apiKey = '9a5b0cf1c2be45edba0b8e0e582e3be9';
const itemId = '0039f9b10d1131e253a381b1b2067639';

async function testVariations() {
  try {
    // Read the test image
    const testImagePath = join(__dirname, 'temp', `poster-modified-${itemId}.png`);
    console.log(`\nReading test image from: ${testImagePath}`);
    
    const imageBuffer = await readFile(testImagePath);
    console.log(`Image size: ${imageBuffer.length} bytes`);
    
    // Test variations
    const variations = [
      {
        name: 'Base64 with Content-Encoding header',
        headers: {
          'Content-Type': 'image/png',
          'Content-Encoding': 'base64'
        },
        body: imageBuffer.toString('base64'),
        auth: 'query'
      },
      {
        name: 'Base64 without Content-Encoding header',
        headers: {
          'Content-Type': 'image/png'
        },
        body: imageBuffer.toString('base64'),
        auth: 'query'
      },
      {
        name: 'Binary data with application/octet-stream',
        headers: {
          'Content-Type': 'application/octet-stream'
        },
        body: imageBuffer,
        auth: 'query'
      },
      {
        name: 'Binary data with image/* content type',
        headers: {
          'Content-Type': 'image/*'
        },
        body: imageBuffer,
        auth: 'query'
      },
      {
        name: 'Base64 with X-Emby-Token header',
        headers: {
          'X-Emby-Token': apiKey,
          'Content-Type': 'image/png',
          'Content-Encoding': 'base64'
        },
        body: imageBuffer.toString('base64'),
        auth: 'header'
      }
    ];
    
    for (const variation of variations) {
      console.log(`\n--- Testing: ${variation.name} ---`);
      
      let url = `${jellyfinUrl}/Items/${itemId}/Images/Primary`;
      if (variation.auth === 'query') {
        url += `?api_key=${apiKey}`;
      }
      
      console.log(`URL: ${url}`);
      console.log('Headers:', variation.headers);
      console.log(`Body type: ${typeof variation.body}, length: ${variation.body.length}`);
      
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: variation.headers,
          body: variation.body
        });
        
        console.log(`Status: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.log(`Response body: ${errorText}`);
        } else {
          console.log('Upload successful!');
          break; // Stop on first success
        }
      } catch (reqError) {
        console.error(`Request error: ${reqError.message}`);
      }
    }
    
  } catch (error) {
    console.error('Error during test:', error.message);
  }
}

// Run the test
testVariations();
