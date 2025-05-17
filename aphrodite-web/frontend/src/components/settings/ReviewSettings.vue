import { ref, reactive, onMounted } from 'vue';
import api from '@/api/config.js';

export default {
  name: 'ReviewSettings',
  
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const saving = ref(false);
    const success = ref(false);
    
    // Function to convert relative image paths to absolute URLs
    const getBaseUrl = () => {
      if (window.APHRODITE_BASE_URL) {
        return window.APHRODITE_BASE_URL;
      }
      if (process.env.VUE_APP_API_URL) {
        return process.env.VUE_APP_API_URL;
      }
      return '';
    };
    
    // Update image mappings to use absolute URLs
    const updateImageUrls = () => {
      const baseUrl = getBaseUrl();
      if (settings.ImageBadges && settings.ImageBadges.codec_image_directory) {
        // Keep track of the original directory for saving back to the settings file
        settings._originalImageDir = settings.ImageBadges.codec_image_directory;
        
        // Make sure directory path works with URLs (replace backslashes with forward slashes)
        settings.ImageBadges.codec_image_directory = settings.ImageBadges.codec_image_directory.replace(/\\/g, '/');
        
        // If not starting with a slash, add one
        if (!settings.ImageBadges.codec_image_directory.startsWith('/')) {
          settings.ImageBadges.codec_image_directory = '/' + settings.ImageBadges.codec_image_directory;
        }
      }
    };

    // Settings data structure
    const settings = reactive({
      General: {
        general_badge_size: 100,
        general_edge_padding: 30,
        general_badge_position: 'bottom-left', // Different default position than others
        general_text_padding: 20, // Increased padding for reviews
        use_dynamic_sizing: true,
        
        // Review-specific settings
        badge_orientation: 'vertical',
        badge_spacing: 10,
        max_badges_to_display: 5
      },
      Text: {
        font: "AvenirNextLTProBold.otf",
        fallback_font: "DejaVuSans.ttf",
        "text-color": "#FFFFFF",
        "text-size": 42  // Smaller text for reviews
      },
      Background: {
        "background-color": "#2C2C2C",  // Different background color
        background_opacity: 60  // Higher opacity
      },
      Border: {
        "border-color": "#2C2C2C",
        "border-radius": 10,
        border_width: 1
      },
      Shadow: {
        shadow_enable: true,  // Enabled by default for reviews
        shadow_blur: 5,
        shadow_offset_x: 2,
        shadow_offset_y: 2
      },
      ImageBadges: {
        enable_image_badges: true,
        codec_image_directory: "images/rating",
        fallback_to_text: true,
        image_padding: 5,
        image_mapping: {
          "Trakt": "Trakt.png",
          "AniDB": "AniDB.png",
          "IMDb": "IMDb.png",
          "IMDbTop": "IMDbTop.png",
          "IMDbTop100": "IMDbTop100.png",
          "IMDbTop250": "IMDbTop250.png",
          "IMDbTop1000": "IMDbTop1000.png",
          "Letterboxd": "Letterboxd.png",
          "Metacritic": "metacritic_logo.png",
          "MAL": "MAL.png",
          "MDBList": "MDBList.png",
          "MetacriticTop": "MetacriticTop.png",
          "RT-Aud-Fresh": "RT-Aud-Fresh.png",
          "RT-Aud-Rotten": "RT-Aud-Rotten.png",
          "RT-Aud-Top": "RT-Aud-Top.png",
          "RT-Crit-Fresh": "RT-Crit-Fresh.png",
          "RT-Crit-Rotten": "RT-Crit-Rotten.png",
          "RT-Crit-Top": "RT-Crit-Top.png",
          "Star": "Star.png",
          "TMDb": "TMDb.png"
        }
      }
    });
    
    // For handling image mappings
    const tempMapping = reactive({});
    
    // For adding new mappings
    const newMapping = reactive({
      source: '',
      image: ''
    });
    
    // Add new mapping
    const addMapping = () => {
      if (newMapping.source && newMapping.image) {
        settings.ImageBadges.image_mapping[newMapping.source] = newMapping.image;
        newMapping.source = '';
        newMapping.image = '';
      }
    };
    
    // Remove mapping
    const removeMapping = (key) => {
      const mapping = { ...settings.ImageBadges.image_mapping };
      delete mapping[key];
      settings.ImageBadges.image_mapping = mapping;
    };
    
  // ──────── LOAD from disk ────────
  const loadSettings = async () => {
    loading.value = true;
    error.value   = null;
    try {
      const res = await api.getConfig('badge_settings_review.yml');
      Object.assign(settings, res.data.config);
      
      // Update image URLs to use absolute paths
      updateImageUrls();
    } catch (err) {
      error.value = err.response?.data?.error || err.message;
    } finally {
      loading.value = false;
    }
  };

  onMounted(loadSettings);

  // ──────── SAVE to disk ────────
  const saveSettings = async () => {
    saving.value = true;
    error.value  = null;
    try {
      // If we have an original image directory path, restore it before saving
      if (settings._originalImageDir) {
        settings.ImageBadges.codec_image_directory = settings._originalImageDir;
        delete settings._originalImageDir;
      }
      
      await api.updateConfig('badge_settings_review.yml', settings);
      success.value = true;
      // clear after 3 seconds
      setTimeout(() => success.value = false, 3000);
      
      // Update image URLs again after saving
      updateImageUrls();
    } catch (err) {
      error.value = err.response?.data?.error || err.message;
    } finally {
      saving.value = false;
    }
  };
    
    return {
      loading,
      error,
      saving,
      settings,
      tempMapping,
      newMapping,
      addMapping,
      success,
      removeMapping,
      saveSettings,
      updateImageUrls,
      getBaseUrl
    };
  }
};
