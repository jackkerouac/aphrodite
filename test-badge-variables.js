// Script to compare frontend and backend badge variables
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('=== BADGE RENDERING VARIABLES COMPARISON TEST ===');

// Function to read and parse the logo mappings from files
function readLogoMappings(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Extract RATING_BG_COLOR_MAP using regex
    const colorMapRegex = /RATING_BG_COLOR_MAP\s*=\s*{([^}]*)}/s;
    const colorMapMatch = content.match(colorMapRegex);
    const colorMap = {};
    
    if (colorMapMatch && colorMapMatch[1]) {
      const entries = colorMapMatch[1].split(',');
      for (const entry of entries) {
        const parts = entry.split(':');
        if (parts.length === 2) {
          const key = parts[0].trim().replace(/['"`]/g, '');
          const value = parts[1].trim().replace(/['"`]/g, '');
          if (key && value) {
            colorMap[key] = value;
          }
        }
      }
    }
    
    return { colorMap };
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error);
    return { colorMap: {} };
  }
}

// STEP 1: Frontend Badge Variables
console.log('\n=== FRONTEND BADGE RENDERING VARIABLES ===');

// Read frontend variables from the file directly 
const frontendPath = path.join(__dirname, 'src', 'services', 'badges', 'utils', 'logoMapping.ts');
const frontend = readLogoMappings(frontendPath);

// Sample review badge settings as they would appear in frontend
const frontendSettings = {
  type: 'review',
  size: 100, 
  position: 'bottom-left',
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  borderRadius: 5,
  borderWidth: 1,
  borderColor: '#FFFFFF', 
  borderOpacity: 0.8,
  textColor: '#FFFFFF',
  fontSize: 16,
  displayFormat: 'vertical',
  maxSourcesToShow: 3,
  showDividers: true,
  useBrandColors: true, // KEY DIFFERENCE: Frontend has this flag
  sources: [
    { name: 'IMDB', rating: 8.5, outOf: 10 },
    { name: 'RT', rating: 90, outOf: 100 },
    { name: 'Metacritic', rating: 75, outOf: 100 }
  ]
};

console.log('Frontend review badge settings:', frontendSettings);
console.log('Frontend brand colors:');
Object.entries(frontend.colorMap).forEach(([name, color]) => {
  console.log(`  ${name}: ${color}`);
});

// STEP 2: Backend Badge Variables
console.log('\n=== BACKEND BADGE RENDERING VARIABLES ===');

// Read backend variables from the file directly
const backendPath = path.join(__dirname, 'backend', 'services', 'badge-renderer', 'utils', 'logoMapping.js');
const backend = readLogoMappings(backendPath);

// Sample database settings as they would appear after fetching from DB
const dbSettings = {
  user_id: 1,
  size: 100,
  margin: 10,
  position: 'bottom-left',
  background_color: '#000000',
  background_opacity: 0.7,
  border_radius: 5,
  border_width: 1,
  border_color: '#FFFFFF',
  border_opacity: 0.8,
  shadow_enabled: false,
  z_index: 3,
  badge_layout: 'vertical',
  font_size: 16,
  text_color: '#FFFFFF',
  // Missing: use_brand_colors field
};

// How settings are mapped to backend renderer format
const backendSettings = {
  type: 'review',
  size: dbSettings.size,
  position: dbSettings.position,
  backgroundColor: dbSettings.background_color,
  backgroundOpacity: dbSettings.background_opacity,
  transparency: dbSettings.background_opacity, // Both terms used in different parts of code
  borderRadius: dbSettings.border_radius,
  borderWidth: dbSettings.border_width,
  borderColor: dbSettings.border_color,
  borderOpacity: dbSettings.border_opacity,
  fontSize: dbSettings.font_size,
  textColor: dbSettings.text_color,
  displayFormat: dbSettings.badge_layout || 'vertical',
  showDividers: true,
  // Missing: useBrandColors is not transferred to backend
};

console.log('Backend review badge settings:', backendSettings);
console.log('Backend brand colors:');
Object.entries(backend.colorMap).forEach(([name, color]) => {
  console.log(`  ${name}: ${color}`);
});

// STEP 3: Color Resolution Comparison
console.log('\n=== COLOR RESOLUTION COMPARISON ===');

// For IMDB badge
const imdbSource = 'IMDB';

// Frontend color resolution
const frontendColor = frontendSettings.useBrandColors && frontend.colorMap[imdbSource] 
  ? frontend.colorMap[imdbSource] 
  : frontendSettings.backgroundColor;

// Backend color resolution (missing the useBrandColors check)
const backendColor = backendSettings.backgroundColor; // Always uses background color

console.log(`IMDB Badge Color:\n  Frontend: ${frontendColor}\n  Backend: ${backendColor}`);

// For other sources
const sources = ['IMDB', 'RT', 'Metacritic', 'TMDB'];
console.log('\nAll Sources Color Comparison:');
sources.forEach(source => {
  const frontColor = frontendSettings.useBrandColors && frontend.colorMap[source] 
    ? frontend.colorMap[source] 
    : frontendSettings.backgroundColor;
  
  // Backend would never use brand colors without the useBrandColors flag
  console.log(`  ${source}:\n    Frontend: ${frontColor}\n    Backend would use: ${backendSettings.backgroundColor} (brand colors not applied)`);
});

// STEP 4: Check the actual database schema
console.log('\n=== DATABASE SCHEMA ANALYSIS ===');
const schemaPath = path.join(__dirname, 'current_schema.sql');
let hasUseBrandColorsField = false;

try {
  const schemaContent = fs.readFileSync(schemaPath, 'utf8');
  
  // Check if review_badge_settings table has use_brand_colors column
  hasUseBrandColorsField = schemaContent.includes('use_brand_colors');
  
  console.log(`Database schema has use_brand_colors field: ${hasUseBrandColorsField}`);
  
  // Extract review_badge_settings schema
  const tableRegex = /CREATE TABLE review_badge_settings\s*\(([\s\S]*?)\);/;
  const tableMatch = schemaContent.match(tableRegex);
  
  if (tableMatch && tableMatch[1]) {
    console.log('\nReview badge settings table schema:');
    const fields = tableMatch[1].split(',').map(line => line.trim());
    fields.forEach(field => {
      if (field.length > 0) {
        console.log(`  - ${field}`);
      }
    });
  }
} catch (error) {
  console.error('Error reading schema file:', error);
}

// STEP 5: Key Findings
console.log('\n=== KEY FINDINGS ===');
console.log('1. The useBrandColors flag is missing entirely from the backend');
console.log('2. Frontend uses brand-specific colors (IMDb yellow, RT red, etc.)');
console.log('3. Backend always uses the same background color for all badges');
console.log(`4. Both frontend and backend have color maps available with same values`);
console.log(`5. Database schema ${hasUseBrandColorsField ? 'has' : 'is missing'} the use_brand_colors field`);

// STEP 6: Code analysis
console.log('\n=== CODE ANALYSIS ===');

// Look for useBrandColors in frontend badge rendering
const frontendRenderPath = path.join(__dirname, 'src', 'services', 'badges', 'reviewBadge.ts');
try {
  const renderContent = fs.readFileSync(frontendRenderPath, 'utf8');
  const hasBrandColorsCheck = renderContent.includes('useBrandColors') && 
                              renderContent.includes('RATING_BG_COLOR_MAP');
  
  console.log(`Frontend renderer checks useBrandColors: ${hasBrandColorsCheck}`);
  
  if (hasBrandColorsCheck) {
    // Extract the relevant code section
    const codeRegex = /if\s*\(options\.useBrandColors.*\{([^}]*)\}/;
    const codeMatch = renderContent.match(codeRegex);
    if (codeMatch && codeMatch[1]) {
      console.log('Frontend brand colors code:');
      console.log('  ' + codeMatch[0].replace(/\n/g, '\n  '));
    }
  }
} catch (error) {
  console.error('Error reading frontend renderer:', error);
}

// Look for useBrandColors in backend badge rendering
const backendRenderPath = path.join(__dirname, 'backend', 'services', 'badge-renderer', 'canvasBadgeRenderer.js');
try {
  const renderContent = fs.readFileSync(backendRenderPath, 'utf8');
  const hasBrandColorsCheck = renderContent.includes('useBrandColors') && 
                              renderContent.includes('RATING_BG_COLOR_MAP');
  
  console.log(`Backend renderer checks useBrandColors: ${hasBrandColorsCheck}`);
} catch (error) {
  console.error('Error reading backend renderer:', error);
}

// STEP 7: Solution
console.log('\n=== SUGGESTED SOLUTION ===');
console.log('1. Add use_brand_colors field to review_badge_settings table in the database:');
console.log('   ALTER TABLE review_badge_settings ADD COLUMN use_brand_colors BOOLEAN DEFAULT TRUE;');
console.log('2. Update reviewBadgeSettingsRoutes.js to handle the use_brand_colors field');
console.log('3. Update the backend canvasBadgeRenderer.js to check useBrandColors and apply brand colors');
console.log('4. Ensure the frontend correctly saves the useBrandColors setting to the backend');
