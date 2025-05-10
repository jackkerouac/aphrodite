import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determine if we're running in a Docker container
const isDocker = process.env.DOCKER_CONTAINER === 'true' || false;

// Base paths
export const BASE_PATH = isDocker ? '/app' : path.resolve(__dirname, '../..');
export const LOGS_PATH = isDocker ? '/app/logs' : path.resolve(BASE_PATH, 'logs');
export const DATA_PATH = isDocker ? '/app/data' : path.resolve(BASE_PATH, 'data');
export const BACKEND_PATH = isDocker ? '/app/backend' : path.resolve(BASE_PATH, 'backend');
export const SCRIPTS_PATH = isDocker ? '/app/scripts' : path.resolve(BASE_PATH, 'scripts');

// Ensure directories exist
import fs from 'fs/promises';

export async function ensureDirectories() {
  try {
    await fs.mkdir(LOGS_PATH, { recursive: true });
    await fs.mkdir(DATA_PATH, { recursive: true });
    console.log(`Directories ensured: logs=${LOGS_PATH}, data=${DATA_PATH}`);
  } catch (error) {
    console.error('Error creating directories:', error);
  }
}

// Initialize on import
ensureDirectories().catch(console.error);
