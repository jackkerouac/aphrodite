import {
  getJellyfinSettingsByUserId,
  upsertJellyfinSettings
} from '../backend/models/jellyfinSettings.js';



(async function run() {
  try {
    console.log('Before:', await getJellyfinSettingsByUserId(1));

    const saved = await upsertJellyfinSettings({
      user_id: 1,
      jellyfin_url: 'http://localhost:8096',
      jellyfin_api_key: 'MYKEY',
      jellyfin_user_id: 'my-user-id',
    });

    console.log('Upserted:', saved);
    console.log('After:', await getJellyfinSettingsByUserId(1));
  } catch (err) {
    console.error('Error in test script:', err);
  } finally {
    process.exit(0);
  }
})();
