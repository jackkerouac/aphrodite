import {
    getTmdbSettingsByUserId,
    upsertTmdbSettings
  } from '../backend/models/tmdbSettings.js';
  
  (async function run() {
    try {
      console.log('Before:', await getTmdbSettingsByUserId(1));
  
      const saved = await upsertTmdbSettings({
        user_id: 1,
        api_key: 'TEST_TMDB_KEY'
      });
  
      console.log('Upserted:', saved);
      console.log('After:', await getTmdbSettingsByUserId(1));
    } catch (err) {
      console.error('Error in TMDb test:', err);
    } finally {
      process.exit(0);
    }
  })();
  