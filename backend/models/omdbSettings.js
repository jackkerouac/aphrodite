import { pool } from '../db.js';

/**
 * Fetch OMDb settings for a given user ID.
 */
export async function getOmdbSettingsByUserId(userId) {
  const result = await pool.query(
    `SELECT id, user_id, api_key
     FROM omdb_settings
     WHERE user_id = $1`,
    [userId]
  );
  return result.rows[0] || null;
}

/**
 * Insert or update OMDb settings for a user.
 */
export async function upsertOmdbSettings({ user_id, api_key }) {
  const result = await pool.query(
    `INSERT INTO omdb_settings (user_id, api_key)
     VALUES ($1, $2)
     ON CONFLICT (user_id) DO UPDATE
       SET api_key     = EXCLUDED.api_key,
           updated_at  = CURRENT_TIMESTAMP
     RETURNING *;`,
    [user_id, api_key]
  );
  return result.rows[0];
}
