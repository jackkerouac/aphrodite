import { pool } from '../db.js';

/**
 * Fetch TMDb settings for a given user ID.
 */
export async function getTmdbSettingsByUserId(userId) {
  const result = await pool.query(
    `SELECT id, user_id, api_key
     FROM tmdb_settings
     WHERE user_id = $1`,
    [userId]
  );
  return result.rows[0] || null;
}

/**
 * Insert or update TMDb settings for a user.
 */
export async function upsertTmdbSettings({ user_id, api_key }) {
  const result = await pool.query(
    `INSERT INTO tmdb_settings (user_id, api_key)
     VALUES ($1, $2)
     ON CONFLICT (user_id) DO UPDATE
       SET api_key     = EXCLUDED.api_key,
           updated_at  = CURRENT_TIMESTAMP
     RETURNING *;`,
    [user_id, api_key]
  );
  return result.rows[0];
}
