#!/usr/bin/env node
/**
 * Script to update API Settings components to use Daisy UI
 */

const fs = require('fs');
const path = require('path');

const componentsDir = 'E:\\programming\\aphrodite\\aphrodite-web\\frontend\\src\\components\\settings\\api';

const components = [
  'OmdbSettings.vue',
  'TmdbSettings.vue', 
  'MdblistSettings.vue',
  'AnidbSettings.vue'
];

const transformTemplate = (content) => {
  // Replace the main container
  content = content.replace(
    /class="bg-white shadow rounded-lg p-4 border border-gray-200"/g,
    'class="card bg-base-100 shadow-xl"'
  );
  
  // Add card-body wrapper
  content = content.replace(
    /<div class="card bg-base-100 shadow-xl">\s*<h3/g,
    '<div class="card bg-base-100 shadow-xl">\n    <div class="card-body">\n      <h3'
  );
  
  // Replace h3 class
  content = content.replace(
    /class="text-lg font-medium mb-3"/g,
    'class="card-title"'
  );
  
  // Replace grid container
  content = content.replace(
    /class="grid grid-cols-1 gap-4"/g,
    'class="space-y-4"'
  );
  
  // Replace form-group divs with form-control
  content = content.replace(
    /<div class="form-group">/g,
    '<div class="form-control w-full">'
  );
  
  // Replace labels
  content = content.replace(
    /<label for="([^"]*)" class="block text-sm font-medium text-gray-700 mb-1">([^<]*)<\/label>/g,
    '<label class="label" for="$1">\n          <span class="label-text">$2</span>\n        </label>'
  );
  
  // Replace input classes
  content = content.replace(
    /class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"/g,
    'class="input input-bordered w-full"'
  );
  
  // Replace select classes
  content = content.replace(
    /class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"/g,
    'class="select select-bordered w-full"'
  );
  
  // Close the card-body div before closing the main div
  content = content.replace(
    /(\s*)<\/div>\s*<\/template>/,
    '$1  </div>\n  </div>\n</template>'
  );
  
  return content;
};

components.forEach(componentFile => {
  const filePath = path.join(componentsDir, componentFile);
  
  if (fs.existsSync(filePath)) {
    console.log(`Updating ${componentFile}...`);
    
    let content = fs.readFileSync(filePath, 'utf8');
    content = transformTemplate(content);
    
    fs.writeFileSync(filePath, content);
    console.log(`✓ Updated ${componentFile}`);
  } else {
    console.log(`✗ File not found: ${componentFile}`);
  }
});

console.log('All API components updated to use Daisy UI!');
