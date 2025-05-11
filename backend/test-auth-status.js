import fetch from 'node-fetch';

// Your Jellyfin server details
const jellyfinUrl = 'https://jellyfin.okaymedia.ca';
const apiKey = 'd66524acc5d544d591e0cbbabff6053c';
const itemId = '0039f9b10d1131e253a381b1b2067639';

async function testAuthentication() {
  console.log('Testing Jellyfin authentication...\n');
  
  // Test 1: Basic API endpoint with query parameter
  console.log('--- Test 1: Query parameter auth ---');
  try {
    const url = `${jellyfinUrl}/Users?api_key=${apiKey}`;
    const response = await fetch(url);
    console.log(`Status: ${response.status} ${response.statusText}`);
    if (response.ok) {
      const data = await response.json();
      console.log(`Users found: ${data.length}`);
    } else {
      const errorText = await response.text();
      console.log(`Response: ${errorText}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
  
  // Test 2: Basic API endpoint with header
  console.log('\n--- Test 2: Header auth (X-Emby-Token) ---');
  try {
    const response = await fetch(`${jellyfinUrl}/Users`, {
      headers: {
        'X-Emby-Token': apiKey
      }
    });
    console.log(`Status: ${response.status} ${response.statusText}`);
    if (response.ok) {
      const data = await response.json();
      console.log(`Users found: ${data.length}`);
    } else {
      const errorText = await response.text();
      console.log(`Response: ${errorText}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
  
  // Test 3: Get item info (using the same item ID from your tests)
  console.log('\n--- Test 3: Get item info ---');
  try {
    const url = `${jellyfinUrl}/Items/${itemId}?api_key=${apiKey}`;
    const response = await fetch(url);
    console.log(`Status: ${response.status} ${response.statusText}`);
    if (response.ok) {
      const data = await response.json();
      console.log(`Item name: ${data.Name}`);
      console.log(`Item type: ${data.Type}`);
    } else {
      const errorText = await response.text();
      console.log(`Response: ${errorText}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
  
  // Test 4: Get existing images for the item
  console.log('\n--- Test 4: Get item images ---');
  try {
    const url = `${jellyfinUrl}/Items/${itemId}/Images?api_key=${apiKey}`;
    const response = await fetch(url);
    console.log(`Status: ${response.status} ${response.statusText}`);
    if (response.ok) {
      const data = await response.json();
      console.log(`Images found: ${JSON.stringify(data, null, 2)}`);
    } else {
      const errorText = await response.text();
      console.log(`Response: ${errorText}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
  
  // Test 5: Delete operation (which you said was working before)
  console.log('\n--- Test 5: Delete operation (should return 204) ---');
  try {
    const url = `${jellyfinUrl}/Items/${itemId}/Images/Primary?api_key=${apiKey}`;
    const response = await fetch(url, {
      method: 'DELETE'
    });
    console.log(`Status: ${response.status} ${response.statusText}`);
    const responseText = await response.text();
    if (responseText) {
      console.log(`Response: ${responseText}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
  
  // Test 6: Check server info
  console.log('\n--- Test 6: Server info ---');
  try {
    const url = `${jellyfinUrl}/System/Info?api_key=${apiKey}`;
    const response = await fetch(url);
    console.log(`Status: ${response.status} ${response.statusText}`);
    if (response.ok) {
      const data = await response.json();
      console.log(`Server Version: ${data.Version}`);
      console.log(`Server Name: ${data.ServerName}`);
    } else {
      const errorText = await response.text();
      console.log(`Response: ${errorText}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

// Run the test
testAuthentication();
