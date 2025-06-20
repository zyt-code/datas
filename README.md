# PySide6 Navicat Clone

一个基于PySide6开发的数据库管理工具，类似于Navicat的功能。支持多种数据库类型，提供直观的图形界面进行数据库操作。

## 功能特性

### 🗄️ 数据库支持
- **MySQL** - 完整支持
- **PostgreSQL** - 完整支持  
- **SQLite** - 完整支持
- **SQL Server** - 基础支持
- **Oracle** - 基础支持

### 🔧 核心功能
- **连接管理** - 创建、保存、管理多个数据库连接
- **SQL编辑器** - 语法高亮、代码补全、格式化
- **数据浏览** - 表格数据查看、编辑、分页显示
- **结构查看** - 数据库表结构、索引、约束查看
- **查询执行** - SQL查询执行、结果导出
- **数据导出** - 支持CSV、JSON、TXT格式导出

### 🎨 界面特性
- 现代化的用户界面
- 可调整的面板布局
- 语法高亮的SQL编辑器
- 表格数据的多种视图
- 右键菜单和快捷键支持

## 安装说明

### 环境要求
- Python 3.8+
- PySide6

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd datas
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行应用**
```bash
python main.py
```

## 使用指南

### 创建数据库连接

1. 点击菜单栏 `文件` -> `新建连接` 或使用快捷键 `Ctrl+N`
2. 在连接对话框中填写数据库信息：
   - 连接名称
   - 数据库类型
   - 主机地址和端口
   - 用户名和密码
   - 数据库名（可选）
3. 点击 `测试连接` 验证连接
4. 点击 `确定` 保存连接

### SQL查询

1. 在左侧连接树中双击连接名称建立连接
2. 在SQL编辑器中输入查询语句
3. 按 `F5` 或点击 `执行查询` 按钮
4. 查看查询结果和执行信息

### 数据浏览

1. 在连接树中展开数据库和表
2. 双击表名查看表数据
3. 使用分页控件浏览大量数据
4. 右键菜单提供复制、导出等功能

### 快捷键

- `Ctrl+N` - 新建连接
- `Ctrl+O` - 打开SQL文件
- `Ctrl+S` - 保存SQL文件
- `F5` - 执行查询
- `Ctrl+/` - 注释/取消注释
- `Tab` - 缩进
- `Shift+Tab` - 反缩进

## 项目结构

```
datas/
├── main.py                 # 应用程序入口
├── requirements.txt        # 依赖包列表
├── README.md              # 项目说明
├── ui/                    # 用户界面模块
│   ├── main_window.py     # 主窗口
│   ├── connection_dialog.py # 连接对话框
│   ├── sql_editor.py      # SQL编辑器
│   ├── query_result.py    # 查询结果显示
│   └── table_viewer.py    # 表格查看器
├── database/              # 数据库模块
│   ├── connection_manager.py # 连接管理器
│   └── query_executor.py  # 查询执行器
└── resources/             # 资源文件
    └── icons/             # 图标文件
```

## 数据库配置

### MySQL
```python
{
    'type': 'MySQL',
    'host': 'localhost',
    'port': 3306,
    'username': 'root',
    'password': 'password',
    'database': 'test'
}
```

### PostgreSQL
```python
{
    'type': 'PostgreSQL',
    'host': 'localhost',
    'port': 5432,
    'username': 'postgres',
    'password': 'password',
    'database': 'postgres'
}
```

### SQLite
```python
{
    'type': 'SQLite',
    'file_path': '/path/to/database.db'
}
```

## 开发说明

### 添加新的数据库支持

1. 在 `connection_manager.py` 中添加新的连接方法
2. 实现数据库特定的信息获取方法
3. 在连接对话框中添加相应的配置选项

### 扩展功能

- 数据库设计器
- 数据同步工具
- 备份和恢复
- 用户权限管理
- 查询性能分析

## 故障排除

### 常见问题

1. **连接失败**
   - 检查数据库服务是否运行
   - 验证连接参数是否正确
   - 确认防火墙设置

2. **依赖包安装失败**
   - 更新pip: `pip install --upgrade pip`
   - 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

3. **界面显示异常**
   - 检查PySide6版本是否兼容
   - 尝试重新安装PySide6

### 日志文件

应用程序会在运行目录生成日志文件，包含详细的错误信息和调试信息。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 代码规范

- 使用Python PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持MySQL、PostgreSQL、SQLite
- 基础的SQL编辑和查询功能
- 数据浏览和导出功能

---

**注意**: 这是一个教育和学习项目，不建议在生产环境中使用。如需商业用途，请考虑使用专业的数据库管理工具。