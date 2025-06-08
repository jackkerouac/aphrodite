/**
 * Extended Database API for Phase B Analytics
 * Additional API functions for comprehensive database analytics
 */

// Get the base URL for API calls
function getApiBaseUrl() {
  // In development, check for environment variable first
  if (process.env.NODE_ENV === 'development' && process.env.VUE_APP_API_URL) {
    return process.env.VUE_APP_API_URL
  }
  
  if (window.APHRODITE_BASE_URL) {
    return window.APHRODITE_BASE_URL
  }
  
  // In production or when served by Flask, use current origin
  if (window.location.port === '2125' || !window.location.port) {
    return window.location.origin
  }
  
  // For development server, use proxy (empty string means relative URLs)
  return ''
}

const API_BASE_URL = getApiBaseUrl()

/**
 * Get comprehensive processing report
 * @param {Object} options - Report options
 * @param {number} options.days - Number of days to analyze (default: 30)
 * @param {string} options.library_id - Optional library filter
 * @returns {Promise} API response with comprehensive report data
 */
export async function getComprehensiveReport(options = {}) {
  const params = new URLSearchParams()
  if (options.days) params.append('days', options.days)
  if (options.library_id) params.append('library_id', options.library_id)
  
  const url = `${API_BASE_URL}/api/database/comprehensive-report?${params}`
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 30000,
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return await response.json()
}

/**
 * Get paginated list of processed items with filtering
 * @param {Object} options - Query options
 * @param {number} options.page - Page number (default: 1)
 * @param {number} options.limit - Items per page (default: 20)
 * @param {string} options.search - Search term for title
 * @param {string} options.status - Filter by processing status
 * @param {string} options.library - Filter by library ID
 * @returns {Promise} API response with paginated items
 */
export async function getProcessedItems(options = {}) {
  const params = new URLSearchParams()
  if (options.page) params.append('page', options.page)
  if (options.limit) params.append('limit', options.limit)
  if (options.search) params.append('search', options.search)
  if (options.status) params.append('status', options.status)
  if (options.library) params.append('library', options.library)
  
  const url = `${API_BASE_URL}/api/database/processed-items?${params}`
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 15000,
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return await response.json()
}

/**
 * Get list of libraries with statistics
 * @returns {Promise} API response with libraries data
 */
export async function getLibraries() {
  const url = `${API_BASE_URL}/api/database/libraries`
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000,
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return await response.json()
}

/**
 * Export report data to specified format
 * @param {Object} options - Export options
 * @param {string} options.format - Export format ('csv' or 'json')
 * @param {number} options.days - Number of days to include
 * @param {string} options.library_id - Optional library filter
 * @returns {Promise} API response with export data
 */
export async function exportReportData(options = {}) {
  // For now, we'll use the comprehensive report and format client-side
  // In a full implementation, you might want a dedicated export endpoint
  const reportData = await getComprehensiveReport(options)
  
  if (options.format === 'csv') {
    return {
      success: true,
      data: convertReportToCSV(reportData.report),
      filename: `aphrodite_report_${new Date().toISOString().split('T')[0]}.csv`
    }
  } else if (options.format === 'json') {
    return {
      success: true,
      data: JSON.stringify(reportData.report, null, 2),
      filename: `aphrodite_report_${new Date().toISOString().split('T')[0]}.json`
    }
  }
  
  throw new Error('Unsupported export format')
}

/**
 * Convert report data to CSV format
 * @param {Object} report - Report data object
 * @returns {string} CSV formatted string
 */
function convertReportToCSV(report) {
  const lines = []
  
  // Summary section
  lines.push('SUMMARY')
  lines.push('Metric,Value')
  lines.push(`Total Items,${report.summary.total_items}`)
  lines.push(`Success Items,${report.summary.success_items}`)
  lines.push(`Failed Items,${report.summary.failed_items}`)
  lines.push(`Success Rate,${report.summary.success_rate}%`)
  lines.push(`Average Processing Time,${report.performance.avg_processing_time}s`)
  lines.push('')
  
  // Performance by type
  if (report.performance.by_type && report.performance.by_type.length > 0) {
    lines.push('PERFORMANCE BY TYPE')
    lines.push('Item Type,Count,Average Duration (s)')
    report.performance.by_type.forEach(item => {
      lines.push(`${item.item_type},${item.count},${item.avg_duration}`)
    })
    lines.push('')
  }
  
  // Errors
  if (report.errors && report.errors.length > 0) {
    lines.push('COMMON ERRORS')
    lines.push('Error Message,Count')
    report.errors.forEach(error => {
      lines.push(`"${error.error_message}",${error.count}`)
    })
    lines.push('')
  }
  
  // Trends
  if (report.trends && report.trends.length > 0) {
    lines.push('DAILY TRENDS')
    lines.push('Date,Total Items,Success Items,Success Rate')
    report.trends.forEach(trend => {
      lines.push(`${trend.date},${trend.total_items},${trend.success_items},${trend.success_rate}%`)
    })
  }
  
  return lines.join('\n')
}
