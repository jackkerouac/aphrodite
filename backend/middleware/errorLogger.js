import logger from '../lib/logger.js';

export function errorLogger(err, req, res, next) {
  const message = `[${req.method}] ${req.originalUrl} — ${err.message}`;
  logger.error(message);

  if (process.env.NODE_ENV === 'development') {
    console.error(err.stack);
  }

  res.status(500).json({ error: 'Internal Server Error' });
}
