// Correct Jellyfin server details
const jellyfinUrl = 'https://jellyfin.okaymedia.ca';
const apiKey = 'd66524acc5d544d591e0cbbabff6053c';
const itemId = '0039f9b10d1131e253a381b1b2067639';

async function testItemValidity() {
  console.log('Testing item validity...\n');
  
  // Test 1: Get item info
  console.log('--- Test 1: Get item info ---');
  try {
    const url = `${jellyfinUrl}/Items/${itemId}?api_key=${apiKey}`;
    const response = await fetch(url);
    console.log(`Status: ${response.status} ${response.statusText}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log(`Item found: ${data.Name}`);
      console.log(`Item type: ${data.Type}`);
      console.log(`Item ID: ${data.Id}`);
    } else {
      const errorText = await response.text();
      console.log(`Response: ${errorText}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
  
  // Test 2: Get item images
  console.log('\n--- Test 2: Get item images ---');
  try {
    const url = `${jellyfinUrl}/Items/${itemId}/Images?api_key=${apiKey}`;
    const response = await fetch(url);
    console.log(`Status: ${response.status} ${response.statusText}`);
    
    if (response.ok) {
      const images = await response.json();
      console.log(`Images found: ${images.length}`);
      images.forEach(img => {
        console.log(`- ${img.ImageType}: ${img.Path}`);
      });
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
  
  // Test 3: Try a different item (test to see if issue is item-specific)
  console.log('\n--- Test 3: Test with a different item ---');
  
  // First, let's get some items from the library
  try {
    const libraryUrl = `${jellyfinUrl}/Items?api_key=${apiKey}&fields=ImageTags&limit=5`;
    const libraryResponse = await fetch(libraryUrl);
    
    if (libraryResponse.ok) {
      const libraryData = await libraryResponse.json();
      console.log(`Found ${libraryData.TotalRecordCount} items`);
      
      if (libraryData.Items && libraryData.Items.length > 0) {
        const firstItem = libraryData.Items[0];
        console.log(`\nTesting with item: ${firstItem.Name}`);
        console.log(`Item ID: ${firstItem.Id}`);
        
        // Try to get images for this item
        const imagesUrl = `${jellyfinUrl}/Items/${firstItem.Id}/Images?api_key=${apiKey}`;
        const imagesResponse = await fetch(imagesUrl);
        console.log(`Images status: ${imagesResponse.status}`);
        
        if (imagesResponse.ok) {
          const images = await imagesResponse.json();
          console.log(`Images found: ${images.length}`);
        }
      }
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

// Run the test
testItemValidity();
