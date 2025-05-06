import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@/components/ui/pagination'
import apiClient from '@/lib/api-client'
import { Loader2, RefreshCw, Trash2, AlertCircle, InfoIcon, AlertTriangle } from 'lucide-react'
import { toast } from 'sonner'

// Log level badge component with appropriate colors
const LogLevelBadge = ({ level }: { level: string }) => {
  const getColorClasses = () => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
      case 'WARN':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
      case 'INFO':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
      case 'DEBUG':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'
    }
  }

  const getLevelIcon = () => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return <AlertCircle className="w-3 h-3 mr-1" />
      case 'WARN':
        return <AlertTriangle className="w-3 h-3 mr-1" />
      case 'INFO':
        return <InfoIcon className="w-3 h-3 mr-1" />
      default:
        return null
    }
  }

  return (
    <div className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${getColorClasses()}`}>
      {getLevelIcon()}
      {level.toUpperCase()}
    </div>
  )
}

export default function Logs() {
  // Basic state
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [totalLogs, setTotalLogs] = useState(0)
  
  // Filter state
  const [levelFilter, setLevelFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  
  // Pagination state
  const [page, setPage] = useState(1)
  const [limit] = useState(50)
  
  // Action state
  const [clearingLogs, setClearingLogs] = useState(false)
  const [manualRefresh, setManualRefresh] = useState(0)

  // Calculate total pages
  const totalPages = Math.ceil(totalLogs / limit)

  // Fetch logs once when component mounts or when filters/pagination/manual refresh changes
  useEffect(() => {
    let isMounted = true
    
    const fetchLogs = async () => {
      if (!isMounted) return
      
      try {
        setLoading(true)
        
        const response = await apiClient.logs.getLogs({
          level: levelFilter !== 'all' ? levelFilter : undefined,
          page,
          limit,
        })
        
        if (!isMounted) return
        
        if (response && Array.isArray(response.logs)) {
          setLogs(response.logs)
          setTotalLogs(response.total || 0)
        } else {
          console.error('Invalid logs response format:', response)
          setLogs([])
          setTotalLogs(0)
        }
      } catch (error) {
        if (!isMounted) return
        
        console.error('Error fetching logs:', error)
        toast.error('Error fetching logs', {
          description: error instanceof Error ? error.message : 'Unknown error',
        })
        
        setLogs([])
        setTotalLogs(0)
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    fetchLogs()
    
    // Cleanup to prevent state updates after unmount
    return () => {
      isMounted = false
    }
  }, [page, limit, levelFilter, manualRefresh])

  // Manual refresh handler
  const handleRefresh = () => {
    toast.success('Refreshing logs...')
    setManualRefresh(prev => prev + 1)
  }

  // Clear logs handler
  const handleClearLogs = async () => {
    if (!window.confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
      return
    }

    try {
      setClearingLogs(true)
      
      await apiClient.logs.clearLogs()
      
      toast.success('Logs cleared', {
        description: 'All logs have been cleared successfully.',
      })
      
      // Reset to first page and trigger a refresh
      setPage(1)
      setManualRefresh(prev => prev + 1)
    } catch (error) {
      console.error('Error clearing logs:', error)
      toast.error('Error clearing logs', {
        description: error instanceof Error ? error.message : 'Unknown error',
      })
    } finally {
      setClearingLogs(false)
    }
  }

  // Filter logs by search query (client-side filtering)
  const filteredLogs = logs.filter((log) => {
    if (!searchQuery) return true
    return log.message?.toLowerCase().includes(searchQuery.toLowerCase())
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Logs</h1>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={loading || clearingLogs}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Refresh
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={handleClearLogs}
            disabled={loading || clearingLogs}
          >
            {clearingLogs ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4 mr-2" />
            )}
            Clear Logs
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="w-full md:w-1/3">
          <Select
            value={levelFilter}
            onValueChange={(value) => {
              setLevelFilter(value)
              setPage(1) // Reset to first page on filter change
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              <SelectItem value="info">Info</SelectItem>
              <SelectItem value="warn">Warning</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="w-full md:w-2/3">
          <Input
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Logs Display */}
      <Card className="rounded-md border overflow-hidden">
        {loading ? (
          <div className="p-8 flex justify-center items-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : filteredLogs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/40">
                  <th className="px-4 py-3 text-left font-medium text-sm">Timestamp</th>
                  <th className="px-4 py-3 text-left font-medium text-sm">Level</th>
                  <th className="px-4 py-3 text-left font-medium text-sm">Message</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredLogs.map((log, index) => (
                  <tr key={index} className="hover:bg-muted/20">
                    <td className="px-4 py-3 text-sm whitespace-nowrap">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <LogLevelBadge level={log.level || 'UNKNOWN'} />
                    </td>
                    <td className="px-4 py-3 text-sm font-mono overflow-auto break-all">
                      {log.message || 'No message'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-muted-foreground">
            No logs found. {searchQuery && 'Try adjusting your search query.'}
          </div>
        )}
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination className="justify-center">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                disabled={page === 1 || loading}
              />
            </PaginationItem>
            
            {/* Simple pagination that shows first, current, and last page with ellipsis */}
            {Array.from({ length: Math.min(3, totalPages) }).map((_, i) => {
              let pageNum: number;
              
              if (totalPages <= 3) {
                // If 3 or fewer pages, show all
                pageNum = i + 1;
              } else if (page === 1 || page === totalPages) {
                // If on first or last page, show first, second, and last
                pageNum = i === 0 ? 1 : i === 1 ? 2 : totalPages;
              } else {
                // Show first, current, and last
                pageNum = i === 0 ? 1 : i === 1 ? page : totalPages;
              }
              
              return (
                <PaginationItem key={pageNum}>
                  {(i === 1 && pageNum > 2 && pageNum < totalPages - 1) && (
                    <PaginationLink
                      onClick={() => setPage(pageNum)}
                      isActive={true}
                    >
                      {pageNum}
                    </PaginationLink>
                  )}
                  
                  {((i === 0 && pageNum === 1) || 
                    (i === 2 && pageNum === totalPages) || 
                    (i === 1 && pageNum <= 2) || 
                    (i === 1 && pageNum >= totalPages - 1)) && (
                    <PaginationLink
                      onClick={() => setPage(pageNum)}
                      isActive={pageNum === page}
                    >
                      {pageNum}
                    </PaginationLink>
                  )}
                  
                  {/* Show ellipsis when appropriate */}
                  {(i === 0 && page > 2) && (
                    <span className="px-2">...</span>
                  )}
                  {(i === 1 && page < totalPages - 1 && page > 2) && (
                    <span className="px-2">...</span>
                  )}
                </PaginationItem>
              );
            })}
            
            <PaginationItem>
              <PaginationNext
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                disabled={page === totalPages || loading}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}
    </div>
  )
}
