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
    logo: '/src/assets/logos/imdb.png' // This will need to be created
  },
  TMDB: {
    score: 8.2,
    logo: '/src/assets/logos/tmdb.png' // This will need to be created
  },
  RottenTomatoes: {
    score: 91,
    logo: '/src/assets/logos/rottentomatoes.png' // This will need to be created
  },
  Metacritic: {
    score: 74,
    logo: '/src/assets/logos/metacritic.png' // This will need to be created
  },
  AniDB: {
    score: 8.5,
    logo: '/src/assets/logos/anidb.png' // This will need to be created
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
