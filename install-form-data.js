const { execSync } = require('child_process');
const path = require('path');

// Change to backend directory and install form-data
const backendDir = path.join(process.cwd(), 'backend');
execSync('npm install form-data', { cwd: backendDir, stdio: 'inherit' });

console.log('form-data has been installed in the backend directory.');
