/**
 * useJobProgress Hook
 * 
 * WebSocket-based real-time job progress updates
 */

import { useEffect, useState, useCallback, useRef } from 'react'

interface ProgressData {
  total_posters: number
  completed_posters: number
  failed_posters: number
  progress_percentage: number
  estimated_completion?: string
  current_poster?: string
}

interface ProgressUpdate {
  type: 'progress_update'
  job_id: string
  data: ProgressData
}

interface UseJobProgressReturn {
  progress: ProgressData | null
  isConnected: boolean
  error: string | null
  reconnect: () => void
}

export const useJobProgress = (jobId: string): UseJobProgressReturn => {
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
    if (!jobId) {
      console.log('❌ No jobId provided to useJobProgress hook')
      return
    }

    console.log(`🔌 Attempting WebSocket connection for job: ${jobId}`)

    try {
      // Use current host for WebSocket connection (works in both dev and Docker)
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/api/v1/workflow/ws/${jobId}`
      console.log(`🔗 Connecting to: ${wsUrl}`)
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setError(null)
        console.log(`✅ WebSocket connected successfully for job ${jobId}`)
      }

      ws.onmessage = (event) => {
        console.log(`📨 WebSocket message received for job ${jobId}:`, event.data)
        try {
          const update: ProgressUpdate = JSON.parse(event.data)
          console.log(`📊 Parsed progress update:`, update)
          if (update.type === 'progress_update') {
            console.log(`🔄 Setting progress state:`, update.data)
            setProgress(update.data)
          }
        } catch (err) {
          console.error('❌ Failed to parse WebSocket message:', err)
        }
      }

      ws.onclose = (event) => {
        setIsConnected(false)
        console.log(`🔌 WebSocket disconnected for job ${jobId}`, event.code, event.reason)
        
        // Clear stale progress data when disconnected
        setProgress(null)
        
        // Only auto-reconnect if it wasn't a normal closure
        if (event.code !== 1000 && event.code !== 1001) {
          console.log(`🔄 Scheduling reconnection for job ${jobId}`)
          reconnectTimeoutRef.current = setTimeout(() => {
            if (wsRef.current?.readyState === WebSocket.CLOSED) {
              console.log(`🔄 Attempting to reconnect WebSocket for job ${jobId}`)
              connect()
            }
          }, 3000)
        }
      }

      ws.onerror = (err) => {
        setError('WebSocket connection error')
        setIsConnected(false)
        console.error(`❌ WebSocket error for job ${jobId}:`, err)
      }

    } catch (err) {
      setError('Failed to connect to job progress')
      console.error(`❌ WebSocket connection failed for job ${jobId}:`, err)
    }
  }, [jobId])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    
    setIsConnected(false)
  }, [])

  const reconnect = useCallback(() => {
    disconnect()
    connect()
  }, [connect, disconnect])

  useEffect(() => {
    connect()
    return disconnect
  }, [connect, disconnect])

  return {
    progress,
    isConnected,
    error,
    reconnect
  }
}
