import fetch from 'node-fetch';
import pkg from 'pg';
const { Pool } = pkg;
import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
config({ path: join(dirname(__dirname), '.env') });

// Create connection pool
const pool = new Pool({
  host: process.env.PG_HOST,
  port: process.env.PG_PORT,
  database: process.env.PG_DATABASE,
  user: process.env.PG_USER,
  password: process.env.PG_PASSWORD
});

// Replicate getJellyfinSettings from posterProcessor.js
async function getJellyfinSettings() {
  const query = 'SELECT * FROM jellyfin_settings LIMIT 1';
  const result = await pool.query(query);
  
  if (result.rows.length === 0) {
    throw new Error('Jellyfin settings not configured');
  }
  
  return result.rows[0];
}

async function testExactFlow() {
  try {
    // Get settings the same way posterProcessor does
    const settings = await getJellyfinSettings();
    console.log('Jellyfin Settings Retrieved:');
    console.log(`URL: ${settings.url}`);
    console.log(`Token Length: ${settings.token ? settings.token.length : 0}`);
    console.log(`Token preview: ${settings.token.slice(0, 8)}...${settings.token.slice(-8)}`);
    
    const itemId = '0039f9b10d1131e253a381b1b2067639';
    
    // Test 1: Download poster (should work)
    console.log('\n--- Test 1: Download poster ---');
    const downloadUrl = `${settings.url}/Items/${itemId}/Images/Primary?api_key=${settings.token}`;
    console.log(`URL: ${downloadUrl}`);
    
    const downloadResponse = await fetch(downloadUrl);
    console.log(`Status: ${downloadResponse.status} ${downloadResponse.statusText}`);
    
    // Test 2: Delete poster (was working before)
    console.log('\n--- Test 2: Delete poster ---');
    const deleteUrl = `${settings.url}/Items/${itemId}/Images/Primary?api_key=${settings.token}`;
    
    const deleteResponse = await fetch(deleteUrl, {
      method: 'DELETE'
    });
    console.log(`Status: ${deleteResponse.status} ${deleteResponse.statusText}`);
    
    // Test 3: Upload poster (the problematic part)
    console.log('\n--- Test 3: Upload poster ---');
    const uploadUrl = `${settings.url}/Items/${itemId}/Images/Primary?api_key=${settings.token}`;
    
    // Create a tiny test image
    const testBuffer = Buffer.from([
      0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
      0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
      0xde, 0x00, 0x00, 0x00, 0x0c, 0x49, 0x44, 0x41,
      0x54, 0x08, 0xd7, 0x63, 0xf8, 0xcf, 0xc0, 0x00,
      0x00, 0x03, 0x01, 0x01, 0x00, 0x18, 0xdd, 0x8d,
      0xb4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e,
      0x44, 0xae, 0x42, 0x60, 0x82
    ]);
    
    // Try multiple upload methods
    const uploadMethods = [
      {
        name: 'Binary with image/png',
        headers: {
          'Content-Type': 'image/png',
          'Content-Length': testBuffer.length.toString()
        },
        body: testBuffer
      },
      {
        name: 'Base64 with Content-Encoding',
        headers: {
          'Content-Type': 'image/png',
          'Content-Encoding': 'base64'
        },
        body: testBuffer.toString('base64')
      }
    ];
    
    for (const method of uploadMethods) {
      console.log(`\nTrying: ${method.name}`);
      
      const uploadResponse = await fetch(uploadUrl, {
        method: 'POST',
        headers: method.headers,
        body: method.body
      });
      
      console.log(`Status: ${uploadResponse.status} ${uploadResponse.statusText}`);
      
      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text();
        console.log(`Error: ${errorText}`);
      }
    }
    
  } catch (error) {
    console.error('Error in test:', error);
  } finally {
    await pool.end();
  }
}

// Run the test
testExactFlow();
