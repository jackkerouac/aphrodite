import express from 'express';
import {
  getBadgeSettings,
  getAllBadgeSettingsForUser,
  saveBadgeSettings,
  saveBatchBadgeSettings,
  deleteBadgeSettingsHandler
} from '../controllers/unifiedBadgeController.js';

const router = express.Router();

/**
 * @route GET /api/v1/unified-badge-settings/:badgeType
 * @desc Get badge settings by type
 * @access Private
 */
router.get('/:badgeType', (req, res) => {
  req.params.userId = req.query.user_id || '1';
  getBadgeSettings(req, res);
});

/**
 * @route GET /api/v1/unified-badge-settings
 * @desc Get all badge settings for a user
 * @access Private
 */
router.get('/', (req, res) => {
  req.params.userId = req.query.user_id || '1';
  getAllBadgeSettingsForUser(req, res);
});

/**
 * @route POST /api/v1/unified-badge-settings/:badgeType
 * @desc Save badge settings
 * @access Private
 */
router.post('/:badgeType', (req, res) => {
  req.params.userId = req.body.user_id || '1';
  saveBadgeSettings(req, res);
});

/**
 * @route POST /api/v1/unified-badge-settings/batch
 * @desc Save multiple badge settings at once
 * @access Private
 */
router.post('/batch', (req, res) => {
  saveBatchBadgeSettings(req, res);
});

/**
 * @route DELETE /api/v1/unified-badge-settings/:badgeType
 * @desc Delete badge settings
 * @access Private
 */
router.delete('/:badgeType', (req, res) => {
  req.params.userId = req.query.user_id || '1';
  deleteBadgeSettingsHandler(req, res);
});

export default router;
