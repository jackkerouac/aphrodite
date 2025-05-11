import fetch from 'node-fetch';

// MANUAL TEST - Replace these values with your actual values
const JELLYFIN_URL = 'https://jellyfin.okaymedia.ca';
const API_KEY = 'YOUR_API_KEY_HERE'; // Replace with your actual API key

async function manualApiTest() {
  console.log('Manual Jellyfin API Test');
  console.log('=======================');
  console.log('URL:', JELLYFIN_URL);
  console.log('API Key:', API_KEY.substring(0, 4) + '...' + API_KEY.slice(-4));
  
  console.log('\n1. Testing with header X-Emby-Token');
  try {
    const response1 = await fetch(`${JELLYFIN_URL}/Users`, {
      headers: { 'X-Emby-Token': API_KEY }
    });
    console.log('Status:', response1.status);
    if (response1.ok) {
      const users = await response1.json();
      console.log('✅ Success! Found', users.length, 'users');
    } else {
      const error = await response1.text();
      console.log('❌ Error:', error.substring(0, 100));
    }
  } catch (e) {
    console.log('❌ Exception:', e.message);
  }
  
  console.log('\n2. Testing with query parameter api_key');
  try {
    const response2 = await fetch(`${JELLYFIN_URL}/Users?api_key=${API_KEY}`);
    console.log('Status:', response2.status);
    if (response2.ok) {
      const users = await response2.json();
      console.log('✅ Success! Found', users.length, 'users');
    } else {
      const error = await response2.text();
      console.log('❌ Error:', error.substring(0, 100));
    }
  } catch (e) {
    console.log('❌ Exception:', e.message);
  }
  
  console.log('\n3. Testing with query parameter ApiKey (capital A)');
  try {
    const response3 = await fetch(`${JELLYFIN_URL}/Users?ApiKey=${API_KEY}`);
    console.log('Status:', response3.status);
    if (response3.ok) {
      const users = await response3.json();
      console.log('✅ Success! Found', users.length, 'users');
    } else {
      const error = await response3.text();
      console.log('❌ Error:', error.substring(0, 100));
    }
  } catch (e) {
    console.log('❌ Exception:', e.message);
  }
  
  console.log('\n4. Testing with Authorization header');
  try {
    const response4 = await fetch(`${JELLYFIN_URL}/Users`, {
      headers: { 'Authorization': `MediaBrowser Token="${API_KEY}"` }
    });
    console.log('Status:', response4.status);
    if (response4.ok) {
      const users = await response4.json();
      console.log('✅ Success! Found', users.length, 'users');
    } else {
      const error = await response4.text();
      console.log('❌ Error:', error.substring(0, 100));
    }
  } catch (e) {
    console.log('❌ Exception:', e.message);
  }
  
  console.log('\nIf all tests fail, the API key is likely invalid.');
  console.log('To create a new API key:');
  console.log('1. Go to Jellyfin Dashboard');
  console.log('2. Navigate to Advanced → API Keys');
  console.log('3. Click "+" to add new API key');
  console.log('4. Name it "Aphrodite"');
  console.log('5. Copy the generated key and update your database');
}

manualApiTest();
