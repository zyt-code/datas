const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const { ConnectionManager } = require('./ConnectionManager');
const { QueryExecutor } = require('./QueryExecutor');

class DataGripLiteApp {
  private mainWindow: any | null = null;
  private connectionManager: any;
  private queryExecutor: any;

  constructor() {
    this.connectionManager = new ConnectionManager();
    this.queryExecutor = new QueryExecutor();
    this.setupApp();
  }

  private setupApp(): void {
    app.whenReady().then(() => {
      this.createWindow();
      this.setupMenu();
      this.setupIpcHandlers();
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow();
      }
    });
  }

  private createWindow(): void {

    this.mainWindow = new BrowserWindow({
      width: 1920,
      height: 1080,
      minWidth: 800,
      minHeight: 600,
      fullscreen: false,
      maximized: true,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: true
      },
      icon: path.join(__dirname, '../assets/icon.png'),
      titleBarStyle: 'default',
      show: false
    });

    // Load the renderer
    this.mainWindow.loadFile(path.join(__dirname, '../dist-renderer/src/renderer/index.html'));

    // Show window when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
    });

    // Open DevTools in development
    if (process.argv.includes('--dev')) {
      this.mainWindow.webContents.openDevTools();
    }
  }

  private setupMenu(): void {
    const template: any[] = [
      {
        label: 'File',
        submenu: [
          {
            label: 'New SQL File',
            accelerator: 'CmdOrCtrl+N',
            click: () => {
              this.mainWindow?.webContents.send('menu-new-file');
            }
          },
          {
            label: 'Open SQL File',
            accelerator: 'CmdOrCtrl+O',
            click: async () => {
              const result = await dialog.showOpenDialog(this.mainWindow!, {
                filters: [{ name: 'SQL Files', extensions: ['sql'] }],
                properties: ['openFile']
              });
              if (!result.canceled && result.filePaths.length > 0) {
                this.mainWindow?.webContents.send('menu-open-file', result.filePaths[0]);
              }
            }
          },
          { type: 'separator' },
          {
            label: 'Exit',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => {
              app.quit();
            }
          }
        ]
      },
      {
        label: 'Edit',
        submenu: [
          { role: 'undo' },
          { role: 'redo' },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' },
          { role: 'selectAll' }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  private setupIpcHandlers(): void {
    // Connection management
    ipcMain.handle('connection-test', async (_: any, connectionConfig: any) => {
      return await this.connectionManager.testConnection(connectionConfig);
    });

    ipcMain.handle('connection-save', async (_: any, connectionConfig: any) => {
      return await this.connectionManager.saveConnection(connectionConfig);
    });

    ipcMain.handle('connection-list', async () => {
      return await this.connectionManager.getConnections();
    });

    ipcMain.handle('connection-delete', async (_: any, connectionId: string) => {
      return await this.connectionManager.deleteConnection(connectionId);
    });

    ipcMain.handle('connection-connect', async (_: any, connectionId: string) => {
      console.log('IPC: connection-connect called with connectionId:', connectionId);
      try {
        const result = await this.connectionManager.connectToDatabase(connectionId);
        console.log('IPC: connection-connect result:', result);
        return result;
      } catch (error) {
        console.error('IPC: connection-connect error:', error);
        throw error;
      }
    });

    ipcMain.handle('connection-disconnect', async (_: any, connectionId: string) => {
      console.log('IPC: connection-disconnect called with connectionId:', connectionId);
      try {
        const result = await this.connectionManager.disconnectFromDatabase(connectionId);
        console.log('IPC: connection-disconnect result:', result);
        return result;
      } catch (error) {
        console.error('IPC: connection-disconnect error:', error);
        throw error;
      }
    });

    ipcMain.handle('connection-get-databases', async (_: any, connectionId: string) => {
      console.log('IPC: connection-get-databases called with connectionId:', connectionId);
      try {
        const result = await this.connectionManager.getDatabases(connectionId);
        console.log('IPC: connection-get-databases result:', result);
        return result;
      } catch (error) {
        console.error('IPC: connection-get-databases error:', error);
        throw error;
      }
    });

    ipcMain.handle('connection-check', async (_: any, connectionId: string) => {
      console.log('IPC: connection-check called with connectionId:', connectionId);
      try {
        const result = await this.connectionManager.checkConnection(connectionId);
        console.log('IPC: connection-check result:', result);
        return result;
      } catch (error) {
        console.error('IPC: connection-check error:', error);
        throw error;
      }
    });

    // Query execution
    ipcMain.handle('query-execute', async (_: any, connectionId: string, query: string) => {
      return await this.queryExecutor.executeQuery(connectionId, query);
    });

    ipcMain.handle('schema-get', async (_: any, connectionId: string) => {
      return await this.queryExecutor.getSchema(connectionId);
    });
  }
}

// Start the application
new DataGripLiteApp();