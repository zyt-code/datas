#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL查询执行器
"""

import re
import time
from typing import Dict, List, Any, Optional, Tuple
from PySide6.QtCore import QObject, Signal, QThread

class QueryThread(QThread):
    """查询执行线程"""
    
    # 信号定义
    query_started = Signal(str)  # 查询开始
    query_progress = Signal(str)  # 查询进度
    query_finished = Signal(dict)  # 查询完成
    query_error = Signal(str)  # 查询错误
    
    def __init__(self, connection, sql, params=None):
        super().__init__()
        self.connection = connection
        self.sql = sql
        self.params = params
        self.is_cancelled = False
        
    def run(self):
        """执行查询"""
        try:
            self.query_started.emit("开始执行查询...")
            start_time = time.time()
            
            # 分割SQL语句
            statements = self._split_sql_statements(self.sql)
            results = []
            
            for i, statement in enumerate(statements):
                if self.is_cancelled:
                    break
                    
                statement = statement.strip()
                if not statement:
                    continue
                    
                self.query_progress.emit(f"执行第 {i+1}/{len(statements)} 条语句...")
                
                try:
                    result = self.connection.execute(statement, self.params)
                    result['sql'] = statement
                    result['execution_time'] = time.time() - start_time
                    results.append(result)
                except Exception as e:
                    error_result = {
                        'error': str(e),
                        'sql': statement,
                        'execution_time': time.time() - start_time
                    }
                    results.append(error_result)
                    
            total_time = time.time() - start_time
            
            final_result = {
                'results': results,
                'total_time': total_time,
                'statement_count': len(statements)
            }
            
            self.query_finished.emit(final_result)
            
        except Exception as e:
            self.query_error.emit(str(e))
            
    def cancel(self):
        """取消查询"""
        self.is_cancelled = True
        
    def _split_sql_statements(self, sql: str) -> List[str]:
        """分割SQL语句"""
        # 简单的SQL语句分割，以分号为分隔符
        # 注意：这个实现比较简单，不处理字符串中的分号
        statements = []
        current_statement = ""
        in_string = False
        string_char = None
        
        i = 0
        while i < len(sql):
            char = sql[i]
            
            if not in_string:
                if char in ("'", '"'):
                    in_string = True
                    string_char = char
                elif char == ';':
                    if current_statement.strip():
                        statements.append(current_statement.strip())
                    current_statement = ""
                    i += 1
                    continue
            else:
                if char == string_char:
                    # 检查是否是转义的引号
                    if i + 1 < len(sql) and sql[i + 1] == string_char:
                        current_statement += char + char
                        i += 2
                        continue
                    else:
                        in_string = False
                        string_char = None
                        
            current_statement += char
            i += 1
            
        # 添加最后一个语句
        if current_statement.strip():
            statements.append(current_statement.strip())
            
        return statements

class QueryExecutor(QObject):
    """查询执行器"""
    
    # 信号定义
    query_started = Signal(str)
    query_progress = Signal(str)
    query_finished = Signal(dict)
    query_error = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.current_thread = None
        self.query_history = []
        self.max_history = 100
        
    def execute(self, connection, sql: str, params=None) -> Dict[str, Any]:
        """同步执行查询"""
        start_time = time.time()
        
        try:
            # 预处理SQL
            sql = self._preprocess_sql(sql)
            
            # 验证SQL
            validation_result = self._validate_sql(sql)
            if not validation_result['valid']:
                raise ValueError(validation_result['message'])
                
            # 执行查询
            result = connection.execute(sql, params)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 添加执行时间到结果中
            if isinstance(result, dict):
                result['execution_time'] = execution_time
                result['sql'] = sql
            
            # 添加到查询历史
            self._add_to_history(sql, result, execution_time)
            
            return result
            
        except Exception as e:
            error_result = {
                'error': str(e),
                'sql': sql,
                'execution_time': time.time() - start_time
            }
            self._add_to_history(sql, error_result, time.time() - start_time)
            raise e
            
    def execute_async(self, connection, sql: str, params=None):
        """异步执行查询"""
        # 停止当前查询（如果有）
        self.stop_query()
        
        # 创建新的查询线程
        self.current_thread = QueryThread(connection, sql, params)
        
        # 连接信号
        self.current_thread.query_started.connect(self.query_started)
        self.current_thread.query_progress.connect(self.query_progress)
        self.current_thread.query_finished.connect(self._on_async_query_finished)
        self.current_thread.query_error.connect(self.query_error)
        
        # 启动线程
        self.current_thread.start()
        
    def stop_query(self):
        """停止当前查询"""
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.cancel()
            self.current_thread.wait(5000)  # 等待5秒
            if self.current_thread.isRunning():
                self.current_thread.terminate()
            self.current_thread = None
            
    def _on_async_query_finished(self, result):
        """异步查询完成处理"""
        # 添加到历史记录
        for stmt_result in result.get('results', []):
            self._add_to_history(
                stmt_result.get('sql', ''),
                stmt_result,
                stmt_result.get('execution_time', 0)
            )
            
        self.query_finished.emit(result)
        self.current_thread = None
        
    def _preprocess_sql(self, sql: str) -> str:
        """预处理SQL语句"""
        # 移除多余的空白字符
        sql = re.sub(r'\s+', ' ', sql.strip())
        
        # 移除SQL注释
        # 移除单行注释 --
        sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)
        
        # 移除多行注释 /* */
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        return sql.strip()
        
    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """验证SQL语句"""
        if not sql.strip():
            return {'valid': False, 'message': 'SQL语句不能为空'}
            
        # 检查危险操作
        dangerous_patterns = [
            r'\bDROP\s+DATABASE\b',
            r'\bDROP\s+SCHEMA\b',
            r'\bTRUNCATE\s+TABLE\b',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                return {
                    'valid': False,
                    'message': f'检测到危险操作，请确认后再执行'
                }
                
        return {'valid': True, 'message': ''}
        
    def _add_to_history(self, sql: str, result: Dict[str, Any], execution_time: float):
        """添加到查询历史"""
        history_item = {
            'sql': sql,
            'result': result,
            'execution_time': execution_time,
            'timestamp': time.time(),
            'success': 'error' not in result
        }
        
        self.query_history.insert(0, history_item)
        
        # 限制历史记录数量
        if len(self.query_history) > self.max_history:
            self.query_history = self.query_history[:self.max_history]
            
    def get_query_history(self) -> List[Dict[str, Any]]:
        """获取查询历史"""
        return self.query_history.copy()
        
    def clear_history(self):
        """清空查询历史"""
        self.query_history.clear()
        
    def explain_query(self, connection, sql: str) -> Dict[str, Any]:
        """解释查询执行计划"""
        try:
            db_type = connection.db_type.lower()
            
            if db_type == 'mysql':
                explain_sql = f"EXPLAIN {sql}"
            elif db_type == 'postgresql':
                explain_sql = f"EXPLAIN ANALYZE {sql}"
            elif db_type == 'sqlite':
                explain_sql = f"EXPLAIN QUERY PLAN {sql}"
            else:
                raise ValueError(f"不支持的数据库类型: {db_type}")
                
            return connection.execute(explain_sql)
            
        except Exception as e:
            raise Exception(f"获取执行计划失败: {str(e)}")
            
    def format_sql(self, sql: str) -> str:
        """格式化SQL语句"""
        # 简单的SQL格式化
        sql = self._preprocess_sql(sql)
        
        # 关键字大写
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW',
            'DATABASE', 'SCHEMA', 'PRIMARY', 'KEY', 'FOREIGN',
            'REFERENCES', 'CONSTRAINT', 'NOT', 'NULL', 'UNIQUE',
            'DEFAULT', 'AUTO_INCREMENT', 'INT', 'INTEGER', 'VARCHAR',
            'CHAR', 'TEXT', 'DATE', 'TIME', 'DATETIME', 'TIMESTAMP',
            'DECIMAL', 'FLOAT', 'DOUBLE', 'BOOLEAN',
            'AND', 'OR', 'IN', 'LIKE', 'BETWEEN', 'IS', 'EXISTS',
            'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
            'UNION', 'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT',
            'OFFSET', 'DISTINCT', 'AS', 'ASC', 'DESC',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
        ]
        
        for keyword in keywords:
            pattern = r'\b' + keyword.lower() + r'\b'
            sql = re.sub(pattern, keyword, sql, flags=re.IGNORECASE)
            
        # 添加换行和缩进
        sql = re.sub(r'\bSELECT\b', '\nSELECT', sql)
        sql = re.sub(r'\bFROM\b', '\nFROM', sql)
        sql = re.sub(r'\bWHERE\b', '\nWHERE', sql)
        sql = re.sub(r'\bGROUP BY\b', '\nGROUP BY', sql)
        sql = re.sub(r'\bORDER BY\b', '\nORDER BY', sql)
        sql = re.sub(r'\bHAVING\b', '\nHAVING', sql)
        sql = re.sub(r'\bLIMIT\b', '\nLIMIT', sql)
        
        # 清理多余的空行
        lines = [line.strip() for line in sql.split('\n') if line.strip()]
        
        return '\n'.join(lines)
        
    def get_query_statistics(self) -> Dict[str, Any]:
        """获取查询统计信息"""
        if not self.query_history:
            return {
                'total_queries': 0,
                'successful_queries': 0,
                'failed_queries': 0,
                'average_execution_time': 0,
                'total_execution_time': 0
            }
            
        total_queries = len(self.query_history)
        successful_queries = sum(1 for item in self.query_history if item['success'])
        failed_queries = total_queries - successful_queries
        
        execution_times = [item['execution_time'] for item in self.query_history]
        total_execution_time = sum(execution_times)
        average_execution_time = total_execution_time / total_queries if total_queries > 0 else 0
        
        return {
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'failed_queries': failed_queries,
            'average_execution_time': average_execution_time,
            'total_execution_time': total_execution_time,
            'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0
        }