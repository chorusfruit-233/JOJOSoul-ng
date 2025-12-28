# JOJO Soul 移动端适配

本目录包含移动端（Android/iOS）适配的相关文件和配置。

## 技术栈

- **BeeWare** - Python 原生移动端开发框架
- **Toga** - BeeWare 的 GUI 工具包

## 开发环境设置

### 安装依赖

```bash
# 安装 Briefcase（BeeWare 的打包工具）
pip install briefcase

# 安装 Toga
pip install toga
```

### 开发模式运行

```bash
# 运行开发版本
briefcase dev

# Android
briefcase run android

# iOS (需要 macOS)
briefcase run ios
```

## 构建发布版本

### Android APK

```bash
briefcase build android
briefcase package android
```

### iOS IPA (需要 macOS)

```bash
briefcase build ios
briefcase package ios
```

## 项目结构

```
mobile/
├── __init__.py
├── app.py              # 移动端主应用
├── display_manager_mobile.py  # 移动端显示管理器
├── resources/          # 资源文件
│   ├── icons/          # 应用图标
│   └── fonts/          # 字体文件
├── build_android.sh    # Android 构建脚本
└── build_ios.sh        # iOS 构建脚本
```

## 注意事项

1. **触摸交互**：移动端需要适配触摸操作，替代鼠标点击
2. **横竖屏**：游戏需要支持横竖屏切换
3. **存档路径**：使用平台特定的存档目录
4. **性能优化**：移动端性能有限，需要优化渲染和计算

## 待实现功能

- [ ] 移动端显示管理器
- [ ] 触摸交互适配
- [ ] 横竖屏支持
- [ ] 存档路径适配
- [ ] 应用图标
- [ ] 启动画面
- [ ] 权限处理（Android）

## 参考资料

- [BeeWare 官方文档](https://beeware.org/)
- [Toga 文档](https://toga.readthedocs.io/)
- [Briefcase 文档](https://briefcase.readthedocs.io/)