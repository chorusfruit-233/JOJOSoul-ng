# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

block_cipher = None

# 获取项目根目录
ROOT_DIR = Path(os.getcwd())

# 平台特定的配置
if sys.platform == "win32":
    # Windows 配置
    icon_path = ROOT_DIR / "icons" / "josoul.ico"
    exe_name = "JOJOSoul"
elif sys.platform == "darwin":
    # macOS 配置
    icon_path = ROOT_DIR / "icons" / "josoul.icns"
    exe_name = "JOJOSoul"
else:
    # Linux 配置
    icon_path = ROOT_DIR / "icons" / "josoul.png"
    exe_name = "josoul"

# 检查图标文件是否存在
use_icon = icon_path.exists()

a = Analysis(
    ["JOJOSoul-ng.py"],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        # 添加数据文件（如果有）
        # (str(ROOT_DIR / "data"), "data"),
    ],
    hiddenimports=[
        # 隐藏导入
        "easygui",
        "tkinter",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if use_icon else None,
)

# macOS 特定配置：创建 .app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="JOJOSoul.app",
        icon=str(icon_path) if use_icon else None,
        bundle_identifier="com.josoul.game",
        info_plist={
            "CFBundleName": "JOJO Soul",
            "CFBundleDisplayName": "JOJO Soul",
            "CFBundleVersion": "2.3.0",
            "CFBundleShortVersionString": "2.3.0",
            "CFBundleExecutable": exe_name,
            "NSHighResolutionCapable": True,
        },
    )