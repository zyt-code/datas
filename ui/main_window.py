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
    QComboBox, QPushButton, QTextBrowser, QApplication
)
from PySide6.QtCore import Qt, QTimer, Signal, QSysInfo
from PySide6.QtGui import QIcon, QKeySequence, QFont, QAction, QClipboard
import platform
import sys
from datetime import datetime

from .connection_dialog import ConnectionDialog
from .sql_editor import SQLEditor
from .table_viewer import TableViewer
from .query_result import QueryResult
from .query_tabs import QueryTabWidget
from database.connection_manager import ConnectionManager
from database.query_executor import QueryExecutor
from database.connection_config import ConnectionConfig
from config_manager import config

class AboutDialog(QDialog):
    """关于对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"关于 {config.get_app_name()}")
        width, height = config.get_about_dialog_size()
        self.setFixedSize(width, height)
        self.setModal(True)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建文本浏览器显示版本信息
        self.text_browser = QTextBrowser()
        self.text_browser.setReadOnly(True)
        self.text_browser.setHtml(self.get_version_info())
        layout.addWidget(self.text_browser)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 复制按钮
        copy_button = QPushButton("复制")
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)
        
        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
    def get_version_info(self):
        """获取版本信息"""
        # 获取系统信息
        system_info = platform.system()
        system_version = platform.release()
        machine = platform.machine()
        processor = platform.processor()
        
        # 获取Python版本
        python_version = sys.version.split()[0]
        
        # 获取PySide6版本
        try:
            import PySide6
            pyside_version = PySide6.__version__
        except:
            pyside_version = "未知"
            
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取屏幕信息
        app = QApplication.instance()
        if app:
            screens = app.screens()
            screen_info = ""
            for i, screen in enumerate(screens):
                geometry = screen.geometry()
                dpr = screen.devicePixelRatio()
                if i == 0:
                    screen_info += f"({geometry.width()}x{geometry.height()})"
                    if dpr > 1:
                        screen_info += "/Retina"
                else:
                    screen_info += f", *({geometry.width()}x{geometry.height()})"
        else:
            screen_info = "未知"
            
        # 获取配置信息
        app_name = config.get_app_name()
        app_description = config.get_app_description()
        app_version = config.get_app_version()
        build_number = config.get_build_number()
        build_id = config.get_build_id()
        app_language = config.get_app_language()
        colors = config.get_about_colors()
        
        # 构建版本信息HTML
        html = f"""
        <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; font-size: 12px; }}
        .title {{ font-size: 16px; font-weight: bold; color: {colors['title_color']}; margin-bottom: 15px; }}
        .info-line {{ margin: 3px 0; }}
        .label {{ font-weight: bold; color: {colors['label_color']}; }}
        </style>
        
        <div class="title">{app_name} - {app_description}</div>
        
        <div class="info-line"><span class="label">设备类型：</span>{machine}</div>
        <div class="info-line"><span class="label">系统版本：</span>{system_info} {system_version}</div>
        <div class="info-line"><span class="label">系统语言：</span>zh-Hans</div>
        <div class="info-line"><span class="label">应用版本：</span>[{current_time}] v{app_version} ({build_number}) #{build_id}</div>
        <div class="info-line"><span class="label">应用语言：</span>{app_language}</div>
        <div class="info-line"><span class="label">Python版本：</span>{python_version}</div>
        <div class="info-line"><span class="label">PySide6版本：</span>{pyside_version}</div>
        <div class="info-line"><span class="label">处理器：</span>{processor}</div>
        <div class="info-line"><span class="label">显示器：</span>{screen_info}</div>
        <div class="info-line"><span class="label">构建时间：</span>{current_time}</div>
        """
        
        return html
        
    def get_plain_text_info(self):
        """获取纯文本版本信息用于复制"""
        # 获取系统信息
        system_info = platform.system()
        system_version = platform.release()
        machine = platform.machine()
        processor = platform.processor()
        
        # 获取Python版本
        python_version = sys.version.split()[0]
        
        # 获取PySide6版本
        try:
            import PySide6
            pyside_version = PySide6.__version__
        except:
            pyside_version = "未知"
            
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取屏幕信息
        app = QApplication.instance()
        if app:
            screens = app.screens()
            screen_info = ""
            for i, screen in enumerate(screens):
                geometry = screen.geometry()
                dpr = screen.devicePixelRatio()
                if i == 0:
                    screen_info += f"({geometry.width()}x{geometry.height()})"
                    if dpr > 1:
                        screen_info += "/Retina"
                else:
                    screen_info += f", *({geometry.width()}x{geometry.height()})"
        else:
            screen_info = "未知"
            
        # 获取配置信息
        app_version = config.get_app_version()
        build_number = config.get_build_number()
        build_id = config.get_build_id()
        app_language = config.get_app_language()
        
        # 构建纯文本信息
        text = f"""设备类型：{machine}
系统版本：{system_info} {system_version}
系统语言：zh-Hans
应用版本：[{current_time}] v{app_version} ({build_number}) #{build_id}
应用语言：{app_language}
Python版本：{python_version}
PySide6版本：{pyside_version}
处理器：{processor}
显示器：{screen_info}
构建时间：{current_time}"""
        
        return text
        
    def copy_to_clipboard(self):
        """复制版本信息到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.get_plain_text_info())
        
        # 显示复制成功提示
        QMessageBox.information(self, "复制成功", "版本信息已复制到剪贴板")

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
        self.setWindowTitle(config.get_window_title())
        width, height = config.get_window_size()
        self.setGeometry(100, 100, width, height)
        
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
        execute_action.triggered.connect(self.execute_current_tab_query)
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
        execute_action.triggered.connect(self.execute_current_tab_query)
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
        
        # 创建查询标签页管理器
        self.query_tabs = QueryTabWidget()
        self.query_tabs.execute_requested.connect(self.execute_query_from_tab)
        right_layout.addWidget(self.query_tabs)
        
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
        
        # 更新标签页连接列表
        self.update_tab_connections()
        
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
                # 将连接保存到树形控件项目中
                root = self.connection_tree.invisibleRootItem()
                for i in range(root.childCount()):
                    item = root.child(i)
                    item_conn_info = item.data(0, Qt.UserRole)
                    if item_conn_info and item_conn_info.get('name') == conn_info['name']:
                        item.connection = connection
                        break
                        
                self.current_connection = connection
                self.status_bar.showMessage(f"已连接到 {conn_info['name']}")
                self.load_database_structure()
                
                # 更新所有标签页的连接列表
                self.update_tab_connections()
            else:
                QMessageBox.warning(self, "连接失败", "无法连接到数据库")
        except Exception as e:
            QMessageBox.critical(self, "连接错误", f"连接数据库时发生错误：{str(e)}")
            
    def load_database_structure(self):
        """加载数据库结构"""
        # TODO: 实现数据库结构加载
        pass
        
    def update_tab_connections(self):
        """更新所有标签页的连接列表"""
        # 获取所有连接名称
        connections = []
        root = self.connection_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            conn_info = item.data(0, Qt.UserRole)
            if conn_info:
                connections.append(conn_info.get('name', ''))
                
        # 更新标签页连接列表
        self.query_tabs.update_connections(connections)
        
    def execute_current_tab_query(self):
        """执行当前标签页的查询"""
        current_tab = self.query_tabs.get_current_tab()
        if current_tab:
            current_tab.execute_query()
        
    def execute_query_from_tab(self, connection_name, database_name, sql, is_user_query=True):
        """从标签页执行查询"""
        try:
            # 获取指定的连接
            connection = self.get_connection_by_name(connection_name)
            if not connection:
                error_msg = f"连接 '{connection_name}' 不存在或未连接"
                self.query_tabs.display_message(error_msg)
                QMessageBox.warning(self, "警告", error_msg)
                return
                
            # 显示执行状态（仅用户查询显示）
            if is_user_query:
                self.status_bar.showMessage("正在执行查询...")
                self.query_tabs.display_message(f"执行SQL: {sql[:100]}{'...' if len(sql) > 100 else ''}")
            
            # 执行查询
            result = self.query_executor.execute(connection, sql)
            
            # 特殊处理SHOW DATABASES查询
            if sql.strip().upper().startswith('SHOW DATABASES'):
                if 'data' in result:
                    databases = [str(row[0]) for row in result['data'] if row]
                    self.query_tabs.update_database_list(databases)
                    
            # 只有用户查询才显示结果
            if is_user_query:
                # 显示结果
                self.query_tabs.display_result(result)
                
                # 更新消息
                if isinstance(result, dict):
                    if 'data' in result:
                        row_count = len(result['data'])
                        self.query_tabs.display_message(f"查询执行成功，返回 {row_count} 行数据")
                    elif 'affected_rows' in result:
                        self.query_tabs.display_message(f"查询执行成功，影响 {result['affected_rows']} 行")
                    else:
                        self.query_tabs.display_message("查询执行成功")
                else:
                    self.query_tabs.display_message("查询执行成功")
                    
                self.status_bar.showMessage("查询执行完成")
            
        except Exception as e:
            error_msg = f"查询执行失败：{str(e)}"
            # 只有用户查询的错误才显示
            if is_user_query:
                self.query_tabs.display_message(error_msg)
                self.status_bar.showMessage("查询执行失败")
                QMessageBox.critical(self, "查询错误", error_msg)
            
    def get_connection_by_name(self, connection_name):
        """根据连接名称获取连接对象"""
        # 遍历连接树，查找对应的连接
        root = self.connection_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            conn_info = item.data(0, Qt.UserRole)
            if conn_info and conn_info.get('name') == connection_name:
                # 检查是否已连接
                if hasattr(item, 'connection') and item.connection:
                    return item.connection
                else:
                    # 尝试连接
                    try:
                        connection = self.connection_manager.create_connection(conn_info)
                        if connection.test_connection():
                            item.connection = connection
                            return connection
                    except Exception:
                        pass
        return None
            
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
                    current_tab = self.query_tabs.get_current_tab()
                    if current_tab:
                        current_tab.set_sql_text(content)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开文件失败：{str(e)}")
                
    def save_sql_file(self):
        """保存SQL文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存SQL文件", "", "SQL文件 (*.sql);;所有文件 (*)"
        )
        if file_path:
            try:
                current_tab = self.query_tabs.get_current_tab()
                if current_tab:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(current_tab.get_sql_text())
                    QMessageBox.information(self, "成功", "文件保存成功")
                else:
                    QMessageBox.warning(self, "警告", "没有可用的查询标签页")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败：{str(e)}")
                
    def load_saved_connections(self):
        """加载已保存的连接"""
        try:
            connections = self.connection_config.load_all_connections()
            for conn_info in connections:
                # 直接添加到树形控件，不调用add_connection_to_tree避免重复更新
                item = QTreeWidgetItem(self.connection_tree)
                item.setText(0, conn_info['name'])
                item.setData(0, Qt.UserRole, conn_info)
                
            # 一次性更新标签页连接列表
            self.update_tab_connections()
                
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
                        
                # 更新标签页连接列表
                self.update_tab_connections()
                        
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
        dialog = AboutDialog(self)
        dialog.exec()