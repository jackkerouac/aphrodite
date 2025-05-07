/**
 * Script to install packages needed for badge image generation
 */

console.log('Installing canvas and multer packages for the backend...');
const { execSync } = require('child_process');

try {
  // Navigate to the backend directory and install required packages
  console.log('Installing canvas (may take a few minutes due to binary compilation)...');
  execSync('cd backend && npm install canvas multer', { stdio: 'inherit' });
  console.log('✅ Successfully installed packages');
} catch (error) {
  console.error('❌ Error installing packages:', error.message);
  process.exit(1);
}
