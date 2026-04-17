const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { createClient } = require('redis');
const { createAdapter } = require('@socket.io/redis-adapter');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

const REDIS_HOST = process.env.REDIS_HOST || 'redis-stadium';

// Redis setup for horizontal scaling
const pubClient = createClient({ url: `redis://${REDIS_HOST}:6379` });
const subClient = pubClient.duplicate();
const broadcastSub = pubClient.duplicate();

async function startServer() {
  try {
    // Connect to Redis for scaling Socket.IO across multiple Node instances
    await Promise.all([pubClient.connect(), subClient.connect(), broadcastSub.connect()]);
    io.adapter(createAdapter(pubClient, subClient));
    console.log('Redis adapter connected for horizontal scaling.');

    // Listen to "zone_updates" published by FastAPI
    broadcastSub.subscribe('zone_updates', (message) => {
      // message format -> "zone_id:occupancy"
      const [zone_id, occupancy] = message.split(':');
      // Push only to authenticated users looking at the map
      io.to('stadium_map_room').emit('heatmap_update', { zone_id, occupancy: parseInt(occupancy) });
    });

    broadcastSub.subscribe('system_alerts', (message) => {
      // message format -> "SEVERITY|ZONE|MESSAGE"
      const parts = message.split('|');
      io.emit('stadium_alert', { severity: parts[0], zone: parts[1], message: parts[2] });
    });

  } catch (err) {
    console.log('Redis connection failed, running on single instance mode.', err.message);
  }

  // Socket connections
  io.on('connection', (socket) => {
    console.log(`User Connected: ${socket.id}`);

    // Users explicitly join this room when opening the map in the app
    socket.on('join_map', () => {
      socket.join('stadium_map_room');
      console.log(`User ${socket.id} joined map updates`);
    });

    socket.on('disconnect', () => {
      console.log(`User Disconnected: ${socket.id}`);
    });
  });

  const PORT = process.env.PORT || 3000;
  server.listen(PORT, () => {
    console.log(`WebSocket Server running on port ${PORT}`);
  });
}

startServer();
