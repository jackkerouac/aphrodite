// Test file to verify frontend types are working
import { defaultReviewSettings } from '../src/components/settings/review/types';

console.log('Default review settings:', defaultReviewSettings);
console.log('Sources section exists:', 'Sources' in defaultReviewSettings);
console.log('MyAnimeList setting exists:', 'enable_myanimelist' in defaultReviewSettings.Sources);
console.log('MyAnimeList default value:', defaultReviewSettings.Sources.enable_myanimelist);
