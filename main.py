#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PySide6 Navicat Clone - 数据库管理工具
主应用程序入口
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow

def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("PySide6 Navicat")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Database Tools")
    
    # 设置应用程序图标
    if os.path.exists("resources/icons/app.png"):
        app.setWindowIcon(QIcon("resources/icons/app.png"))
    
    # 创建主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()