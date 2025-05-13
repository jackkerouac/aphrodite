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
}

interface JobErrorMessage {
  jobId: string;
  error: string;
}

class WebSocketClient {
  private socket: WebSocket | null = null;
  private userId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
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

        // Parse socket.io message format
        if (event.data.startsWith('42')) {
          const jsonData = event.data.substring(2);
          const [eventName, data] = JSON.parse(jsonData);
          this.handleMessage(eventName, data);
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
    const handlers = this.messageHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  disconnect() {
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
}

// Create singleton instance
export const wsClient = new WebSocketClient();

// Hook for using WebSocket in React components
export function useWebSocket() {
  return wsClient;
}

// Export types
export type { JobStatusMessage, JobProgressMessage, JobErrorMessage };
