#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL编辑器组件
"""

from PySide6.QtWidgets import QTextEdit, QCompleter
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
    QTextCursor, QKeySequence
)
import re

class SQLSyntaxHighlighter(QSyntaxHighlighter):
    """SQL语法高亮器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # 关键字格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))  # 蓝色
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        # SQL关键字
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW',
            'DATABASE', 'SCHEMA', 'PRIMARY', 'KEY', 'FOREIGN',
            'REFERENCES', 'CONSTRAINT', 'NOT', 'NULL', 'UNIQUE',
            'DEFAULT', 'AUTO_INCREMENT', 'INT', 'INTEGER', 'VARCHAR',
            'CHAR', 'TEXT', 'DATE', 'TIME', 'DATETIME', 'TIMESTAMP',
            'DECIMAL', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'BOOL',
            'AND', 'OR', 'IN', 'LIKE', 'BETWEEN', 'IS', 'EXISTS',
            'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
            'UNION', 'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT',
            'OFFSET', 'DISTINCT', 'AS', 'ASC', 'DESC', 'COUNT',
            'SUM', 'AVG', 'MIN', 'MAX', 'CASE', 'WHEN', 'THEN',
            'ELSE', 'END', 'IF', 'IFNULL', 'COALESCE'
        ]
        
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            rule = (re.compile(pattern, re.IGNORECASE), keyword_format)
            self.highlighting_rules.append(rule)
            
        # 字符串格式
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(0, 128, 0))  # 绿色
        
        # 单引号字符串
        rule = (re.compile(r"'[^']*'"), string_format)
        self.highlighting_rules.append(rule)
        
        # 双引号字符串
        rule = (re.compile(r'"[^"]*"'), string_format)
        self.highlighting_rules.append(rule)
        
        # 数字格式
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(255, 0, 0))  # 红色
        
        rule = (re.compile(r'\b\d+(\.\d+)?\b'), number_format)
        self.highlighting_rules.append(rule)
        
        # 注释格式
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # 灰色
        comment_format.setFontItalic(True)
        
        # 单行注释
        rule = (re.compile(r'--[^\n]*'), comment_format)
        self.highlighting_rules.append(rule)
        
        # 多行注释
        self.comment_start_expression = re.compile(r'/\*')
        self.comment_end_expression = re.compile(r'\*/')
        self.comment_format = comment_format
        
    def highlightBlock(self, text):
        """高亮文本块"""
        # 应用单行规则
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)
                
        # 处理多行注释
        self.setCurrentBlockState(0)
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_match = self.comment_start_expression.search(text)
            start_index = start_match.start() if start_match else -1
            
        while start_index >= 0:
            end_match = self.comment_end_expression.search(text, start_index)
            if end_match:
                length = end_match.end() - start_index
                self.setFormat(start_index, length, self.comment_format)
                start_match = self.comment_start_expression.search(text, end_match.end())
                start_index = start_match.start() if start_match else -1
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start_index, len(text) - start_index, self.comment_format)
                break

class SQLEditor(QTextEdit):
    """SQL编辑器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_editor()
        self.setup_completer()
        
    def init_editor(self):
        """初始化编辑器"""
        # 设置字体
        font = QFont("Consolas", 12)
        if not font.exactMatch():
            font = QFont("Monaco", 12)
        if not font.exactMatch():
            font = QFont("Courier New", 12)
        self.setFont(font)
        
        # 设置语法高亮
        self.highlighter = SQLSyntaxHighlighter(self.document())
        
        # 设置占位符文本
        self.setPlaceholderText("在此输入SQL语句...\n\n快捷键：\nF5 - 执行查询\nCtrl+/ - 注释/取消注释")
        
        # 设置制表符宽度
        self.setTabStopDistance(40)
        
    def setup_completer(self):
        """设置代码补全"""
        # SQL关键字和函数
        sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW',
            'DATABASE', 'SCHEMA', 'PRIMARY KEY', 'FOREIGN KEY',
            'REFERENCES', 'CONSTRAINT', 'NOT NULL', 'UNIQUE',
            'DEFAULT', 'AUTO_INCREMENT', 'INT', 'INTEGER', 'VARCHAR',
            'CHAR', 'TEXT', 'DATE', 'TIME', 'DATETIME', 'TIMESTAMP',
            'DECIMAL', 'FLOAT', 'DOUBLE', 'BOOLEAN',
            'AND', 'OR', 'IN', 'LIKE', 'BETWEEN', 'IS', 'EXISTS',
            'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL OUTER JOIN',
            'UNION', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT',
            'OFFSET', 'DISTINCT', 'AS', 'ASC', 'DESC',
            'COUNT(*)', 'COUNT()', 'SUM()', 'AVG()', 'MIN()', 'MAX()',
            'CASE WHEN', 'THEN', 'ELSE', 'END', 'IF', 'IFNULL', 'COALESCE'
        ]
        
        # 创建补全器
        self.completer = QCompleter(sql_keywords)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)
        
    def insert_completion(self, completion):
        """插入补全文本"""
        cursor = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        cursor.movePosition(QTextCursor.Left)
        cursor.movePosition(QTextCursor.EndOfWord)
        cursor.insertText(completion[-extra:])
        self.setTextCursor(cursor)
        
    def keyPressEvent(self, event):
        """按键事件处理"""
        # 处理Tab键缩进
        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText("    ")  # 插入4个空格
            return
            
        # 处理Shift+Tab键反缩进
        if event.key() == Qt.Key_Backtab:
            cursor = self.textCursor()
            cursor.select(QTextCursor.LineUnderCursor)
            text = cursor.selectedText()
            if text.startswith("    "):
                cursor.insertText(text[4:])
            elif text.startswith("\t"):
                cursor.insertText(text[1:])
            return
            
        # 处理Ctrl+/注释切换
        if event.key() == Qt.Key_Slash and event.modifiers() == Qt.ControlModifier:
            self.toggle_comment()
            return
            
        # 处理代码补全
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return
                
        super().keyPressEvent(event)
        
        # 触发代码补全
        if event.text() and event.text().isalpha():
            self.show_completion()
            
    def show_completion(self):
        """显示代码补全"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        completion_prefix = cursor.selectedText()
        
        if len(completion_prefix) < 2:
            self.completer.popup().hide()
            return
            
        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0)
            )
            
        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(
            self.completer.popup().sizeHintForColumn(0) +
            self.completer.popup().verticalScrollBar().sizeHint().width()
        )
        self.completer.complete(cursor_rect)
        
    def toggle_comment(self):
        """切换注释"""
        cursor = self.textCursor()
        
        # 如果有选中文本，注释选中的行
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.StartOfLine)
            start_line = cursor.blockNumber()
            
            cursor.setPosition(end)
            end_line = cursor.blockNumber()
            
            # 处理多行注释
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.StartOfLine)
            
            for line_num in range(start_line, end_line + 1):
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.select(QTextCursor.LineUnderCursor)
                line_text = cursor.selectedText()
                
                if line_text.strip().startswith('--'):
                    # 取消注释
                    new_text = line_text.replace('--', '', 1)
                    cursor.insertText(new_text)
                else:
                    # 添加注释
                    cursor.insertText('--' + line_text)
                    
                cursor.movePosition(QTextCursor.NextBlock)
        else:
            # 注释当前行
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.select(QTextCursor.LineUnderCursor)
            line_text = cursor.selectedText()
            
            if line_text.strip().startswith('--'):
                # 取消注释
                new_text = line_text.replace('--', '', 1)
                cursor.insertText(new_text)
            else:
                # 添加注释
                cursor.insertText('--' + line_text)
                
    def get_selected_text(self):
        """获取选中的文本"""
        cursor = self.textCursor()
        if cursor.hasSelection():
            return cursor.selectedText()
        return ""
        
    def format_sql(self):
        """格式化SQL语句"""
        # 简单的SQL格式化
        text = self.toPlainText()
        
        # 基本格式化规则
        formatted = text.upper()
        
        # 在关键字前后添加换行
        keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING']
        for keyword in keywords:
            formatted = formatted.replace(keyword, '\n' + keyword)
            
        # 清理多余的空行
        lines = [line.strip() for line in formatted.split('\n') if line.strip()]
        formatted = '\n'.join(lines)
        
        self.setPlainText(formatted)