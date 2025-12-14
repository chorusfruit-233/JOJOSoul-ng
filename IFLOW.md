# JOJO Soul (Refactored) 项目概述

## 项目简介
这是一个基于 Python 的 JOJO 奇妙冒险同人游戏，经过重构和优化。游戏采用图形界面，玩家需要通过战斗和升级来阻止普奇神父重启世界。

## 技术栈
- **语言**: Python 3.12
- **GUI 库**: easygui
- **打包工具**: PyInstaller
- **CI/CD**: GitHub Actions

## 项目结构
```
JOJOSoul-ng/
├── JOJOSoul-ng.py    # 主游戏文件
├── requirements.txt  # 项目依赖
├── README.md        # 项目说明文档
├── .gitignore       # Git 忽略文件配置
└── .github/workflows/
    └── build.yml    # CI/CD 构建配置
```

## 游戏机制
- **角色系统**: 玩家拥有生命值、攻击力、金币、暴击倍率和氧气数量
- **战斗系统**: 基于元素属性的回合制战斗，包含火焰、水、土地、暗黑魔法和闪光五种元素
- **难度系统**: 提供无限金币版、简单、普通、坤难和炼狱五种难度
- **商店系统**: 可购买装备升级角色属性
- **剧情系统**: 包含多个地图区域和最终 Boss 战

## 安装与运行

### 环境要求
- Python 3.12+
- easygui 库
- PyInstaller (用于打包)

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行游戏
```bash
python JOJOSoul-ng.py
```

### 打包为可执行文件
```bash
pyinstaller --onefile --windowed --name "JOJOSoul" JOJOSoul-ng.py
```

## 开发规范

### 代码风格
- 使用 4 空格缩进
- 类名使用 PascalCase
- 函数和变量使用 snake_case
- 包含必要的中文注释

### 游戏设计模式
- 使用面向对象设计，分离玩家逻辑和游戏逻辑
- 统一的战斗系统接口，便于扩展新敌人
- 元素伤害倍率系统，支持正负伤害计算

### Git 工作流
- 主分支: master
- 推送到主分支时自动触发 Windows 可执行文件构建
- 构建产物自动上传为 GitHub Actions artifacts

## 扩展指南

### 添加新敌人
在 `Game.run()` 方法中添加新的战斗选项，使用 `battle()` 方法：
```python
self.battle("新敌人名称", 基础血量, 基础攻击力, 金币奖励, 
            {'火焰': 倍率, '水': 倍率, '土地': 倍率, '暗黑魔法': 倍率, '闪光': 倍率})
```

### 添加新商店物品
在 `shop()` 方法中扩展选择列表，添加相应的购买逻辑。

### 元素系统
- 正倍率: 对敌人造成伤害
- 负倍率: 敌人回血
- 0 倍率: 无效果

## 已知特性
- 彩蛋系统: 当暴击上限等于下限时触发奖励
- 隐藏结局: 收集足够氧气后在最终战斗中使用
- 难度倍率系统: 影响敌人血量和攻击力