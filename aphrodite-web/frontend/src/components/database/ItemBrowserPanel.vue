<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Item Browser</h2>
      <p class="mb-4">Search and filter processed items</p>
      
      <div class="space-y-6">
        <!-- Search and Filter Controls -->
        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- Search -->
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Search</span>
                </label>
                <input 
                  v-model="searchTerm"
                  @input="debouncedSearch"
                  type="text" 
                  placeholder="Search by title..." 
                  class="input input-bordered input-sm"
                />
              </div>
              
              <!-- Status Filter -->
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Status</span>
                </label>
                <select 
                  v-model="statusFilter" 
                  @change="loadItems"
                  class="select select-bordered select-sm"
                >
                  <option value="">All Statuses</option>
                  <option value="success">Success</option>
                  <option value="failed">Failed</option>
                  <option value="partial_success">Partial Success</option>
                </select>
              </div>
              
              <!-- Items per page -->
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Per Page</span>
                </label>
                <select 
                  v-model="itemsPerPage" 
                  @change="loadItems"
                  class="select select-bordered select-sm"
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                </select>
              </div>

              <!-- Clear Filters -->
              <div class="form-control">
                <label class="label">
                  <span class="label-text">&nbsp;</span>
                </label>
                <button 
                  v-if="hasActiveFilters" 
                  @click="clearFilters"
                  class="btn btn-outline btn-sm"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading && items.length === 0" class="flex justify-center py-12">
          <span class="loading loading-spinner loading-lg"></span>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-error">
          <span>{{ error }}</span>
          <button @click="loadItems" class="btn btn-sm">Retry</button>
        </div>

        <!-- Items Table -->
        <div v-else-if="items.length > 0" class="card bg-base-100 shadow">
          <div class="card-body">
            <div class="flex justify-between items-center mb-4">
              <h3 class="card-title">
                {{ totalItems }} Items Found
                <span v-if="loading" class="loading loading-spinner loading-sm ml-2"></span>
              </h3>
            </div>
            
            <div class="overflow-x-auto">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Processed</th>
                    <th>Duration</th>
                    <th>Review Score</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in items" :key="item.id" class="hover">
                    <td>
                      <div class="flex flex-col">
                        <div class="font-semibold">{{ item.title }}</div>
                        <div class="text-sm opacity-60" v-if="item.year">({{ item.year }})</div>
                      </div>
                    </td>
                    <td>
                      <div class="badge badge-outline">{{ item.item_type }}</div>
                    </td>
                    <td>
                      <div class="badge" :class="getStatusBadgeClass(item.status)">
                        {{ formatStatus(item.status) }}
                      </div>
                    </td>
                    <td>
                      <div class="text-sm">{{ formatDate(item.last_processed_at) }}</div>
                      <div class="text-xs opacity-60" v-if="item.processing_count > 1">
                        {{ item.processing_count }} times
                      </div>
                    </td>
                    <td>
                      <span v-if="item.duration">{{ item.duration }}s</span>
                      <span v-else class="opacity-50">-</span>
                    </td>
                    <td>
                      <div v-if="item.review_score" class="flex items-center">
                        <span class="text-warning mr-1">★</span>
                        {{ item.review_score }}
                      </div>
                      <span v-else class="opacity-50">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div class="flex justify-between items-center mt-4">
              <div class="text-sm opacity-70">
                Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, totalItems) }} of {{ totalItems }} items
              </div>
              
              <div class="join">
                <button 
                  @click="goToPage(currentPage - 1)"
                  :disabled="currentPage <= 1 || loading"
                  class="join-item btn btn-sm"
                >
                  Previous
                </button>
                
                <template v-for="page in visiblePages" :key="page">
                  <button 
                    v-if="page !== '...'"
                    @click="goToPage(page)"
                    :disabled="loading"
                    class="join-item btn btn-sm"
                    :class="{ 'btn-active': page === currentPage }"
                  >
                    {{ page }}
                  </button>
                  <span v-else class="join-item btn btn-sm btn-disabled">...</span>
                </template>
                
                <button 
                  @click="goToPage(currentPage + 1)"
                  :disabled="currentPage >= totalPages || loading"
                  class="join-item btn btn-sm"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- No Items State -->
        <div v-else class="text-center py-12">
          <div class="text-base-content/50 mb-4">
            <div class="text-6xl mb-4">📋</div>
            <h3 class="text-lg font-semibold mb-2">No Items Found</h3>
            <p v-if="hasActiveFilters">Try adjusting your search criteria or filters.</p>
            <p v-else>No processed items available. Start processing some media to see them here.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getProcessedItems } from '../../api/database-extended.js'

export default {
  name: 'ItemBrowserPanel',
  data() {
    return {
      items: [],
      loading: false,
      error: null,
      searchTerm: '',
      statusFilter: '',
      itemsPerPage: 20,
      currentPage: 1,
      totalItems: 0,
      totalPages: 0,
      searchTimeout: null
    }
  },
  computed: {
    hasActiveFilters() {
      return this.searchTerm || this.statusFilter
    },
    
    visiblePages() {
      const pages = []
      const current = this.currentPage
      const total = this.totalPages
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        if (current <= 4) {
          for (let i = 1; i <= 5; i++) pages.push(i)
          pages.push('...')
          pages.push(total)
        } else if (current >= total - 3) {
          pages.push(1)
          pages.push('...')
          for (let i = total - 4; i <= total; i++) pages.push(i)
        } else {
          pages.push(1)
          pages.push('...')
          for (let i = current - 1; i <= current + 1; i++) pages.push(i)
          pages.push('...')
          pages.push(total)
        }
      }
      
      return pages
    }
  },
  mounted() {
    this.loadItems()
  },
  methods: {
    async loadItems() {
      this.loading = true
      this.error = null
      
      try {
        const options = {
          page: this.currentPage,
          limit: parseInt(this.itemsPerPage),
          search: this.searchTerm.trim(),
          status: this.statusFilter
        }
        
        const response = await getProcessedItems(options)
        
        if (response.success) {
          this.items = response.items
          this.totalItems = response.total
          this.totalPages = response.pages
        } else {
          this.error = response.message || 'Failed to load items'
        }
      } catch (error) {
        this.error = `Error loading items: ${error.message}`
        console.error('Failed to load items:', error)
      } finally {
        this.loading = false
      }
    },
    
    debouncedSearch() {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
        this.loadItems()
      }, 500)
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page
        this.loadItems()
      }
    },
    
    clearFilters() {
      this.searchTerm = ''
      this.statusFilter = ''
      this.currentPage = 1
      this.loadItems()
    },
    
    getStatusBadgeClass(status) {
      switch (status) {
        case 'success': return 'badge-success'
        case 'failed': return 'badge-error'
        case 'partial_success': return 'badge-warning'
        default: return 'badge-ghost'
      }
    },
    
    formatStatus(status) {
      switch (status) {
        case 'success': return 'Success'
        case 'failed': return 'Failed'
        case 'partial_success': return 'Partial'
        default: return status || 'Unknown'
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  }
}
</script>

<style scoped>
.table th {
  background-color: hsl(var(--b2));
}

.hover:hover {
  background-color: hsl(var(--b2));
}

.join-item.btn-active {
  background-color: hsl(var(--p));
  color: hsl(var(--pc));
}
</style>
