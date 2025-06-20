#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询结果显示组件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHeaderView, QAbstractItemView, QMenu,
    QMessageBox, QFileDialog, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QClipboard, QAction
import csv
import json

class ExportThread(QThread):
    """导出数据线程"""
    progress = Signal(int)
    finished = Signal(bool, str)
    
    def __init__(self, data, headers, file_path, format_type):
        super().__init__()
        self.data = data
        self.headers = headers
        self.file_path = file_path
        self.format_type = format_type
        
    def run(self):
        try:
            if self.format_type == 'csv':
                self.export_csv()
            elif self.format_type == 'json':
                self.export_json()
            elif self.format_type == 'txt':
                self.export_txt()
            self.finished.emit(True, "导出成功")
        except Exception as e:
            self.finished.emit(False, str(e))
            
    def export_csv(self):
        """导出为CSV格式"""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            
            total = len(self.data)
            for i, row in enumerate(self.data):
                writer.writerow(row)
                progress = int((i + 1) / total * 100)
                self.progress.emit(progress)
                
    def export_json(self):
        """导出为JSON格式"""
        json_data = []
        total = len(self.data)
        
        for i, row in enumerate(self.data):
            row_dict = {}
            for j, header in enumerate(self.headers):
                row_dict[header] = row[j] if j < len(row) else None
            json_data.append(row_dict)
            
            progress = int((i + 1) / total * 100)
            self.progress.emit(progress)
            
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            
    def export_txt(self):
        """导出为文本格式"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            # 写入表头
            f.write('\t'.join(self.headers) + '\n')
            f.write('-' * 50 + '\n')
            
            total = len(self.data)
            for i, row in enumerate(self.data):
                f.write('\t'.join(str(cell) for cell in row) + '\n')
                progress = int((i + 1) / total * 100)
                self.progress.emit(progress)

class TableViewer(QTableWidget):
    """表格查看器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_table()
        
    def init_table(self):
        """初始化表格"""
        # 设置表格属性
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        
        # 设置表头
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setVisible(True)
        
        # 设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 复制单元格
        copy_cell_action = QAction("复制单元格", self)
        copy_cell_action.triggered.connect(self.copy_cell)
        menu.addAction(copy_cell_action)
        
        # 复制行
        copy_row_action = QAction("复制行", self)
        copy_row_action.triggered.connect(self.copy_row)
        menu.addAction(copy_row_action)
        
        # 复制所有数据
        copy_all_action = QAction("复制所有数据", self)
        copy_all_action.triggered.connect(self.copy_all)
        menu.addAction(copy_all_action)
        
        menu.exec(self.mapToGlobal(position))
        
    def copy_cell(self):
        """复制单元格内容"""
        current_item = self.currentItem()
        if current_item:
            clipboard = QClipboard()
            clipboard.setText(current_item.text())
            
    def copy_row(self):
        """复制选中行"""
        selected_rows = set()
        for item in self.selectedItems():
            selected_rows.add(item.row())
            
        if selected_rows:
            clipboard = QClipboard()
            text_data = []
            
            for row in sorted(selected_rows):
                row_data = []
                for col in range(self.columnCount()):
                    item = self.item(row, col)
                    row_data.append(item.text() if item else "")
                text_data.append('\t'.join(row_data))
                
            clipboard.setText('\n'.join(text_data))
            
    def copy_all(self):
        """复制所有数据"""
        clipboard = QClipboard()
        text_data = []
        
        # 复制表头
        headers = []
        for col in range(self.columnCount()):
            headers.append(self.horizontalHeaderItem(col).text())
        text_data.append('\t'.join(headers))
        
        # 复制数据
        for row in range(self.rowCount()):
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                row_data.append(item.text() if item else "")
            text_data.append('\t'.join(row_data))
            
        clipboard.setText('\n'.join(text_data))

class QueryResult(QWidget):
    """查询结果组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = []
        self.current_headers = []
        self.export_thread = None
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 结果信息标签
        self.info_label = QLabel("无查询结果")
        toolbar_layout.addWidget(self.info_label)
        
        toolbar_layout.addStretch()
        
        # 导出按钮
        self.export_button = QPushButton("导出数据")
        self.export_button.clicked.connect(self.export_data)
        self.export_button.setEnabled(False)
        toolbar_layout.addWidget(self.export_button)
        
        # 刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setEnabled(False)
        toolbar_layout.addWidget(self.refresh_button)
        
        layout.addLayout(toolbar_layout)
        
        # 表格
        self.table = TableViewer()
        layout.addWidget(self.table)
        
        # 进度条（初始隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def display_result(self, result):
        """显示查询结果"""
        
        if not result:
            self.clear_result()
            return
            
        try:
            # 检查结果格式
            if isinstance(result, dict):
                # 检查是否是查询结果格式（包含data和headers）
                if 'data' in result and 'headers' in result:
                    data = result.get('data', [])
                    headers = result.get('headers', [])
                    info_text = f"查询结果: {len(data)} 行, {len(headers)} 列"
                    if 'execution_time' in result:
                        info_text += f" (执行时间: {result['execution_time']:.3f}s)"
                # 检查是否是非查询语句结果格式（包含affected_rows）
                elif 'affected_rows' in result:
                    # 对于非查询语句，显示执行信息
                    affected_rows = result.get('affected_rows', 0)
                    execution_time = result.get('execution_time', 0)
                    sql = result.get('sql', '')
                    
                    # 创建一个简单的信息表格
                    headers = ['属性', '值']
                    data = [
                        ['SQL语句', sql],
                        ['影响行数', str(affected_rows)],
                        ['执行时间', f"{execution_time:.3f}s"]
                    ]
                    info_text = f"命令执行完成: 影响 {affected_rows} 行 (执行时间: {execution_time:.3f}s)"
                else:
                    # 其他字典格式，尝试转换为表格
                    headers = list(result.keys())
                    data = [list(result.values())]
                    info_text = f"结果: 1 行, {len(headers)} 列"
            elif isinstance(result, list):
                # 如果是列表，假设第一行是表头
                if result and isinstance(result[0], dict):
                    headers = list(result[0].keys())
                    data = [[row[col] for col in headers] for row in result]
                else:
                    data = result
                    headers = [f"Column {i+1}" for i in range(len(data[0]) if data else 0)]
                info_text = f"查询结果: {len(data)} 行, {len(headers)} 列"
            else:
                data = []
                headers = []
                info_text = "无查询结果"
                
            self.current_data = data
            self.current_headers = headers
            
            # 设置表格
            self.table.setRowCount(len(data))
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            
            # 填充数据
            for row_idx, row_data in enumerate(data):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                    self.table.setItem(row_idx, col_idx, item)
                    
            # 调整列宽
            self.table.resizeColumnsToContents()
            
            # 更新信息标签
            self.info_label.setText(info_text)
            
            # 启用按钮
            self.export_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"显示查询结果时发生错误：{str(e)}")
            
    def clear_result(self):
        """清空结果"""
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.current_data = []
        self.current_headers = []
        self.info_label.setText("无查询结果")
        self.export_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        
    def export_data(self):
        """导出数据"""
        if not self.current_data:
            QMessageBox.warning(self, "警告", "没有数据可导出")
            return
            
        # 选择导出格式和文件路径
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "导出数据", "",
            "CSV文件 (*.csv);;JSON文件 (*.json);;文本文件 (*.txt)"
        )
        
        if not file_path:
            return
            
        # 确定导出格式
        if selected_filter.startswith("CSV"):
            format_type = 'csv'
        elif selected_filter.startswith("JSON"):
            format_type = 'json'
        else:
            format_type = 'txt'
            
        # 开始导出
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.export_thread = ExportThread(
            self.current_data, self.current_headers, file_path, format_type
        )
        self.export_thread.progress.connect(self.progress_bar.setValue)
        self.export_thread.finished.connect(self.on_export_finished)
        self.export_thread.start()
        
    def on_export_finished(self, success, message):
        """导出完成回调"""
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", f"导出失败：{message}")
            
    def refresh_data(self):
        """刷新数据"""
        # TODO: 重新执行查询
        pass
        
    def get_selected_data(self):
        """获取选中的数据"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
            
        if not selected_rows:
            return []
            
        selected_data = []
        for row in sorted(selected_rows):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            selected_data.append(row_data)
            
        return selected_data