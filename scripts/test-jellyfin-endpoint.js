// Script to test the Jellyfin settings endpoint directly

const fetch = require('node-fetch');

// Configuration
const API_BASE_URL = 'http://localhost:5000';
const USER_ID = 1;  // Default user ID

async function testJellyfinEndpoint() {
  try {
    console.log(`Testing Jellyfin endpoint for user ${USER_ID}...`);
    
    // Make request to the API
    const url = `${API_BASE_URL}/api/jellyfin-settings/${USER_ID}`;
    console.log(`Making GET request to: ${url}`);
    
    const response = await fetch(url);
    console.log(`Response status: ${response.status} ${response.statusText}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Response data:', JSON.stringify(data, null, 2));
    } else {
      console.error('Error response:', await response.text());
    }
  } catch (error) {
    console.error('Error executing test:', error);
  }
}

// Run the test
testJellyfinEndpoint();
