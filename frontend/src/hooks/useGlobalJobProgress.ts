/**
 * Global Job Progress Manager
 * 
 * Manages WebSocket connections for all active jobs globally,
 * independent of which tab/component is currently visible.
 */

import { useState, useEffect, useCallback, useRef } from 'react'

interface ProgressData {
  total_posters: number
  completed_posters: number
  failed_posters: number
  progress_percentage: number
  estimated_completion?: string
  current_poster?: string
}

interface Job {
  job_id: string
  name: string
  status: string
  total_posters: number
  completed_posters: number
  failed_posters: number
  created_at: string
}

interface JobProgressState {
  [jobId: string]: {
    progress: ProgressData | null
    lastUpdate: number
  }
}

class GlobalJobProgressManager {
  private connections: Map<string, WebSocket> = new Map()
  private progressStates: JobProgressState = {}
  private listeners: Set<(jobId: string, progress: ProgressData | null) => void> = new Set()
  private jobListeners: Set<() => void> = new Set()
  
  constructor() {
    // Only initialize on client side
    if (typeof window === 'undefined') {
      return
    }
    
    // Poll for active jobs every 30 seconds and ensure WebSocket connections
    setInterval(() => {
      this.ensureActiveJobConnections()
    }, 30000)
    
    // Initial connection setup
    setTimeout(() => {
      this.ensureActiveJobConnections()
    }, 1000)
  }
  
  private async ensureActiveJobConnections() {
    // Only run on client side
    if (typeof window === 'undefined') {
      return
    }
    
    try {
      console.log('🔄 GlobalJobProgressManager: Checking for active jobs...')
      
      // Use relative URL - will work correctly in browser
      const response = await fetch('/api/v1/workflow/jobs/')
      if (!response.ok) return
      
      const jobs: Job[] = await response.json()
      const activeJobs = jobs.filter(job => 
        ['processing', 'paused', 'queued'].includes(job.status)
      )
      
      console.log(`📋 Found ${activeJobs.length} active jobs`)
      
      // Connect to active jobs that don't have connections
      for (const job of activeJobs) {
        if (!this.connections.has(job.job_id)) {
          console.log(`🔌 Connecting to job ${job.job_id}...`)
          this.connectToJob(job.job_id)
        }
      }
      
      // Disconnect from jobs that are no longer active
      const activeJobIds = new Set(activeJobs.map(j => j.job_id))
      for (const [jobId, ws] of this.connections) {
        if (!activeJobIds.has(jobId)) {
          console.log(`🔌 Disconnecting from completed job ${jobId}`)
          ws.close()
          this.connections.delete(jobId)
        }
      }
      
      // Notify job list listeners
      this.jobListeners.forEach(listener => listener())
      
    } catch (error) {
      console.error('❌ GlobalJobProgressManager: Error checking active jobs:', error)
    }
  }
  
  private connectToJob(jobId: string) {
    // Only run on client side
    if (typeof window === 'undefined') {
      return
    }
    
    if (this.connections.has(jobId)) {
      return // Already connected
    }
    
    const wsUrl = `ws://localhost:8000/api/v1/workflow/ws/${jobId}`
    console.log(`🔗 GlobalJobProgressManager: Connecting to ${wsUrl}`)
    
    try {
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log(`✅ GlobalJobProgressManager: Connected to job ${jobId}`)
        this.connections.set(jobId, ws)
      }
      
      ws.onmessage = (event) => {
        try {
          const update = JSON.parse(event.data)
          if (update.type === 'progress_update' && update.data) {
            console.log(`📊 GlobalJobProgressManager: Progress update for ${jobId}:`, update.data)
            
            // Store progress state
            this.progressStates[jobId] = {
              progress: update.data,
              lastUpdate: Date.now()
            }
            
            // Notify all listeners
            this.listeners.forEach(listener => {
              listener(jobId, update.data)
            })
          }
        } catch (error) {
          console.error('❌ GlobalJobProgressManager: Failed to parse message:', error)
        }
      }
      
      ws.onclose = (event) => {
        console.log(`🔌 GlobalJobProgressManager: Disconnected from job ${jobId}`, event.code)
        this.connections.delete(jobId)
        
        // If it wasn't a normal closure, try to reconnect
        if (event.code !== 1000 && event.code !== 1001) {
          setTimeout(() => {
            this.connectToJob(jobId)
          }, 5000)
        }
      }
      
      ws.onerror = (error) => {
        console.error(`❌ GlobalJobProgressManager: WebSocket error for job ${jobId}:`, error)
      }
      
    } catch (error) {
      console.error(`❌ GlobalJobProgressManager: Failed to create WebSocket for job ${jobId}:`, error)
    }
  }
  
  public getProgress(jobId: string): ProgressData | null {
    return this.progressStates[jobId]?.progress || null
  }
  
  public addProgressListener(listener: (jobId: string, progress: ProgressData | null) => void) {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }
  
  public addJobListener(listener: () => void) {
    this.jobListeners.add(listener)
    return () => this.jobListeners.delete(listener)
  }
  
  public forceConnectToJob(jobId: string) {
    console.log(`🎯 GlobalJobProgressManager: Force connecting to job ${jobId}`)
    this.connectToJob(jobId)
  }
  
  public getActiveJobIds(): string[] {
    return Array.from(this.connections.keys())
  }
}

// Global singleton instance - only create on client side
let globalJobProgressManager: GlobalJobProgressManager | null = null

if (typeof window !== 'undefined') {
  globalJobProgressManager = new GlobalJobProgressManager()
}

/**
 * Hook to use global job progress manager
 */
export const useGlobalJobProgress = (jobId?: string) => {
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  
  useEffect(() => {
    if (!jobId || !globalJobProgressManager) return
    
    // Get initial progress if available
    const initialProgress = globalJobProgressManager.getProgress(jobId)
    if (initialProgress) {
      setProgress(initialProgress)
    }
    
    // Check if connected
    setIsConnected(globalJobProgressManager.getActiveJobIds().includes(jobId))
    
    // Listen for progress updates
    const unsubscribeProgress = globalJobProgressManager.addProgressListener((updateJobId, updateProgress) => {
      if (updateJobId === jobId) {
        setProgress(updateProgress)
      }
    })
    
    // Listen for job list changes
    const unsubscribeJobs = globalJobProgressManager.addJobListener(() => {
      setIsConnected(globalJobProgressManager!.getActiveJobIds().includes(jobId))
    })
    
    return () => {
      unsubscribeProgress()
      unsubscribeJobs()
    }
  }, [jobId])
  
  return {
    progress,
    isConnected,
    error: null, // Global manager handles errors internally
    reconnect: () => jobId && globalJobProgressManager?.forceConnectToJob(jobId)
  }
}

/**
 * Hook to trigger WebSocket connection when a job is created
 */
export const useJobCreationHandler = () => {
  const handleJobCreated = useCallback((jobId: string) => {
    if (!globalJobProgressManager) {
      console.warn('⚠️ GlobalJobProgressManager not available on server side')
      return
    }
    
    console.log(`🎯 Job created: ${jobId} - establishing WebSocket connection`)
    globalJobProgressManager.forceConnectToJob(jobId)
  }, [])
  
  return handleJobCreated
}

export default globalJobProgressManager
