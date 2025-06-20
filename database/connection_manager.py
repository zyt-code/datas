#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接管理器
"""

import sqlite3
import json
import os
from typing import Dict, Any, Optional

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    
try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    
try:
    import pyodbc
    SQLSERVER_AVAILABLE = True
except ImportError:
    SQLSERVER_AVAILABLE = False
    
try:
    import cx_Oracle
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

class DatabaseConnection:
    """数据库连接封装类"""
    
    def __init__(self, connection, db_type, conn_info):
        self.connection = connection
        self.db_type = db_type
        self.conn_info = conn_info
        self.is_connected = True
        
    def execute(self, sql, params=None):
        """执行SQL语句"""
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
                
            # 检查是否是查询语句（返回结果集的语句）
            sql_upper = sql.strip().upper()
            is_query = (sql_upper.startswith('SELECT') or 
                       sql_upper.startswith('SHOW') or 
                       sql_upper.startswith('DESCRIBE') or 
                       sql_upper.startswith('DESC') or 
                       sql_upper.startswith('EXPLAIN'))
            
            if is_query:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                # 转换sqlite3.Row对象为普通列表
                if rows and hasattr(rows[0], '__getitem__') and hasattr(rows[0], 'keys'):
                    # 这是sqlite3.Row对象
                    data = [list(row) for row in rows]
                else:
                    # 普通元组或列表
                    data = [list(row) if isinstance(row, (tuple, list)) else [row] for row in rows]
                
                return {
                    'headers': columns,
                    'data': data,
                    'row_count': len(data)
                }
            else:
                # 对于非查询语句，提交事务
                self.connection.commit()
                return {
                    'affected_rows': cursor.rowcount
                }
        finally:
            cursor.close()
            
    def close(self):
        """关闭连接"""
        if self.is_connected:
            self.connection.close()
            self.is_connected = False
            
    def __del__(self):
        """析构函数"""
        self.close()

class ConnectionManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self.connections = {}  # 存储活动连接
        self.connection_configs = {}  # 存储连接配置
        self.config_file = "connections.json"
        self.load_connections()
        
    def create_connection(self, conn_info: Dict[str, Any]) -> Optional[DatabaseConnection]:
        """创建数据库连接"""
        db_type = conn_info.get('type', '').lower()
        
        try:
            if db_type == 'mysql':
                return self._create_mysql_connection(conn_info)
            elif db_type == 'postgresql':
                return self._create_postgresql_connection(conn_info)
            elif db_type == 'sqlite':
                return self._create_sqlite_connection(conn_info)
            elif db_type == 'sql server':
                return self._create_sqlserver_connection(conn_info)
            elif db_type == 'oracle':
                return self._create_oracle_connection(conn_info)
            else:
                raise ValueError(f"不支持的数据库类型: {db_type}")
        except Exception as e:
            raise Exception(f"连接数据库失败: {str(e)}")
            
    def _create_mysql_connection(self, conn_info: Dict[str, Any]) -> DatabaseConnection:
        """创建MySQL连接"""
        if not MYSQL_AVAILABLE:
            raise ImportError("PyMySQL库未安装，请运行: pip install pymysql")
            
        connection = pymysql.connect(
            host=conn_info.get('host', 'localhost'),
            port=conn_info.get('port', 3306),
            user=conn_info.get('username', ''),
            password=conn_info.get('password', ''),
            database=conn_info.get('database', ''),
            charset=conn_info.get('charset', 'utf8mb4'),
            connect_timeout=conn_info.get('timeout', 30)
        )
        
        return DatabaseConnection(connection, 'mysql', conn_info)
        
    def _create_postgresql_connection(self, conn_info: Dict[str, Any]) -> DatabaseConnection:
        """创建PostgreSQL连接"""
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("psycopg2库未安装，请运行: pip install psycopg2-binary")
            
        connection = psycopg2.connect(
            host=conn_info.get('host', 'localhost'),
            port=conn_info.get('port', 5432),
            user=conn_info.get('username', ''),
            password=conn_info.get('password', ''),
            database=conn_info.get('database', ''),
            connect_timeout=conn_info.get('timeout', 30)
        )
        
        return DatabaseConnection(connection, 'postgresql', conn_info)
        
    def _create_sqlite_connection(self, conn_info: Dict[str, Any]) -> DatabaseConnection:
        """创建SQLite连接"""
        file_path = conn_info.get('file_path', '')
        if not file_path:
            raise ValueError("SQLite数据库文件路径不能为空")
            
        # SQLite会自动创建不存在的数据库文件
        connection = sqlite3.connect(
            file_path,
            timeout=conn_info.get('timeout', 30)
        )
        
        # 设置行工厂，使结果可以通过列名访问
        connection.row_factory = sqlite3.Row
        
        return DatabaseConnection(connection, 'sqlite', conn_info)
        
    def _create_sqlserver_connection(self, conn_info: Dict[str, Any]) -> DatabaseConnection:
        """创建SQL Server连接"""
        if not SQLSERVER_AVAILABLE:
            raise ImportError("pyodbc库未安装，请运行: pip install pyodbc")
            
        # 构建连接字符串
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={conn_info.get('host', 'localhost')},{conn_info.get('port', 1433)};"
            f"DATABASE={conn_info.get('database', '')};"
            f"UID={conn_info.get('username', '')};"
            f"PWD={conn_info.get('password', '')}"
        )
        
        connection = pyodbc.connect(
            conn_str,
            timeout=conn_info.get('timeout', 30)
        )
        
        return DatabaseConnection(connection, 'sqlserver', conn_info)
        
    def _create_oracle_connection(self, conn_info: Dict[str, Any]) -> DatabaseConnection:
        """创建Oracle连接"""
        if not ORACLE_AVAILABLE:
            raise ImportError("cx_Oracle库未安装，请运行: pip install cx_Oracle")
            
        # 构建DSN
        dsn = cx_Oracle.makedsn(
            conn_info.get('host', 'localhost'),
            conn_info.get('port', 1521),
            service_name=conn_info.get('database', '')
        )
        
        connection = cx_Oracle.connect(
            user=conn_info.get('username', ''),
            password=conn_info.get('password', ''),
            dsn=dsn
        )
        
        return DatabaseConnection(connection, 'oracle', conn_info)
        
    def test_connection(self, conn_info: Dict[str, Any]) -> bool:
        """测试数据库连接"""
        try:
            connection = self.create_connection(conn_info)
            if connection:
                # 执行简单查询测试连接
                if conn_info.get('type', '').lower() == 'mysql':
                    connection.execute("SELECT 1")
                elif conn_info.get('type', '').lower() == 'postgresql':
                    connection.execute("SELECT 1")
                elif conn_info.get('type', '').lower() == 'sqlite':
                    connection.execute("SELECT 1")
                elif conn_info.get('type', '').lower() == 'sql server':
                    connection.execute("SELECT 1")
                elif conn_info.get('type', '').lower() == 'oracle':
                    connection.execute("SELECT 1 FROM DUAL")
                    
                connection.close()
                return True
        except Exception:
            return False
        return False
        
    def save_connection(self, conn_info: Dict[str, Any]):
        """保存连接配置"""
        conn_name = conn_info.get('name', '')
        if conn_name:
            # 如果不保存密码，则移除密码字段
            if not conn_info.get('save_password', True):
                conn_info = conn_info.copy()
                conn_info.pop('password', None)
                
            self.connection_configs[conn_name] = conn_info
            self.save_connections()
            
    def load_connections(self):
        """加载连接配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.connection_configs = json.load(f)
            except Exception:
                self.connection_configs = {}
        else:
            self.connection_configs = {}
            
    def save_connections(self):
        """保存连接配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.connection_configs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存连接配置失败: {e}")
            
    def get_saved_connections(self) -> Dict[str, Dict[str, Any]]:
        """获取已保存的连接配置"""
        return self.connection_configs.copy()
        
    def delete_connection(self, conn_name: str):
        """删除连接配置"""
        if conn_name in self.connection_configs:
            del self.connection_configs[conn_name]
            self.save_connections()
            
    def get_database_info(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """获取数据库信息"""
        db_type = connection.db_type.lower()
        
        try:
            if db_type == 'mysql':
                return self._get_mysql_info(connection)
            elif db_type == 'postgresql':
                return self._get_postgresql_info(connection)
            elif db_type == 'sqlite':
                return self._get_sqlite_info(connection)
            elif db_type == 'sqlserver':
                return self._get_sqlserver_info(connection)
            elif db_type == 'oracle':
                return self._get_oracle_info(connection)
        except Exception as e:
            return {'error': str(e)}
            
        return {}
        
    def _get_mysql_info(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """获取MySQL数据库信息"""
        # 获取数据库列表
        result = connection.execute("SHOW DATABASES")
        databases = [row[0] for row in result['data']]
        
        # 获取表列表（如果指定了数据库）
        tables = []
        if connection.conn_info.get('database'):
            result = connection.execute("SHOW TABLES")
            tables = [row[0] for row in result['data']]
            
        return {
            'databases': databases,
            'tables': tables,
            'version': self._get_mysql_version(connection)
        }
        
    def _get_mysql_version(self, connection: DatabaseConnection) -> str:
        """获取MySQL版本"""
        try:
            result = connection.execute("SELECT VERSION()")
            return result['data'][0][0] if result['data'] else 'Unknown'
        except Exception:
            return 'Unknown'
            
    def _get_postgresql_info(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """获取PostgreSQL数据库信息"""
        # 获取数据库列表
        result = connection.execute(
            "SELECT datname FROM pg_database WHERE datistemplate = false"
        )
        databases = [row[0] for row in result['data']]
        
        # 获取表列表
        result = connection.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        tables = [row[0] for row in result['data']]
        
        return {
            'databases': databases,
            'tables': tables,
            'version': self._get_postgresql_version(connection)
        }
        
    def _get_postgresql_version(self, connection: DatabaseConnection) -> str:
        """获取PostgreSQL版本"""
        try:
            result = connection.execute("SELECT version()")
            return result['data'][0][0] if result['data'] else 'Unknown'
        except Exception:
            return 'Unknown'
            
    def _get_sqlite_info(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """获取SQLite数据库信息"""
        # 获取表列表
        result = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in result['data']]
        
        return {
            'databases': [os.path.basename(connection.conn_info.get('file_path', ''))],
            'tables': tables,
            'version': self._get_sqlite_version(connection)
        }
        
    def _get_sqlite_version(self, connection: DatabaseConnection) -> str:
        """获取SQLite版本"""
        try:
            result = connection.execute("SELECT sqlite_version()")
            return result['data'][0][0] if result['data'] else 'Unknown'
        except Exception:
            return 'Unknown'
            
    def _get_sqlserver_info(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """获取SQL Server数据库信息"""
        # TODO: 实现SQL Server信息获取
        return {'databases': [], 'tables': [], 'version': 'Unknown'}
        
    def _get_oracle_info(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """获取Oracle数据库信息"""
        # TODO: 实现Oracle信息获取
        return {'databases': [], 'tables': [], 'version': 'Unknown'}