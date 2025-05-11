import CanvasBadgeRenderer from './services/badge-renderer/canvasBadgeRenderer.js';
import fs from 'fs/promises';
import path from 'path';

async function testBadgeRenderer() {
  const renderer = new CanvasBadgeRenderer();
  await renderer.init();
  
  // Test resolution badge
  const resolutionSettings = {
    backgroundColor: '#14532D',
    backgroundOpacity: 0.9,
    borderColor: '#15803D',
    borderWidth: 2,
    borderOpacity: 1,
    borderRadius: 8,
    shadowEnabled: true,
    shadowColor: '#000000',
    shadowBlur: 8,
    shadowOffsetX: 2,
    shadowOffsetY: 2,
    textColor: '#DCFCE7',
    fontSize: 18,
    fontFamily: 'Arial',
    margin: 12,
    size: 80
  };
  
  const resolutionMetadata = {
    resolution: '4K'
  };
  
  const resolutionImagePath = await renderer.getResolutionImagePath('4K');
  console.log('Resolution image path:', resolutionImagePath);
  
  const resolutionBadge = await renderer.renderBadge(
    'resolution',
    resolutionSettings,
    resolutionMetadata,
    resolutionImagePath
  );
  
  // Save the badge for visual inspection
  await fs.writeFile('test-resolution-badge.png', resolutionBadge);
  console.log('Resolution badge saved to test-resolution-badge.png');
  
  // Test audio badge
  const audioSettings = {
    backgroundColor: '#1E3A8A',
    backgroundOpacity: 0.9,
    borderColor: '#1D4ED8',
    borderWidth: 2,
    borderOpacity: 1,
    borderRadius: 8,
    shadowEnabled: true,
    shadowColor: '#000000',
    shadowBlur: 8,
    shadowOffsetX: 2,
    shadowOffsetY: 2,
    textColor: '#DBEAFE',
    fontSize: 18,
    fontFamily: 'Arial',
    margin: 12,
    size: 80
  };
  
  const audioMetadata = {
    audioFormat: 'DTS'
  };
  
  const audioImagePath = await renderer.getAudioImagePath('DTS');
  console.log('Audio image path:', audioImagePath);
  
  const audioBadge = await renderer.renderBadge(
    'audio',
    audioSettings,
    audioMetadata,
    audioImagePath
  );
  
  // Save the badge for visual inspection
  await fs.writeFile('test-audio-badge.png', audioBadge);
  console.log('Audio badge saved to test-audio-badge.png');
  
  // Test review badge with multiple ratings
  const reviewSettings = {
    backgroundColor: '#78350F',
    backgroundOpacity: 0.9,
    borderColor: '#92400E',
    borderWidth: 2,
    borderOpacity: 1,
    borderRadius: 8,
    shadowEnabled: true,
    shadowColor: '#000000',
    shadowBlur: 8,
    shadowOffsetX: 2,
    shadowOffsetY: 2,
    textColor: '#FEF3C7',
    fontSize: 18,
    fontFamily: 'Arial',
    margin: 12,
    size: 80,
    displayFormat: 'vertical',
    useBrandColors: false
  };
  
  const reviewMetadata = {
    rating: [
      { name: 'IMDB', rating: '8.5', outOf: 10 },
      { name: 'RT', rating: '90', outOf: 100 },
      { name: 'Metacritic', rating: '85', outOf: 100 }
    ]
  };
  
  const reviewBadge = await renderer.renderBadge(
    'review',
    reviewSettings,
    reviewMetadata,
    null
  );
  
  // Save the badge for visual inspection
  await fs.writeFile('test-review-badge.png', reviewBadge);
  console.log('Review badge saved to test-review-badge.png');
  
  // Test horizontal review badge
  const horizontalReviewSettings = {
    ...reviewSettings,
    displayFormat: 'horizontal',
    useBrandColors: true
  };
  
  const horizontalReviewBadge = await renderer.renderBadge(
    'review',
    horizontalReviewSettings,
    reviewMetadata,
    null
  );
  
  await fs.writeFile('test-review-badge-horizontal.png', horizontalReviewBadge);
  console.log('Horizontal review badge saved to test-review-badge-horizontal.png');
}

// Run the test
testBadgeRenderer().catch(console.error);
