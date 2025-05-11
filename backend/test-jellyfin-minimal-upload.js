import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Your Jellyfin server details
const jellyfinUrl = 'https://jellyfin.okaymedia.ca';
const apiKey = '9a5b0cf1c2be45edba0b8e0e582e3be9';
const itemId = '0039f9b10d1131e253a381b1b2067639';

// Create a minimal PNG image (1x1 pixel red dot)
function createMinimalPNG() {
  // This is a minimal valid PNG file (red pixel)
  const png = Buffer.from([
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, // PNG signature
    0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    0xde, 0x00, 0x00, 0x00, 0x0c, 0x49, 0x44, 0x41, // IDAT chunk
    0x54, 0x08, 0xd7, 0x63, 0xf8, 0xcf, 0xc0, 0x00,
    0x00, 0x03, 0x01, 0x01, 0x00, 0x18, 0xdd, 0x8d,
    0xb4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, // IEND chunk
    0x44, 0xae, 0x42, 0x60, 0x82
  ]);
  return png;
}

async function testMinimalUpload() {
  try {
    console.log('\n--- Testing with minimal PNG ---');
    
    const minimalPNG = createMinimalPNG();
    console.log(`Minimal PNG size: ${minimalPNG.length} bytes`);
    
    // Test 1: Upload as base64
    console.log('\n--- Test 1: Base64 upload ---');
    const base64Data = minimalPNG.toString('base64');
    
    const uploadUrl = `${jellyfinUrl}/Items/${itemId}/Images/Primary?api_key=${apiKey}`;
    
    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'image/png',
        'Content-Encoding': 'base64'
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
    
    // Test 2: Upload as binary
    console.log('\n--- Test 2: Binary upload ---');
    
    const response2 = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'image/png'
      },
      body: minimalPNG
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
testMinimalUpload();
