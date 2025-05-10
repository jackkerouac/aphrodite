import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import logger from './lib/logger.js';
import { errorLogger } from './middleware/errorLogger.js';
import { requestLogger } from './middleware/requestLogger.js';

// Import route modules
import healthRoutes from './routes/health.js';
import jellyfinSettingsRoutes from './routes/jellyfinSettingsRoutes.js';
import omdbSettingsRoutes from './routes/omdbSettingsRoutes.js';
import tmdbSettingsRoutes from './routes/tmdbSettingsRoutes.js';
import anidbSettingsRoutes from './routes/anidbSettingsRoutes.js';
import resolutionBadgeSettingsRoutes from './routes/resolutionBadgeSettingsRoutes.js';
import audioBadgeSettingsRoutes from './routes/audioBadgeSettingsRoutes.js';
import reviewBadgeSettingsRoutes from './routes/reviewBadgeSettingsRoutes.js';
import connectionTestsRoutes from './routes/connectionTestsRoutes.js';
import jellyfinLibrariesRoutes from './routes/jellyfinLibrariesRoutes.js';
import libraryItemsRoutes from './routes/libraryItemsRoutes.js';
import logsRoutes from './logsRoutes.js';
import badgeFilesRoutes from './routes/badgeFilesRoutes.js';
import jobsRoutes from './routes/jobsRoutes.js';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

// Middleware
app.use(cors());
// Increase JSON payload size limit to handle base64 encoded images
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));
app.use(requestLogger);

// Mount route modules
app.use('/api/health', healthRoutes);
app.use('/api/jellyfin-settings', jellyfinSettingsRoutes);
app.use('/api/omdb-settings', omdbSettingsRoutes);
app.use('/api/tmdb-settings', tmdbSettingsRoutes);
app.use('/api/anidb-settings', anidbSettingsRoutes);
app.use('/api/resolution-badge-settings', resolutionBadgeSettingsRoutes);
app.use('/api/audio-badge-settings', audioBadgeSettingsRoutes);
app.use('/api/review-badge-settings', reviewBadgeSettingsRoutes);
app.use('/api/jellyfin-libraries', jellyfinLibrariesRoutes);
app.use('/api/library-items', libraryItemsRoutes);
app.use('/api/logs', logsRoutes);
app.use('/api/badge-files', badgeFilesRoutes);
app.use('/api/jobs', jobsRoutes);
app.use('/api/connection-tests', connectionTestsRoutes);

// Error logger middleware - should be used after all routes
app.use(errorLogger);

// Start server
app.listen(port, () => {
  logger.info(`Server running on port ${port}`);
});