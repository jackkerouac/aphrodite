import winston from 'winston';
import path from 'path';
import fs from 'fs';

// Ensure logs directory exists
const logDir = path.resolve('backend/logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir);
}

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message }) => {
      return `[${timestamp}] ${level.toUpperCase()}: ${message}`;
    })
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({
      filename: path.join(logDir, 'aphrodite.log'),
      level: 'info',
    }),
  ],
});

export default logger;
