# 开发环境设置指南

## 环境要求

- Python 3.12+
- Git

## 初始化开发环境

### 1. 克隆仓库
```bash
git clone git@github.com:chorusfruit-233/JOJOSoul-ng.git
cd JOJOSoul-ng
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
```

### 3. 激活虚拟环境

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 验证安装
```bash
python JOJOSoul-ng.py
```

## 开发工作流

### 运行游戏
```bash
# 激活虚拟环境后
python JOJOSoul-ng.py
```

### 打包为可执行文件
```bash
pyinstaller --onefile --windowed --name "JOJOSoul" JOJOSoul-ng.py
```

### 测试
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_player.py -v

# 运行特定测试方法
python -m pytest tests/test_player.py::TestPlayer::test_player_initialization -v
```

### 代码格式化
```bash
# 格式化代码
black .

# 检查代码格式
black --check .

# 排序导入
isort .

# 检查代码质量
flake8 .
```

## 项目结构说明

```
JOJOSoul-ng/
├── JOJOSoul-ng.py    # 主游戏文件
├── requirements.txt  # 项目依赖
├── DEVELOPMENT.md    # 开发环境设置指南
├── README.md        # 项目说明文档
├── IFLOW.md         # iFlow 上下文文件
├── .gitignore       # Git 忽略文件配置
├── venv/            # 虚拟环境目录（不提交到版本控制）
└── .github/workflows/
    └── build.yml    # CI/CD 构建配置
```

## 常见问题

### 1. 模块未找到错误
确保已激活虚拟环境并安装了依赖：
```bash
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. 图形界面无法显示
确保系统支持图形界面，easygui 需要图形环境。

### 3. 打包失败
检查 PyInstaller 版本是否与 requirements.txt 中一致。

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 发布流程

项目使用 GitHub Actions 自动构建 Windows 可执行文件。当代码推送到 master 分支时，会自动触发构建流程。