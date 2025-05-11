import PosterProcessor from './services/badge-renderer/posterProcessor.js';
import fs from 'fs/promises';
import path from 'path';

/**
 * Test the resilience of the badge application process
 * This script verifies that the system will continue processing even if certain steps fail
 */
async function testBadgeResilience() {
  console.log('Testing badge application resilience...');
  
  // Create a PosterProcessor instance
  const processor = new PosterProcessor();
  await processor.init();
  
  // Use a sample poster for testing
  const tempDir = path.join(process.cwd(), 'temp');
  await fs.mkdir(tempDir, { recursive: true });
  
  const samplePosterPath = path.join(tempDir, 'test-poster.png');
  
  // Create a sample poster if it doesn't exist
  try {
    await fs.access(samplePosterPath);
  } catch (err) {
    // Create a basic 1000x1500 black poster
    const sharp = (await import('sharp')).default;
    await sharp({
      create: {
        width: 1000,
        height: 1500,
        channels: 4,
        background: { r: 0, g: 0, b: 0, alpha: 1 }
      }
    })
    .png()
    .toFile(samplePosterPath);
    console.log(`Created sample poster at ${samplePosterPath}`);
  }
  
  // Set up test badge configs
  const badgeConfigs = [
    // Audio badge with valid settings
    {
      enabled: true,
      settings: {
        type: 'audio',
        position: 'top-left',
        size: 100,
        fontFamily: 'Arial',
        textColor: '#FFFFFF',
        backgroundColor: '#2E51A2',
        background_color: '#2E51A2', // Test both naming conventions
        borderRadius: 10,
        borderWidth: 1,
        borderColor: '#ffffff',
        borderOpacity: 0.9,
        shadowEnabled: false,
        shadowColor: '#000000',
        shadowBlur: 5,
        shadowOffsetX: 2,
        shadowOffsetY: 2,
        padding: 20,
        margin: 20,
        transparency: 0.8,
        stackingOrder: 1
      },
      value: 'aac'
    },
    // Resolution badge with valid settings
    {
      enabled: true,
      settings: {
        type: 'resolution',
        position: 'top-right',
        size: 100,
        fontFamily: 'Arial',
        textColor: '#FFFFFF',
        backgroundColor: '#FA320A',
        borderRadius: 10,
        borderWidth: 1,
        borderColor: '#ffffff',
        borderOpacity: 0.9,
        shadowEnabled: false,
        padding: 20,
        margin: 20,
        transparency: 0.8,
        stackingOrder: 2
      },
      value: '1080p'
    },
    // Review badge with valid settings
    {
      enabled: true,
      settings: {
        type: 'review',
        position: 'bottom-left',
        size: 100,
        fontFamily: 'Arial',
        textColor: '#FFFFFF',
        backgroundColor: '#000000',
        borderRadius: 10,
        borderWidth: 1,
        borderColor: '#ffffff',
        borderOpacity: 0.9,
        shadowEnabled: false,
        padding: 20,
        margin: 20,
        transparency: 0.8,
        stackingOrder: 3,
        displayFormat: 'horizontal',
        maxSourcesToShow: 2
      },
      value: [
        { name: 'IMDB', rating: 7.5, outOf: 10 },
        { name: 'RT', rating: 85, outOf: 100 }
      ]
    },
    // Audio badge with invalid settings to test error handling
    {
      enabled: true,
      settings: {
        type: 'audio',
        position: 'bottom-right',
        size: -100, // Negative size to trigger an error
        fontFamily: 'Arial',
        textColor: '#FFFFFF',
        backgroundColor: '#000000',
        borderRadius: 10,
        borderWidth: 1,
        borderColor: '#ffffff',
        borderOpacity: 0.9,
        shadowEnabled: false,
        padding: 20,
        margin: 20,
        transparency: 0.8,
        stackingOrder: 4
      },
      value: 'invalid-format'
    }
  ];
  
  try {
    console.log('Testing canvas badge renderer with both valid and invalid configurations...');
    
    // Apply badges with canvas renderer
    const modifiedPosterBuffer = await processor.applyBadgesWithCanvas(samplePosterPath, badgeConfigs);
    
    // Save the result
    const outputPath = path.join(tempDir, 'test-resilience-output.png');
    await fs.writeFile(outputPath, modifiedPosterBuffer);
    
    console.log(`Test completed successfully! Output saved to ${outputPath}`);
    console.log('The badge application process should have continued despite any errors with individual badges.');
    
    // Now test the full item processing with error handling
    console.log('\nTesting full processItem method with fallback behavior...');
    
    // Mock item, job, and user for testing
    const mockItem = {
      id: 'test-item',
      jellyfin_item_id: 'test-poster'
    };
    
    // Override methods to avoid actual DB calls or Jellyfin interaction
    processor.getBadgeSettings = async () => badgeConfigs;
    processor.updateItemStatus = async () => console.log('Mock: updateItemStatus called');
    processor.downloadPoster = async (id, path) => {
      console.log(`Mock: Downloading poster ${id} to ${path}`);
      await fs.copyFile(samplePosterPath, path);
    };
    processor.uploadPoster = async () => console.log('Mock: uploadPoster called');
    
    // Process the mock item
    const result = await processor.processItem(mockItem, 'test-job', 'test-user');
    
    console.log('\nProcessItem result:', result);
    console.log('\nTest completed successfully!');
    
  } catch (error) {
    console.error('Test failed with error:', error);
  }
}

// Run the test
testBadgeResilience().catch(err => {
  console.error('Failed to run tests:', err);
});