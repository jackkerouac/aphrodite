import { pool } from '../db.js';

export async function getJellyfinSettingsByUserId(userId) {
  const result = await pool.query(
    `SELECT id, user_id, jellyfin_url, jellyfin_api_key, jellyfin_user_id
     FROM jellyfin_settings
     WHERE user_id = $1`,
    [userId]
  );
  return result.rows[0] || null;
}

export async function upsertJellyfinSettings(settings) {
  const { user_id, jellyfin_url, jellyfin_api_key, jellyfin_user_id } = settings;
  const result = await pool.query(
    `INSERT INTO jellyfin_settings (user_id, jellyfin_url, jellyfin_api_key, jellyfin_user_id)
     VALUES ($1, $2, $3, $4)
     ON CONFLICT (user_id) DO UPDATE
       SET jellyfin_url     = EXCLUDED.jellyfin_url,
           jellyfin_api_key = EXCLUDED.jellyfin_api_key,
           jellyfin_user_id = EXCLUDED.jellyfin_user_id,
           updated_at       = CURRENT_TIMESTAMP
     RETURNING *;`,
    [user_id, jellyfin_url, jellyfin_api_key, jellyfin_user_id]
  );
  return result.rows[0];
}
