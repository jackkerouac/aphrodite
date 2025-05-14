#!/usr/bin/env node
import { execSync } from 'child_process';
import { platform } from 'os';

// Define the packages to install
const packages = [
  'canvas',
  'sharp'
];

console.log('Installing Canvas and Sharp for Badge Rendering...');

try {
  // Install packages
  execSync(`npm install ${packages.join(' ')}`, { stdio: 'inherit' });
  console.log('Successfully installed dependencies!');
} catch (error) {
  console.error('Error installing dependencies:', error.message);
  process.exit(1);
}
