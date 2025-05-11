import fetch from 'node-fetch';
import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Mimic the exact flow from posterProcessor.js
const jellyfinUrl = 'https://jellyfin.okaymedia.ca';
const apiKey = 'd66524acc5d544d591e0cbbabff6053c';
const itemId = '0039f9b10d1131e253a381b1b2067639';

async function testPosterProcessorFlow() {
  try {
    console.log('Testing poster processor flow...\n');
    
    // Step 1: Delete existing poster (this was working in posterProcessor)
    console.log('--- Step 1: Delete existing poster ---');
    const deleteUrl = `${jellyfinUrl}/Items/${itemId}/Images/Primary?api_key=${apiKey}`;
    
    const deleteResponse = await fetch(deleteUrl, {
      method: 'DELETE'
    });
    
    console.log(`Delete status: ${deleteResponse.status} ${deleteResponse.statusText}`);
    
    // Wait a moment after deletion
    console.log('Waiting 1 second after deletion...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Step 2: Upload new poster
    console.log('\n--- Step 2: Upload new poster ---');
    
    // Read the modified poster
    const posterPath = join(__dirname, 'temp', `poster-modified-${itemId}.png`);
    console.log(`Reading poster from: ${posterPath}`);
    
    const posterBuffer = await readFile(posterPath);
    console.log(`Poster size: ${posterBuffer.length} bytes`);
    
    // Try the upload methods
    const uploadUrl = `${jellyfinUrl}/Items/${itemId}/Images/Primary?api_key=${apiKey}`;
    
    // Method 1: Base64 encoding (as suggested by the Python code)
    console.log('\nMethod 1: Base64 encoding');
    const base64Data = posterBuffer.toString('base64');
    
    const uploadResponse1 = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'image/png',
        'Content-Encoding': 'base64'
      },
      body: base64Data
    });
    
    console.log(`Upload status: ${uploadResponse1.status} ${uploadResponse1.statusText}`);
    
    if (!uploadResponse1.ok) {
      const errorText = await uploadResponse1.text();
      console.log(`Error: ${errorText}`);
      
      // Try Method 2: Binary upload
      console.log('\nMethod 2: Binary upload');
      
      const uploadResponse2 = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'image/png',
          'Content-Length': posterBuffer.length.toString()
        },
        body: posterBuffer
      });
      
      console.log(`Upload status: ${uploadResponse2.status} ${uploadResponse2.statusText}`);
      
      if (!uploadResponse2.ok) {
        const errorText2 = await uploadResponse2.text();
        console.log(`Error: ${errorText2}`);
      } else {
        console.log('Upload successful!');
      }
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
    console.error('Error in flow:', error);
  }
}

// Run the test
testPosterProcessorFlow();
