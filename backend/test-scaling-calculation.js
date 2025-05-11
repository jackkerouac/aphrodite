// Test scaling calculations for different poster sizes

const previewWidth = 1000;
const previewHeight = 1500;

const testPosters = [
  { width: 1000, height: 1500, name: "Preview size" },
  { width: 2000, height: 3000, name: "2x size" },
  { width: 500, height: 750, name: "0.5x size" },
  { width: 3840, height: 5760, name: "4K poster" },
  { width: 1280, height: 1920, name: "HD poster" },
  { width: 680, height: 1000, name: "Small poster" }
];

const originalMargin = 21; // Audio badge margin from DB

console.log("Scaling calculations for different poster sizes:\n");

testPosters.forEach(poster => {
  // Calculate both width and height scaling factors
  const widthScale = poster.width / previewWidth;
  const heightScale = poster.height / previewHeight;
  
  // Use the smaller of width and height scaling to be more conservative
  let scaleFactor = Math.min(widthScale, heightScale);
  
  // Ensure minimum scale factor to prevent badges from becoming too small
  scaleFactor = Math.max(scaleFactor, 0.3);
  
  // Calculate margin scale factor
  const marginScaleFactor = Math.max(scaleFactor * 0.9, 0.8);
  
  // Cap the margin scaling for very large posters
  const cappedMarginScaleFactor = Math.min(marginScaleFactor, 1.5);
  
  // Calculate final margin
  const scaledMargin = Math.round(originalMargin * cappedMarginScaleFactor);
  
  console.log(`${poster.name} (${poster.width}x${poster.height}):`);
  console.log(`  Width scale: ${widthScale.toFixed(2)}`);
  console.log(`  Height scale: ${heightScale.toFixed(2)}`);
  console.log(`  Final scale factor: ${scaleFactor.toFixed(2)}`);
  console.log(`  Margin scale factor: ${cappedMarginScaleFactor.toFixed(2)}`);
  console.log(`  Original margin: ${originalMargin}px`);
  console.log(`  Scaled margin: ${scaledMargin}px`);
  console.log();
});
