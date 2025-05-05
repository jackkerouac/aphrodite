import {
    getOmdbSettingsByUserId,
    upsertOmdbSettings
  } from '../backend/models/omdbSettings.js';
  
  (async function run() {
    try {
      console.log('Before:', await getOmdbSettingsByUserId(1));
  
      const saved = await upsertOmdbSettings({
        user_id: 1,
        api_key: 'TEST_OMDB_KEY'
      });
  
      console.log('Upserted:', saved);
      console.log('After:', await getOmdbSettingsByUserId(1));
    } catch (err) {
      console.error('Error in OMDb test:', err);
    } finally {
      process.exit(0);
    }
  })();
  