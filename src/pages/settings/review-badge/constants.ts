// Review source options
export const reviewSources = [
  'IMDB',
  'TMDB',
  'RottenTomatoes',
  'Metacritic',
  'AniDB'
];

// Badge position options
export const positionOptions = [
  'top-left',
  'top-right',
  'bottom-left',
  'bottom-right',
  'top-center',
  'bottom-center'
];

// Badge layout options
export const layoutOptions = [
  'horizontal', 
  'vertical'
];

// Font family options
export const fontFamilyOptions = [
  'Inter',
  'Arial',
  'Helvetica',
  'Roboto',
  'Open Sans',
  'Montserrat'
];

// Score format options
export const scoreFormatOptions = [
  'percentage',
  'decimal',
  'stars',
  'fraction'
];

// Dummy review data for preview
export const dummyReviewData = {
  IMDB: {
    score: 7.8,
    logo: '/src/assets/rating/IMDb.png'
  },
  TMDB: {
    score: 8.2,
    logo: '/src/assets/rating/TMDb.png'
  },
  RottenTomatoes: {
    score: 91,
    logo: '/src/assets/rating/RT-Crit-Fresh.png'
  },
  Metacritic: {
    score: 74,
    logo: '/src/assets/rating/metacritic_logo.png'
  },
  AniDB: {
    score: 8.5,
    logo: '/src/assets/rating/AniDB.png'
  }
};

// Helper function to format review scores based on format type and source
export const formatScore = (score: number, format: string, source: string): string => {
  switch (format) {
    case 'percentage':
      // IMDB and TMDB are on a 0-10 scale, convert to percentage
      if (source === 'IMDB' || source === 'TMDB' || source === 'AniDB') {
        return `${Math.round(score * 10)}%`;
      }
      // Rotten Tomatoes and Metacritic are already on a 0-100 scale
      else {
        return `${Math.round(score)}%`;
      }
    case 'decimal':
      // For consistency, all scores displayed in decimal format are on a 0-10 scale
      if (source === 'RottenTomatoes' || source === 'Metacritic') {
        return (score / 10).toFixed(1);
      } else {
        return score.toFixed(1);
      }
    case 'stars':
      // Convert all scores to a 0-10 scale for star rating
      let normalizedScore = score;
      if (source === 'RottenTomatoes' || source === 'Metacritic') {
        normalizedScore = score / 10;
      }
      return '★'.repeat(Math.round(normalizedScore / 2)) + '☆'.repeat(5 - Math.round(normalizedScore / 2));
    case 'fraction':
      // For consistency, all scores in fraction format show as x/10
      if (source === 'RottenTomatoes' || source === 'Metacritic') {
        return `${(score / 10).toFixed(1)}/10`;
      } else {
        return `${score.toFixed(1)}/10`;
      }
    default:
      return score.toString();
  }
};
