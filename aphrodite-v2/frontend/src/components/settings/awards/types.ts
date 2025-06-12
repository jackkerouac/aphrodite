export interface AwardsSettings {
  General: {
    enabled: boolean;
    general_badge_size: number;
    general_badge_position: string;
    general_edge_padding: number;
    general_text_padding: number;
    use_dynamic_sizing: boolean;
  };
  Awards: {
    color_scheme: string;
    award_sources: string[];
  };
  Text: {
    font: string;
    fallback_font: string;
    'text-color': string;
    'text-size': number;
  };
  Background: {
    'background-color': string;
    background_opacity: number;
  };
  Border: {
    'border-color': string;
    'border-radius': number;
    border_width: number;
  };
  Shadow: {
    shadow_enable: boolean;
    shadow_blur: number;
    shadow_offset_x: number;
    shadow_offset_y: number;
  };
  ImageBadges: {
    enable_image_badges: boolean;
    codec_image_directory: string;
    fallback_to_text: boolean;
    image_padding: number;
    image_mapping: Record<string, string>;
  };
}

export interface ColorScheme {
  value: string;
  label: string;
  bgClass: string;
  previewClass: string;
  textClass: string;
}

export interface AwardSource {
  value: string;
  label: string;
  priority?: string;
}

export const defaultAwardsSettings: AwardsSettings = {
  General: {
    enabled: true,
    general_badge_size: 120,
    general_badge_position: 'bottom-right-flush',
    general_edge_padding: 0,
    general_text_padding: 0,
    use_dynamic_sizing: false
  },
  Awards: {
    color_scheme: 'yellow',
    award_sources: [
      'oscars', 'emmys', 'golden', 'bafta', 'cannes', 'crunchyroll'
    ]
  },
  Text: {
    font: 'AvenirNextLTProBold.otf',
    fallback_font: 'DejaVuSans.ttf',
    'text-color': '#FFFFFF',
    'text-size': 90
  },
  Background: {
    'background-color': '#000000',
    background_opacity: 40
  },
  Border: {
    'border-color': '#000000',
    'border-radius': 10,
    border_width: 1
  },
  Shadow: {
    shadow_enable: false,
    shadow_blur: 8,
    shadow_offset_x: 2,
    shadow_offset_y: 2
  },
  ImageBadges: {
    enable_image_badges: true,
    codec_image_directory: 'images/awards',
    fallback_to_text: false,
    image_padding: 0,
    image_mapping: {
      oscars: 'oscars.png',
      emmys: 'emmys.png',
      golden: 'golden.png',
      bafta: 'bafta.png',
      cannes: 'cannes.png',
      crunchyroll: 'crunchyroll.png',
      berlinale: 'berlinale.png',
      cesar: 'cesar.png',
      choice: 'choice.png',
      imdb: 'imdb.png',
      letterboxd: 'letterboxd.png',
      metacritic: 'metacritic.png',
      netflix: 'netflix.png',
      razzie: 'razzie.png',
      rotten: 'rotten.png',
      rottenverified: 'rottenverified.png',
      spirit: 'spirit.png',
      sundance: 'sundance.png',
      venice: 'venice.png'
    }
  }
};

export const colorSchemes: ColorScheme[] = [
  { 
    value: 'black', 
    label: 'Black', 
    bgClass: 'bg-gray-100',
    previewClass: 'bg-black border-gray-300',
    textClass: 'text-gray-900'
  },
  { 
    value: 'gray', 
    label: 'Gray', 
    bgClass: 'bg-gray-100',
    previewClass: 'bg-gray-500 border-gray-300',
    textClass: 'text-gray-700'
  },
  { 
    value: 'red', 
    label: 'Red', 
    bgClass: 'bg-red-50',
    previewClass: 'bg-red-600 border-red-300',
    textClass: 'text-red-700'
  },
  { 
    value: 'yellow', 
    label: 'Yellow', 
    bgClass: 'bg-yellow-50',
    previewClass: 'bg-yellow-500 border-yellow-300',
    textClass: 'text-yellow-700'
  }
];

export const awardSources: AwardSource[] = [
  { value: 'oscars', label: 'Academy Awards (Oscars)', priority: 'Highest' },
  { value: 'cannes', label: 'Cannes Film Festival', priority: 'Very High' },
  { value: 'golden', label: 'Golden Globe Awards', priority: 'High' },
  { value: 'bafta', label: 'BAFTA Awards', priority: 'High' },
  { value: 'emmys', label: 'Emmy Awards', priority: 'High' },
  { value: 'crunchyroll', label: 'Crunchyroll Anime Awards', priority: 'High' },
  { value: 'berlinale', label: 'Berlin International Film Festival', priority: 'Medium' },
  { value: 'venice', label: 'Venice Film Festival', priority: 'Medium' },
  { value: 'sundance', label: 'Sundance Film Festival', priority: 'Medium' },
  { value: 'spirit', label: 'Independent Spirit Awards', priority: 'Medium' },
  { value: 'choice', label: 'Critics Choice Awards', priority: 'Medium' },
  { value: 'cesar', label: 'César Awards', priority: 'Low' },
  { value: 'imdb', label: 'IMDb Top Lists', priority: 'Low' },
  { value: 'letterboxd', label: 'Letterboxd', priority: 'Low' },
  { value: 'metacritic', label: 'Metacritic', priority: 'Low' },
  { value: 'netflix', label: 'Netflix', priority: 'Low' },
  { value: 'razzie', label: 'Golden Raspberry Awards', priority: 'Low' },
  { value: 'rotten', label: 'Rotten Tomatoes', priority: 'Low' },
  { value: 'rottenverified', label: 'Rotten Tomatoes (Verified)', priority: 'Low' }
];
