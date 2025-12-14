# JOJO Soul (Refactored)

这是一个基于 Python 的 JOJO 奇妙冒险同人游戏，经过了重构和优化。

## 游戏简介

你降落在一个被普奇神父控制的大陆上，他想重启世界。你需要通过战斗和升级来阻止他，拯救这个世界！

## 游戏特色

- 🎭 基于 JOJO 奇妙冒险的原创剧情
- ⚔️ 五种元素属性的战斗系统（火焰、水、土地、暗黑魔法、闪光）
- 🛒 商店系统，购买装备升级角色
- 🎯 五种难度选择（无限金币版、简单、普通、坤难、炼狱）
- 🎮 简单易用的图形界面
- 🌟 隐藏结局和彩蛋系统

## 快速开始

### 环境要求

- Python 3.12+
- 支持 GUI 的操作系统环境

### 安装与运行

1. **克隆仓库**
   ```bash
   git clone git@github.com:chorusfruit-233/JOJOSoul-ng.git
   cd JOJOSoul-ng
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行游戏**
   ```bash
   python JOJOSoul-ng.py
   ```

### 打包为可执行文件

```bash
pyinstaller --onefile --windowed --name "JOJOSoul" JOJOSoul-ng.py
```

## 游戏玩法

### 角色属性

- **生命值**: 角色的生存能力
- **攻击力**: 基础伤害数值
- **金币**: 购买装备和道具的货币
- **伤害倍率**: 暴击伤害的范围（0x-2x）
- **纯氧数量**: 特殊道具，用于解锁隐藏结局

### 战斗系统

每个敌人对不同元素有不同的抗性：
- 🔥 **火焰**: 对植物类敌人有效
- 💧 **水**: 对火属性敌人有效
- 🌍 **土地**: 对水属性敌人有效
- 🌑 **暗黑魔法**: 高伤害元素
- ✨ **闪光**: 特殊效果，对某些敌人有奇效

### 地图区域

- 🌳 **丛林**: 对战树妖
- ⛰️ **山洞**: 对战吸血鬼
- 🦠 **腐化之地**: 对战沼泽怪
- 🌋 **熔岩地下城**: 对战熔岩怪
- 🌌 **天国**: 最终 Boss 战

### 商店物品

- 🛡️ **盔甲** [100G]: +30 生命上限
- ⚔️ **剑** [100G]: +5 攻击力
- 🧪 **药水** [50G]: 回满生命值
- 📦 **宝箱** [70G]: 随机属性变化

## 开发信息

详细的开发环境设置和贡献指南请查看 [DEVELOPMENT.md](DEVELOPMENT.md)

### 项目结构

```
JOJOSoul-ng/
├── JOJOSoul-ng.py    # 主游戏文件
├── requirements.txt  # 项目依赖
├── DEVELOPMENT.md    # 开发环境设置指南
├── README.md        # 项目说明文档
├── IFLOW.md         # iFlow 上下文文件
├── pyproject.toml   # 代码格式化配置
├── tests/           # 测试文件
└── .github/workflows/
    └── build.yml    # CI/CD 构建配置
```

## 版本历史

- **重构版**: 代码优化、添加测试、完善文档
- **原版**: 基础游戏功能

## 下载

### 最新版本
访问 [Releases 页面](https://github.com/chorusfruit-233/JOJOSoul-ng/releases) 下载最新稳定版本。

### 夜间构建
可以在 [Actions 页面](https://github.com/chorusfruit-233/JOJOSoul-ng/actions) 下载最新的测试构建。

详细的发布信息请查看 [RELEASE.md](RELEASE.md)

## 贡献者

- YricOTF (原作者)
- 重构优化

## 许可证

本项目为同人游戏作品，仅供学习和交流使用。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

感谢所有 JOJO 奇妙冒险的粉丝和支持者们！
