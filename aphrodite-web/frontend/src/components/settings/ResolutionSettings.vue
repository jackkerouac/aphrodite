<template>
  <div class="resolution-settings">
    <h2 class="text-xl font-bold mb-4">Resolution Badge Settings</h2>
    
    <form @submit.prevent="saveSettings" class="space-y-6">
      <!-- General Settings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">General Settings</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control w-full">
              <label class="label" for="badge-size">
                <span class="label-text">Badge Size</span>
              </label>
              <input 
                id="badge-size" 
                v-model.number="settings.General.general_badge_size" 
                type="number" 
                min="10"
                class="input input-bordered w-full"
                placeholder="100"
              />
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="edge-padding">
                <span class="label-text">Edge Padding</span>
              </label>
              <input 
                id="edge-padding" 
                v-model.number="settings.General.general_edge_padding" 
                type="number" 
                min="0"
                class="input input-bordered w-full"
                placeholder="30"
              />
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="badge-position">
                <span class="label-text">Badge Position</span>
              </label>
              <select 
                id="badge-position" 
                v-model="settings.General.general_badge_position" 
                class="select select-bordered w-full"
              >
                <option value="top-left">Top Left</option>
                <option value="top-right">Top Right</option>
                <option value="bottom-left">Bottom Left</option>
                <option value="bottom-right">Bottom Right</option>
              </select>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="text-padding">
                <span class="label-text">Text Padding</span>
              </label>
              <input 
                id="text-padding" 
                v-model.number="settings.General.general_text_padding" 
                type="number" 
                min="0"
                class="input input-bordered w-full"
                placeholder="12"
              />
            </div>
            
            <div class="form-control col-span-full">
              <label class="label cursor-pointer justify-start">
                <input 
                  id="dynamic-sizing" 
                  v-model="settings.General.use_dynamic_sizing" 
                  type="checkbox" 
                  class="checkbox checkbox-primary"
                />
                <span class="label-text ml-2">Use Dynamic Sizing</span>
              </label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Text Settings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Text Settings</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control w-full">
              <label class="label" for="font">
                <span class="label-text">Font</span>
              </label>
              <select 
                id="font" 
                v-model="settings.Text.font" 
                class="select select-bordered w-full"
              >
                <option value="">Select a font...</option>
                <option v-for="font in availableFonts" :key="font" :value="font">
                  {{ font }}
                </option>
              </select>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="fallback-font">
                <span class="label-text">Fallback Font</span>
              </label>
              <select 
                id="fallback-font" 
                v-model="settings.Text.fallback_font" 
                class="select select-bordered w-full"
              >
                <option value="">Select a font...</option>
                <option v-for="font in availableFonts" :key="font" :value="font">
                  {{ font }}
                </option>
              </select>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="text-color">
                <span class="label-text">Text Color</span>
              </label>
              <div class="join w-full">
                <input 
                  id="text-color-picker" 
                  type="color" 
                  v-model="settings.Text['text-color']" 
                  class="input input-bordered join-item w-16"
                />
                <input 
                  id="text-color" 
                  v-model="settings.Text['text-color']" 
                  type="text" 
                  class="input input-bordered join-item flex-1"
                  placeholder="#FFFFFF"
                />
              </div>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="text-size">
                <span class="label-text">Text Size</span>
              </label>
              <input 
                id="text-size" 
                v-model.number="settings.Text['text-size']" 
                type="number" 
                min="10"
                class="input input-bordered w-full"
                placeholder="90"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Background Settings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Background Settings</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control w-full">
              <label class="label" for="background-color">
                <span class="label-text">Background Color</span>
              </label>
              <div class="join w-full">
                <input 
                  id="background-color-picker" 
                  type="color" 
                  v-model="settings.Background['background-color']" 
                  class="input input-bordered join-item w-16"
                />
                <input 
                  id="background-color" 
                  v-model="settings.Background['background-color']" 
                  type="text" 
                  class="input input-bordered join-item flex-1"
                  placeholder="#000000"
                />
              </div>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="background-opacity">
                <span class="label-text">Background Opacity (%)</span>
              </label>
              <input 
                id="background-opacity" 
                v-model.number="settings.Background.background_opacity" 
                type="number" 
                min="0"
                max="100"
                class="input input-bordered w-full"
                placeholder="40"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Border Settings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Border Settings</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control w-full">
              <label class="label" for="border-color">
                <span class="label-text">Border Color</span>
              </label>
              <div class="join w-full">
                <input 
                  id="border-color-picker" 
                  type="color" 
                  v-model="settings.Border['border-color']" 
                  class="input input-bordered join-item w-16"
                />
                <input 
                  id="border-color" 
                  v-model="settings.Border['border-color']" 
                  type="text" 
                  class="input input-bordered join-item flex-1"
                  placeholder="#000000"
                />
              </div>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="border-width">
                <span class="label-text">Border Width</span>
              </label>
              <input 
                id="border-width" 
                v-model.number="settings.Border.border_width" 
                type="number" 
                min="0"
                class="input input-bordered w-full"
                placeholder="1"
              />
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="border-radius">
                <span class="label-text">Border Radius</span>
              </label>
              <input 
                id="border-radius" 
                v-model.number="settings.Border.border_radius" 
                type="number" 
                min="0"
                class="input input-bordered w-full"
                placeholder="10"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Shadow Settings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Shadow Settings</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control col-span-full">
              <label class="label cursor-pointer justify-start">
                <input 
                  id="shadow-enable" 
                  v-model="settings.Shadow.shadow_enable" 
                  type="checkbox" 
                  class="checkbox checkbox-primary"
                />
                <span class="label-text ml-2">Enable Shadow</span>
              </label>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="shadow-blur">
                <span class="label-text">Shadow Blur</span>
              </label>
              <input 
                id="shadow-blur" 
                v-model.number="settings.Shadow.shadow_blur" 
                type="number" 
                min="0"
                class="input input-bordered w-full"
                placeholder="8"
              />
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="shadow-x">
                <span class="label-text">Shadow X Offset</span>
              </label>
              <input 
                id="shadow-x" 
                v-model.number="settings.Shadow.shadow_offset_x" 
                type="number" 
                class="input input-bordered w-full"
                placeholder="2"
              />
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="shadow-y">
                <span class="label-text">Shadow Y Offset</span>
              </label>
              <input 
                id="shadow-y" 
                v-model.number="settings.Shadow.shadow_offset_y" 
                type="number" 
                class="input input-bordered w-full"
                placeholder="2"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Image Badge Settings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Image Badge Settings</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control col-span-full">
              <label class="label cursor-pointer justify-start">
                <input 
                  id="enable-image-badges" 
                  v-model="settings.ImageBadges.enable_image_badges" 
                  type="checkbox" 
                  class="checkbox checkbox-primary"
                />
                <span class="label-text ml-2">Use Image Badges</span>
              </label>
            </div>
            
            <div class="form-control col-span-full">
              <label class="label cursor-pointer justify-start">
                <input 
                  id="fallback-to-text" 
                  v-model="settings.ImageBadges.fallback_to_text" 
                  type="checkbox" 
                  class="checkbox checkbox-primary"
                />
                <span class="label-text ml-2">Fallback to Text</span>
              </label>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="image-dir">
                <span class="label-text">Image Directory</span>
              </label>
              <input 
                id="image-dir" 
                v-model="settings.ImageBadges.codec_image_directory" 
                type="text" 
                class="input input-bordered w-full"
                placeholder="images/resolution"
              />
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="image-padding">
                <span class="label-text">Image Padding</span>
              </label>
              <input 
                id="image-padding" 
                v-model.number="settings.ImageBadges.image_padding" 
                type="number" 
                min="0"
                class="input input-bordered w-full"
                placeholder="20"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Image Mappings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Image Mappings</h3>
          <p class="text-sm opacity-70 mb-4">Map resolution names to image filenames</p>
          
          <div class="space-y-2 max-h-80 overflow-y-auto p-2">
            <div v-for="(imageName, resolutionName) in settings.ImageBadges.image_mapping" :key="resolutionName" class="grid grid-cols-12 gap-2 items-center">
              <input 
                v-model="tempMapping[resolutionName]" 
                type="text" 
                class="col-span-5 input input-bordered input-sm" 
                :placeholder="resolutionName"
                :disabled="!settings.ImageBadges.enable_image_badges"
              />
              <span class="col-span-1 text-center">→</span>
              <input 
                v-model="settings.ImageBadges.image_mapping[resolutionName]" 
                type="text" 
                class="col-span-5 input input-bordered input-sm" 
                :placeholder="imageName"
                :disabled="!settings.ImageBadges.enable_image_badges"
              />
              <button 
                @click="removeMapping(resolutionName)" 
                type="button" 
                class="col-span-1 btn btn-ghost btn-sm btn-circle text-error hover:bg-error hover:text-error-content"
                :disabled="!settings.ImageBadges.enable_image_badges"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 000 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
            
            <!-- Add new mapping -->
            <div class="grid grid-cols-12 gap-2 items-center mt-4 pt-4 border-t border-base-300">
              <input 
                v-model="newMapping.codec" 
                type="text" 
                class="col-span-5 input input-bordered input-sm" 
                placeholder="Resolution Name"
                :disabled="!settings.ImageBadges.enable_image_badges"
              />
              <span class="col-span-1 text-center">→</span>
              <input 
                v-model="newMapping.image" 
                type="text" 
                class="col-span-5 input input-bordered input-sm" 
                placeholder="Image Name"
                :disabled="!settings.ImageBadges.enable_image_badges"
              />
              <button 
                @click="addMapping" 
                type="button" 
                class="col-span-1 btn btn-ghost btn-sm btn-circle text-success hover:bg-success hover:text-success-content"
                :disabled="!settings.ImageBadges.enable_image_badges || !newMapping.codec || !newMapping.image"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Submit Button -->
      <div class="flex justify-end">
        <button
          @click="saveSettings"
          :disabled="saving"
          class="btn btn-primary"
        >
          <span v-if="saving" class="loading loading-spinner loading-sm"></span>
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
    const availableFonts = ref([]);
    
    // For handling image mappings
    const tempMapping = reactive({});
    
    // For adding new mappings
    const newMapping = reactive({
      codec: '',
      image: ''
    });

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

    // Load settings
    const loadSettings = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const res = await api.getConfig('badge_settings_resolution.yml');
        console.log('DEBUG: Resolution config loaded from file:', res.data.config);
        console.log('DEBUG: Current settings before merge:', JSON.parse(JSON.stringify(settings)));
        
        // Replace entire sections instead of deep merge to ensure reactivity
        if (res.data.config) {
          Object.keys(res.data.config).forEach(sectionKey => {
            if (settings[sectionKey] && typeof settings[sectionKey] === 'object') {
              // Replace the entire section
              Object.assign(settings[sectionKey], res.data.config[sectionKey]);
            } else {
              // Create new section if it doesn't exist
              settings[sectionKey] = res.data.config[sectionKey];
            }
          });
        }
        
        console.log('DEBUG: Settings after merge:', JSON.parse(JSON.stringify(settings)));
        console.log('DEBUG: Badge position after merge:', settings.General.general_badge_position);
        
        // Update image URLs to use absolute paths
        updateImageUrls();
        
        // Initialize tempMapping with existing keys
        if (settings.ImageBadges.image_mapping) {
          Object.keys(settings.ImageBadges.image_mapping)
                .forEach(k => tempMapping[k] = k);
        }
      } catch (err) {
        console.error('DEBUG: Error loading resolution settings:', err);
        error.value = err.response?.data?.error || err.message;
      } finally {
        loading.value = false;
      }
    };

    // Function to update image URLs to use absolute paths
    const updateImageUrls = () => {
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
    
    // Add new mapping
    const addMapping = () => {
      if (newMapping.codec && newMapping.image) {
        if (!settings.ImageBadges.image_mapping) {
          settings.ImageBadges.image_mapping = {};
        }
        settings.ImageBadges.image_mapping[newMapping.codec] = newMapping.image;
        tempMapping[newMapping.codec] = newMapping.codec;
        newMapping.codec = '';
        newMapping.image = '';
      }
    };
    
    // Remove mapping
    const removeMapping = (key) => {
      const mapping = { ...settings.ImageBadges.image_mapping };
      delete mapping[key];
      delete tempMapping[key];
      settings.ImageBadges.image_mapping = mapping;
    };
    
    // Save settings
    const saveSettings = async () => {
      saving.value = true;
      error.value = null;
      
      try {
        // If we have an original image directory path, restore it before saving
        if (settings._originalImageDir) {
          settings.ImageBadges.codec_image_directory = settings._originalImageDir;
          delete settings._originalImageDir;
        }
        
        await api.updateConfig('badge_settings_resolution.yml', settings);
        success.value = true;
        setTimeout(() => success.value = false, 3000);
        
        // Update image URLs again after saving
        updateImageUrls();
      } catch (err) {
        console.error('DEBUG: Error saving resolution settings:', err);
        error.value = err.response?.data?.error || err.message;
      } finally {
        saving.value = false;
      }
    };

    // Load available fonts
    const loadFonts = async () => {
      try {
        const response = await api.getFonts();
        availableFonts.value = response.data.fonts || [];
        console.log('Loaded fonts:', availableFonts.value);
      } catch (err) {
        console.error('Error loading fonts:', err);
        availableFonts.value = [];
      }
    };
    
    onMounted(async () => {
      await loadFonts();
      await loadSettings();
    });
    
    return {
      loading,
      error,
      saving,
      success,
      settings,
      availableFonts,
      saveSettings,
      tempMapping,
      newMapping,
      addMapping,
      removeMapping,
      updateImageUrls
    };
  }
};
</script>
