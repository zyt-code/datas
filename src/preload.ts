const { contextBridge, ipcRenderer } = require('electron');

// Define the API interface
interface ElectronAPI {
  // Connection management
  testConnection: (config: any) => Promise<boolean>;
  saveConnection: (config: any) => Promise<string>;
  getConnections: () => Promise<any[]>;
  deleteConnection: (id: string) => Promise<boolean>;
  connectToDatabase: (connectionId: string) => Promise<boolean>;
  disconnectFromDatabase: (connectionId: string) => Promise<boolean>;
  getDatabases: (connectionId: string) => Promise<string[]>;
  checkConnection: (connectionId: string) => Promise<boolean>;
  
  // Query execution
  executeQuery: (connectionId: string, query: string) => Promise<any>;
  getSchema: (connectionId: string) => Promise<any>;
  
  // Menu events
  onMenuNewFile: (callback: () => void) => void;
  onMenuOpenFile: (callback: (filePath: string) => void) => void;
  onMenuNewConnection: (callback: () => void) => void;
  onMenuManageConnections: (callback: () => void) => void;
  
  // File operations
  readFile: (filePath: string) => Promise<string>;
  writeFile: (filePath: string, content: string) => Promise<void>;
}

// Expose the API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Connection management
  testConnection: (config: any) => ipcRenderer.invoke('connection-test', config),
  saveConnection: (config: any) => ipcRenderer.invoke('connection-save', config),
  getConnections: () => ipcRenderer.invoke('connection-list'),
  deleteConnection: (id: string) => ipcRenderer.invoke('connection-delete', id),
  connectToDatabase: (connectionId: string) => ipcRenderer.invoke('connection-connect', connectionId),
  disconnectFromDatabase: (connectionId: string) => ipcRenderer.invoke('connection-disconnect', connectionId),
  getDatabases: (connectionId: string) => ipcRenderer.invoke('connection-get-databases', connectionId),
  checkConnection: (connectionId: string) => ipcRenderer.invoke('connection-check', connectionId),
  
  // Query execution
  executeQuery: async (connectionId: string, query: string) => {
    const multiResult = await ipcRenderer.invoke('query-execute', connectionId, query);
    
    // Convert MultiQueryResult to QueryResult for frontend
    if (!multiResult || !multiResult.results || multiResult.results.length === 0) {
      return {
        error: 'No results returned',
        executionTime: 0,
        rowCount: 0
      };
    }
    
    // Handle multiple statements - combine results
    const allRows: any[][] = [];
    let columns: string[] = [];
    let totalRowCount = 0;
    let hasError = false;
    let errorMessage = '';
    let messages: string[] = [];
    
    for (const result of multiResult.results) {
      if (!result.success) {
        hasError = true;
        errorMessage = result.error || 'Query execution failed';
        break;
      }
      
      if (result.data && Array.isArray(result.data)) {
        // SELECT query with data
        if (result.data.length > 0) {
          // Extract columns from fields or first row
          if (result.fields && result.fields.length > 0) {
            columns = result.fields.map(field => field.name);
          } else if (result.data.length > 0) {
            columns = Object.keys(result.data[0]);
          }
          
          // Convert data to rows format
          const rows = result.data.map(row => 
            columns.map(col => row[col])
          );
          allRows.push(...rows);
          totalRowCount += result.data.length;
        }
      } else {
        // Non-SELECT query (INSERT, UPDATE, DELETE, etc.)
        if (result.affectedRows !== undefined) {
          totalRowCount += result.affectedRows;
          messages.push(`${result.affectedRows} rows affected`);
        }
        if (result.insertId) {
          messages.push(`Insert ID: ${result.insertId}`);
        }
      }
    }
    
    if (hasError) {
      return {
        error: errorMessage,
        executionTime: multiResult.totalExecutionTime,
        rowCount: 0
      };
    }
    
    return {
      columns: columns.length > 0 ? columns : undefined,
      rows: allRows.length > 0 ? allRows : undefined,
      executionTime: multiResult.totalExecutionTime,
      rowCount: totalRowCount,
      messages: messages.length > 0 ? messages.join('\n') : undefined
    };
  },
  getSchema: (connectionId: string) => ipcRenderer.invoke('schema-get', connectionId),
  
  // Menu event listeners
  onMenuNewFile: (callback: () => void) => {
    ipcRenderer.on('menu-new-file', callback);
  },
  onMenuOpenFile: (callback: (filePath: string) => void) => {
    ipcRenderer.on('menu-open-file', (_: any, filePath: string) => callback(filePath));
  },
  onMenuNewConnection: (callback: () => void) => {
    ipcRenderer.on('menu-new-connection', callback);
  },
  onMenuManageConnections: (callback: () => void) => {
    ipcRenderer.on('menu-manage-connections', callback);
  },
  
  // File operations
  readFile: (filePath: string) => ipcRenderer.invoke('file-read', filePath),
  writeFile: (filePath: string, content: string) => 
    ipcRenderer.invoke('file-write', filePath, content)
} as ElectronAPI);

// Declare global type for TypeScript
// Global type declaration moved to separate .d.ts file if needed