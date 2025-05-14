#!/usr/bin/env node
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

// Get current directory (ES modules don't have __dirname)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define source and destination paths
const SRC_AUDIO_PATH = path.join(__dirname, '..', 'src', 'assets', 'audio_codec', 'compact');
const SRC_RESOLUTION_PATH = path.join(__dirname, '..', 'src', 'assets', 'resolution');
const SRC_REVIEW_PATH = path.join(__dirname, '..', 'src', 'assets', 'rating');

const DST_AUDIO_PATH = path.join(__dirname, 'public', 'assets', 'audio_codec', 'compact');
const DST_RESOLUTION_PATH = path.join(__dirname, 'public', 'assets', 'resolution');
const DST_REVIEW_PATH = path.join(__dirname, 'public', 'assets', 'rating');

// Function to copy files
async function copyFiles(srcDir, dstDir) {
  try {
    // Ensure destination directory exists
    await fs.mkdir(dstDir, { recursive: true });
    
    // Get all files from the source directory
    const files = await fs.readdir(srcDir);
    
    for (const file of files) {
      if (file.endsWith('.png') || file.endsWith('.jpg') || file.endsWith('.svg')) {
        const srcFile = path.join(srcDir, file);
        const dstFile = path.join(dstDir, file);
        
        // Copy the file
        console.log(`Copying ${srcFile} to ${dstFile}`);
        await fs.copyFile(srcFile, dstFile);
      }
    }
    
    console.log(`Successfully copied all image files from ${srcDir} to ${dstDir}`);
    return true;
  } catch (error) {
    console.error(`Error copying files from ${srcDir} to ${dstDir}:`, error.message);
    return false;
  }
}

// Main function
async function main() {
  console.log('Copying badge assets from frontend to backend...');
  
  try {
    // Copy audio codec images
    await copyFiles(SRC_AUDIO_PATH, DST_AUDIO_PATH);
    
    // Copy resolution images
    await copyFiles(SRC_RESOLUTION_PATH, DST_RESOLUTION_PATH);
    
    // Copy review source images
    await copyFiles(SRC_REVIEW_PATH, DST_REVIEW_PATH);
    
    console.log('Successfully copied all badge assets!');
  } catch (error) {
    console.error('Error copying badge assets:', error.message);
    process.exit(1);
  }
}

// Run the script
main();
