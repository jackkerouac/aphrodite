// WebSocket instance holder
let ioInstance = null;

export function setIOInstance(io) {
  ioInstance = io;
}

export function getIOInstance() {
  return ioInstance;
}

// Helper function to emit events to user rooms
export function emitToUser(userId, event, data) {
  if (ioInstance) {
    ioInstance.to(`user-${userId}`).emit(event, data);
  }
}
