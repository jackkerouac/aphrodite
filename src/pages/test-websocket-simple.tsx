import React, { useState, useEffect } from 'react';
import { Button, Card, CardContent } from '@/components/ui';
import { io } from 'socket.io-client';

export default function TestWebSocketSimple() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [socket, setSocket] = useState<any>(null);

  const connect = () => {
    const newSocket = io('http://localhost:5000', {
      transports: ['websocket', 'polling'],
      autoConnect: true
    });

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
      addMessage('Connected to server');
      
      // Join user room
      newSocket.emit('join-user-room', '1');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
      addMessage('Disconnected from server');
    });

    newSocket.on('error', (error: any) => {
      console.error('Socket error:', error);
      addMessage(`Error: ${error}`);
    });

    // Listen for job events
    newSocket.on('job-status', (data: any) => {
      addMessage(`Job status: ${JSON.stringify(data)}`);
    });

    newSocket.on('job-progress', (data: any) => {
      addMessage(`Job progress: ${JSON.stringify(data)}`);
    });

    setSocket(newSocket);
  };

  const disconnect = () => {
    if (socket) {
      socket.disconnect();
      setSocket(null);
    }
  };

  const addMessage = (msg: string) => {
    setMessages(prev => [...prev, `${new Date().toISOString()}: ${msg}`]);
  };

  const testEmit = () => {
    if (socket) {
      socket.emit('test-message', { hello: 'world' });
      addMessage('Sent test message');
    }
  };

  useEffect(() => {
    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [socket]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">WebSocket Test - Simple</h1>
      
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Button onClick={connect} disabled={connected}>
                Connect
              </Button>
              <Button onClick={disconnect} disabled={!connected}>
                Disconnect
              </Button>
              <Button onClick={testEmit} disabled={!connected}>
                Test Emit
              </Button>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span>{connected ? 'Connected' : 'Disconnected'}</span>
              </div>
            </div>

            <div className="border rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
              {messages.map((msg, idx) => (
                <div key={idx} className="mb-1">{msg}</div>
              ))}
              {messages.length === 0 && (
                <div className="text-muted-foreground">No messages yet...</div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
