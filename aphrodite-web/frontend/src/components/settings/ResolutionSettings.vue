<template>
  <div class="resolution-settings">
    <h2 class="text-xl font-bold mb-4">Resolution Badge Settings</h2>
    
    <form @submit.prevent="saveSettings" class="space-y-6">
      <!-- General Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">General Settings</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="badge-size" class="block text-sm font-medium text-gray-700 mb-1">Badge Size</label>
            <input 
              id="badge-size" 
              v-model.number="settings.General.general_badge_size" 
              type="number" 
              min="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="100"
            />
          </div>
          
          <div class="form-group">
            <label for="edge-padding" class="block text-sm font-medium text-gray-700 mb-1">Edge Padding</label>
            <input 
              id="edge-padding" 
              v-model.number="settings.General.general_edge_padding" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="30"
            />
          </div>
          
          <div class="form-group">
            <label for="badge-position" class="block text-sm font-medium text-gray-700 mb-1">Badge Position</label>
            <select 
              id="badge-position" 
              v-model="settings.General.general_badge_position" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="top-left">Top Left</option>
              <option value="top-right">Top Right</option>
              <option value="bottom-left">Bottom Left</option>
              <option value="bottom-right">Bottom Right</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="text-padding" class="block text-sm font-medium text-gray-700 mb-1">Text Padding</label>
            <input 
              id="text-padding" 
              v-model.number="settings.General.general_text_padding" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="12"
            />
          </div>
          
          <div class="form-group col-span-full">
            <div class="flex items-center">
              <input 
                id="dynamic-sizing" 
                v-model="settings.General.use_dynamic_sizing" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="dynamic-sizing" class="ml-2 block text-sm text-gray-700">Use Dynamic Sizing</label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Text Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">Text Settings</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="font" class="block text-sm font-medium text-gray-700 mb-1">Font</label>
            <input 
              id="font" 
              v-model="settings.Text.font" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="AvenirNextLTProBold.otf"
            />
          </div>
          
          <div class="form-group">
            <label for="fallback-font" class="block text-sm font-medium text-gray-700 mb-1">Fallback Font</label>
            <input 
              id="fallback-font" 
              v-model="settings.Text.fallback_font" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="DejaVuSans.ttf"
            />
          </div>
          
          <div class="form-group">
            <label for="text-color" class="block text-sm font-medium text-gray-700 mb-1">Text Color</label>
            <div class="flex">
              <input 
                id="text-color-picker" 
                type="color" 
                v-model="settings.Text['text-color']" 
                class="h-10 w-10 rounded-l-md border border-gray-300 border-r-0"
              />
              <input 
                id="text-color" 
                v-model="settings.Text['text-color']" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-r-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="#FFFFFF"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="text-size" class="block text-sm font-medium text-gray-700 mb-1">Text Size</label>
            <input 
              id="text-size" 
              v-model.number="settings.Text['text-size']" 
              type="number" 
              min="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="90"
            />
          </div>
        </div>
      </div>
      
      <!-- Background Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">Background Settings</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="background-color" class="block text-sm font-medium text-gray-700 mb-1">Background Color</label>
            <div class="flex">
              <input 
                id="background-color-picker" 
                type="color" 
                v-model="settings.Background['background-color']" 
                class="h-10 w-10 rounded-l-md border border-gray-300 border-r-0"
              />
              <input 
                id="background-color" 
                v-model="settings.Background['background-color']" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-r-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="#000000"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="background-opacity" class="block text-sm font-medium text-gray-700 mb-1">Background Opacity (%)</label>
            <input 
              id="background-opacity" 
              v-model.number="settings.Background.background_opacity" 
              type="number" 
              min="0"
              max="100"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="40"
            />
          </div>
        </div>
      </div>
      
      <!-- Border Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">Border Settings</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-group">
            <label for="border-color" class="block text-sm font-medium text-gray-700 mb-1">Border Color</label>
            <div class="flex">
              <input 
                id="border-color-picker" 
                type="color" 
                v-model="settings.Border['border-color']" 
                class="h-10 w-10 rounded-l-md border border-gray-300 border-r-0"
              />
              <input 
                id="border-color" 
                v-model="settings.Border['border-color']" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-r-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="#000000"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="border-radius" class="block text-sm font-medium text-gray-700 mb-1">Border Radius</label>
            <input 
              id="border-radius" 
              v-model.number="settings.Border['border-radius']" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="10"
            />
          </div>
          
          <div class="form-group">
            <label for="border-width" class="block text-sm font-medium text-gray-700 mb-1">Border Width</label>
            <input 
              id="border-width" 
              v-model.number="settings.Border.border_width" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="1"
            />
          </div>
        </div>
      </div>
      
      <!-- Shadow Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">Shadow Settings</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group col-span-full">
            <div class="flex items-center">
              <input 
                id="shadow-enable" 
                v-model="settings.Shadow.shadow_enable" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="shadow-enable" class="ml-2 block text-sm text-gray-700">Enable Shadow</label>
            </div>
          </div>
          
          <div class="form-group">
            <label for="shadow-blur" class="block text-sm font-medium text-gray-700 mb-1">Shadow Blur</label>
            <input 
              id="shadow-blur" 
              v-model.number="settings.Shadow.shadow_blur" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="8"
              :disabled="!settings.Shadow.shadow_enable"
            />
          </div>
          
          <div class="form-group">
            <label for="shadow-offset-x" class="block text-sm font-medium text-gray-700 mb-1">Shadow Offset X</label>
            <input 
              id="shadow-offset-x" 
              v-model.number="settings.Shadow.shadow_offset_x" 
              type="number" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="2"
              :disabled="!settings.Shadow.shadow_enable"
            />
          </div>
          
          <div class="form-group">
            <label for="shadow-offset-y" class="block text-sm font-medium text-gray-700 mb-1">Shadow Offset Y</label>
            <input 
              id="shadow-offset-y" 
              v-model.number="settings.Shadow.shadow_offset_y" 
              type="number" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="2"
              :disabled="!settings.Shadow.shadow_enable"
            />
          </div>
        </div>
      </div>
      
      <!-- Image Badge Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">Image Badge Settings</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group col-span-full">
            <div class="flex items-center">
              <input 
                id="enable-image-badges" 
                v-model="settings.ImageBadges.enable_image_badges" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="enable-image-badges" class="ml-2 block text-sm text-gray-700">Enable Image Badges</label>
            </div>
          </div>
          
          <div class="form-group col-span-full">
            <label for="codec-image-directory" class="block text-sm font-medium text-gray-700 mb-1">Resolution Image Directory</label>
            <input 
              id="codec-image-directory" 
              v-model="settings.ImageBadges.codec_image_directory" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="images/resolution"
              :disabled="!settings.ImageBadges.enable_image_badges"
            />
          </div>
          
          <div class="form-group">
            <div class="flex items-center">
              <input 
                id="fallback-to-text" 
                v-model="settings.ImageBadges.fallback_to_text" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                :disabled="!settings.ImageBadges.enable_image_badges"
              />
              <label for="fallback-to-text" class="ml-2 block text-sm text-gray-700">Fallback to Text</label>
            </div>
          </div>
          
          <div class="form-group">
            <label for="image-padding" class="block text-sm font-medium text-gray-700 mb-1">Image Padding</label>
            <input 
              id="image-padding" 
              v-model.number="settings.ImageBadges.image_padding" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="20"
              :disabled="!settings.ImageBadges.enable_image_badges"
            />
          </div>
        </div>
      </div>
      
      <!-- Image Mappings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">Image Mappings</h3>
        <p class="text-sm text-gray-600 mb-4">Map resolution values to image filenames</p>
        
        <div class="space-y-2 max-h-80 overflow-y-auto p-2">
          <div v-for="(imageName, resolution) in settings.ImageBadges.image_mapping" :key="resolution" class="grid grid-cols-12 gap-2 items-center">
            <input 
              v-model="tempMapping[resolution]" 
              type="text" 
              class="col-span-5 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
              :placeholder="resolution"
              :disabled="!settings.ImageBadges.enable_image_badges"
            />
            <span class="col-span-1 text-center">→</span>
            <input 
              v-model="settings.ImageBadges.image_mapping[resolution]" 
              type="text" 
              class="col-span-5 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
              :placeholder="imageName"
              :disabled="!settings.ImageBadges.enable_image_badges"
            />
            <button 
              @click="removeMapping(resolution)" 
              type="button" 
              class="col-span-1 text-red-500 hover:text-red-700 focus:outline-none"
              :disabled="!settings.ImageBadges.enable_image_badges"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 000 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          
          <!-- Add new mapping -->
          <div class="grid grid-cols-12 gap-2 items-center mt-4">
            <input 
              v-model="newMapping.resolution" 
              type="text" 
              class="col-span-5 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
              placeholder="Resolution (e.g., 1080p)"
              :disabled="!settings.ImageBadges.enable_image_badges"
            />
            <span class="col-span-1 text-center">→</span>
            <input 
              v-model="newMapping.image" 
              type="text" 
              class="col-span-5 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
              placeholder="Image Name (e.g., 1080p.png)"
              :disabled="!settings.ImageBadges.enable_image_badges"
            />
            <button 
              @click="addMapping" 
              type="button" 
              class="col-span-1 text-green-500 hover:text-green-700 focus:outline-none"
              :disabled="!settings.ImageBadges.enable_image_badges || !newMapping.resolution || !newMapping.image"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Submit Button -->
      <div class="flex justify-end">
        <button
          @click="saveSettings"
          :disabled="saving"
          class="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {{ saving ? 'Saving…' : 'Save Resolution Settings' }}
        </button>
        <p v-if="error" class="mt-2 text-sm text-red-500">{{ error }}</p>
      </div>
      <!-- Toast (appears top-right) -->
        <div class="toast toast-top toast-end w-64" v-if="success">
        <div class="alert alert-success shadow-lg w-64 flex items-center space-x-2">
          <!-- icon -->
          <svg xmlns="http://www.w3.org/2000/svg" 
              class="stroke-current h-6 w-6 flex-shrink-0" 
              fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" 
                  stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <!-- text -->
          <span>Resolution settings saved!</span>
        </div>
      </div>
      <div class="toast toast-top toast-end w-64" v-if="error">
          <div class="alert alert-error shadow-lg w-64 flex items-center space-x-2">
            <div>
              <!-- icon -->
              <svg xmlns="http://www.w3.org/2000/svg" 
                  class="stroke-current h-6 w-6 flex-shrink-0" 
                  fill="none" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" 
                      stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Resolution settings NOT saved!</span>
            </div>
          </div>
        </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import api from '@/api/config.js';

export default {
  name: 'ResolutionSettings',
  
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const saving = ref(false);
    const success = ref(false);

    // ──────── LOAD from disk ────────
  const loadSettings = async () => {
    loading.value = true;
    error.value   = null;
    try {
      const res = await api.getConfig('badge_settings_resolution.yml');
      Object.assign(settings, res.data.config);
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
      await api.updateConfig('badge_settings_resolution.yml', settings);
      success.value = true;
      // clear after 3 seconds
      setTimeout(() => success.value = false, 3000);
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
      saveSettings
    };
  }
};
</script>
