#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口类
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QToolBar, QStatusBar, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QTableWidget, QMessageBox,
    QFileDialog, QInputDialog, QDialog, QMenu, QLabel,
    QComboBox, QPushButton
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QKeySequence, QFont, QAction

from .connection_dialog import ConnectionDialog
from .sql_editor import SQLEditor
from .table_viewer import TableViewer
from .query_result import QueryResult
from database.connection_manager import ConnectionManager
from database.query_executor import QueryExecutor
from database.connection_config import ConnectionConfig

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.connection_manager = ConnectionManager()
        self.query_executor = QueryExecutor()
        self.connection_config = ConnectionConfig()
        self.current_connection = None
        
        self.init_ui()
        self.setup_connections()
        self.load_saved_connections()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("PySide6 Navicat - 数据库管理工具")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 创建中央部件
        self.create_central_widget()
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_connection_action = QAction("新建连接(&N)", self)
        new_connection_action.setShortcut(QKeySequence.New)
        new_connection_action.triggered.connect(self.new_connection)
        file_menu.addAction(new_connection_action)
        
        file_menu.addSeparator()
        
        open_sql_action = QAction("打开SQL文件(&O)", self)
        open_sql_action.setShortcut(QKeySequence.Open)
        open_sql_action.triggered.connect(self.open_sql_file)
        file_menu.addAction(open_sql_action)
        
        save_sql_action = QAction("保存SQL文件(&S)", self)
        save_sql_action.setShortcut(QKeySequence.Save)
        save_sql_action.triggered.connect(self.save_sql_file)
        file_menu.addAction(save_sql_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        # 查询菜单
        query_menu = menubar.addMenu("查询(&Q)")
        
        execute_action = QAction("执行查询(&E)", self)
        execute_action.setShortcut("F5")
        execute_action.triggered.connect(self.execute_query)
        query_menu.addAction(execute_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 新建连接
        new_conn_action = QAction("新建连接", self)
        new_conn_action.triggered.connect(self.new_connection)
        toolbar.addAction(new_conn_action)
        
        toolbar.addSeparator()
        
        # 执行查询
        execute_action = QAction("执行查询", self)
        execute_action.triggered.connect(self.execute_query)
        toolbar.addAction(execute_action)
        
        # 停止查询
        stop_action = QAction("停止查询", self)
        stop_action.triggered.connect(self.stop_query)
        toolbar.addAction(stop_action)
        
    def create_central_widget(self):
        """创建中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # 左侧面板 - 连接和数据库结构
        self.create_left_panel(main_splitter)
        
        # 右侧面板 - SQL编辑器和结果
        self.create_right_panel(main_splitter)
        
        # 设置分割器比例
        main_splitter.setSizes([300, 1100])
        
    def create_left_panel(self, parent):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 连接树
        self.connection_tree = QTreeWidget()
        self.connection_tree.setHeaderLabel("数据库连接")
        self.connection_tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        self.connection_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connection_tree.customContextMenuRequested.connect(self.show_connection_context_menu)
        left_layout.addWidget(self.connection_tree)
        
        parent.addWidget(left_widget)
        
    def create_right_panel(self, parent):
        """创建右侧面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 创建工具栏
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # 数据库选择下拉框
        toolbar_layout.addWidget(QLabel("数据库:"))
        
        self.database_combo = QComboBox()
        self.database_combo.setMinimumWidth(150)
        self.database_combo.addItem("请选择数据库")
        self.database_combo.currentTextChanged.connect(self.on_database_changed)
        toolbar_layout.addWidget(self.database_combo)
        
        # 刷新数据库列表按钮
        refresh_db_btn = QPushButton("刷新")
        refresh_db_btn.clicked.connect(self.refresh_database_list)
        toolbar_layout.addWidget(refresh_db_btn)
        
        # 添加弹性空间
        toolbar_layout.addStretch()
        
        # 执行按钮
        execute_btn = QPushButton("执行 (F5)")
        execute_btn.clicked.connect(self.execute_query)
        execute_btn.setShortcut(QKeySequence("F5"))
        toolbar_layout.addWidget(execute_btn)
        
        right_layout.addWidget(toolbar_widget)
        
        # 创建垂直分割器
        right_splitter = QSplitter(Qt.Vertical)
        right_layout.addWidget(right_splitter)
        
        # SQL编辑器
        self.sql_editor = SQLEditor()
        right_splitter.addWidget(self.sql_editor)
        
        # 结果标签页
        self.result_tabs = QTabWidget()
        
        # 查询结果
        self.query_result = QueryResult()
        self.result_tabs.addTab(self.query_result, "查询结果")
        
        # 消息
        self.message_text = QTextEdit()
        self.message_text.setMaximumHeight(150)
        self.result_tabs.addTab(self.message_text, "消息")
        
        right_splitter.addWidget(self.result_tabs)
        
        # 设置分割器比例
        right_splitter.setSizes([400, 500])
        
        parent.addWidget(right_widget)
        
    def setup_connections(self):
        """设置信号连接"""
        pass
        
    def new_connection(self):
        """新建数据库连接"""
        dialog = ConnectionDialog(self)
        if dialog.exec() == QDialog.Accepted:
            conn_info = dialog.get_connection_info()
            
            # 保存连接配置
            if self.connection_config.save_connection(conn_info):
                self.add_connection_to_tree(conn_info)
                self.status_bar.showMessage(f"连接 '{conn_info['name']}' 已保存")
            else:
                QMessageBox.warning(self, "保存失败", "无法保存连接配置")
                self.add_connection_to_tree(conn_info)  # 仍然添加到当前会话
            
    def add_connection_to_tree(self, conn_info):
        """添加连接到树形控件"""
        item = QTreeWidgetItem(self.connection_tree)
        item.setText(0, conn_info['name'])
        item.setData(0, Qt.UserRole, conn_info)
        
    def on_tree_item_double_clicked(self, item, column):
        """树形控件项目双击事件"""
        conn_info = item.data(0, Qt.UserRole)
        if conn_info:
            self.connect_to_database(conn_info)
            
    def connect_to_database(self, conn_info):
        """连接到数据库"""
        try:
            connection = self.connection_manager.create_connection(conn_info)
            if connection:
                self.current_connection = connection
                self.status_bar.showMessage(f"已连接到 {conn_info['name']}")
                self.load_database_structure()
                # 自动刷新数据库列表
                self.refresh_database_list()
            else:
                QMessageBox.warning(self, "连接失败", "无法连接到数据库")
        except Exception as e:
            QMessageBox.critical(self, "连接错误", f"连接数据库时发生错误：{str(e)}")
            
    def load_database_structure(self):
        """加载数据库结构"""
        # TODO: 实现数据库结构加载
        pass
        
    def execute_query(self):
        """执行查询"""
        if not self.current_connection:
            QMessageBox.warning(self, "警告", "请先连接到数据库")
            return
            
        sql = self.sql_editor.get_selected_text() or self.sql_editor.toPlainText()
        if not sql.strip():
            QMessageBox.warning(self, "警告", "请输入SQL语句")
            return
            
        try:
            # 显示执行状态
            self.status_bar.showMessage("正在执行查询...")
            self.message_text.append(f"执行SQL: {sql[:100]}{'...' if len(sql) > 100 else ''}")
            
            # 执行查询
            result = self.query_executor.execute(self.current_connection, sql)
            

            
            # 显示结果
            self.query_result.display_result(result)
            
            # 更新消息
            if isinstance(result, dict):
                if 'data' in result:
                    row_count = len(result['data'])
                    self.message_text.append(f"查询执行成功，返回 {row_count} 行数据")
                elif 'affected_rows' in result:
                    self.message_text.append(f"查询执行成功，影响 {result['affected_rows']} 行")
                else:
                    self.message_text.append("查询执行成功")
            else:
                self.message_text.append("查询执行成功")
                
            self.status_bar.showMessage("查询执行完成")
            
        except Exception as e:
            error_msg = f"查询执行失败：{str(e)}"
            self.message_text.append(error_msg)
            self.status_bar.showMessage("查询执行失败")
            QMessageBox.critical(self, "查询错误", error_msg)
            
    def stop_query(self):
        """停止查询"""
        # TODO: 实现查询停止功能
        pass
        
    def open_sql_file(self):
        """打开SQL文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开SQL文件", "", "SQL文件 (*.sql);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.sql_editor.setPlainText(content)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开文件失败：{str(e)}")
                
    def save_sql_file(self):
        """保存SQL文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存SQL文件", "", "SQL文件 (*.sql);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.sql_editor.toPlainText())
                QMessageBox.information(self, "成功", "文件保存成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败：{str(e)}")
                
    def load_saved_connections(self):
        """加载已保存的连接"""
        try:
            connections = self.connection_config.load_all_connections()
            for conn_info in connections:
                self.add_connection_to_tree(conn_info)
                
            if connections:
                self.status_bar.showMessage(f"已加载 {len(connections)} 个保存的连接")
            else:
                self.status_bar.showMessage("未找到保存的连接")
                
        except Exception as e:
            QMessageBox.warning(self, "加载连接失败", f"无法加载保存的连接：{str(e)}")
            
    def delete_connection(self, connection_name: str):
        """删除连接"""
        try:
            if self.connection_config.delete_connection(connection_name):
                # 从树形控件中移除
                root = self.connection_tree.invisibleRootItem()
                for i in range(root.childCount()):
                    item = root.child(i)
                    conn_info = item.data(0, Qt.UserRole)
                    if conn_info and conn_info.get('name') == connection_name:
                        root.removeChild(item)
                        break
                        
                self.status_bar.showMessage(f"连接 '{connection_name}' 已删除")
                return True
            else:
                QMessageBox.warning(self, "删除失败", "无法删除连接配置")
                return False
                
        except Exception as e:
            QMessageBox.critical(self, "删除错误", f"删除连接时发生错误：{str(e)}")
            return False
            
    def show_connection_context_menu(self, position):
        """显示连接右键菜单"""
        item = self.connection_tree.itemAt(position)
        if not item:
            return
            
        conn_info = item.data(0, Qt.UserRole)
        if not conn_info:
            return
            
        menu = QMenu(self)
        
        # 连接/断开连接
        if self.current_connection:
            disconnect_action = QAction("断开连接", self)
            disconnect_action.triggered.connect(lambda: self.disconnect_from_database())
            menu.addAction(disconnect_action)
        else:
            connect_action = QAction("连接", self)
            connect_action.triggered.connect(lambda: self.connect_to_database(conn_info))
            menu.addAction(connect_action)
            
        menu.addSeparator()
        
        # 编辑连接
        edit_action = QAction("编辑连接", self)
        edit_action.triggered.connect(lambda: self.edit_connection(conn_info))
        menu.addAction(edit_action)
        
        # 删除连接
        delete_action = QAction("删除连接", self)
        delete_action.triggered.connect(lambda: self.confirm_delete_connection(conn_info['name']))
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # 复制连接
        copy_action = QAction("复制连接", self)
        copy_action.triggered.connect(lambda: self.copy_connection(conn_info))
        menu.addAction(copy_action)
        
        menu.exec(self.connection_tree.mapToGlobal(position))
        
    def disconnect_from_database(self):
        """断开数据库连接"""
        if self.current_connection:
            try:
                self.current_connection.close()
                self.current_connection = None
                self.status_bar.showMessage("已断开数据库连接")
            except Exception as e:
                QMessageBox.warning(self, "断开连接失败", f"断开连接时发生错误：{str(e)}")
                
    def edit_connection(self, conn_info):
        """编辑连接"""
        dialog = ConnectionDialog(self)
        
        # 填充现有连接信息
        dialog.name_edit.setText(conn_info.get('name', ''))
        
        # 设置数据库类型
        db_type = conn_info.get('type', 'MySQL')
        index = dialog.db_type_combo.findText(db_type)
        if index >= 0:
            dialog.db_type_combo.setCurrentIndex(index)
            
        # 根据数据库类型填充相应字段
        if db_type == 'SQLite':
            dialog.file_path_edit.setText(conn_info.get('file_path', ''))
        else:
            dialog.host_edit.setText(conn_info.get('host', ''))
            dialog.port_spin.setValue(conn_info.get('port', 3306))
            dialog.database_edit.setText(conn_info.get('database', ''))
            dialog.username_edit.setText(conn_info.get('username', ''))
            if conn_info.get('save_password', False):
                dialog.password_edit.setText(conn_info.get('password', ''))
                
        # 高级设置
        dialog.timeout_spin.setValue(conn_info.get('timeout', 30))
        dialog.charset_combo.setCurrentText(conn_info.get('charset', 'utf8mb4'))
        dialog.ssl_check.setChecked(conn_info.get('ssl', False))
        dialog.auto_connect_check.setChecked(conn_info.get('auto_connect', False))
        dialog.save_password_check.setChecked(conn_info.get('save_password', True))
        
        if dialog.exec() == QDialog.Accepted:
            new_conn_info = dialog.get_connection_info()
            
            # 更新连接配置
            if self.connection_config.update_connection(conn_info['name'], new_conn_info):
                # 更新树形控件中的显示
                root = self.connection_tree.invisibleRootItem()
                for i in range(root.childCount()):
                    item = root.child(i)
                    if item.data(0, Qt.UserRole) == conn_info:
                        item.setText(0, new_conn_info['name'])
                        item.setData(0, Qt.UserRole, new_conn_info)
                        break
                        
                self.status_bar.showMessage(f"连接 '{new_conn_info['name']}' 已更新")
            else:
                QMessageBox.warning(self, "更新失败", "无法更新连接配置")
                
    def confirm_delete_connection(self, connection_name):
        """确认删除连接"""
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除连接 '{connection_name}' 吗？\n此操作无法撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_connection(connection_name)
            
    def copy_connection(self, conn_info):
        """复制连接"""
        dialog = ConnectionDialog(self)
        
        # 复制连接信息，但修改名称
        new_conn_info = conn_info.copy()
        new_conn_info['name'] = f"{conn_info['name']}_副本"
        
        # 填充连接信息
        dialog.name_edit.setText(new_conn_info['name'])
        
        # 设置数据库类型
        db_type = new_conn_info.get('type', 'MySQL')
        index = dialog.db_type_combo.findText(db_type)
        if index >= 0:
            dialog.db_type_combo.setCurrentIndex(index)
            
        # 根据数据库类型填充相应字段
        if db_type == 'SQLite':
            dialog.file_path_edit.setText(new_conn_info.get('file_path', ''))
        else:
            dialog.host_edit.setText(new_conn_info.get('host', ''))
            dialog.port_spin.setValue(new_conn_info.get('port', 3306))
            
    def refresh_database_list(self):
        """刷新数据库列表"""
        if not self.current_connection:
            QMessageBox.warning(self, "警告", "请先连接到数据库服务器")
            return
            
        try:
            # 执行 SHOW DATABASES 查询
            result = self.current_connection.execute("SHOW DATABASES")
            
            # 清空当前下拉框
            self.database_combo.clear()
            self.database_combo.addItem("请选择数据库")
            
            # 添加数据库到下拉框
            if 'data' in result:
                for row in result['data']:
                    if row:  # 确保行不为空
                        database_name = str(row[0])  # 数据库名通常在第一列
                        self.database_combo.addItem(database_name)
                        
            self.status_bar.showMessage(f"已刷新数据库列表，找到 {len(result.get('data', []))} 个数据库")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新数据库列表失败：{str(e)}")
            self.status_bar.showMessage("刷新数据库列表失败")
            
    def on_database_changed(self, database_name):
        """数据库选择改变时的处理"""
        if database_name == "请选择数据库" or not database_name:
            return
            
        if not self.current_connection:
            QMessageBox.warning(self, "警告", "请先连接到数据库服务器")
            return
            
        try:
            # 切换到选定的数据库
            self.current_connection.execute(f"USE `{database_name}`")
            self.status_bar.showMessage(f"已切换到数据库: {database_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"切换数据库失败：{str(e)}")
            self.status_bar.showMessage("切换数据库失败")
            dialog.database_edit.setText(new_conn_info.get('database', ''))
            dialog.username_edit.setText(new_conn_info.get('username', ''))
            # 不复制密码
            dialog.password_edit.setText('')
                
        # 高级设置
        dialog.timeout_spin.setValue(new_conn_info.get('timeout', 30))
        dialog.charset_combo.setCurrentText(new_conn_info.get('charset', 'utf8mb4'))
        dialog.ssl_check.setChecked(new_conn_info.get('ssl', False))
        dialog.auto_connect_check.setChecked(new_conn_info.get('auto_connect', False))
        dialog.save_password_check.setChecked(False)  # 默认不保存密码
        
        if dialog.exec() == QDialog.Accepted:
            final_conn_info = dialog.get_connection_info()
            
            # 保存新连接
            if self.connection_config.save_connection(final_conn_info):
                self.add_connection_to_tree(final_conn_info)
                self.status_bar.showMessage(f"连接 '{final_conn_info['name']}' 已复制")
            else:
                QMessageBox.warning(self, "复制失败", "无法保存复制的连接配置")
                
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于", 
            "PySide6 Navicat Clone\n\n"
            "一个基于PySide6的数据库管理工具\n"
            "版本: 1.0.0\n\n"
            "支持MySQL、PostgreSQL、SQLite等数据库"
        )