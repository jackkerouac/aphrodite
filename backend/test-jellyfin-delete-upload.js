import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Your Jellyfin server details
const jellyfinUrl = 'https://jellyfin.okaymedia.ca';
const apiKey = '9a5b0cf1c2be45edba0b8e0e582e3be9';
const itemId = '0039f9b10d1131e253a381b1b2067639';

async function testDeleteAndUpload() {
  try {
    // Read the test image
    const testImagePath = join(__dirname, 'temp', `poster-modified-${itemId}.png`);
    console.log(`\nReading test image from: ${testImagePath}`);
    
    const imageBuffer = await readFile(testImagePath);
    console.log(`Image size: ${imageBuffer.length} bytes`);
    
    // Step 1: Delete existing poster
    console.log('\n--- Step 1: Delete existing poster ---');
    const deleteUrl = `${jellyfinUrl}/Items/${itemId}/Images/Primary?api_key=${apiKey}`;
    
    const deleteResponse = await fetch(deleteUrl, {
      method: 'DELETE'
    });
    
    console.log(`Delete status: ${deleteResponse.status} ${deleteResponse.statusText}`);
    
    // Wait a bit after deletion
    console.log('Waiting 1 second after deletion...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Step 2: Upload new poster with base64 encoding
    console.log('\n--- Step 2: Upload new poster (base64) ---');
    const uploadUrl = `${jellyfinUrl}/Items/${itemId}/Images/Primary?api_key=${apiKey}`;
    const base64Data = imageBuffer.toString('base64');
    
    const uploadResponse = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'image/png',
        'Content-Encoding': 'base64'
      },
      body: base64Data
    });
    
    console.log(`Upload status: ${uploadResponse.status} ${uploadResponse.statusText}`);
    
    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      console.log(`Upload error: ${errorText}`);
    } else {
      console.log('Upload successful!');
    }
    
    // Step 3: Verify the upload
    console.log('\n--- Step 3: Verify upload ---');
    const verifyUrl = `${jellyfinUrl}/Items/${itemId}/Images?api_key=${apiKey}`;
    
    const verifyResponse = await fetch(verifyUrl);
    console.log(`Verify status: ${verifyResponse.status}`);
    
    if (verifyResponse.ok) {
      const images = await verifyResponse.json();
      console.log('Current images:', JSON.stringify(images, null, 2));
    }
    
  } catch (error) {
    console.error('Error during test:', error.message);
  }
}

// Run the test
testDeleteAndUpload();
