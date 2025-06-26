export interface IElectronAPI {
  getConnections: () => Promise<Connection[]>;
  saveConnection: (connection: ConnectionData) => Promise<void>;
  testConnection: (connection: ConnectionData) => Promise<{ success: boolean; error?: string }>;
  executeQuery: (connectionId: string, query: string) => Promise<QueryResult>;
  openFile: () => Promise<string | null>;
  saveFile: (content: string, filePath?: string) => Promise<string | null>;
  showSaveDialog: () => Promise<string | null>;

  // 新增的连接管理方法
  connectToDatabase: (connectionId: string) => Promise<boolean>;
  disconnectFromDatabase: (connectionId: string) => Promise<boolean>;
  getDatabases: (connectionId: string) => Promise<{ success: boolean; databases?: string[]; error?: string }>;
  checkConnection: (connectionId: string) => Promise<boolean>;
  deleteConnection: (id: string) => Promise<boolean>;
}

export interface Connection {
  id: string;
  name: string;
  type: string;
  host: string;
  port: number;
  database?: string;
  username?: string;
  password?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ConnectionData {
  id?: string;
  name: string;
  type: string;
  host: string;
  port: number;
  database?: string;
  username?: string;
  password?: string;
}

export interface QueryResult {
  columns?: string[];
  rows?: any[][];
  error?: string;
  executionTime?: number;
  messages?: string;
  rowCount?: number;
}

declare global {
  interface Window {
    electronAPI: IElectronAPI;
  }
}