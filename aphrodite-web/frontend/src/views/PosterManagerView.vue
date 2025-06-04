<template>
  <div class="poster-manager">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Poster Manager</h1>
      <div class="flex items-center gap-4">
        <button 
          v-if="selectedLibrary"
          class="btn btn-outline btn-sm"
          :class="selectMode ? 'btn-active' : ''"
          @click="toggleSelectMode"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ selectMode ? 'Exit Select Mode' : 'Select Mode' }}
        </button>
        <div class="text-sm opacity-70">
          Manage and organize your Jellyfin poster collection
        </div>
      </div>
    </div>

    <!-- Library Selection -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title">Select Library</h2>
        <div class="flex flex-wrap gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Library</span>
            </label>
            <select 
              class="select select-bordered w-full max-w-xs" 
              v-model="selectedLibrary"
              @change="loadLibraryPosters"
              :disabled="isLoading"
            >
              <option value="">Choose a library...</option>
              <option v-for="library in libraries" :key="library.id" :value="library.id">
                {{ library.name }} ({{ library.itemCount }} items)
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div v-if="selectedLibrary" class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title">Filters</h2>
        <div class="flex flex-wrap gap-4">
          <!-- Search -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Search</span>
            </label>
            <input 
              type="text" 
              placeholder="Search titles..." 
              class="input input-bordered w-full max-w-xs" 
              v-model="searchQuery"
              @input="debouncedSearch"
            />
          </div>
          
          <!-- Media Type Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Media Type</span>
            </label>
            <select 
              class="select select-bordered w-full max-w-xs" 
              v-model="mediaTypeFilter"
              @change="applyFilters"
            >
              <option value="">All Types</option>
              <option value="Movie">Movies</option>
              <option value="Series">TV Series</option>
            </select>
          </div>
          
          <!-- Badge Status Filter -->
          <div class="form-control">
            <label class="label">
              <span class="label-text">Badge Status</span>
            </label>
            <select 
              class="select select-bordered w-full max-w-xs" 
              v-model="badgeStatusFilter"
              @change="applyFilters"
            >
              <option value="">All Posters</option>
              <option value="badged">With Badges</option>
              <option value="original">Original Only</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Bulk Action Bar -->
    <div v-if="selectMode && selectedPosters.size > 0" class="card bg-primary text-primary-content shadow-xl mb-6">
      <div class="card-body py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-4">
            <span class="font-semibold">{{ selectedPosters.size }} poster{{ selectedPosters.size !== 1 ? 's' : '' }} selected</span>
            <button class="btn btn-sm btn-ghost" @click="deselectAll">
              Deselect All
            </button>
          </div>
          <button 
            class="btn btn-accent"
            @click="showBulkConfirmation"
            :disabled="selectedPosters.size === 0"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Apply Badges to Selected
          </button>
        </div>
      </div>
    </div>

    <!-- Poster Grid -->
    <div v-else-if="filteredItems.length > 0" class="space-y-6">
      <!-- Results Summary -->
      <div class="stats shadow">
        <div class="stat">
          <div class="stat-title">Total Items</div>
          <div class="stat-value">{{ filteredItems.length }}</div>
        </div>
        <div class="stat">
          <div class="stat-title">With Badges</div>
          <div class="stat-value text-primary">{{ badgedCount }}</div>
        </div>
        <div class="stat">
          <div class="stat-title">Original Only</div>
          <div class="stat-value text-secondary">{{ originalCount }}</div>
        </div>
        <div v-if="selectMode" class="stat">
          <div class="stat-title">Selected</div>
          <div class="stat-value text-accent">{{ selectedPosters.size }}</div>
        </div>
      </div>

      <!-- Select All Option -->
      <div v-if="selectMode" class="flex justify-start mb-4">
        <label class="flex items-center gap-2 cursor-pointer">
          <input 
            type="checkbox" 
            class="checkbox checkbox-primary" 
            :checked="isAllSelected"
            :indeterminate="isSomeSelected && !isAllSelected"
            @change="toggleSelectAll"
          />
          <span class="text-sm font-medium">Select All ({{ filteredItems.length }} items)</span>
        </label>
      </div>

      <!-- Grid Display -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        <div 
          v-for="item in paginatedItems" 
          :key="item.id"
          class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow"
          :class="{
            'cursor-pointer': !selectMode,
            'ring-2 ring-primary ring-offset-2': selectMode && selectedPosters.has(item.id)
          }"
          @click="selectMode ? togglePosterSelection(item.id) : openItemDetails(item)"
        >
          <figure class="relative">
            <img 
              :src="item.poster_url || '/images/professor_relaxing.png'" 
              :alt="item.name"
              class="w-full h-80 object-cover"
              @error="handleImageError"
            />
            <!-- Selection Checkbox -->
            <div v-if="selectMode" class="absolute top-2 left-2">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary checkbox-lg" 
                :checked="selectedPosters.has(item.id)"
                @click.stop
                @change="togglePosterSelection(item.id)"
              />
            </div>
            <!-- Badge Status Indicator -->
            <div class="absolute top-2 right-2">
              <div 
                class="badge"
                :class="item.poster_status?.has_modified ? 'badge-primary' : 'badge-ghost'"
              >
                {{ item.poster_status?.has_modified ? 'Badged' : 'Original' }}
              </div>
            </div>
          </figure>
          <div class="card-body p-3">
            <h3 class="card-title text-sm">{{ item.name }}</h3>
            <p class="text-xs opacity-70">{{ item.year }}</p>
            <p class="text-xs opacity-60 line-clamp-2">{{ item.overview }}</p>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center">
        <div class="join">
          <button 
            class="join-item btn" 
            :disabled="currentPage === 1"
            @click="currentPage = 1"
          >
            First
          </button>
          <button 
            class="join-item btn" 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            «
          </button>
          <button class="join-item btn btn-active">{{ currentPage }}</button>
          <button 
            class="join-item btn" 
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            »
          </button>
          <button 
            class="join-item btn" 
            :disabled="currentPage === totalPages"
            @click="currentPage = totalPages"
          >
            Last
          </button>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-else-if="selectedLibrary && !isLoading" class="text-center py-8">
      <div class="text-6xl opacity-20 mb-4">🎬</div>
      <h3 class="text-xl font-bold mb-2">No items found</h3>
      <p class="opacity-70">Try adjusting your filters or search terms</p>
    </div>

    <!-- No Library Selected -->
    <div v-else-if="!selectedLibrary" class="text-center py-8">
      <div class="text-6xl opacity-20 mb-4">📚</div>
      <h3 class="text-xl font-bold mb-2">Select a library to get started</h3>
      <p class="opacity-70">Choose a Jellyfin library from the dropdown above</p>
    </div>

    <!-- Item Details Modal -->
    <ItemDetailsModal 
      v-if="selectedItem"
      :item="selectedItem"
      @close="selectedItem = null"
      @item-updated="handleItemUpdated"
      @gallery-refresh="handleGalleryRefresh"
    />

    <!-- Bulk Confirmation Dialog -->
    <BulkConfirmationDialog
      v-if="showBulkDialog"
      :selected-count="selectedPosters.size"
      :selected-items="Array.from(selectedPosters).map(id => allItems.find(item => item.id === id)).filter(Boolean)"
      @confirm="handleBulkConfirm"
      @cancel="showBulkDialog = false"
    />

    <!-- Bulk Progress Modal -->
    <BulkProgressModal
      v-if="showBulkProgress"
      :batch-id="bulkJobId"
      @close="handleBulkComplete"
    />
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';
import { debounce } from 'lodash';
import ItemDetailsModal from '@/components/poster-manager/ItemDetailsModal.vue';
import BulkConfirmationDialog from '@/components/poster-manager/BulkConfirmationDialog.vue';
import BulkProgressModal from '@/components/poster-manager/BulkProgressModal.vue';
import api from '@/api';

export default {
  name: 'PosterManagerView',
  components: {
    ItemDetailsModal,
    BulkConfirmationDialog,
    BulkProgressModal
  },
  setup() {
    const libraries = ref([]);
    const selectedLibrary = ref('');
    const allItems = ref([]);
    const isLoading = ref(false);
    const searchQuery = ref('');
    const mediaTypeFilter = ref('');
    const badgeStatusFilter = ref('');
    const selectedItem = ref(null);
    const currentPage = ref(1);
    const itemsPerPage = 24;
    
    // Bulk selection state
    const selectMode = ref(false);
    const selectedPosters = ref(new Set());
    const showBulkDialog = ref(false);
    const showBulkProgress = ref(false);
    const bulkJobId = ref(null);

    // Computed properties
    const filteredItems = computed(() => {
      let items = allItems.value;

      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        items = items.filter(item => 
          item.name.toLowerCase().includes(query)
        );
      }

      // Media type filter
      if (mediaTypeFilter.value) {
        items = items.filter(item => item.type === mediaTypeFilter.value);
      }

      // Badge status filter
      if (badgeStatusFilter.value) {
        items = items.filter(item => {
          const hasModified = item.poster_status?.has_modified;
          return badgeStatusFilter.value === 'badged' ? hasModified : !hasModified;
        });
      }

      // Sort alphabetically by name (case-insensitive)
      items.sort((a, b) => {
        const nameA = a.name.toLowerCase();
        const nameB = b.name.toLowerCase();
        if (nameA < nameB) return -1;
        if (nameA > nameB) return 1;
        return 0;
      });

      return items;
    });

    const paginatedItems = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      return filteredItems.value.slice(start, end);
    });

    const totalPages = computed(() => {
      return Math.ceil(filteredItems.value.length / itemsPerPage);
    });

    const badgedCount = computed(() => {
      return allItems.value.filter(item => item.poster_status?.has_modified).length;
    });

    const originalCount = computed(() => {
      return allItems.value.filter(item => !item.poster_status?.has_modified).length;
    });

    // Bulk selection computed properties
    const isAllSelected = computed(() => {
      return filteredItems.value.length > 0 && 
             filteredItems.value.every(item => selectedPosters.value.has(item.id));
    });

    const isSomeSelected = computed(() => {
      return selectedPosters.value.size > 0 && 
             filteredItems.value.some(item => selectedPosters.value.has(item.id));
    });

    // Methods
    const loadLibraries = async () => {
      try {
        const response = await api.get('/api/libraries/');
        const data = response.data;
        if (data.success) {
          libraries.value = data.libraries;
        }
      } catch (error) {
        console.error('Error loading libraries:', error);
      }
    };

    const loadLibraryPosters = async () => {
      if (!selectedLibrary.value) return;

      isLoading.value = true;
      try {
        const params = new URLSearchParams();
        if (searchQuery.value) params.append('search', searchQuery.value);
        if (mediaTypeFilter.value) params.append('type', mediaTypeFilter.value);
        if (badgeStatusFilter.value) params.append('badges', badgeStatusFilter.value);

        const response = await api.get(`/api/poster-manager/library/${selectedLibrary.value}?${params}`);
        const data = response.data;
        
        if (data.success) {
          allItems.value = data.items;
          currentPage.value = 1; // Reset to first page
        } else {
          console.error('Error loading posters:', data.message);
        }
      } catch (error) {
        console.error('Error loading library posters:', error);
      } finally {
        isLoading.value = false;
      }
    };

    const applyFilters = () => {
      currentPage.value = 1;
      loadLibraryPosters();
    };

    const debouncedSearch = debounce(() => {
      applyFilters();
    }, 300);

    const openItemDetails = (item) => {
      selectedItem.value = item;
    };

    const handleItemUpdated = () => {
      // Refresh the entire library to get updated poster status
      loadLibraryPosters();
    };

    const handleGalleryRefresh = () => {
      // Refresh the gallery with cache-busting for poster URLs
      loadLibraryPosters();
    };

    const handleImageError = (event) => {
      event.target.src = '/images/professor_relaxing.png';
    };

    // Bulk selection methods
    const toggleSelectMode = () => {
      selectMode.value = !selectMode.value;
      if (!selectMode.value) {
        selectedPosters.value.clear();
      }
    };

    const togglePosterSelection = (itemId) => {
      if (selectedPosters.value.has(itemId)) {
        selectedPosters.value.delete(itemId);
      } else {
        selectedPosters.value.add(itemId);
      }
    };

    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        // Deselect all
        selectedPosters.value.clear();
      } else {
        // Select all currently visible/filtered items
        filteredItems.value.forEach(item => {
          selectedPosters.value.add(item.id);
        });
      }
    };

    const deselectAll = () => {
      selectedPosters.value.clear();
    };

    const showBulkConfirmation = () => {
      showBulkDialog.value = true;
    };

    const handleBulkConfirm = async (selectedBadges) => {
      showBulkDialog.value = false;
      
      try {
        const itemIds = Array.from(selectedPosters.value);
        const response = await api.post('/api/poster-manager/bulk/reprocess', {
          item_ids: itemIds,
          badge_types: selectedBadges
        });
        
        const data = response.data;
        if (data.success) {
          bulkJobId.value = data.batch_id;
          showBulkProgress.value = true;
          selectedPosters.value.clear();
          selectMode.value = false;
        } else {
          console.error('Bulk processing failed:', data.message);
          // Could add error notification here
        }
      } catch (error) {
        console.error('Error starting bulk processing:', error);
        // Could add error notification here
      }
    };

    const handleBulkComplete = () => {
      showBulkProgress.value = false;
      bulkJobId.value = null;
      // Refresh the gallery to show updated posters
      loadLibraryPosters();
    };

    // Watch for filter changes to reset pagination and clear selection
    watch([mediaTypeFilter, badgeStatusFilter], () => {
      currentPage.value = 1;
      selectedPosters.value.clear();
    });
    
    // Watch for library changes to reset selection
    watch(selectedLibrary, () => {
      selectedPosters.value.clear();
      selectMode.value = false;
    });

    watch(filteredItems, () => {
      if (currentPage.value > totalPages.value && totalPages.value > 0) {
        currentPage.value = totalPages.value;
      }
    });

    // Load libraries on mount
    onMounted(() => {
      loadLibraries();
    });

    return {
      libraries,
      selectedLibrary,
      allItems,
      filteredItems,
      paginatedItems,
      isLoading,
      searchQuery,
      mediaTypeFilter,
      badgeStatusFilter,
      selectedItem,
      currentPage,
      totalPages,
      badgedCount,
      originalCount,
      // Bulk selection
      selectMode,
      selectedPosters,
      showBulkDialog,
      showBulkProgress,
      bulkJobId,
      isAllSelected,
      isSomeSelected,
      loadLibraryPosters,
      applyFilters,
      debouncedSearch,
      openItemDetails,
      handleItemUpdated,
      handleGalleryRefresh,
      handleImageError,
      // Bulk methods
      toggleSelectMode,
      togglePosterSelection,
      toggleSelectAll,
      deselectAll,
      showBulkConfirmation,
      handleBulkConfirm,
      handleBulkComplete
    };
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
