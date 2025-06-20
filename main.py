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
from config_manager import config

def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName(config.get_app_name())
    app.setApplicationVersion(config.get_app_version())
    app.setOrganizationName(config.get_organization())
    
    # 设置应用程序图标
    icon_path = config.get_icon_path()
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建主窗口
    main_window = MainWindow()
    main_window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()