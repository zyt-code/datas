#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 检查依赖并运行应用程序
"""

import sys
import os
import subprocess
import importlib.util

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_package(package_name, import_name=None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name
        
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def install_package(package_name):
    """安装包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """检查并安装依赖"""
    required_packages = [
        ("PySide6", "PySide6"),
        ("PyMySQL", "pymysql"),
        ("psycopg2-binary", "psycopg2"),
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    if missing_packages:
        print("检测到缺失的依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        
        response = input("\n是否自动安装缺失的依赖包? (y/n): ")
        if response.lower() in ['y', 'yes', '是']:
            print("\n正在安装依赖包...")
            
            for package in missing_packages:
                print(f"安装 {package}...")
                if install_package(package):
                    print(f"✓ {package} 安装成功")
                else:
                    print(f"✗ {package} 安装失败")
                    print(f"请手动安装: pip install {package}")
                    return False
        else:
            print("\n请手动安装依赖包:")
            print("pip install -r requirements.txt")
            return False
    
    return True

def create_directories():
    """创建必要的目录"""
    directories = [
        "resources",
        "resources/icons",
        "logs",
        "exports"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")

def main():
    """主函数"""
    print("PySide6 Navicat Clone - 启动检查")
    print("=" * 40)
    
    # 检查Python版本
    print("检查Python版本...")
    if not check_python_version():
        sys.exit(1)
    print(f"✓ Python版本: {sys.version.split()[0]}")
    
    # 检查并安装依赖
    print("\n检查依赖包...")
    if not check_and_install_dependencies():
        sys.exit(1)
    print("✓ 所有依赖包已安装")
    
    # 创建必要目录
    print("\n创建必要目录...")
    create_directories()
    print("✓ 目录结构检查完成")
    
    # 启动应用程序
    print("\n启动应用程序...")
    print("=" * 40)
    
    try:
        # 导入并运行主程序
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"错误: 无法导入主程序模块: {e}")
        print("请确保main.py文件存在且可访问")
        sys.exit(1)
    except Exception as e:
        print(f"应用程序运行时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()