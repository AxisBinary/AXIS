const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  sendLogin: (accessCode, accessPassword) => ipcRenderer.send('login-request', { accessCode, accessPassword }),
  onLoginResponse: (callback) => ipcRenderer.on('login-response', (event, response) => callback(response)),
  loadDashboard: () => ipcRenderer.send('load-dashboard')
});