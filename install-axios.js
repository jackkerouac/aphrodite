#!/usr/bin/env node
import { execSync } from 'child_process';

console.log('Installing axios for frontend API calls...');

try {
  // Install axios
  execSync('npm install axios', { stdio: 'inherit' });
  console.log('Successfully installed axios!');
} catch (error) {
  console.error('Error installing axios:', error.message);
  process.exit(1);
}
