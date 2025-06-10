<template>
  <div class="review-settings">
    <h2 class="text-xl font-bold mb-4">Review Badge Settings</h2>
    
    <!-- Review Sources Status Notice -->
    <div class="alert alert-info mb-6">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div>
        <h3 class="font-bold">Review Source Availability</h3>
        <div class="text-sm mt-1">
          <p class="mb-2">Not all review sources are currently functional. Here are the sources that are currently working:</p>
          <div class="flex flex-wrap gap-2">
            <span class="badge badge-success badge-sm">aniDB</span>
            <span class="badge badge-success badge-sm">IMDb</span>
            <span class="badge badge-success badge-sm">Metacritic</span>
            <span class="badge badge-success badge-sm">MyAnimeList</span>
            <span class="badge badge-success badge-sm">Rotten Tomatoes Audience</span>
            <span class="badge badge-success badge-sm">Rotten Tomatoes Critics</span>
            <span class="badge badge-success badge-sm">TMDb</span>
          </div>
          <p class="mt-2 text-xs opacity-75">Other sources are included for future functionality and testing purposes. I will get to them, I promise!</p>
        </div>
      </div>
    </div>
    
    <form @submit.prevent="saveAllSettings" class="space-y-6">
      
      <!-- NEW: Review Sources Control -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title flex items-center">
            <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Review Sources Control
          </h3>
          <p class="text-base-content/70 mb-4">Configure which review sources to display and their priority order</p>
          
          <!-- Source Selection Settings -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="form-control">
              <label class="label">
                <span class="label-text">Max Badges to Display</span>
              </label>
              <input 
                v-model.number="reviewSourceSettings.max_badges_display" 
                type="number" 
                min="1" 
                max="10"
                class="input input-bordered w-full"
              />
            </div>
            
            <div class="form-control">
              <label class="label">
                <span class="label-text">Selection Mode</span>
              </label>
              <select 
                v-model="reviewSourceSettings.source_selection_mode" 
                class="select select-bordered w-full"
              >
                <option value="priority">Priority Order</option>
                <option value="enabled_only">Enabled Only</option>
                <option value="custom">Custom Logic</option>
              </select>
            </div>
            
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text">Convert all to percentage format</span>
                <input 
                  v-model="reviewSourceSettings.show_percentage_only" 
                  type="checkbox" 
                  class="checkbox checkbox-primary"
                />
              </label>
            </div>
          </div>
          
          <!-- Draggable Sources List -->
          <div class="bg-base-200 rounded-lg p-4">
            <h4 class="text-lg font-semibold mb-3 flex items-center">
              <svg class="w-4 h-4 mr-2 text-base-content/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
              Review Sources (Drag to reorder)
            </h4>
            
            <div class="space-y-2">
              <div 
                v-for="source in reviewSources" 
                :key="source.id"
                class="card bg-base-100 shadow-sm hover:shadow-md transition-shadow cursor-move"
                :class="{ 'opacity-50': !source.enabled }"
                draggable="true"
                @dragstart="handleDragStart($event, source)"
                @dragover.prevent="handleDragOver($event)"
                @drop="handleDrop($event, source)"
                @dragend="handleDragEnd"
              >
                <div class="card-body p-3">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                      <!-- Drag Handle -->
                      <svg class="w-5 h-5 text-base-content/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"></path>
                      </svg>
                      
                      <!-- Priority Order -->
                      <div class="badge badge-primary badge-sm">
                        {{ source.priority }}
                      </div>
                      
                      <!-- Source Info -->
                      <div class="flex-1">
                        <div class="flex items-center space-x-2">
                          <span class="font-medium">{{ source.source_name }}</span>
                          <div v-if="source.conditions" class="badge badge-warning badge-xs">
                            {{ getConditionLabel(source.conditions) }}
                          </div>
                        </div>
                        <div class="text-sm text-base-content/60">
                          Max variants: {{ source.max_variants }} • 
                          <span :class="source.enabled ? 'text-success' : 'text-error'">
                            {{ source.enabled ? 'Enabled' : 'Disabled' }}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Controls -->
                    <div class="flex items-center space-x-2">
                      <!-- Max Variants -->
                      <div class="form-control">
                        <label class="label label-text text-xs">Max:</label>
                        <select 
                          v-model.number="source.max_variants"
                          @change="updateSource(source)"
                          class="select select-bordered select-xs w-16"
                        >
                          <option value="1">1</option>
                          <option value="2">2</option>
                          <option value="3">3</option>
                          <option value="4">4</option>
                          <option value="5">5</option>
                        </select>
                      </div>
                      
                      <!-- Enable/Disable Toggle -->
                      <input 
                        type="checkbox" 
                        v-model="source.enabled"
                        @change="updateSource(source)"
                        class="toggle toggle-primary"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
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
                placeholder="20"
              />
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="badge-orientation">
                <span class="label-text">Badge Orientation</span>
              </label>
              <select 
                id="badge-orientation" 
                v-model="settings.General.badge_orientation" 
                class="select select-bordered w-full"
              >
                <option value="horizontal">Horizontal</option>
                <option value="vertical">Vertical</option>
              </select>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="badge-spacing">
                <span class="label-text">Badge Spacing</span>
              </label>
              <input 
                id="badge-spacing" 
                v-model.number="settings.General.badge_spacing" 
                type="number" 
                min="0"
                class="input input-bordered w-full"
                placeholder="15"
              />
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="max-badges">
                <span class="label-text">Max Badges to Display</span>
              </label>
              <input 
                id="max-badges" 
                v-model.number="settings.General.max_badges_to_display" 
                type="number" 
                min="1"
                class="input input-bordered w-full"
                placeholder="4"
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
                placeholder="60"
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
              <label class="label" for="bg-color">
                <span class="label-text">Background Color</span>
              </label>
              <div class="join w-full">
                <input 
                  id="bg-color-picker" 
                  type="color" 
                  v-model="settings.Background['background-color']" 
                  class="input input-bordered join-item w-16"
                />
                <input 
                  id="bg-color" 
                  v-model="settings.Background['background-color']" 
                  type="text" 
                  class="input input-bordered join-item flex-1"
                  placeholder="#2C2C2C"
                />
              </div>
            </div>
            
            <div class="form-control w-full">
              <label class="label" for="bg-opacity">
                <span class="label-text">Background Opacity (%)</span>
              </label>
              <input 
                id="bg-opacity" 
                v-model.number="settings.Background.background_opacity" 
                type="number" 
                min="0"
                max="100"
                class="input input-bordered w-full"
                placeholder="60"
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
                  placeholder="#2C2C2C"
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
                placeholder="5"
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
                placeholder="images/rating"
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
                placeholder="5"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Image Mappings -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h3 class="card-title">Image Mappings</h3>
          <p class="text-sm opacity-70 mb-4">Map rating names to image filenames</p>
          
          <div class="space-y-2 max-h-80 overflow-y-auto p-2">
            <div v-for="(imageName, ratingName) in settings.ImageBadges.image_mapping" :key="ratingName" class="grid grid-cols-12 gap-2 items-center">
              <input 
                v-model="tempMapping[ratingName]" 
                type="text" 
                class="col-span-5 input input-bordered input-sm" 
                :placeholder="ratingName"
                :disabled="!settings.ImageBadges.enable_image_badges"
              />
              <span class="col-span-1 text-center">→</span>
              <input 
                v-model="settings.ImageBadges.image_mapping[ratingName]" 
                type="text" 
                class="col-span-5 input input-bordered input-sm" 
                :placeholder="imageName"
                :disabled="!settings.ImageBadges.enable_image_badges"
              />
              <button 
                @click="removeMapping(ratingName)" 
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
                v-model="newMapping.rating" 
                type="text" 
                class="col-span-5 input input-bordered input-sm" 
                placeholder="Rating Name"
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
                :disabled="!settings.ImageBadges.enable_image_badges || !newMapping.rating || !newMapping.image"
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
          @click="saveAllSettings"
          :disabled="saving"
          class="btn btn-primary"
        >
          <span v-if="saving" class="loading loading-spinner loading-sm"></span>
          {{ saving ? 'Saving…' : 'Save Review Settings' }}
        </button>
        
        <!-- Success Toast -->
        <div class="toast toast-top toast-end" v-if="success">
          <div class="alert alert-success">
            <svg xmlns="http://www.w3.org/2000/svg" 
                class="stroke-current shrink-0 h-6 w-6" 
                fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" 
                    stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Review settings saved!</span>
          </div>
        </div>
        
        <!-- Error Toast -->
        <div class="toast toast-top toast-end" v-if="error">
          <div class="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" 
                class="stroke-current shrink-0 h-6 w-6" 
                fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" 
                    stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Review settings NOT saved!</span>
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
  name: 'ReviewSettings',
  
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const saving = ref(false);
    const success = ref(false);
    const availableFonts = ref([]);
    
    // Review sources data
    const reviewSources = ref([]);
    const reviewSourceSettings = reactive({
      max_badges_display: 4,
      source_selection_mode: 'priority',
      show_percentage_only: true,
      group_related_sources: true,
      anime_sources_for_anime_only: true
    });
    
    // Drag and drop state
    const draggedSource = ref(null);
    
    // For handling image mappings
    const tempMapping = reactive({});
    
    // For adding new mappings
    const newMapping = reactive({
      rating: '',
      image: ''
    });

    // Initialize all sections with default values
    const settings = reactive({
      General: {
        general_badge_size: 100,
        general_edge_padding: 30,
        general_badge_position: 'bottom-left',
        general_text_padding: 20,
        use_dynamic_sizing: true,
        badge_orientation: 'vertical',
        badge_spacing: 15,
        max_badges_to_display: 4
      },
      Text: {
        fallback_font: "DejaVuSans.ttf",
        font: "AvenirNextLTProBold.otf",
        "text-color": "#FFFFFF",
        "text-size": 60
      },
      Background: {
        "background-color": "#2C2C2C",
        background_opacity: 60
      },
      Border: {
        "border-color": "#2C2C2C",
        border_radius: 10,
        border_width: 1
      },
      Shadow: {
        shadow_blur: 5,
        shadow_enable: false,
        shadow_offset_x: 2,
        shadow_offset_y: 2
      },
      ImageBadges: {
        codec_image_directory: "images/rating",
        enable_image_badges: true,
        fallback_to_text: true,
        image_mapping: {},
        image_padding: 5
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
      if (newMapping.rating && newMapping.image) {
        if (!settings.ImageBadges.image_mapping) {
          settings.ImageBadges.image_mapping = {};
        }
        settings.ImageBadges.image_mapping[newMapping.rating] = newMapping.image;
        tempMapping[newMapping.rating] = newMapping.rating;
        newMapping.rating = '';
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

    // Load settings
    const loadSettings = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const res = await api.getConfig('badge_settings_review.yml');
        console.log('DEBUG: Review settings loaded:', res.data.config);
        
        // Properly merge nested objects instead of using Object.assign
        if (res.data.config) {
          deepMerge(settings, res.data.config);
        }
        
        // Update image URLs to use absolute paths
        updateImageUrls();
        
        // Initialize tempMapping with existing keys
        if (settings.ImageBadges.image_mapping) {
          Object.keys(settings.ImageBadges.image_mapping)
                .forEach(k => tempMapping[k] = k);
        }
      } catch (err) {
        console.error('DEBUG: Error loading review settings:', err);
        error.value = err.response?.data?.error || err.message;
      } finally {
        loading.value = false;
      }
    };

    // Load review sources from database
    const loadReviewSources = async () => {
      try {
        console.log('Attempting to load review sources...');
        const response = await api.getReviewSources();
        reviewSources.value = response.data;
        console.log('Loaded review sources:', reviewSources.value);
      } catch (err) {
        console.error('Error loading review sources:', err);
        console.error('Error details:', err.response?.data, err.response?.status);
        
        // Show fallback data to test the UI
        console.log('Using fallback review sources data');
        reviewSources.value = [
          { id: 1, source_name: 'IMDb', enabled: true, display_order: 1, priority: 1, max_variants: 3, conditions: null },
          { id: 2, source_name: 'Rotten Tomatoes Critics', enabled: true, display_order: 2, priority: 2, max_variants: 3, conditions: null },
          { id: 3, source_name: 'Metacritic', enabled: true, display_order: 3, priority: 3, max_variants: 2, conditions: null },
          { id: 4, source_name: 'TMDb', enabled: true, display_order: 4, priority: 4, max_variants: 1, conditions: null },
          { id: 5, source_name: 'AniDB', enabled: true, display_order: 5, priority: 5, max_variants: 1, conditions: '{"content_type": "anime"}' },
          { id: 6, source_name: 'Rotten Tomatoes Audience', enabled: false, display_order: 6, priority: 6, max_variants: 3, conditions: null },
          { id: 7, source_name: 'Letterboxd', enabled: false, display_order: 7, priority: 7, max_variants: 1, conditions: null },
          { id: 8, source_name: 'MyAnimeList', enabled: false, display_order: 8, priority: 8, max_variants: 1, conditions: '{"content_type": "anime"}' },
          { id: 9, source_name: 'Trakt', enabled: false, display_order: 9, priority: 9, max_variants: 1, conditions: null },
          { id: 10, source_name: 'MDBList', enabled: false, display_order: 10, priority: 10, max_variants: 1, conditions: null }
        ];
        console.log('Fallback data set, reviewSources.value:', reviewSources.value);
      }
    };
    
    // Load review source settings from database
    const loadReviewSourceSettings = async () => {
      try {
        const response = await api.getReviewSettings();
        Object.assign(reviewSourceSettings, response.data);
        console.log('Loaded review source settings:', reviewSourceSettings);
      } catch (err) {
        console.error('Error loading review source settings:', err);
      }
    };
    
    // Update a single review source
    const updateSource = async (source) => {
      try {
        await api.updateReviewSource(source.id, source);
        console.log('Updated review source:', source.source_name);
      } catch (err) {
        console.error('Error updating review source:', err);
      }
    };
    
    // Save all settings (both badge settings and review sources)
    const saveAllSettings = async () => {
      saving.value = true;
      error.value = null;
      
      try {
        // Save badge settings
        if (settings._originalImageDir) {
          settings.ImageBadges.codec_image_directory = settings._originalImageDir;
          delete settings._originalImageDir;
        }
        
        await api.updateConfig('badge_settings_review.yml', settings);
        
        // Save review source settings
        await api.updateReviewSettings(reviewSourceSettings);
        
        success.value = true;
        setTimeout(() => success.value = false, 3000);
        
        updateImageUrls();
      } catch (err) {
        console.error('DEBUG: Error saving settings:', err);
        error.value = err.response?.data?.error || err.message;
      } finally {
        saving.value = false;
      }
    };
    
    // Keep original save method for backward compatibility
    const saveSettings = saveAllSettings;
    
    // Helper function to get condition label
    const getConditionLabel = (conditions) => {
      if (!conditions) return '';
      try {
        const parsed = JSON.parse(conditions);
        return parsed.content_type || 'conditional';
      } catch (e) {
        return 'conditional';
      }
    };
    
    // Drag and Drop handlers
    const handleDragStart = (event, source) => {
      draggedSource.value = source;
      event.dataTransfer.effectAllowed = 'move';
      event.target.style.opacity = '0.5';
    };
    
    const handleDragOver = (event) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    };
    
    const handleDrop = async (event, targetSource) => {
      event.preventDefault();
      
      if (!draggedSource.value || draggedSource.value.id === targetSource.id) {
        return;
      }
      
      // Get the current positions
      const draggedIndex = reviewSources.value.findIndex(s => s.id === draggedSource.value.id);
      const targetIndex = reviewSources.value.findIndex(s => s.id === targetSource.id);
      
      if (draggedIndex === -1 || targetIndex === -1) return;
      
      // Remove the dragged item and insert it at the target position
      const newSources = [...reviewSources.value];
      const [draggedItem] = newSources.splice(draggedIndex, 1);
      newSources.splice(targetIndex, 0, draggedItem);
      
      // Update priorities based on new order
      newSources.forEach((source, index) => {
        source.priority = index + 1;
        source.display_order = index + 1;
      });
      
      // Update the reactive array
      reviewSources.value = newSources;
      
      // Save the new order to the backend
      try {
        await api.reorderReviewSources(newSources);
        console.log('Successfully reordered review sources');
      } catch (error) {
        console.error('Error saving new order:', error);
        // You might want to add a toast notification here
      }
    };
    
    const handleDragEnd = (event) => {
      event.target.style.opacity = '1';
      draggedSource.value = null;
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
      await loadReviewSources();
      await loadReviewSourceSettings();
    });
    
    return {
      loading,
      error,
      saving,
      success,
      settings,
      availableFonts,
      reviewSources,
      reviewSourceSettings,
      saveSettings,
      saveAllSettings,
      updateSource,
      getConditionLabel,
      handleDragStart,
      handleDragOver,
      handleDrop,
      handleDragEnd,
      tempMapping,
      newMapping,
      addMapping,
      removeMapping,
      updateImageUrls
    };
  }
};
</script>