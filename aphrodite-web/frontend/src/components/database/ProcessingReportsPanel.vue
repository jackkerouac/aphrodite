<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Processing Reports</h2>
      <p class="mb-4">Comprehensive analysis and performance metrics</p>
      
      <!-- Controls -->
      <div class="flex flex-wrap gap-3 mb-4">
        <select 
          v-model="selectedDays" 
          @change="loadReport"
          class="select select-bordered select-sm"
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="60">Last 60 days</option>
        </select>
        
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-sm btn-outline">
            Export
          </div>
          <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-32">
            <li><button @click="exportData('csv')" :disabled="loading">CSV</button></li>
            <li><button @click="exportData('json')" :disabled="loading">JSON</button></li>
          </ul>
        </div>
        
        <button 
          @click="loadReport" 
          :disabled="loading"
          class="btn btn-sm btn-primary"
        >
          <span v-if="loading" class="loading loading-spinner loading-sm"></span>
          <span v-else>Refresh</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading && !report" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg"></span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
        <button @click="loadReport" class="btn btn-sm">Retry</button>
      </div>

      <!-- Report Content -->
      <div v-else-if="report">
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="card bg-base-200">
            <div class="card-body p-4">
              <h3 class="text-lg font-medium">Total Items</h3>
              <div class="text-2xl font-bold text-primary">{{ report.summary.total_items }}</div>
              <p class="text-sm">{{ selectedDays }}-day period</p>
            </div>
          </div>
          
          <div class="card bg-base-200">
            <div class="card-body p-4">
              <h3 class="text-lg font-medium">Success Rate</h3>
              <div class="text-2xl font-bold" :class="getSuccessRateColor(report.summary.success_rate)">
                {{ report.summary.success_rate }}%
              </div>
              <p class="text-sm">{{ report.summary.success_items }} successful</p>
            </div>
          </div>
          
          <div class="card bg-base-200">
            <div class="card-body p-4">
              <h3 class="text-lg font-medium">Avg Duration</h3>
              <div class="text-2xl font-bold text-secondary">{{ report.performance.avg_processing_time }}s</div>
              <p class="text-sm">Per item processing</p>
            </div>
          </div>
          
          <div class="card bg-base-200">
            <div class="card-body p-4">
              <h3 class="text-lg font-medium">Failed Items</h3>
              <div class="text-2xl font-bold text-error">{{ report.summary.failed_items }}</div>
              <p class="text-sm">Require attention</p>
            </div>
          </div>
        </div>

        <!-- Performance by Type -->
        <div v-if="report.performance.by_type && report.performance.by_type.length > 0" class="mb-6">
          <h3 class="text-xl font-bold mb-4">Performance by Item Type</h3>
          <div class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Item Type</th>
                  <th>Count</th>
                  <th>Avg Duration</th>
                  <th>Performance</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in report.performance.by_type" :key="item.item_type">
                  <td>
                    <div class="badge badge-outline">{{ item.item_type }}</div>
                  </td>
                  <td>{{ item.count }}</td>
                  <td>{{ item.avg_duration }}s</td>
                  <td>
                    <div class="rating rating-sm">
                      <div 
                        v-for="i in 5" 
                        :key="i"
                        class="mask mask-star-2"
                        :class="i <= getPerformanceStars(item.avg_duration) ? 'bg-warning' : 'bg-base-300'"
                      ></div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Processing Trends -->
        <div v-if="report.trends && report.trends.length > 0">
          <h3 class="text-xl font-bold mb-4">Daily Processing Trends</h3>
          <div class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Total Items</th>
                  <th>Success Items</th>
                  <th>Success Rate</th>
                  <th>Trend</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trend in report.trends" :key="trend.date">
                  <td>{{ formatDate(trend.date) }}</td>
                  <td>{{ trend.total_items }}</td>
                  <td>{{ trend.success_items }}</td>
                  <td>
                    <div class="badge" :class="getSuccessRateBadgeClass(trend.success_rate)">
                      {{ trend.success_rate }}%
                    </div>
                  </td>
                  <td>
                    <div class="w-24 bg-base-200 rounded-full h-2">
                      <div 
                        class="h-2 rounded-full transition-all duration-300"
                        :class="getSuccessRateBarClass(trend.success_rate)"
                        :style="`width: ${trend.success_rate}%`"
                      ></div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- No Data State -->
      <div v-else class="text-center py-12">
        <div class="text-base-content/50 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 class="text-lg font-semibold mb-2">No Processing Data Available</h3>
          <p>Start processing some items to see comprehensive reports and analytics here.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getComprehensiveReport, exportReportData, getLibraries } from '../../api/database-extended.js'

export default {
  name: 'ProcessingReportsPanel',
  data() {
    return {
      report: null,
      libraries: [],
      loading: false,
      loadingLibraries: false,
      error: null,
      selectedDays: 30,
      selectedLibrary: ''
    }
  },
  mounted() {
    this.loadLibraries()
    this.loadReport()
  },
  methods: {
    async loadLibraries() {
      this.loadingLibraries = true
      try {
        const response = await getLibraries()
        if (response.success) {
          this.libraries = response.libraries
        }
      } catch (error) {
        console.error('Failed to load libraries:', error)
      } finally {
        this.loadingLibraries = false
      }
    },
    
    async loadReport() {
      this.loading = true
      this.error = null
      
      try {
        const options = {
          days: this.selectedDays
        }
        if (this.selectedLibrary) {
          options.library_id = this.selectedLibrary
        }
        
        const response = await getComprehensiveReport(options)
        
        if (response.success) {
          this.report = response.report
        } else {
          this.error = response.message || 'Failed to load report'
        }
      } catch (error) {
        this.error = `Error loading report: ${error.message}`
        console.error('Failed to load report:', error)
      } finally {
        this.loading = false
      }
    },
    
    async exportData(format) {
      try {
        const options = {
          format,
          days: this.selectedDays
        }
        if (this.selectedLibrary) {
          options.library_id = this.selectedLibrary
        }
        
        const response = await exportReportData(options)
        
        if (response.success) {
          // Create and trigger download
          const blob = new Blob([response.data], { 
            type: format === 'csv' ? 'text/csv' : 'application/json' 
          })
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = response.filename
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          window.URL.revokeObjectURL(url)
        }
      } catch (error) {
        console.error('Export failed:', error)
        // Could show a toast notification here
      }
    },
    
    getSuccessRateColor(rate) {
      if (rate >= 90) return 'text-success'
      if (rate >= 70) return 'text-warning'
      return 'text-error'
    },
    
    getSuccessRateBadgeClass(rate) {
      if (rate >= 90) return 'badge-success'
      if (rate >= 70) return 'badge-warning'
      return 'badge-error'
    },
    
    getSuccessRateBarClass(rate) {
      if (rate >= 90) return 'bg-success'
      if (rate >= 70) return 'bg-warning'
      return 'bg-error'
    },
    
    getAlertClass(type) {
      switch (type) {
        case 'warning': return 'alert-warning'
        case 'error': return 'alert-error'
        case 'success': return 'alert-success'
        default: return 'alert-info'
      }
    },
    
    getPerformanceStars(duration) {
      if (duration <= 5) return 5
      if (duration <= 10) return 4
      if (duration <= 20) return 3
      if (duration <= 30) return 2
      return 1
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
/* Minimal styles - let DaisyUI handle everything */
.card-actions {
  justify-content: flex-end;
}
</style>