// WebSocket client for real-time job updates
// Using native WebSocket instead of socket.io-client

interface JobStatusMessage {
  jobId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  totalItems?: number;
  processedCount?: number;
  failedCount?: number;
}

interface JobProgressMessage {
  jobId: string;
  itemId: string;
  status: 'completed' | 'failed';
  error?: string;
  processedCount: number;
  failedCount: number;
  progress: number;
  badgeType?: string;       // Badge type being processed (audio, resolution, review)
  badgeDetails?: {         // Additional badge-specific details
    badge_type: string;    // Matches badgeType, but included for consistency
    badge_position: string;
    success?: boolean;     // Whether this specific badge was applied successfully
  };
}

interface JobErrorMessage {
  jobId: string;
  error: string;
}

class WebSocketClient {
  private socket: WebSocket | null = null;
  private userId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;  // Increased for long-running jobs
  private reconnectDelay = 1000;
  private lastPingTime = 0;
  private pingInterval: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, Function[]> = new Map();
  private isReconnecting = false;

  connect(userId: string) {
    // Don't try to connect if already connected
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected, skipping connect');
      return;
    }
    
    // If there's a socket in CONNECTING state, don't create a new one
    if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket already connecting, skipping connect');
      return;
    }
    
    // If there's a socket in CLOSING state, wait for it to close before reconnecting
    if (this.socket && this.socket.readyState === WebSocket.CLOSING) {
      console.log('WebSocket is closing, will reconnect after close');
      return;
    }

    this.userId = userId;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let host = '';
    
    try {
      // Try to get the host from environment or window location
      host = process.env.NODE_ENV === 'development' 
        ? 'localhost:5000' 
        : window.location.host;
    } catch (error) {
      console.error('Error determining host:', error);
      host = 'localhost:5000'; // Fallback to localhost
    }
    
    const url = `${protocol}//${host}/socket.io/?EIO=4&transport=websocket`;
    console.log(`Connecting to WebSocket at ${url}`);

    try {
      // Create a new socket only if we don't have one or if it's CLOSED
      if (!this.socket || this.socket.readyState === WebSocket.CLOSED) {
        this.socket = new WebSocket(url);
        this.setupEventHandlers();
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.socket = null;
      this.scheduleReconnect();
    }
  }

  private setupEventHandlers() {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.isReconnecting = false;
      
      // Send handshake for socket.io compatibility
      this.socket?.send('2probe');
      
      // Join user-specific room
      if (this.userId) {
        this.emit('join-user-room', this.userId);
      }
      
      // Start ping interval for connection monitoring
      this.setupPingInterval();
      
      this.emit('connect', {});
    };

    this.socket.onmessage = (event) => {
      try {
        // Handle socket.io protocol messages
        if (event.data === '3probe') {
          this.socket?.send('5'); // Acknowledge probe
          return;
        }

        // Skip ping/pong frames
        if (event.data === '2' || event.data === '3') {
          if (event.data === '2') this.socket?.send('3'); // Respond to ping with pong
          return;
        }
        
        // Handle socket.io pong response
        if (event.data === '3') {
          this.lastPingTime = Date.now();
          return;
        }

        // Parse socket.io message format
        if (event.data.startsWith('42')) {
          const jsonData = event.data.substring(2);
          try {
            const [eventName, data] = JSON.parse(jsonData);
            
            // Enhanced logging for job status and progress
            if (eventName === 'job-status') {
              console.log(`Job ${data.jobId} status: ${data.status}`);
            } else if (eventName === 'job-progress' && data.badgeType) {
              console.log(`Processing ${data.badgeType} badge for item ${data.itemId}`);
            }
            
            this.handleMessage(eventName, data);
          } catch (parseError) {
            console.error('Error parsing WebSocket message:', parseError, jsonData);
          }
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.emit('disconnect', {});
      this.scheduleReconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private scheduleReconnect() {
    if (this.isReconnecting || this.reconnectAttempts >= this.maxReconnectAttempts) {
      return;
    }

    this.isReconnecting = true;
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (this.userId) {
        this.connect(this.userId);
      }
    }, delay);
  }

  private handleMessage(event: string, data: any) {
    // Handle pong responses for connection monitoring
    if (event === 'pong') {
      this.lastPingTime = Date.now();
      return;
    }
    
    // Enhanced logging for job-related events
    if (event.startsWith('job-')) {
      const statusInfo = data.status ? ` (status: ${data.status})` : '';
      console.log(`WebSocket received ${event}${statusInfo} for job ${data.jobId}`);
    }
    
    const handlers = this.messageHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    } else {
      console.log(`No handlers registered for event: ${event}`);
    }
  }

  disconnect() {
    // Clear ping interval if it exists
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  on(event: string, callback: Function) {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, []);
    }
    this.messageHandlers.get(event)?.push(callback);
    
    // If this is the first handler for 'connect' and we already have an open connection,
    // immediately trigger the callback
    if (event === 'connect' && 
        this.socket && 
        this.socket.readyState === WebSocket.OPEN && 
        this.messageHandlers.get(event)?.length === 1) {
      callback({});
    }
  }

  off(event: string, callback: Function) {
    const handlers = this.messageHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(callback);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }

  emit(event: string, data: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      // Format message for socket.io protocol
      const message = `42${JSON.stringify([event, data])}`;
      this.socket.send(message);
    } else {
      console.warn('WebSocket is not connected');
    }
  }
  
  // Setup ping interval to monitor connection health
  private setupPingInterval() {
    // Clear existing interval if any
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
    }
    
    // Initialize last ping time
    this.lastPingTime = Date.now();
    
    // Setup interval to ping server every 25 seconds
    this.pingInterval = setInterval(() => {
      // Only ping if socket is open
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        // If we haven't received a pong in more than 60 seconds, reconnect
        const timeSinceLastPing = Date.now() - this.lastPingTime;
        if (timeSinceLastPing > 60000) {
          console.warn('No ping response received in 60 seconds, reconnecting...');
          this.disconnect();
          if (this.userId) {
            this.connect(this.userId);
          }
          return;
        }
        
        // Send ping
        this.emit('ping', { timestamp: Date.now() });
      }
    }, 25000);
  }
}

// Create singleton instance
export const wsClient = new WebSocketClient();

// Hook for using WebSocket in React components
export function useWebSocket() {
  return wsClient;
}

// Export types
export type { JobStatusMessage, JobProgressMessage, JobErrorMessage };
