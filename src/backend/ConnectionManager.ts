const fs = require('fs').promises;
const path = require('path');
const { app } = require('electron');
let mysql: any;

try {
  mysql = require('mysql2/promise');
} catch (error) {
  console.error('Failed to load mysql2:', error);
}

export interface ConnectionConfig {
  id?: string;
  name: string;
  host: string;
  port: number;
  username: string;
  password: string;
  database?: string;
  ssl?: boolean;
  timeout?: number;
}

export interface SavedConnection extends ConnectionConfig {
  id: string;
  createdAt: Date;
  lastUsed?: Date;
}

export class ConnectionManager {
  private connections: Map<string, any> = new Map();
  private savedConnections: SavedConnection[] = [];
  private configPath: string;

  constructor() {
    this.configPath = path.join(app.getPath('userData'), 'connections.json');
    this.loadSavedConnections();
  }

  async testConnection(config: ConnectionConfig): Promise<{ success: boolean; error?: string }> {
    try {
      const connection = await mysql.createConnection({
        host: config.host,
        port: config.port,
        user: config.username,
        password: config.password,
        database: config.database,
        ssl: config.ssl ? {} : undefined,
        connectTimeout: config.timeout || 10000
      });

      await connection.ping();
      await connection.end();
      return { success: true };
    } catch (error: any) {
      console.error('Connection test failed:', error);
      const errorMessage = error?.message || error?.code || 'Unknown connection error';
      return { success: false, error: errorMessage };
    }
  }

  async saveConnection(config: ConnectionConfig): Promise<string> {
    console.log('ConnectionManager - saveConnection called with config:', config);
    const id = config.id || this.generateId();
    console.log('ConnectionManager - using id:', id, 'original config.id:', config.id);
    const savedConnection: SavedConnection = {
      ...config,
      id,
      createdAt: new Date(),
      lastUsed: new Date()
    };

    // Update existing or add new
    const existingIndex = this.savedConnections.findIndex(conn => conn.id === id);
    console.log('ConnectionManager - existingIndex:', existingIndex);
    if (existingIndex >= 0) {
      console.log('ConnectionManager - updating existing connection at index:', existingIndex);
      this.savedConnections[existingIndex] = savedConnection;
    } else {
      console.log('ConnectionManager - adding new connection');
      this.savedConnections.push(savedConnection);
    }

    await this.saveToDisk();
    return id;
  }

  async getConnections(): Promise<SavedConnection[]> {
    return this.savedConnections;
  }

  async deleteConnection(id: string): Promise<boolean> {
    const index = this.savedConnections.findIndex(conn => conn.id === id);
    if (index >= 0) {
      this.savedConnections.splice(index, 1);
      await this.saveToDisk();

      // Close active connection if exists
      const activeConnection = this.connections.get(id);
      if (activeConnection) {
        await activeConnection.end();
        this.connections.delete(id);
      }

      return true;
    }
    return false;
  }

  async getConnection(id: string): Promise<any | null> {
    console.log('ConnectionManager: getConnection called with id:', id);
    console.log('ConnectionManager: Current connections map size:', this.connections.size);
    console.log('ConnectionManager: Saved connections count:', this.savedConnections.length);

    // Return existing connection if available
    const existingConnection = this.connections.get(id);
    if (existingConnection) {
      console.log('ConnectionManager: Found existing connection, testing ping');
      try {
        await existingConnection.ping();
        console.log('ConnectionManager: Existing connection ping successful');
        return existingConnection;
      } catch (error) {
        console.log('ConnectionManager: Existing connection ping failed, removing:', error);
        // Connection is dead, remove it
        this.connections.delete(id);
      }
    }

    // Create new connection
    console.log('ConnectionManager: Looking for config with id:', id);
    const config = this.savedConnections.find(conn => conn.id === id);
    console.log('ConnectionManager: Found config:', config ? 'yes' : 'no');

    if (!config) {
      console.error('ConnectionManager: No config found for id:', id);
      return null;
    }

    console.log('ConnectionManager: Creating new MySQL connection with config:', {
      host: config.host,
      port: config.port,
      user: config.username,
      database: config.database,
      ssl: config.ssl,
      timeout: config.timeout
    });

    try {
      const connection = await mysql.createConnection({
        host: config.host,
        port: config.port,
        user: config.username,
        password: config.password,
        database: config.database,
        ssl: config.ssl ? {} : undefined,
        connectTimeout: config.timeout || 10000
      });

      console.log('ConnectionManager: MySQL connection created successfully');
      this.connections.set(id, connection);

      // Update last used time
      config.lastUsed = new Date();
      await this.saveToDisk();

      return connection;
    } catch (error) {
      console.error('ConnectionManager: Failed to create connection:', error);
      return null;
    }
  }

  async closeConnection(id: string): Promise<void> {
    const connection = this.connections.get(id);
    if (connection) {
      await connection.end();
      this.connections.delete(id);
    }
  }

  async closeAllConnections(): Promise<void> {
    const promises = Array.from(this.connections.keys()).map(id => this.closeConnection(id));
    await Promise.all(promises);
  }

  async connectToDatabase(id: string): Promise<boolean> {
    try {
      console.log('ConnectionManager: connectToDatabase called with id:', id);
      const connection = await this.getConnection(id);
      console.log('ConnectionManager: getConnection result:', connection ? 'success' : 'null');
      return connection !== null;
    } catch (error) {
      console.error('ConnectionManager: Failed to connect to database:', error);
      return false;
    }
  }

  async disconnectFromDatabase(id: string): Promise<boolean> {
    try {
      await this.closeConnection(id);
      return true;
    } catch (error) {
      console.error('Failed to disconnect from database:', error);
      return false;
    }
  }

  async getDatabases(id: string): Promise<{ success: boolean; databases?: string[]; error?: string }> {
    try {
      console.log('ConnectionManager: getDatabases called with id:', id);
      const connection = await this.getConnection(id);
      console.log('ConnectionManager: getDatabases getConnection result:', connection ? 'success' : 'null');

      if (!connection) {
        console.error('ConnectionManager: No connection found for id:', id);
        return { success: false, error: 'No connection found' };
      }

      console.log('ConnectionManager: Executing SHOW DATABASES query');
      const [rows] = await connection.execute('SHOW DATABASES');
      console.log('ConnectionManager: SHOW DATABASES raw result:', rows);

      const databases = rows.map((row: any) => row.Database).filter((db: string) =>
        !['information_schema', 'performance_schema', 'mysql', 'sys'].includes(db)
      );
      console.log('ConnectionManager: Filtered databases:', databases);

      return { success: true, databases };
    } catch (error) {
      console.error('ConnectionManager: Failed to get databases:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return { success: false, error: errorMessage };
    }
  }

  async checkConnection(id: string): Promise<boolean> {
    try {
      const connection = this.connections.get(id);
      if (!connection) {
        return false;
      }

      await connection.ping();
      return true;
    } catch (error) {
      // Connection is dead, remove it
      this.connections.delete(id);
      return false;
    }
  }

  private async loadSavedConnections(): Promise<void> {
    try {
      const data = await fs.readFile(this.configPath, 'utf-8');
      this.savedConnections = JSON.parse(data);
    } catch (error) {
      // File doesn't exist or is corrupted, start with empty array
      this.savedConnections = [];
    }
  }

  private async saveToDisk(): Promise<void> {
    try {
      await fs.writeFile(this.configPath, JSON.stringify(this.savedConnections, null, 2));
    } catch (error) {
      console.error('Failed to save connections:', error);
    }
  }

  private generateId(): string {
    return `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}