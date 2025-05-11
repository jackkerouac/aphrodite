import fs from 'fs/promises';
import CanvasBadgeRenderer from './services/badge-renderer/canvasBadgeRenderer.js';

async function testBackgroundColorHandling() {
  console.log('Testing badge background color handling...');
  
  const renderer = new CanvasBadgeRenderer();
  
  // Test 1: Custom background color (snake_case)
  const customColorSettings = {
    background_color: '#FF5500',  // Using snake_case (from DB)
    size: 100,
    borderRadius: 10,
    textColor: '#FFFFFF',
    position: 'top-left',
    margin: 10,
    use_brand_colors: false      // Don't use brand colors
  };
  
  // Test 2: Brand colors enabled, no custom color
  const brandColorSettings = {
    size: 100,
    borderRadius: 10,
    textColor: '#FFFFFF',
    position: 'top-left',
    margin: 10,
    use_brand_colors: true        // Use brand colors
  };
  
  // Test 3: Custom background color (camelCase)
  const camelCaseColorSettings = {
    backgroundColor: '#00AAFF',  // Using camelCase (from frontend)
    size: 100,
    borderRadius: 10,
    textColor: '#FFFFFF',
    position: 'top-left',
    margin: 10,
    use_brand_colors: false       // Don't use brand colors
  };
  
  // Test 4: Custom color priority over brand colors
  const prioritySettings = {
    background_color: '#22DD22',  // Should take priority
    size: 100,
    borderRadius: 10,
    textColor: '#FFFFFF',
    position: 'top-left',
    margin: 10,
    use_brand_colors: true        // This should be ignored due to custom color
  };
  
  try {
    // Test Audio badges
    console.log('\nTesting Audio Badge:');
    const audioMetadata = { audioFormat: 'DTS' };
    
    const test1Audio = await renderer.renderBadge('audio', customColorSettings, audioMetadata);
    await fs.writeFile('./test-audio-custom-color.png', test1Audio);
    console.log('- Custom snake_case color (orange) test saved to test-audio-custom-color.png');
    
    const test2Audio = await renderer.renderBadge('audio', brandColorSettings, audioMetadata);
    await fs.writeFile('./test-audio-brand-color.png', test2Audio);
    console.log('- Brand color (blue) test saved to test-audio-brand-color.png');
    
    const test3Audio = await renderer.renderBadge('audio', camelCaseColorSettings, audioMetadata);
    await fs.writeFile('./test-audio-camelcase-color.png', test3Audio);
    console.log('- Custom camelCase color (light blue) test saved to test-audio-camelcase-color.png');
    
    const test4Audio = await renderer.renderBadge('audio', prioritySettings, audioMetadata);
    await fs.writeFile('./test-audio-priority-color.png', test4Audio);
    console.log('- Priority color (green) test saved to test-audio-priority-color.png');
    
    // Test Resolution badges
    console.log('\nTesting Resolution Badge:');
    const resolutionMetadata = { resolution: '4K' };
    
    const test1Resolution = await renderer.renderBadge('resolution', customColorSettings, resolutionMetadata);
    await fs.writeFile('./test-resolution-custom-color.png', test1Resolution);
    console.log('- Custom snake_case color (orange) test saved to test-resolution-custom-color.png');
    
    const test2Resolution = await renderer.renderBadge('resolution', brandColorSettings, resolutionMetadata);
    await fs.writeFile('./test-resolution-brand-color.png', test2Resolution);
    console.log('- Brand color (red) test saved to test-resolution-brand-color.png');
    
    // Test Review badges
    console.log('\nTesting Review Badge:');
    const reviewMetadata = { 
      rating: [
        { name: 'IMDB', rating: 7.5, outOf: 10 },
        { name: 'RT', rating: 85, outOf: 100 }
      ]
    };
    
    const test1Review = await renderer.renderBadge('review', customColorSettings, reviewMetadata);
    await fs.writeFile('./test-review-custom-color.png', test1Review);
    console.log('- Custom snake_case color (orange) test saved to test-review-custom-color.png');
    
    const test2Review = await renderer.renderBadge('review', brandColorSettings, reviewMetadata);
    await fs.writeFile('./test-review-brand-color.png', test2Review);
    console.log('- Brand colors (IMDb yellow, RT red) test saved to test-review-brand-color.png');
    
    const test3Review = await renderer.renderBadge('review', prioritySettings, reviewMetadata);
    await fs.writeFile('./test-review-priority-color.png', test3Review);
    console.log('- Priority color (green) test saved to test-review-priority-color.png');
    
    console.log('\nAll tests completed! Check the output files to verify colors are applied correctly.');
    
  } catch (error) {
    console.error('Error during testing:', error);
  }
}

// Run the test
testBackgroundColorHandling().catch(err => {
  console.error('Failed to run tests:', err);
});