const express = require('express');
const { WebSocketServer } = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const chokidar = require('chokidar');

const app = express();
const server = http.createServer(app);

// SECURITY: Bind to localhost only - not accessible from network
const HOST = process.env.MONITOR_HOST || '127.0.0.1';
const PORT = process.env.MONITOR_PORT || 3847;

// SECURITY: Validate and sanitize log directory path
const HOME = process.env.HOME || '/tmp';
const DEFAULT_LOG_DIR = path.join(HOME, '.claude', 'logs');
let LOG_DIR = process.env.CLAUDE_LOG_DIR || DEFAULT_LOG_DIR;

// Path traversal protection - must be under home directory
LOG_DIR = path.resolve(LOG_DIR);
if (!LOG_DIR.startsWith(HOME)) {
  console.error('SECURITY: CLAUDE_LOG_DIR must be under HOME directory');
  LOG_DIR = DEFAULT_LOG_DIR;
}

const LOG_FILE = path.join(LOG_DIR, 'monitor.jsonl');

// SECURITY: Allowed log entry types (whitelist)
const ALLOWED_TYPES = ['hook', 'tool', 'agent', 'orch', 'sub', 'prompt', 'response', 'error', 'system', 'enforcement', 'raw'];
const MAX_FIELD_LENGTH = 1000;
const MAX_ENTRY_SIZE = 10000;

// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

// SECURITY: HTML escape function to prevent XSS
function escapeHtml(str) {
  if (typeof str !== 'string') return String(str || '');
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// SECURITY: Sanitize log entry - validate and truncate fields
function sanitizeEntry(entry) {
  if (typeof entry !== 'object' || entry === null) {
    return null;
  }
  
  // Check total size
  const entryStr = JSON.stringify(entry);
  if (entryStr.length > MAX_ENTRY_SIZE) {
    return null;
  }
  
  const sanitized = {
    timestamp: typeof entry.timestamp === 'number' ? entry.timestamp : Date.now(),
    received: Date.now()
  };
  
  // Validate type
  if (entry.type && ALLOWED_TYPES.includes(entry.type)) {
    sanitized.type = entry.type;
  } else {
    sanitized.type = 'raw';
  }
  
  // Sanitize string fields with length limits
  const stringFields = ['hook', 'tool', 'agent', 'status', 'message', 'content', 'file', 'event'];
  for (const field of stringFields) {
    if (entry[field] !== undefined) {
      const val = String(entry[field]).slice(0, MAX_FIELD_LENGTH);
      sanitized[field] = escapeHtml(val);
    }
  }
  
  // Copy numeric fields
  const numericFields = ['complexity', 'duration', 'depth'];
  for (const field of numericFields) {
    if (typeof entry[field] === 'number') {
      sanitized[field] = entry[field];
    }
  }
  
  // Copy boolean fields
  if (typeof entry.blocked === 'boolean') {
    sanitized.blocked = entry.blocked;
  }
  
  return sanitized;
}

// SECURITY: Check if request is from localhost
function isLocalhost(req) {
  const ip = req.ip || req.connection.remoteAddress || '';
  return ip === '127.0.0.1' || ip === '::1' || ip === '::ffff:127.0.0.1';
}

// Store connected clients
const clients = new Set();

// Broadcast to all connected clients
function broadcast(data) {
  const message = JSON.stringify(data);
  clients.forEach(client => {
    if (client.readyState === 1) {
      client.send(message);
    }
  });
}

// WebSocket server - SECURITY: localhost only via server binding
const wss = new WebSocketServer({ server });

wss.on('connection', (ws, req) => {
  // SECURITY: Verify connection is from localhost
  const ip = req.socket.remoteAddress || '';
  if (ip !== '127.0.0.1' && ip !== '::1' && ip !== '::ffff:127.0.0.1') {
    console.warn(`SECURITY: Rejected WebSocket from ${ip}`);
    ws.close();
    return;
  }
  
  clients.add(ws);
  console.log(`Client connected from ${ip}. Total: ${clients.size}`);
  
  // Send recent logs on connect (already sanitized when stored)
  if (fs.existsSync(LOG_FILE)) {
    const lines = fs.readFileSync(LOG_FILE, 'utf-8').split('\n').filter(Boolean).slice(-100);
    lines.forEach(line => {
      try {
        ws.send(line);
      } catch (e) {}
    });
  }
  
  ws.on('close', () => {
    clients.delete(ws);
    console.log(`Client disconnected. Total: ${clients.size}`);
  });
});

// Watch log file for changes
let lastSize = 0;
if (fs.existsSync(LOG_FILE)) {
  lastSize = fs.statSync(LOG_FILE).size;
}

chokidar.watch(LOG_FILE, { persistent: true }).on('change', () => {
  const stat = fs.statSync(LOG_FILE);
  if (stat.size > lastSize) {
    const stream = fs.createReadStream(LOG_FILE, { start: lastSize, encoding: 'utf-8' });
    let buffer = '';
    stream.on('data', chunk => buffer += chunk);
    stream.on('end', () => {
      buffer.split('\n').filter(Boolean).forEach(line => {
        try {
          const parsed = JSON.parse(line);
          broadcast(parsed);
        } catch (e) {
          broadcast({ type: 'raw', content: escapeHtml(line), timestamp: Date.now() });
        }
      });
    });
    lastSize = stat.size;
  }
});

// API endpoint to receive logs from hooks
app.use(express.json({ limit: '50kb' })); // SECURITY: Limit request size

// SECURITY: Localhost-only middleware for sensitive endpoints
const localhostOnly = (req, res, next) => {
  if (!isLocalhost(req)) {
    console.warn(`SECURITY: Rejected request from ${req.ip} to ${req.path}`);
    return res.status(403).json({ error: 'Forbidden - localhost only' });
  }
  next();
};

app.post('/log', localhostOnly, (req, res) => {
  // SECURITY: Validate and sanitize entry
  const entry = sanitizeEntry(req.body);
  
  if (!entry) {
    return res.status(400).json({ error: 'Invalid log entry' });
  }
  
  // SECURITY: Use async file write to not block event loop
  fs.appendFile(LOG_FILE, JSON.stringify(entry) + '\n', (err) => {
    if (err) {
      console.error('Failed to write log:', err.message);
    }
  });
  
  // Broadcast immediately
  broadcast(entry);
  
  res.json({ ok: true });
});

// API to get recent logs
app.get('/api/logs', localhostOnly, (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 100, 500);
  if (!fs.existsSync(LOG_FILE)) {
    return res.json([]);
  }
  const lines = fs.readFileSync(LOG_FILE, 'utf-8').split('\n').filter(Boolean).slice(-limit);
  res.json(lines.map(l => { try { return JSON.parse(l); } catch { return { type: 'raw', content: escapeHtml(l) }; } }));
});

// SECURITY: Require confirmation token for destructive operations
app.post('/api/logs/clear', localhostOnly, (req, res) => {
  // Require explicit confirmation
  if (req.body.confirm !== 'CLEAR_ALL_LOGS') {
    return res.status(400).json({ error: 'Confirmation required', hint: 'Send {"confirm": "CLEAR_ALL_LOGS"}' });
  }
  
  fs.writeFileSync(LOG_FILE, '');
  lastSize = 0;
  broadcast({ type: 'system', action: 'clear', timestamp: Date.now() });
  res.json({ ok: true, cleared: true });
});

// Serve static files
app.use(express.static(path.join(__dirname, '../web')));

// SECURITY: Bind to localhost only
server.listen(PORT, HOST, () => {
  console.log(`Claude Monitor running at http://${HOST}:${PORT}`);
  console.log(`Log file: ${LOG_FILE}`);
  console.log('SECURITY: Bound to localhost only');
});
