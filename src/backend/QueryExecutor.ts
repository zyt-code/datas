import * as mysql from 'mysql2/promise';
import { ConnectionManager } from './ConnectionManager';

export interface QueryResult {
  success: boolean;
  data?: any[];
  fields?: mysql.FieldPacket[];
  affectedRows?: number;
  insertId?: number;
  error?: string;
  executionTime: number;
}

export interface MultiQueryResult {
  results: QueryResult[];
  totalExecutionTime: number;
}

export interface SchemaInfo {
  databases: DatabaseInfo[];
}

export interface DatabaseInfo {
  name: string;
  tables: TableInfo[];
}

export interface TableInfo {
  name: string;
  type: 'table' | 'view';
  columns: ColumnInfo[];
}

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  key: string;
  default: any;
  extra: string;
}

export class QueryExecutor {
  private connectionManager: ConnectionManager;

  constructor() {
    this.connectionManager = new ConnectionManager();
  }

  async executeQuery(connectionId: string, query: string): Promise<MultiQueryResult> {
    const connection = await this.connectionManager.getConnection(connectionId);
    if (!connection) {
      return {
        results: [{
          success: false,
          error: 'Connection not found or failed to connect',
          executionTime: 0
        }],
        totalExecutionTime: 0
      };
    }

    const startTime = Date.now();
    const statements = this.splitStatements(query);
    const results: QueryResult[] = [];

    for (const statement of statements) {
      if (statement.trim()) {
        const result = await this.executeSingleStatement(connection, statement);
        results.push(result);
      }
    }

    const totalExecutionTime = Date.now() - startTime;

    return {
      results,
      totalExecutionTime
    };
  }

  async getSchema(connectionId: string): Promise<SchemaInfo | null> {
    const connection = await this.connectionManager.getConnection(connectionId);
    if (!connection) {
      return null;
    }

    try {
      // Get all databases
      const [databases] = await connection.query('SHOW DATABASES');
      const databaseList = (databases as any[]).map(row => row.Database)
        .filter(db => !['information_schema', 'performance_schema', 'mysql', 'sys'].includes(db));

      const schemaInfo: SchemaInfo = {
        databases: []
      };

      for (const dbName of databaseList) {
        const databaseInfo: DatabaseInfo = {
          name: dbName,
          tables: []
        };

        // Get tables for this database
        const [tables] = await connection.query(`SHOW FULL TABLES FROM \`${dbName}\``);

        for (const tableRow of tables as any[]) {
          const tableName = tableRow[`Tables_in_${dbName}`];
          const tableType = tableRow.Table_type === 'VIEW' ? 'view' : 'table';

          // Get columns for this table
          const [columns] = await connection.query(
            `SHOW FULL COLUMNS FROM \`${dbName}\`.\`${tableName}\``
          );

          const columnInfo: ColumnInfo[] = (columns as any[]).map(col => ({
            name: col.Field,
            type: col.Type,
            nullable: col.Null === 'YES',
            key: col.Key,
            default: col.Default,
            extra: col.Extra
          }));

          databaseInfo.tables.push({
            name: tableName,
            type: tableType,
            columns: columnInfo
          });
        }

        schemaInfo.databases.push(databaseInfo);
      }

      return schemaInfo;
    } catch (error) {
      console.error('Failed to get schema:', error);
      return null;
    }
  }

  private async executeSingleStatement(connection: mysql.Connection, statement: string): Promise<QueryResult> {
    const startTime = Date.now();

    try {
      const [results, fields] = await connection.query(statement);
      const executionTime = Date.now() - startTime;

      if (Array.isArray(results)) {
        // SELECT query
        return {
          success: true,
          data: results,
          fields: fields as mysql.FieldPacket[],
          executionTime
        };
      } else {
        // INSERT, UPDATE, DELETE, etc.
        const result = results as mysql.ResultSetHeader;
        return {
          success: true,
          affectedRows: result.affectedRows,
          insertId: result.insertId,
          executionTime
        };
      }
    } catch (error: any) {
      const executionTime = Date.now() - startTime;
      return {
        success: false,
        error: error.message || 'Unknown error occurred',
        executionTime
      };
    }
  }

  private splitStatements(query: string): string[] {
    // Simple statement splitter - splits on semicolons not inside quotes
    const statements: string[] = [];
    let current = '';
    let inSingleQuote = false;
    let inDoubleQuote = false;
    let inBacktick = false;
    let escaped = false;

    for (let i = 0; i < query.length; i++) {
      const char = query[i];
      const prevChar = i > 0 ? query[i - 1] : '';

      if (escaped) {
        current += char;
        escaped = false;
        continue;
      }

      if (char === '\\') {
        escaped = true;
        current += char;
        continue;
      }

      if (char === "'" && !inDoubleQuote && !inBacktick) {
        inSingleQuote = !inSingleQuote;
      } else if (char === '"' && !inSingleQuote && !inBacktick) {
        inDoubleQuote = !inDoubleQuote;
      } else if (char === '`' && !inSingleQuote && !inDoubleQuote) {
        inBacktick = !inBacktick;
      }

      if (char === ';' && !inSingleQuote && !inDoubleQuote && !inBacktick) {
        if (current.trim()) {
          statements.push(current.trim());
        }
        current = '';
      } else {
        current += char;
      }
    }

    // Add the last statement if it doesn't end with semicolon
    if (current.trim()) {
      statements.push(current.trim());
    }

    return statements;
  }
}