# -*- coding: utf-8 -*-
"""
查询标签页组件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QComboBox, QPushButton, QSplitter, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence

from .sql_editor import SQLEditor
from .query_result import QueryResult


class QueryTab(QWidget):
    """单个查询标签页"""
    
    # 信号定义
    execute_requested = Signal(str, str, str, bool)  # connection_name, database_name, sql, is_user_query
    
    def __init__(self, tab_name="查询", parent=None):
        super().__init__(parent)
        self.tab_name = tab_name
        self.current_connection = None
        self.current_database = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 创建工具栏
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # 连接选择下拉框
        toolbar_layout.addWidget(QLabel("连接:"))
        self.connection_combo = QComboBox()
        self.connection_combo.setMinimumWidth(150)
        self.connection_combo.addItem("请选择连接")
        self.connection_combo.currentTextChanged.connect(self.on_connection_changed)
        toolbar_layout.addWidget(self.connection_combo)
        
        # 数据库选择下拉框
        toolbar_layout.addWidget(QLabel("数据库:"))
        self.database_combo = QComboBox()
        self.database_combo.setMinimumWidth(150)
        self.database_combo.addItem("请选择数据库")
        self.database_combo.setEnabled(False)
        self.database_combo.currentTextChanged.connect(self.on_database_changed)
        toolbar_layout.addWidget(self.database_combo)
        
        # 刷新数据库列表按钮
        refresh_db_btn = QPushButton("刷新")
        refresh_db_btn.clicked.connect(self.refresh_database_list)
        refresh_db_btn.setEnabled(False)
        self.refresh_db_btn = refresh_db_btn
        toolbar_layout.addWidget(refresh_db_btn)
        
        # 添加弹性空间
        toolbar_layout.addStretch()
        
        # 执行按钮
        execute_btn = QPushButton("执行 (F5)")
        execute_btn.clicked.connect(self.execute_query)
        execute_btn.setShortcut(QKeySequence("F5"))
        toolbar_layout.addWidget(execute_btn)
        
        layout.addWidget(toolbar_widget)
        
        # 创建垂直分割器
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # SQL编辑器
        self.sql_editor = SQLEditor()
        splitter.addWidget(self.sql_editor)
        
        # 结果标签页
        self.result_tabs = QTabWidget()
        
        # 查询结果
        self.query_result = QueryResult()
        self.result_tabs.addTab(self.query_result, "查询结果")
        
        # 消息
        self.message_text = QTextEdit()
        self.message_text.setMaximumHeight(150)
        self.result_tabs.addTab(self.message_text, "消息")
        
        splitter.addWidget(self.result_tabs)
        
        # 设置分割器比例
        splitter.setSizes([400, 500])
        
    def update_connections(self, connections):
        """更新连接列表"""
        self.connection_combo.clear()
        self.connection_combo.addItem("请选择连接")
        
        for conn_name in connections:
            self.connection_combo.addItem(conn_name)
            
    def on_connection_changed(self, connection_name):
        """连接改变时的处理"""
        if connection_name == "请选择连接":
            self.current_connection = None
            self.database_combo.clear()
            self.database_combo.addItem("请选择数据库")
            self.database_combo.setEnabled(False)
            self.refresh_db_btn.setEnabled(False)
            return
            
        self.current_connection = connection_name
        self.database_combo.setEnabled(True)
        self.refresh_db_btn.setEnabled(True)
        
        # 自动刷新数据库列表
        self.refresh_database_list()
        
    def on_database_changed(self, database_name):
        """数据库改变时的处理"""
        if database_name == "请选择数据库":
            self.current_database = None
            return
            
        self.current_database = database_name
        
        # 如果有连接，执行USE语句切换数据库（后台查询，不显示结果）
        if self.current_connection and self.current_database:
            use_sql = f"USE `{self.current_database}`;"
            self.execute_requested.emit(self.current_connection, self.current_database, use_sql, False)
            
    def refresh_database_list(self):
        """刷新数据库列表"""
        if not self.current_connection:
            return
            
        # 发送SHOW DATABASES查询请求（后台查询，不显示结果）
        show_db_sql = "SHOW DATABASES;"
        self.execute_requested.emit(self.current_connection, "", show_db_sql, False)
        
    def update_database_list(self, databases):
        """更新数据库列表"""
        current_db = self.database_combo.currentText()
        self.database_combo.clear()
        self.database_combo.addItem("请选择数据库")
        
        for db_name in databases:
            self.database_combo.addItem(db_name)
            
        # 尝试恢复之前选择的数据库
        if current_db and current_db != "请选择数据库":
            index = self.database_combo.findText(current_db)
            if index >= 0:
                self.database_combo.setCurrentIndex(index)
                
    def execute_query(self):
        """执行查询"""
        if not self.current_connection:
            QMessageBox.warning(self, "警告", "请先选择连接")
            return
            
        sql = self.sql_editor.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "警告", "请输入SQL语句")
            return
            
        # 发送查询请求（用户主动查询，显示结果）
        database = self.current_database or ""
        self.execute_requested.emit(self.current_connection, database, sql, True)
        
    def display_result(self, result):
        """显示查询结果"""
        self.query_result.display_result(result)
        
    def display_message(self, message):
        """显示消息"""
        self.message_text.append(message)
        
    def get_sql_text(self):
        """获取SQL文本"""
        return self.sql_editor.get_text()
        
    def set_sql_text(self, text):
        """设置SQL文本"""
        self.sql_editor.set_text(text)


class QueryTabWidget(QTabWidget):
    """查询标签页管理器"""
    
    # 信号定义
    execute_requested = Signal(str, str, str, bool)  # connection_name, database_name, sql, is_user_query
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_counter = 1
        self.connections = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        
        # 添加第一个标签页
        self.add_new_tab()
        
        # 添加新建标签页按钮
        new_tab_btn = QPushButton("+")
        new_tab_btn.setMaximumSize(30, 30)
        new_tab_btn.clicked.connect(self.add_new_tab)
        self.setCornerWidget(new_tab_btn, Qt.TopRightCorner)
        
    def add_new_tab(self):
        """添加新的查询标签页"""
        tab_name = f"查询 {self.tab_counter}"
        query_tab = QueryTab(tab_name)
        query_tab.execute_requested.connect(self.execute_requested)
        
        # 更新连接列表
        query_tab.update_connections(self.connections)
        
        index = self.addTab(query_tab, tab_name)
        self.setCurrentIndex(index)
        self.tab_counter += 1
        
    def close_tab(self, index):
        """关闭标签页"""
        if self.count() <= 1:
            # 至少保留一个标签页
            return
            
        self.removeTab(index)
        
    def update_connections(self, connections):
        """更新所有标签页的连接列表"""
        self.connections = connections
        
        for i in range(self.count()):
            tab = self.widget(i)
            if isinstance(tab, QueryTab):
                tab.update_connections(connections)
                
    def get_current_tab(self):
        """获取当前标签页"""
        return self.currentWidget()
        
    def display_result(self, result):
        """在当前标签页显示查询结果"""
        current_tab = self.get_current_tab()
        if isinstance(current_tab, QueryTab):
            current_tab.display_result(result)
            
    def display_message(self, message):
        """在当前标签页显示消息"""
        current_tab = self.get_current_tab()
        if isinstance(current_tab, QueryTab):
            current_tab.display_message(message)
            
    def update_database_list(self, databases):
        """更新当前标签页的数据库列表"""
        current_tab = self.get_current_tab()
        if isinstance(current_tab, QueryTab):
            current_tab.update_database_list(databases)