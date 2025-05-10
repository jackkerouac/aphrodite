// @ts-ignore - socket.io-client import will work at runtime 
import io from 'socket.io-client';

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
  private socket: any = null;
  private userId: string | null = null;

  connect(userId: string) {
    if (this.socket && this.socket.connected) {
      return;
    }

    this.userId = userId;
    const url = process.env.NODE_ENV === 'development' 
      ? 'http://localhost:5000' 
      : window.location.origin;

    this.socket = io(url, {
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      // Join user-specific room
      this.socket.emit('join-user-room', userId);
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('WebSocket connection error:', error);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  on(event: string, callback: Function) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event: string, callback: Function) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  emit(event: string, data: any) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data);
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
