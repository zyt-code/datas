# -*- coding: utf-8 -*-
"""
数据库连接配置管理器
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional

class ConnectionConfig:
    """数据库连接配置管理器"""
    
    def __init__(self):
        """初始化配置管理器"""
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "connections.json"
        self._ensure_config_directory()
        
    def _get_config_directory(self) -> Path:
        """获取配置目录路径"""
        # 获取用户数据目录
        if os.name == 'nt':  # Windows
            data_dir = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        elif os.name == 'posix':  # macOS/Linux
            if os.uname().sysname == 'Darwin':  # macOS
                data_dir = Path.home() / 'Library' / 'Application Support'
            else:  # Linux
                data_dir = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        else:
            data_dir = Path.home()
            
        return data_dir / 'PySide6Navicat'
        
    def _ensure_config_directory(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def save_connection(self, conn_info: Dict) -> bool:
        """保存连接信息"""
        try:
            connections = self.load_all_connections()
            
            # 检查是否已存在同名连接
            existing_index = -1
            for i, conn in enumerate(connections):
                if conn.get('name') == conn_info.get('name'):
                    existing_index = i
                    break
                    
            if existing_index >= 0:
                # 更新现有连接
                connections[existing_index] = conn_info
            else:
                # 添加新连接
                connections.append(conn_info)
                
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(connections, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"保存连接配置失败: {e}")
            return False
            
    def load_all_connections(self) -> List[Dict]:
        """加载所有连接信息"""
        try:
            if not self.config_file.exists():
                return []
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                connections = json.load(f)
                
            # 验证连接信息格式
            valid_connections = []
            for conn in connections:
                if isinstance(conn, dict) and 'name' in conn and 'type' in conn:
                    valid_connections.append(conn)
                    
            return valid_connections
            
        except Exception as e:
            print(f"加载连接配置失败: {e}")
            return []
            
    def delete_connection(self, connection_name: str) -> bool:
        """删除指定连接"""
        try:
            connections = self.load_all_connections()
            
            # 查找并删除连接
            updated_connections = [conn for conn in connections if conn.get('name') != connection_name]
            
            if len(updated_connections) == len(connections):
                return False  # 未找到要删除的连接
                
            # 保存更新后的连接列表
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(updated_connections, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"删除连接配置失败: {e}")
            return False
            
    def get_connection(self, connection_name: str) -> Optional[Dict]:
        """获取指定连接信息"""
        connections = self.load_all_connections()
        for conn in connections:
            if conn.get('name') == connection_name:
                return conn
        return None
        
    def update_connection(self, connection_name: str, conn_info: Dict) -> bool:
        """更新连接信息"""
        try:
            connections = self.load_all_connections()
            
            # 查找并更新连接
            for i, conn in enumerate(connections):
                if conn.get('name') == connection_name:
                    connections[i] = conn_info
                    
                    # 保存到文件
                    with open(self.config_file, 'w', encoding='utf-8') as f:
                        json.dump(connections, f, ensure_ascii=False, indent=2)
                        
                    return True
                    
            return False  # 未找到要更新的连接
            
        except Exception as e:
            print(f"更新连接配置失败: {e}")
            return False
            
    def get_config_file_path(self) -> str:
        """获取配置文件路径"""
        return str(self.config_file)
        
    def backup_connections(self, backup_path: str) -> bool:
        """备份连接配置"""
        try:
            if self.config_file.exists():
                import shutil
                shutil.copy2(self.config_file, backup_path)
                return True
            return False
        except Exception as e:
            print(f"备份连接配置失败: {e}")
            return False
            
    def restore_connections(self, backup_path: str) -> bool:
        """恢复连接配置"""
        try:
            if os.path.exists(backup_path):
                import shutil
                shutil.copy2(backup_path, self.config_file)
                return True
            return False
        except Exception as e:
            print(f"恢复连接配置失败: {e}")
            return False