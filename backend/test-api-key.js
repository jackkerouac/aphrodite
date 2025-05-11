import dotenv from 'dotenv';
import { pool as db } from './db.js';

dotenv.config();

async function testApiKey() {
  try {
    // Get Jellyfin settings from database for user ID 1
    const userId = 1; // Adjust this if needed
    const settingsQuery = `
      SELECT jellyfin_url as url, jellyfin_api_key as token, jellyfin_user_id 
      FROM jellyfin_settings 
      WHERE user_id = $1
    `;
    
    const settingsResult = await db.query(settingsQuery, [userId]);
    const settings = settingsResult.rows[0];

    if (!settings) {
      console.log('No Jellyfin settings found for user ID:', userId);
      return;
    }

    console.log('API Key Analysis:');
    console.log('----------------');
    console.log('Length:', settings.token?.length);
    console.log('Type:', typeof settings.token);
    console.log('Starts with spaces?', settings.token?.startsWith(' '));
    console.log('Ends with spaces?', settings.token?.endsWith(' '));
    console.log('Contains spaces?', settings.token?.includes(' '));
    console.log('First 10 chars:', JSON.stringify(settings.token?.substring(0, 10)));
    console.log('Last 10 chars:', JSON.stringify(settings.token?.slice(-10)));
    
    // Check if it's a valid format (usually alphanumeric)
    const isAlphanumeric = /^[a-zA-Z0-9]+$/.test(settings.token);
    console.log('Is alphanumeric?', isAlphanumeric);
    
    // Check for common API key formats
    const hasHexFormat = /^[a-fA-F0-9]+$/.test(settings.token);
    console.log('Has hex format?', hasHexFormat);
    
    // Check if it might be base64
    const isBase64 = /^[A-Za-z0-9+/]+=*$/.test(settings.token);
    console.log('Looks like base64?', isBase64);

    // Try to clean the token
    const cleanedToken = settings.token?.trim();
    console.log('\nCleaned token length:', cleanedToken?.length);
    console.log('Different from original?', cleanedToken !== settings.token);

  } catch (error) {
    console.error('Error:', error);
  } finally {
    process.exit(0);
  }
}

testApiKey();
