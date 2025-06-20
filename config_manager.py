# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import toml
from typing import Dict, Any

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.toml"):
        self.config_file = config_file
        self._config = None
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = toml.load(f)
            else:
                # 如果配置文件不存在，使用默认配置
                self._config = self._get_default_config()
                self.save_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self._config = self._get_default_config()
    
    def save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                toml.dump(self._config, f)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, section: str, key: str = None, default=None) -> Any:
        """获取配置值"""
        if not self._config:
            return default
        
        if key is None:
            return self._config.get(section, default)
        
        section_data = self._config.get(section, {})
        return section_data.get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """设置配置值"""
        if not self._config:
            self._config = {}
        
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
    
    def get_app_name(self) -> str:
        """获取应用名称"""
        return self.get('app', 'name', 'PySide6 Navicat')
    
    def get_app_version(self) -> str:
        """获取应用版本"""
        return self.get('app', 'version', '1.0.0')
    
    def get_build_number(self) -> int:
        """获取构建号"""
        return self.get('app', 'build_number', 1000)
    
    def get_build_id(self) -> str:
        """获取构建ID"""
        return self.get('app', 'build_id', 'dev001')
    
    def get_app_description(self) -> str:
        """获取应用描述"""
        return self.get('app', 'description', '数据库管理工具')
    
    def get_organization(self) -> str:
        """获取组织名称"""
        return self.get('app', 'organization', 'Database Tools')
    
    def get_app_language(self) -> str:
        """获取应用语言"""
        return self.get('app', 'language', 'zh-Hans')
    
    def get_window_title(self) -> str:
        """获取窗口标题"""
        return self.get('window', 'title', 'PySide6 Navicat - 数据库管理工具')
    
    def get_window_size(self) -> tuple:
        """获取窗口大小"""
        width = self.get('window', 'width', 1400)
        height = self.get('window', 'height', 900)
        return (width, height)
    
    def get_icon_path(self) -> str:
        """获取图标路径"""
        return self.get('window', 'icon_path', 'resources/icons/app.png')
    
    def get_about_dialog_size(self) -> tuple:
        """获取关于对话框大小"""
        width = self.get('about', 'dialog_width', 500)
        height = self.get('about', 'dialog_height', 400)
        return (width, height)
    
    def get_about_colors(self) -> dict:
        """获取关于对话框颜色配置"""
        return {
            'title_color': self.get('about', 'title_color', '#2c3e50'),
            'label_color': self.get('about', 'label_color', '#34495e')
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'app': {
                'name': 'PySide6 Navicat',
                'version': '1.0.0',
                'build_number': 1000,
                'build_id': 'dev001',
                'description': '数据库管理工具',
                'organization': 'Database Tools',
                'language': 'zh-Hans'
            },
            'window': {
                'title': 'PySide6 Navicat - 数据库管理工具',
                'width': 1400,
                'height': 900,
                'icon_path': 'resources/icons/app.png'
            },
            'database': {
                'supported_types': ['MySQL', 'PostgreSQL', 'SQLite', 'SQL Server'],
                'default_port': {
                    'MySQL': 3306,
                    'PostgreSQL': 5432,
                    'SQLite': 0,
                    'SQL Server': 1433
                }
            },
            'ui': {
                'default_font': 'Microsoft YaHei',
                'font_size': 12,
                'theme': 'default'
            },
            'about': {
                'title_color': '#2c3e50',
                'label_color': '#34495e',
                'dialog_width': 500,
                'dialog_height': 400
            }
        }

# 全局配置管理器实例
config = ConfigManager()