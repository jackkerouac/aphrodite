#!/usr/bin/env node

/**
 * Script to replace all API_BASE_URL references with buildApiUrl() calls
 * in the frontend API service file
 */

const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'frontend', 'src', 'services', 'api.ts');

try {
  // Read the current file
  let content = fs.readFileSync(filePath, 'utf8');
  
  console.log('🔧 Updating API service to use dynamic URL resolution...');
  
  // Replace all instances of `${API_BASE_URL}` with `buildApiUrl(`
  content = content.replace(/\$\{API_BASE_URL\}/g, '${buildApiUrl(');
  
  // Fix the specific cases where we need to close the buildApiUrl call properly
  // Replace patterns like `buildApiUrl(/api/path` with `buildApiUrl('/api/path')`
  content = content.replace(/buildApiUrl\(([^)]+)\)/g, (match, path) => {
    // If the path is already properly quoted, keep it
    if (path.includes("'") || path.includes('"')) {
      return `buildApiUrl(${path})`;
    }
    // If it's a template literal, convert it
    if (path.includes('`')) {
      return `buildApiUrl(${path})`;
    }
    // Otherwise, wrap in quotes
    return `buildApiUrl('${path}')`;
  });
  
  // Handle URL construction patterns
  content = content.replace(/buildApiUrl\('\$\{([^}]+)\}([^']+)'\)/g, 'buildApiUrl(`${$1}$2`)');
  
  // Write the updated file
  fs.writeFileSync(filePath, content, 'utf8');
  
  console.log('✅ Successfully updated API service');
  console.log('📝 All API calls now use dynamic URL resolution');
  
} catch (error) {
  console.error('❌ Error updating API service:', error.message);
  process.exit(1);
}
