// Import logos directly to ensure Vite bundles them correctly
import IMDbLogo from '@/assets/rating/IMDb.png';
import RTLogo from '@/assets/rating/RT-Crit-Fresh.png';
import MALLogo from '@/assets/rating/MAL.png';
import TMDbLogo from '@/assets/rating/TMDb.png';
import MetacriticLogo from '@/assets/rating/metacritic_logo.png';
import LetterboxdLogo from '@/assets/rating/Letterboxd.png';
import TraktLogo from '@/assets/rating/Trakt.png';
import AniDBLogo from '@/assets/rating/AniDB.png';

// Map of rating source names to logo paths
export const RATING_LOGO_MAP: Record<string, string> = {
  'IMDB': IMDbLogo,
  'RT': RTLogo,
  'MAL': MALLogo,
  'TMDB': TMDbLogo,
  'Metacritic': MetacriticLogo,
  'Letterboxd': LetterboxdLogo,
  'Trakt': TraktLogo,
  'AniDB': AniDBLogo
};

// Map of rating source names to their standard background colors
export const RATING_BG_COLOR_MAP: Record<string, string> = {
  'IMDB': '#F5C518',      // IMDb yellow
  'RT': '#FA320A',       // Rotten Tomatoes red
  'MAL': '#2E51A2',      // MyAnimeList blue
  'TMDB': '#0D253F',     // TMDb dark blue
  'Metacritic': '#000000', // Metacritic black
  'Letterboxd': '#00E054', // Letterboxd green
  'Trakt': '#ED2224',    // Trakt red
  'AniDB': '#3A3744'     // AniDB purple
};