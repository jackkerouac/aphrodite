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
            <input 
              id="text-color" 
              v-model="settings.Text['text-color']" 
              type="color" 
              class="w-full h-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
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
            <label for="bg-color" class="block text-sm font-medium text-gray-700 mb-1">Background Color</label>
            <input 
              id="bg-color" 
              v-model="settings.Background['background-color']" 
              type="color" 
              class="w-full h-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div class="form-group">
            <label for="bg-opacity" class="block text-sm font-medium text-gray-700 mb-1">Background Opacity (%)</label>
            <input 
              id="bg-opacity" 
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
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="border-color" class="block text-sm font-medium text-gray-700 mb-1">Border Color</label>
            <input 
              id="border-color" 
              v-model="settings.Border['border-color']" 
              type="color" 
              class="w-full h-10 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
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
          
          <div class="form-group">
            <label for="border-radius" class="block text-sm font-medium text-gray-700 mb-1">Border Radius</label>
            <input 
              id="border-radius" 
              v-model.number="settings.Border.border_radius" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="10"
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
            />
          </div>
          
          <div class="form-group">
            <label for="shadow-x" class="block text-sm font-medium text-gray-700 mb-1">Shadow X Offset</label>
            <input 
              id="shadow-x" 
              v-model.number="settings.Shadow.shadow_offset_x" 
              type="number" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="2"
            />
          </div>
          
          <div class="form-group">
            <label for="shadow-y" class="block text-sm font-medium text-gray-700 mb-1">Shadow Y Offset</label>
            <input 
              id="shadow-y" 
              v-model.number="settings.Shadow.shadow_offset_y" 
              type="number" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="2"
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
              <label for="enable-image-badges" class="ml-2 block text-sm text-gray-700">Use Image Badges</label>
            </div>
          </div>
          
          <div class="form-group col-span-full">
            <div class="flex items-center">
              <input 
                id="fallback-to-text" 
                v-model="settings.ImageBadges.fallback_to_text" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="fallback-to-text" class="ml-2 block text-sm text-gray-700">Fallback to Text</label>
            </div>
          </div>
          
          <div class="form-group">
            <label for="image-dir" class="block text-sm font-medium text-gray-700 mb-1">Image Directory</label>
            <input 
              id="image-dir" 
              v-model="settings.ImageBadges.codec_image_directory" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="images/resolution"
            />
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
            />
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

    // Initialize all sections with default values
    const settings = reactive({
      General: {
        general_badge_size: 100,
        general_edge_padding: 30,
        general_badge_position: 'top-right',
        general_text_padding: 12,
        use_dynamic_sizing: true
      },
      Text: {
        fallback_font: "DejaVuSans.ttf",
        font: "AvenirNextLTProBold.otf",
        "text-color": "#FFFFFF",
        "text-size": 90
      },
      Background: {
        "background-color": "#000000",
        background_opacity: 40
      },
      Border: {
        "border-color": "#000000",
        border_radius: 10,
        border_width: 1
      },
      Shadow: {
        shadow_blur: 8,
        shadow_enable: false,
        shadow_offset_x: 2,
        shadow_offset_y: 2
      },
      ImageBadges: {
        codec_image_directory: "images/resolution",
        enable_image_badges: true,
        fallback_to_text: true,
        image_mapping: {},
        image_padding: 20
      }
    });

    // Deep merge function for nested objects
    const deepMerge = (target, source) => {
      for (const key in source) {
        // Using Object.prototype.hasOwnProperty.call instead of source.hasOwnProperty
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
            // If we don't have this property yet, create it
            if (!target[key]) Object.assign(target, { [key]: {} });
            
            // Recursively merge nested objects
            deepMerge(target[key], source[key]);
          } else {
            // For primitives and arrays, simply copy the value
            Object.assign(target, { [key]: source[key] });
          }
        }
      }
      return target;
    };

    // Load settings
    const loadSettings = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const res = await api.getConfig('badge_settings_resolution.yml');
        console.log('DEBUG: Resolution settings loaded:', res.data.config);
        
        // Properly merge nested objects instead of using Object.assign
        if (res.data.config) {
          deepMerge(settings, res.data.config);
        }
      } catch (err) {
        console.error('DEBUG: Error loading resolution settings:', err);
        error.value = err.response?.data?.error || err.message;
      } finally {
        loading.value = false;
      }
    };

    // Save settings
    const saveSettings = async () => {
      saving.value = true;
      error.value = null;
      
      try {
        await api.updateConfig('badge_settings_resolution.yml', settings);
        success.value = true;
        setTimeout(() => success.value = false, 3000);
      } catch (err) {
        console.error('DEBUG: Error saving resolution settings:', err);
        error.value = err.response?.data?.error || err.message;
      } finally {
        saving.value = false;
      }
    };

    onMounted(loadSettings);
    
    return {
      loading,
      error,
      saving,
      success,
      settings,
      saveSettings
    };
  }
};
</script>
