<template>
  <div class="awards-settings">
    <h2 class="text-xl font-bold mb-4">Awards Badge Settings</h2>
    
    <form @submit.prevent="saveSettings" class="space-y-6">
      <!-- General Settings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">General Settings</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control col-span-full">
              <label class="label cursor-pointer justify-start">
                <input
                  id="awards-enabled"
                  v-model="settings.General.enabled"
                  type="checkbox"
                  class="checkbox checkbox-primary"
                />
                <span class="label-text ml-2">Enable Awards Badges</span>
              </label>
              <p class="text-xs opacity-70 mt-1">Awards badges appear flush in the bottom-right corner when media has won specific awards</p>
            </div>

            <div class="form-control w-full">
              <label class="label" for="badge-size">
                <span class="label-text">Badge Size</span>
              </label>
              <input
                id="badge-size"
                v-model.number="settings.General.general_badge_size"
                type="number"
                min="50"
                max="200"
                class="input input-bordered w-full"
                placeholder="120"
                :disabled="!settings.General.enabled"
              />
              <p class="text-xs opacity-70 mt-1">Recommended: 120px for ribbon visibility</p>
            </div>

            <div class="form-control w-full">
              <label class="label">
                <span class="label-text">Badge Position</span>
              </label>
              <div class="text-sm opacity-80 bg-base-200 p-3 rounded">
                <strong>Bottom-Right Flush</strong>
                <p class="text-xs mt-1">Awards badges are always positioned flush to the bottom-right corner with no padding for optimal ribbon appearance</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Awards Configuration -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Awards Configuration</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Color Scheme Selection -->
            <div class="form-control">
              <label class="label mb-3">
                <span class="label-text">Color Scheme</span>
              </label>
              <div class="grid grid-cols-2 gap-3">
                <div v-for="color in colorSchemes" :key="color.value" class="relative">
                  <input
                    :id="`color-${color.value}`"
                    v-model="settings.Awards.color_scheme"
                    :value="color.value"
                    type="radio"
                    class="peer sr-only"
                    :disabled="!settings.General.enabled"
                  />
                  <label
                    :for="`color-${color.value}`"
                    class="flex items-center justify-center p-3 border rounded-lg cursor-pointer transition-all"
                  :class="[
                    'peer-checked:border-blue-500 peer-checked:bg-blue-50',
                    !settings.General.enabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-gray-400',
                    color.bgClass
                  ]"
                >
                  <div class="flex items-center space-x-2">
                    <div 
                      class="w-4 h-4 rounded border-2"
                      :class="color.previewClass"
                    ></div>
                    <span class="text-sm font-medium" :class="color.textClass">{{ color.label }}</span>
                  </div>
                </label>
              </div>
              </div>

              <!-- Color Preview -->
              <div v-if="settings.General.enabled && selectedColorPreview" class="mt-4 p-3 bg-base-200 rounded">
                <p class="text-sm font-medium mb-2">Preview:</p>
                <div class="flex items-center space-x-2">
                  <img
                    :src="selectedColorPreview"
                    :alt="`${settings.Awards.color_scheme} award preview`"
                    class="h-8 object-contain"
                    @error="handleImageError"
                  />
                  <span class="text-sm opacity-80">{{ settings.Awards.color_scheme }} scheme</span>
                </div>
              </div>
            </div>

            <!-- Award Sources Selection -->
            <div class="form-control">
              <label class="label mb-3">
                <span class="label-text">Award Sources</span>
              </label>
              <div class="max-h-64 overflow-y-auto border border-base-300 rounded p-3">
                <div class="space-y-2">
                  <div v-for="source in awardSources" :key="source.value" class="flex items-center">
                    <input
                      :id="`award-${source.value}`"
                      :value="source.value"
                      type="checkbox"
                      v-model="settings.Awards.award_sources"
                      class="checkbox checkbox-primary"
                      :disabled="!settings.General.enabled"
                    />
                    <label
                      :for="`award-${source.value}`"
                      class="ml-2 text-sm"
                      :class="!settings.General.enabled ? 'opacity-50' : ''"
                    >
                      {{ source.label }}
                    </label>
                    <span v-if="source.priority" class="ml-auto text-xs opacity-70">({{ source.priority }})</span>
                  </div>
                </div>
              </div>
              <p class="text-xs opacity-70 mt-2">
                Selected awards will be detected automatically. Priority order: Oscars → Cannes → Golden Globe → BAFTA → Emmy → Others
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Image Badge Settings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Image Settings</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control col-span-full">
              <label class="label" for="awards-image-directory">
                <span class="label-text">Awards Image Directory</span>
              </label>
              <input
                id="awards-image-directory"
                v-model="settings.ImageBadges.codec_image_directory"
                type="text"
                class="input input-bordered w-full"
                placeholder="images/awards"
                :disabled="!settings.General.enabled"
                readonly
              />
              <p class="text-xs opacity-70 mt-1">This directory contains color-coded subdirectories (black, gray, red, yellow)</p>
            </div>

            <div class="form-control">
              <label class="label cursor-pointer justify-start">
                <input
                  id="enable-image-badges"
                  v-model="settings.ImageBadges.enable_image_badges"
                  type="checkbox"
                  class="checkbox checkbox-primary"
                  :disabled="!settings.General.enabled"
                  readonly
                />
                <span class="label-text ml-2">Enable Image Badges</span>
              </label>
              <p class="text-xs opacity-70 mt-1">Awards are image-only (no text fallback)</p>
            </div>

            <div class="form-control">
              <label class="label" for="image-padding">
                <span class="label-text">Image Padding</span>
              </label>
              <input
                id="image-padding"
                v-model.number="settings.ImageBadges.image_padding"
                type="number"
                min="0"
                class="input input-bordered w-full"
                placeholder="0"
                :disabled="!settings.General.enabled"
                readonly
              />
              <p class="text-xs opacity-70 mt-1">Awards use 0 padding for flush positioning</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Award Statistics -->
      <div v-if="settings.General.enabled" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 class="text-lg font-medium mb-3 text-blue-900">Award Detection Info</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p class="font-medium text-blue-800 mb-2">Detection Sources:</p>
            <ul class="space-y-1 text-blue-700">
              <li>• Static mapping database (140+ titles)</li>
              <li>• TMDb API (real-time data)</li>
              <li>• OMDB API (fallback data)</li>
              <li>• 7-day API caching system</li>
            </ul>
          </div>
          <div>
            <p class="font-medium text-blue-800 mb-2">Coverage:</p>
            <ul class="space-y-1 text-blue-700">
              <li>• 80+ award-winning movies</li>
              <li>• 60+ award-winning TV shows</li>
              <li>• {{ settings.Awards.award_sources.length }} selected award types</li>
              <li>• Priority-based detection system</li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- Submit Button -->
      <div class="flex justify-end">
        <button
          @click="saveSettings"
          :disabled="saving || !settings.General.enabled"
          class="btn btn-primary"
        >
          <span v-if="saving" class="loading loading-spinner loading-sm mr-2"></span>
          {{ saving ? 'Saving…' : 'Save Awards Settings' }}
        </button>
        
        <!-- Success Toast -->
        <div class="toast toast-top toast-end w-64" v-if="success">
          <div class="alert alert-success shadow-lg w-64 flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" 
                class="stroke-current h-6 w-6 flex-shrink-0" 
                fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" 
                    stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>Awards settings saved!</span>
          </div>
        </div>
        
        <!-- Error Toast -->
        <div class="toast toast-top toast-end w-64" v-if="error">
          <div class="alert alert-error shadow-lg w-64 flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" 
                class="stroke-current h-6 w-6 flex-shrink-0" 
                fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" 
                    stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>Awards settings NOT saved!</span>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue';
import api from '@/api/config.js';

export default {
  name: 'AwardsSettings',
  
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const saving = ref(false);
    const success = ref(false);

    // Color schemes available
    const colorSchemes = [
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

    // Award sources with priority indicators
    const awardSources = [
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

    // Settings data structure
    const settings = reactive({
      General: {
        general_badge_position: 'bottom-right-flush',
        general_badge_size: 120,
        general_edge_padding: 0,
        general_text_padding: 0,
        use_dynamic_sizing: false,
        enabled: true
      },
      Awards: {
        color_scheme: 'yellow',
        award_sources: [
          'oscars', 'emmys', 'golden', 'bafta', 'cannes', 'crunchyroll'
        ]
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
        codec_image_directory: "images/awards",
        fallback_to_text: false,
        image_padding: 0,
        image_mapping: {
          oscars: "oscars.png",
          emmys: "emmys.png",
          golden: "golden.png",
          bafta: "bafta.png",
          cannes: "cannes.png",
          crunchyroll: "crunchyroll.png",
          berlinale: "berlinale.png",
          cesar: "cesar.png",
          choice: "choice.png",
          imdb: "imdb.png",
          letterboxd: "letterboxd.png",
          metacritic: "metacritic.png",
          netflix: "netflix.png",
          razzie: "razzie.png",
          rotten: "rotten.png",
          rottenverified: "rottenverified.png",
          spirit: "spirit.png",
          sundance: "sundance.png",
          venice: "venice.png"
        }
      }
    });

    // Computed property for color preview
    const selectedColorPreview = computed(() => {
      if (!settings.General.enabled || !settings.Awards.color_scheme) return null;
      return `/images/awards/${settings.Awards.color_scheme}/oscars.png`;
    });

    // Helper function for deep merge
    const deepMerge = (target, source) => {
      Object.keys(source).forEach(key => {
        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
          if (!target[key] || typeof target[key] !== 'object') {
            target[key] = {};
          }
          deepMerge(target[key], source[key]);
        } else {
          target[key] = source[key];
        }
      });
    };

    // Load settings from disk
    const loadSettings = async () => {
      loading.value = true;
      error.value = null;
      try {
        const res = await api.getConfig('badge_settings_awards.yml');
        // Use deep merge instead of Object.assign to properly merge nested objects
        deepMerge(settings, res.data.config);
      } catch (err) {
        console.warn('Could not load awards settings, using defaults:', err);
        error.value = err.response?.data?.error || err.message;
      } finally {
        loading.value = false;
      }
    };

    onMounted(loadSettings);

    // Save settings to disk
    const saveSettings = async () => {
      saving.value = true;
      error.value = null;
      try {
        await api.updateConfig('badge_settings_awards.yml', settings);
        success.value = true;
        setTimeout(() => success.value = false, 3000);
      } catch (err) {
        error.value = err.response?.data?.error || err.message;
      } finally {
        saving.value = false;
      }
    };

    // Handle image loading errors
    const handleImageError = () => {
      console.warn('Could not load preview image for', settings.Awards.color_scheme);
    };

    return {
      loading,
      error,
      saving,
      success,
      settings,
      colorSchemes,
      awardSources,
      selectedColorPreview,
      saveSettings,
      handleImageError
    };
  }
};
</script>

<style scoped>
.toast {
  position: fixed;
  z-index: 1000;
}
</style>
