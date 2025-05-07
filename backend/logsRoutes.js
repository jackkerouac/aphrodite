import express from 'express';
const router = express.Router();
import fs from 'fs';
import path from 'path';
import logger from './lib/logger.js';

router.get('/', async (req, res) => {
    try {
        const { level, limit = 100, page = 1 } = req.query;
        const skip = (page - 1) * limit;

        const logDir = path.resolve('./logs');
        const logFile = path.join(logDir, 'aphrodite.log');

        if (!fs.existsSync(logFile)) {
            console.log('Log file not found, creating empty one');
            try {
                if (!fs.existsSync(logDir)) {
                    fs.mkdirSync(logDir, { recursive: true });
                }
                fs.writeFileSync(logFile, '');
            } catch (err) {
                console.error(`Error creating log file: ${err.message}`);
            }

            return res.json({
                total: 0,
                page: parseInt(page),
                limit: parseInt(limit),
                logs: []
            });
        }

        const content = fs.readFileSync(logFile, 'utf8');

        if (!content || content.trim() === '') {
            console.log('Log file is empty');
            return res.json({
                total: 0,
                page: parseInt(page),
                limit: parseInt(limit),
                logs: []
            });
        }

        const lines = content.trim().split('\n');
        let logs = lines.map(line => {
            try {
                const timestampMatch = line.match(/\[(.*?)\]/);
                const levelMatch = line.match(/\] (.*?):\s/);

                if (timestampMatch && levelMatch) {
                    const timestamp = timestampMatch[1];
                    const logLevel = levelMatch[1];
                    const message = line.substring(line.indexOf(': ') + 2);

                    return {
                        timestamp,
                        level: logLevel,
                        message
                    };
                }
                return null;
            } catch (err) {
                logger.error(`Error parsing log line: ${err.message}`);
                return null;
            }
        }).filter(log => log !== null);

        if (level) {
            logs = logs.filter(log => log.level.toLowerCase() === level.toLowerCase());
        }

        logs.reverse();

        const paginatedLogs = logs.slice(skip, skip + parseInt(limit));

        res.json({
            total: logs.length,
            page: parseInt(page),
            limit: parseInt(limit),
            logs: paginatedLogs
        });
    } catch (err) {
        logger.error(`Error fetching logs: ${err.message}`);
        res.status(500).json({ message: 'Server error', error: err.message });
    }
});

router.post('/clear', async (req, res) => {
    console.log('Logs cleared by user');
    try {
        const logDir = path.resolve('./logs');
        const logFile = path.join(logDir, 'aphrodite.log');

        if (!fs.existsSync(logFile)) {
            logger.warn('Log file not found');
            return res.status(404).json({ message: 'Log file not found' });
        }

        fs.writeFileSync(logFile, '');

        console.log('Logs cleared by user - ' + new Date().toISOString());

        res.json({ success: true, message: 'Logs cleared successfully' });
    } catch (err) {
        logger.error(`Error clearing logs: ${err.message}`);
        res.status(500).json({ message: 'Server error', error: err.message });
    }
});

export default router;