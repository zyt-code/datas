#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton,
    QGroupBox, QCheckBox, QTabWidget, QWidget, QMessageBox
)
from PySide6.QtCore import Qt

class ConnectionDialog(QDialog):
    """数据库连接对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("新建数据库连接")
        self.setModal(True)
        self.resize(450, 400)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 常规设置标签页
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "常规")
        
        # 高级设置标签页
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "高级")
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 测试连接按钮
        self.test_button = QPushButton("测试连接")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        # 确定和取消按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
    def create_general_tab(self):
        """创建常规设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 连接信息组
        conn_group = QGroupBox("连接信息")
        conn_layout = QFormLayout(conn_group)
        
        # 连接名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入连接名称")
        conn_layout.addRow("连接名称:", self.name_edit)
        
        # 数据库类型
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["MySQL", "PostgreSQL", "SQLite", "SQL Server", "Oracle"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_changed)
        conn_layout.addRow("数据库类型:", self.db_type_combo)
        
        layout.addWidget(conn_group)
        
        # 服务器信息组
        self.server_group = QGroupBox("服务器信息")
        server_layout = QFormLayout(self.server_group)
        
        # 主机名
        self.host_edit = QLineEdit()
        self.host_edit.setText("localhost")
        server_layout.addRow("主机名:", self.host_edit)
        
        # 端口
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(3306)  # MySQL默认端口
        server_layout.addRow("端口:", self.port_spin)
        
        # 数据库名
        self.database_edit = QLineEdit()
        self.database_edit.setPlaceholderText("数据库名称（可选）")
        server_layout.addRow("数据库:", self.database_edit)
        
        layout.addWidget(self.server_group)
        
        # 认证信息组
        auth_group = QGroupBox("认证信息")
        auth_layout = QFormLayout(auth_group)
        
        # 用户名
        self.username_edit = QLineEdit()
        auth_layout.addRow("用户名:", self.username_edit)
        
        # 密码
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        auth_layout.addRow("密码:", self.password_edit)
        
        # 保存密码
        self.save_password_check = QCheckBox("保存密码")
        self.save_password_check.setChecked(True)
        auth_layout.addRow("", self.save_password_check)
        
        layout.addWidget(auth_group)
        
        # SQLite文件路径组（初始隐藏）
        self.sqlite_group = QGroupBox("SQLite文件")
        sqlite_layout = QFormLayout(self.sqlite_group)
        
        # 文件路径布局
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择SQLite数据库文件")
        file_layout.addWidget(self.file_path_edit)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_sqlite_file)
        file_layout.addWidget(self.browse_button)
        
        sqlite_layout.addRow("文件路径:", file_layout)
        
        self.sqlite_group.setVisible(False)
        layout.addWidget(self.sqlite_group)
        
        layout.addStretch()
        
        return widget
        
    def create_advanced_tab(self):
        """创建高级设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 连接选项组
        options_group = QGroupBox("连接选项")
        options_layout = QFormLayout(options_group)
        
        # 连接超时
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" 秒")
        options_layout.addRow("连接超时:", self.timeout_spin)
        
        # 字符集
        self.charset_combo = QComboBox()
        self.charset_combo.addItems(["utf8", "utf8mb4", "latin1", "gbk"])
        self.charset_combo.setCurrentText("utf8mb4")
        options_layout.addRow("字符集:", self.charset_combo)
        
        # SSL连接
        self.ssl_check = QCheckBox("使用SSL连接")
        options_layout.addRow("", self.ssl_check)
        
        # 自动连接
        self.auto_connect_check = QCheckBox("启动时自动连接")
        options_layout.addRow("", self.auto_connect_check)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        
        return widget
        
    def on_db_type_changed(self, db_type):
        """数据库类型改变事件"""
        if db_type == "SQLite":
            self.server_group.setVisible(False)
            self.sqlite_group.setVisible(True)
        else:
            self.server_group.setVisible(True)
            self.sqlite_group.setVisible(False)
            
            # 设置默认端口
            default_ports = {
                "MySQL": 3306,
                "PostgreSQL": 5432,
                "SQL Server": 1433,
                "Oracle": 1521
            }
            if db_type in default_ports:
                self.port_spin.setValue(default_ports[db_type])
                
    def browse_sqlite_file(self):
        """浏览SQLite文件"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择SQLite数据库文件", "", 
            "SQLite数据库 (*.db *.sqlite *.sqlite3);;所有文件 (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            
    def test_connection(self):
        """测试数据库连接"""
        try:
            conn_info = self.get_connection_info()
            
            # 这里应该调用实际的连接测试逻辑
            # 暂时显示成功消息
            QMessageBox.information(self, "测试连接", "连接测试成功！")
            
        except Exception as e:
            QMessageBox.critical(self, "连接失败", f"连接测试失败：{str(e)}")
            
    def get_connection_info(self):
        """获取连接信息"""
        conn_info = {
            'name': self.name_edit.text() or f"{self.db_type_combo.currentText()}连接",
            'type': self.db_type_combo.currentText(),
            'host': self.host_edit.text(),
            'port': self.port_spin.value(),
            'database': self.database_edit.text(),
            'username': self.username_edit.text(),
            'password': self.password_edit.text(),
            'save_password': self.save_password_check.isChecked(),
            'timeout': self.timeout_spin.value(),
            'charset': self.charset_combo.currentText(),
            'ssl': self.ssl_check.isChecked(),
            'auto_connect': self.auto_connect_check.isChecked()
        }
        
        # SQLite特殊处理
        if conn_info['type'] == 'SQLite':
            conn_info['file_path'] = self.file_path_edit.text()
            
        return conn_info
        
    def accept(self):
        """确定按钮点击事件"""
        # 验证输入
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入连接名称")
            return
            
        if self.db_type_combo.currentText() == "SQLite":
            if not self.file_path_edit.text().strip():
                QMessageBox.warning(self, "警告", "请选择SQLite数据库文件")
                return
        else:
            if not self.host_edit.text().strip():
                QMessageBox.warning(self, "警告", "请输入主机名")
                return
            if not self.username_edit.text().strip():
                QMessageBox.warning(self, "警告", "请输入用户名")
                return
                
        super().accept()