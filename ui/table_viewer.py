#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格查看器组件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
    QPushButton, QSpinBox, QComboBox, QLineEdit,
    QHeaderView, QAbstractItemView, QMessageBox,
    QSplitter, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class TableStructureViewer(QTableWidget):
    """表结构查看器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_table()
        
    def init_table(self):
        """初始化表格"""
        # 设置列
        headers = ["字段名", "数据类型", "长度", "允许空值", "默认值", "主键", "自增", "注释"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # 设置表格属性
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        
        # 设置只读
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    def display_structure(self, structure_data):
        """显示表结构"""
        if not structure_data:
            self.setRowCount(0)
            return
            
        self.setRowCount(len(structure_data))
        
        for row_idx, field_info in enumerate(structure_data):
            # 字段名
            self.setItem(row_idx, 0, QTableWidgetItem(field_info.get('name', '')))
            
            # 数据类型
            self.setItem(row_idx, 1, QTableWidgetItem(field_info.get('type', '')))
            
            # 长度
            length = field_info.get('length', '')
            self.setItem(row_idx, 2, QTableWidgetItem(str(length) if length else ''))
            
            # 允许空值
            nullable = "是" if field_info.get('nullable', False) else "否"
            self.setItem(row_idx, 3, QTableWidgetItem(nullable))
            
            # 默认值
            default = field_info.get('default', '')
            self.setItem(row_idx, 4, QTableWidgetItem(str(default) if default else ''))
            
            # 主键
            primary_key = "是" if field_info.get('primary_key', False) else "否"
            self.setItem(row_idx, 5, QTableWidgetItem(primary_key))
            
            # 自增
            auto_increment = "是" if field_info.get('auto_increment', False) else "否"
            self.setItem(row_idx, 6, QTableWidgetItem(auto_increment))
            
            # 注释
            comment = field_info.get('comment', '')
            self.setItem(row_idx, 7, QTableWidgetItem(comment))
            
        # 调整列宽
        self.resizeColumnsToContents()

class TableDataViewer(QWidget):
    """表数据查看器"""
    
    data_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_table = None
        self.current_page = 1
        self.page_size = 100
        self.total_rows = 0
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(self.refresh_button)
        
        # 添加行按钮
        self.add_row_button = QPushButton("添加行")
        self.add_row_button.clicked.connect(self.add_row)
        toolbar_layout.addWidget(self.add_row_button)
        
        # 删除行按钮
        self.delete_row_button = QPushButton("删除行")
        self.delete_row_button.clicked.connect(self.delete_row)
        toolbar_layout.addWidget(self.delete_row_button)
        
        toolbar_layout.addStretch()
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索...")
        self.search_edit.returnPressed.connect(self.search_data)
        toolbar_layout.addWidget(QLabel("搜索:"))
        toolbar_layout.addWidget(self.search_edit)
        
        # 搜索按钮
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_data)
        toolbar_layout.addWidget(self.search_button)
        
        layout.addLayout(toolbar_layout)
        
        # 数据表格
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.data_table)
        
        # 分页工具栏
        pagination_layout = QHBoxLayout()
        
        # 页面信息
        self.page_info_label = QLabel("第 0 页，共 0 页")
        pagination_layout.addWidget(self.page_info_label)
        
        pagination_layout.addStretch()
        
        # 每页行数
        pagination_layout.addWidget(QLabel("每页:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["50", "100", "200", "500"])
        self.page_size_combo.setCurrentText("100")
        self.page_size_combo.currentTextChanged.connect(self.change_page_size)
        pagination_layout.addWidget(self.page_size_combo)
        pagination_layout.addWidget(QLabel("行"))
        
        # 分页按钮
        self.first_page_button = QPushButton("首页")
        self.first_page_button.clicked.connect(self.first_page)
        pagination_layout.addWidget(self.first_page_button)
        
        self.prev_page_button = QPushButton("上一页")
        self.prev_page_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_page_button)
        
        # 页码输入
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.valueChanged.connect(self.goto_page)
        pagination_layout.addWidget(self.page_spin)
        
        self.next_page_button = QPushButton("下一页")
        self.next_page_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_page_button)
        
        self.last_page_button = QPushButton("末页")
        self.last_page_button.clicked.connect(self.last_page)
        pagination_layout.addWidget(self.last_page_button)
        
        layout.addLayout(pagination_layout)
        
    def display_data(self, table_name, data, headers, total_count=None):
        """显示表数据"""
        self.current_table = table_name
        
        if total_count is not None:
            self.total_rows = total_count
        else:
            self.total_rows = len(data)
            
        # 设置表格
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(headers))
        self.data_table.setHorizontalHeaderLabels(headers)
        
        # 填充数据
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                self.data_table.setItem(row_idx, col_idx, item)
                
        # 调整列宽
        self.data_table.resizeColumnsToContents()
        
        # 更新分页信息
        self.update_pagination_info()
        
    def update_pagination_info(self):
        """更新分页信息"""
        total_pages = (self.total_rows + self.page_size - 1) // self.page_size
        self.page_info_label.setText(f"第 {self.current_page} 页，共 {total_pages} 页 (总计 {self.total_rows} 行)")
        
        # 更新页码输入框
        self.page_spin.setMaximum(max(1, total_pages))
        self.page_spin.setValue(self.current_page)
        
        # 更新按钮状态
        self.first_page_button.setEnabled(self.current_page > 1)
        self.prev_page_button.setEnabled(self.current_page > 1)
        self.next_page_button.setEnabled(self.current_page < total_pages)
        self.last_page_button.setEnabled(self.current_page < total_pages)
        
    def change_page_size(self, size_text):
        """改变每页行数"""
        self.page_size = int(size_text)
        self.current_page = 1
        self.refresh_data()
        
    def first_page(self):
        """跳转到首页"""
        self.current_page = 1
        self.refresh_data()
        
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_data()
            
    def next_page(self):
        """下一页"""
        total_pages = (self.total_rows + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_data()
            
    def last_page(self):
        """跳转到末页"""
        total_pages = (self.total_rows + self.page_size - 1) // self.page_size
        self.current_page = max(1, total_pages)
        self.refresh_data()
        
    def goto_page(self, page):
        """跳转到指定页"""
        self.current_page = page
        self.refresh_data()
        
    def refresh_data(self):
        """刷新数据"""
        if self.current_table:
            # TODO: 重新加载表数据
            self.data_changed.emit()
            
    def search_data(self):
        """搜索数据"""
        search_text = self.search_edit.text().strip()
        if search_text:
            # TODO: 实现搜索功能
            QMessageBox.information(self, "搜索", f"搜索功能待实现: {search_text}")
        else:
            self.refresh_data()
            
    def add_row(self):
        """添加新行"""
        # TODO: 实现添加行功能
        QMessageBox.information(self, "添加行", "添加行功能待实现")
        
    def delete_row(self):
        """删除选中行"""
        selected_rows = set()
        for item in self.data_table.selectedItems():
            selected_rows.add(item.row())
            
        if selected_rows:
            # TODO: 实现删除行功能
            QMessageBox.information(self, "删除行", f"删除行功能待实现，选中了 {len(selected_rows)} 行")
        else:
            QMessageBox.warning(self, "警告", "请先选择要删除的行")

class TableViewer(QWidget):
    """表格查看器主组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_table = None
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 表信息
        info_group = QGroupBox("表信息")
        info_layout = QFormLayout(info_group)
        
        self.table_name_label = QLabel("未选择表")
        info_layout.addRow("表名:", self.table_name_label)
        
        self.table_engine_label = QLabel("-")
        info_layout.addRow("存储引擎:", self.table_engine_label)
        
        self.table_rows_label = QLabel("-")
        info_layout.addRow("行数:", self.table_rows_label)
        
        self.table_size_label = QLabel("-")
        info_layout.addRow("大小:", self.table_size_label)
        
        layout.addWidget(info_group)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 数据标签页
        self.data_viewer = TableDataViewer()
        self.tab_widget.addTab(self.data_viewer, "数据")
        
        # 结构标签页
        self.structure_viewer = TableStructureViewer()
        self.tab_widget.addTab(self.structure_viewer, "结构")
        
        # SQL标签页
        self.sql_text = QTextEdit()
        self.sql_text.setFont(QFont("Consolas", 10))
        self.sql_text.setReadOnly(True)
        self.tab_widget.addTab(self.sql_text, "SQL")
        
        layout.addWidget(self.tab_widget)
        
    def display_table(self, table_info):
        """显示表信息"""
        self.current_table = table_info.get('name', '')
        
        # 更新表信息
        self.table_name_label.setText(table_info.get('name', '-'))
        self.table_engine_label.setText(table_info.get('engine', '-'))
        self.table_rows_label.setText(str(table_info.get('rows', '-')))
        self.table_size_label.setText(table_info.get('size', '-'))
        
        # 显示表结构
        structure_data = table_info.get('structure', [])
        self.structure_viewer.display_structure(structure_data)
        
        # 显示表数据
        data = table_info.get('data', [])
        headers = table_info.get('headers', [])
        total_count = table_info.get('total_count')
        self.data_viewer.display_data(self.current_table, data, headers, total_count)
        
        # 显示创建SQL
        create_sql = table_info.get('create_sql', '')
        self.sql_text.setPlainText(create_sql)
        
    def clear_table(self):
        """清空表显示"""
        self.current_table = None
        self.table_name_label.setText("未选择表")
        self.table_engine_label.setText("-")
        self.table_rows_label.setText("-")
        self.table_size_label.setText("-")
        
        self.structure_viewer.setRowCount(0)
        self.data_viewer.data_table.setRowCount(0)
        self.data_viewer.data_table.setColumnCount(0)
        self.sql_text.clear()