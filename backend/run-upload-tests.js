import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const tests = [
  { name: 'Base64 Upload Test', file: 'test-jellyfin-upload-base64.js' },
  { name: 'Variations Test', file: 'test-jellyfin-upload-variations.js' },
  { name: 'Delete and Upload Test', file: 'test-jellyfin-delete-upload.js' },
  { name: 'Minimal PNG Test', file: 'test-jellyfin-minimal-upload.js' }
];

async function runTest(testFile, testName) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Running: ${testName}`);
  console.log(`${'='.repeat(50)}`);
  
  return new Promise((resolve) => {
    const child = spawn('node', [testFile], { cwd: __dirname });
    
    child.stdout.on('data', (data) => {
      process.stdout.write(data);
    });
    
    child.stderr.on('data', (data) => {
      process.stderr.write(data);
    });
    
    child.on('close', (code) => {
      resolve(code);
    });
  });
}

async function runAllTests() {
  console.log('Starting Jellyfin upload tests...');
  
  for (const test of tests) {
    await runTest(test.file, test.name);
  }
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('All tests completed!');
  console.log(`${'='.repeat(50)}`);
}

runAllTests();
