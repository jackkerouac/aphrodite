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

// Helper function to format review scores based on format type
export const formatScore = (score: number, format: string): string => {
  switch (format) {
    case 'percentage':
      return `${Math.round(score * 10)}%`;
    case 'decimal':
      return score.toFixed(1);
    case 'stars':
      return '★'.repeat(Math.round(score / 2)) + '☆'.repeat(5 - Math.round(score / 2));
    case 'fraction':
      return `${score.toFixed(1)}/10`;
    default:
      return score.toString();
  }
};
