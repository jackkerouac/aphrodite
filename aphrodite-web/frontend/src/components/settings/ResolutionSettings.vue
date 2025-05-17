import { ref, reactive, onMounted } from 'vue';
import api from '@/api/config.js';

export default {
  name: 'ResolutionSettings',
  
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

    // ──────── LOAD from disk ────────
  const loadSettings = async () => {
    loading.value = true;
    error.value   = null;
    try {
      const res = await api.getConfig('badge_settings_resolution.yml');
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

    // Settings data structure
    const settings = reactive({
      General: {
        general_badge_size: 100,
        general_edge_padding: 30,
        general_badge_position: 'top-right', // Different default position than audio
        general_text_padding: 12,
        use_dynamic_sizing: true
      },
      Text: {
        font: "AvenirNextLTProBold.otf",
        fallback_font: "DejaVuSans.ttf",
        "text-color": "#FFFFFF",
        "text-size": 90
      },
      Background: {
        "background-color": "#000000",
        background_opacity: 40
      },
      Border: {
        "border-color": "#000000",
        "border-radius": 10,
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
        codec_image_directory: "images/resolution",
        fallback_to_text: true,
        image_padding: 20,
        image_mapping: {
          "480": "480.png",
          "480p": "480p.png",
          "480pdv": "480pdv.png",
          "480pdvhdr": "480pdvhdr.png",
          "480pdvhdrplus": "480pdvhdrplus.png",
          "480phdr": "480phdr.png",
          "480pplus": "480pplus.png",
          "576p": "576p.png",
          "576pdv": "576pdv.png",
          "576pdvhdr": "576pdvhdr.png",
          "576pdvhdrplus": "576pdvhdrplus.png",
          "576phdr": "576phdr.png",
          "576pplus": "576pplus.png",
          "720": "720.png",
          "720p": "720p.png",
          "720pdv": "720pdv.png",
          "720pdvhdr": "720pdvhdr.png",
          "720pdvhdrplus": "720pdvhdrplus.png",
          "720phdr": "720phdr.png",
          "720pplus": "720pplus.png",
          "1080": "1080.png",
          "1080p": "1080p.png",
          "1080pdv": "1080pdv.png",
          "1080pdvhdr": "1080pdvhdr.png",
          "1080pdvhdrplus": "1080pdvhdrplus.png",
          "1080phdr": "1080phdr.png",
          "1080pplus": "1080pplus.png",
          "2160": "2160.png",
          "dv": "dv.png",
          "dvhdr": "dvhdr.png",
          "dvhdrplus": "dvhdrplus.png",
          "hdr": "hdr.png",
          "plus": "plus.png",
          "4k": "4k.png",
          "4kdv": "4kdv.png",
          "4kdvhdr": "4kdvhdr.png",
          "4kdvhdrplus": "4kdvhdrplus.png",
          "4khdr": "4khdr.png",
          "4kplus": "4kplus.png",
          "4ksvg": "4k.svg"
        }
      }
    });
    
    // For handling image mappings
    const tempMapping = reactive({});
    
    // For adding new mappings
    const newMapping = reactive({
      resolution: '',
      image: ''
    });
    
    // Add new mapping
    const addMapping = () => {
      if (newMapping.resolution && newMapping.image) {
        settings.ImageBadges.image_mapping[newMapping.resolution] = newMapping.image;
        newMapping.resolution = '';
        newMapping.image = '';
      }
    };
    
    // Remove mapping
    const removeMapping = (key) => {
      const mapping = { ...settings.ImageBadges.image_mapping };
      delete mapping[key];
      settings.ImageBadges.image_mapping = mapping;
    };
    
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
      
      await api.updateConfig('badge_settings_resolution.yml', settings);
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
