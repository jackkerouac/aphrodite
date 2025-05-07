import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import logger from './lib/logger.js';
import { errorLogger } from './middleware/errorLogger.js';
import { requestLogger } from './requestLogger.js';

// Import route modules
import jellyfinSettingsRoutes from './routes/jellyfinSettingsRoutes.js';
import omdbSettingsRoutes from './routes/omdbSettingsRoutes.js';
import tmdbSettingsRoutes from './routes/tmdbSettingsRoutes.js';
import anidbSettingsRoutes from './routes/anidbSettingsRoutes.js';
import resolutionBadgeSettingsRoutes from './routes/resolutionBadgeSettingsRoutes.js';
import audioBadgeSettingsRoutes from './routes/audioBadgeSettingsRoutes.js';
import reviewBadgeSettingsRoutes from './routes/reviewBadgeSettingsRoutes.js';
import connectionTestsRoutes from './routes/connectionTestsRoutes.js';
import jellyfinLibrariesRoutes from './routes/jellyfinLibrariesRoutes.js';
import logsRoutes from './logsRoutes.js';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(requestLogger);

// Mount route modules
app.use('/api/jellyfin-settings', jellyfinSettingsRoutes);
app.use('/api/omdb-settings', omdbSettingsRoutes);
app.use('/api/tmdb-settings', tmdbSettingsRoutes);
app.use('/api/anidb-settings', anidbSettingsRoutes);
app.use('/api/resolution-badge-settings', resolutionBadgeSettingsRoutes);
app.use('/api/audio-badge-settings', audioBadgeSettingsRoutes);
app.use('/api/review-badge-settings', reviewBadgeSettingsRoutes);
app.use('/api/jellyfin-libraries', jellyfinLibrariesRoutes);
app.use('/api/logs', logsRoutes);
app.use('/api', connectionTestsRoutes);

// Error logger middleware - should be used after all routes
app.use(errorLogger);

// Start server
app.listen(port, () => {
  logger.info(`Server running on port ${port}`);
});