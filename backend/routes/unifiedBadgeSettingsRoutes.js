import express from 'express';
import {
  getBadgeSettings,
  getAllBadgeSettingsForUser,
  saveBadgeSettings,
  deleteBadgeSettingsHandler
} from '../controllers/unifiedBadgeController.js';

const router = express.Router();

/**
 * @route GET /api/badge-settings/:userId/:badgeType
 * @desc Get badge settings by type
 * @access Private
 */
router.get('/:userId/:badgeType', getBadgeSettings);

/**
 * @route GET /api/badge-settings/:userId
 * @desc Get all badge settings for a user
 * @access Private
 */
router.get('/:userId', getAllBadgeSettingsForUser);

/**
 * @route POST /api/badge-settings/:userId/:badgeType
 * @desc Save badge settings
 * @access Private
 */
router.post('/:userId/:badgeType', saveBadgeSettings);

/**
 * @route DELETE /api/badge-settings/:userId/:badgeType
 * @desc Delete badge settings
 * @access Private
 */
router.delete('/:userId/:badgeType', deleteBadgeSettingsHandler);

export default router;
