const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls
  toggleAlwaysOnTop: () => ipcRenderer.invoke('toggle-always-on-top'),
  getWindowState: () => ipcRenderer.invoke('get-window-state'),
  minimizeToTray: () => ipcRenderer.send('minimize-to-tray'),
  
  // Agent log listeners
  onAgentLog: (callback) => {
    ipcRenderer.on('agent-log', (event, data) => callback(data));
  },
  onAgentError: (callback) => {
    ipcRenderer.on('agent-error', (event, data) => callback(data));
  },
  
  // Remove listeners
  removeAgentListeners: () => {
    ipcRenderer.removeAllListeners('agent-log');
    ipcRenderer.removeAllListeners('agent-error');
  },
  
  // Platform info
  platform: process.platform,
  isElectron: true
});

// Inject CSS to indicate Electron mode
window.addEventListener('DOMContentLoaded', () => {
  // Add electron-specific styling
  const style = document.createElement('style');
  style.textContent = `
    /* Electron-specific styles */
    body {
      -webkit-app-region: no-drag;
    }
    
    /* Draggable title bar area (if using frameless) */
    .electron-drag {
      -webkit-app-region: drag;
    }
    
    .electron-no-drag {
      -webkit-app-region: no-drag;
    }
    
    /* Electron indicator */
    .electron-badge {
      position: fixed;
      bottom: 8px;
      right: 8px;
      background: rgba(124, 58, 237, 0.8);
      color: white;
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      z-index: 9999;
      pointer-events: none;
    }
  `;
  document.head.appendChild(style);
  
  // Add Electron badge
  const badge = document.createElement('div');
  badge.className = 'electron-badge';
  badge.textContent = 'Electron';
  document.body.appendChild(badge);
  
  // Add window control buttons for frameless window (optional)
  // This is handled by the main process frame: true setting
});
