import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';

const execPromise = promisify(exec);

async function runCommand(command, cwd = '.') {
  console.log(`Running: ${command}`);
  try {
    const { stdout, stderr } = await execPromise(command, { cwd });
    if (stdout) console.log(stdout);
    if (stderr) console.error(stderr);
    return true;
  } catch (error) {
    console.error(`Error executing command: ${command}`);
    console.error(error.message);
    return false;
  }
}

async function setupProject() {
  console.log('Starting Aphrodite UI setup...');
  
  // Install main project dependencies
  console.log('\n1. Installing main project dependencies...');
  await runCommand('npm install');
  
  // Install scripts dependencies
  console.log('\n2. Installing scripts dependencies...');
  const scriptsDir = path.join(process.cwd(), 'scripts');
  try {
    await fs.access(path.join(scriptsDir, 'package.json'));
    await runCommand('npm install', scriptsDir);
  } catch (error) {
    console.log('Scripts package.json not found, skipping...');
  }
  
  // Install backend dependencies
  console.log('\n3. Installing backend dependencies...');
  const backendDir = path.join(process.cwd(), 'backend');
  try {
    await fs.access(path.join(backendDir, 'package.json'));
    await runCommand('npm install', backendDir);
  } catch (error) {
    console.log('Backend package.json not found, skipping...');
  }
  
  // Create .env file if it doesn't exist
  console.log('\n4. Setting up environment variables...');
  try {
    await fs.access('.env');
    console.log('.env file already exists, skipping...');
  } catch (error) {
    try {
      await fs.copyFile('.env.example', '.env');
      console.log('Created .env file from .env.example');
    } catch (copyError) {
      console.error('Error creating .env file:', copyError.message);
    }
  }
  
  // Setup database
  console.log('\n5. Setting up database...');
  console.log('Note: Make sure PostgreSQL is running and the database is created.');
  console.log('Running database setup script...');
  const success = await runCommand('npm run setup-db');
  
  if (success) {
    console.log('\nSetup completed successfully!');
    console.log('\nNext steps:');
    console.log('1. Edit the .env file with your database credentials if needed');
    console.log('2. Start the backend server: npm run server');
    console.log('3. Start the frontend development server: npm run dev');
    console.log('4. Access the application at: http://localhost:5173');
  } else {
    console.log('\nSetup completed with some errors.');
    console.log('Please check the error messages above and try again.');
  }
}

setupProject().catch(console.error);
