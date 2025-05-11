import CanvasBadgeRenderer from './backend/services/badge-renderer/canvasBadgeRenderer.js';
import MetadataService from './backend/services/badge-renderer/metadataService.js';
import path from 'path';
import fs from 'fs/promises';

async function testBadgeRendering() {
  const renderer = new CanvasBadgeRenderer();
  const metadataService = new MetadataService();
  
  try {
    await renderer.init();
    console.log('CanvasBadgeRenderer initialized successfully');
    
    // Test resolution badge
    const resolutionSettings = {
      type: 'resolution',
      size: 100,
      position: 'top-right',
      backgroundColor: '#000000',
      textColor: '#FFFFFF',
      transparency: 0.8,
      borderRadius: 10,
      fontFamily: 'Roboto',
      margin: 10
    };
    
    // Test with 4K resolution
    const resolutionImagePath = await renderer.getResolutionImagePath('4K');
    console.log('Resolution image path:', resolutionImagePath);
    
    const resolutionBadge = await renderer.renderBadge(
      'resolution',
      resolutionSettings,
      { resolution: '4K' },
      resolutionImagePath
    );
    
    await fs.writeFile('test-resolution-badge.png', resolutionBadge);
    console.log('Resolution badge created successfully');
    
    // Test audio badge
    const audioSettings = {
      type: 'audio',
      size: 100,
      position: 'top-left',
      backgroundColor: '#000000',
      textColor: '#FFFFFF',
      transparency: 0.8,
      borderRadius: 10,
      fontFamily: 'Roboto',
      margin: 10
    };
    
    // Test with Dolby Digital format
    const audioImagePath = await renderer.getAudioImagePath('Dolby Digital');
    console.log('Audio image path:', audioImagePath);
    
    const audioBadge = await renderer.renderBadge(
      'audio',
      audioSettings,
      { audioFormat: 'Dolby Digital' },
      audioImagePath
    );
    
    await fs.writeFile('test-audio-badge.png', audioBadge);
    console.log('Audio badge created successfully');
    
    // Test review badge
    const reviewSettings = {
      type: 'review',
      size: 80,
      position: 'bottom-left',
      backgroundColor: '#000000',
      textColor: '#FFFFFF',
      transparency: 0.8,
      borderRadius: 10,
      fontFamily: 'Roboto',
      useBrandColors: true,
      displayFormat: 'horizontal',
      maxSourcesToShow: 3
    };
    
    const reviewBadge = await renderer.renderBadge(
      'review',
      reviewSettings,
      { 
        rating: [
          { name: 'IMDb', rating: 8.5, outOf: 10 },
          { name: 'RT', rating: 90, outOf: 100 },
          { name: 'Metacritic', rating: 75, outOf: 100 }
        ]
      }
    );
    
    await fs.writeFile('test-review-badge.png', reviewBadge);
    console.log('Review badge created successfully');
    
    // Test with poster size validation
    const posterWidth = 1000;
    const posterHeight = 1500;
    
    // Test badge that would be too large
    const largeBadgeSettings = {
      type: 'resolution',
      size: 2000, // This should get limited
      position: 'top-right',
      backgroundColor: '#FF0000',
      textColor: '#FFFFFF',
      transparency: 0.8,
      borderRadius: 10,
      fontFamily: 'Roboto',
      margin: 10
    };
    
    const largeBadge = await renderer.renderBadge(
      'resolution',
      largeBadgeSettings,
      { resolution: '8K' }
    );
    
    await fs.writeFile('test-large-badge.png', largeBadge);
    console.log('Large badge created successfully (should be limited in size)');
    
    console.log('\n✅ All badges rendered successfully!');
    console.log('Check the following files:');
    console.log('- test-resolution-badge.png');
    console.log('- test-audio-badge.png');
    console.log('- test-review-badge.png');
    console.log('- test-large-badge.png');
    
  } catch (error) {
    console.error('Error during badge rendering test:', error);
    throw error;
  }
}

// Run the test
testBadgeRendering().catch(console.error);
