const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const mongoose = require('mongoose');
const { PythonShell } = require('python-shell');

let mainWindow;

async function connectToMongoDB() {
  try {
    await mongoose.connect('mongodb://localhost:27017/axislimited', {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    console.log('Connected to MongoDB (axislimited database)');
  } catch (err) {
    console.error('MongoDB connection error:', err);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Remove the menu bar
  mainWindow.setMenu(null);

  // Maximize the window on load
  mainWindow.maximize();

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  connectToMongoDB();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// IPC to handle login requests
ipcMain.on('login-request', (event, { accessCode, accessPassword }) => {
  let pyshell = new PythonShell('backend.py', {
    mode: 'json',
    pythonOptions: ['-u']
  });

  pyshell.send({ access_code: accessCode, password: accessPassword });

  pyshell.on('message', (message) => {
    event.reply('login-response', message);
  });

  pyshell.on('error', (err) => {
    console.error('Python script error:', err);
    event.reply('login-response', { success: false, message: 'Server error' });
  });
});

// IPC to load dashboard
ipcMain.on('load-dashboard', () => {
  mainWindow.loadFile('dashboard.html');
});