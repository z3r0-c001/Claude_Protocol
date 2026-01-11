const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

// Configuration
const MONITOR_PORT = process.env.CLAUDE_MONITOR_PORT || 3847;
const MONITOR_URL = `http://localhost:${MONITOR_PORT}`;

let mainWindow = null;
let tray = null;
let serverProcess = null;
let agentProcess = null;
let isQuitting = false;

// Window configuration
const WINDOW_CONFIG = {
  width: 1400,
  height: 900,
  minWidth: 800,
  minHeight: 600,
  x: 100,
  y: 100,
  title: 'Claude Monitor',
  backgroundColor: '#0f0f0f',
  webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    preload: path.join(__dirname, 'preload.js')
  },
  // Window frame options
  frame: true,
  titleBarStyle: 'hiddenInset', // macOS: nice integrated title bar
  vibrancy: 'dark', // macOS: dark vibrancy effect
  
  // Keep on top option (can be toggled)
  alwaysOnTop: false,
  
  // Show in taskbar
  skipTaskbar: false,
  
  // Icon
  icon: path.join(__dirname, 'icons', 'icon.png')
};

// Check if server is running
function checkServer() {
  return new Promise((resolve) => {
    http.get(`${MONITOR_URL}/api/logs`, (res) => {
      resolve(res.statusCode === 200);
    }).on('error', () => {
      resolve(false);
    });
  });
}

// Start the WebSocket server
function startServer() {
  return new Promise((resolve, reject) => {
    const serverPath = path.join(__dirname, '..', 'server', 'index.js');
    
    serverProcess = spawn('node', [serverPath], {
      env: { ...process.env, MONITOR_PORT },
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    serverProcess.stdout.on('data', (data) => {
      console.log(`[Server] ${data}`);
      if (data.toString().includes('running at')) {
        resolve();
      }
    });
    
    serverProcess.stderr.on('data', (data) => {
      console.error(`[Server Error] ${data}`);
    });
    
    serverProcess.on('error', reject);
    
    // Timeout fallback
    setTimeout(resolve, 3000);
  });
}

// Start the monitor agent
function startMonitorAgent() {
  const agentPath = path.join(__dirname, '..', 'monitor-agent.py');
  
  agentProcess = spawn('python3', [agentPath, '--watch'], {
    env: process.env,
    stdio: ['ignore', 'pipe', 'pipe']
  });
  
  agentProcess.stdout.on('data', (data) => {
    console.log(`[Agent] ${data}`);
    // Forward to renderer if window exists
    if (mainWindow) {
      mainWindow.webContents.send('agent-log', data.toString());
    }
  });
  
  agentProcess.stderr.on('data', (data) => {
    console.error(`[Agent] ${data}`);
    if (mainWindow) {
      mainWindow.webContents.send('agent-error', data.toString());
    }
  });
}

// Create the main window
function createWindow() {
  mainWindow = new BrowserWindow(WINDOW_CONFIG);
  
  // Load the dashboard
  mainWindow.loadURL(MONITOR_URL);
  
  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
  
  // Window events
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
  });
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  // Dev tools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

// Create system tray
function createTray() {
  // Create tray icon (use a simple colored circle as fallback)
  const iconPath = path.join(__dirname, 'icons', 'tray-icon.png');
  let trayIcon;
  
  try {
    trayIcon = nativeImage.createFromPath(iconPath);
  } catch {
    // Create a simple icon programmatically
    trayIcon = nativeImage.createEmpty();
  }
  
  // Resize for tray (16x16 on most platforms)
  if (!trayIcon.isEmpty()) {
    trayIcon = trayIcon.resize({ width: 16, height: 16 });
  }
  
  tray = new Tray(trayIcon);
  tray.setToolTip('Claude Monitor');
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show Dashboard',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        } else {
          createWindow();
        }
      }
    },
    {
      label: 'Always on Top',
      type: 'checkbox',
      checked: false,
      click: (menuItem) => {
        if (mainWindow) {
          mainWindow.setAlwaysOnTop(menuItem.checked);
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Server Status',
      enabled: false
    },
    {
      label: 'Restart Server',
      click: async () => {
        if (serverProcess) {
          serverProcess.kill();
        }
        await startServer();
        if (mainWindow) {
          mainWindow.reload();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Open in Browser',
      click: () => {
        shell.openExternal(MONITOR_URL);
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setContextMenu(contextMenu);
  
  // Click to show/hide
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    } else {
      createWindow();
    }
  });
}

// IPC handlers
function setupIPC() {
  // Toggle always on top
  ipcMain.handle('toggle-always-on-top', () => {
    if (mainWindow) {
      const current = mainWindow.isAlwaysOnTop();
      mainWindow.setAlwaysOnTop(!current);
      return !current;
    }
    return false;
  });
  
  // Get window state
  ipcMain.handle('get-window-state', () => {
    if (mainWindow) {
      return {
        alwaysOnTop: mainWindow.isAlwaysOnTop(),
        isMaximized: mainWindow.isMaximized(),
        isFullScreen: mainWindow.isFullScreen()
      };
    }
    return null;
  });
  
  // Minimize to tray
  ipcMain.on('minimize-to-tray', () => {
    if (mainWindow) {
      mainWindow.hide();
    }
  });
}

// App lifecycle
app.whenReady().then(async () => {
  // Check if server is already running
  const serverRunning = await checkServer();
  
  if (!serverRunning) {
    console.log('Starting monitor server...');
    await startServer();
  } else {
    console.log('Monitor server already running');
  }
  
  // Start monitor agent
  console.log('Starting monitor agent...');
  startMonitorAgent();
  
  // Setup IPC
  setupIPC();
  
  // Create tray
  createTray();
  
  // Create window
  createWindow();
  
  // macOS: recreate window on dock click
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else if (mainWindow) {
      mainWindow.show();
    }
  });
});

// Cleanup on quit
app.on('before-quit', () => {
  isQuitting = true;
});

app.on('will-quit', () => {
  // Kill server and agent processes
  if (serverProcess) {
    serverProcess.kill();
  }
  if (agentProcess) {
    agentProcess.kill();
  }
});

// macOS: don't quit when all windows closed (keep in tray)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    // On Windows/Linux, keep running in tray
    // app.quit();
  }
});

// Handle certificate errors for localhost
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (url.startsWith('https://localhost')) {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});
