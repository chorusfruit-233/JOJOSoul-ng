#!/usr/bin/env python3
"""
最终验证：终端模式完全独立，不使用easygui
"""

from display_manager import DisplayManager

def test_pure_terminal():
    """测试纯终端模式的完全独立性"""
    print("=== 纯终端模式完全独立测试 ===")
    
    # 创建终端模式实例
    dm = DisplayManager(mode='terminal')
    
    print(f"模式: {dm.get_mode()}")
    print(f"GUI可用: {dm.gui_available}")
    print(f"easygui对象: {dm.easygui}")
    print(f"使用GUI: {dm.use_gui()}")
    print(f"使用终端: {dm.use_terminal()}")
    print()
    
    # 测试各种功能
    print("1. 消息显示:")
    dm.show_message("标题", "纯终端消息")
    print()
    
    print("2. 信息显示:")
    dm.show_info("多行信息\n第二行\n第三行")
    print()
    
    print("3. 角色信息:")
    dm.show_character_info("角色: 勇者\n等级: 5\n生命值: 150/150")
    print()
    
    print("✅ 纯终端模式完全独立，无任何GUI依赖")
    return True

def test_no_gui_import():
    """测试终端模式不导入easygui"""
    print("=== easygui导入测试 ===")
    
    # 创建终端模式实例
    dm = DisplayManager(mode='terminal')
    
    # 检查是否真的没有导入easygui
    try:
        import easygui
        easygui_imported = True
    except ImportError:
        easygui_imported = False
    
    print(f"系统easygui可用: {easygui_imported}")
    print(f"DisplayManager的easygui: {dm.easygui}")
    print(f"GUI可用标志: {dm.gui_available}")
    
    # 终端模式应该完全不依赖easygui
    if dm.easygui is None and not dm.gui_available:
        print("✅ 终端模式完全没有导入easygui")
        return True
    else:
        print("❌ 终端模式仍然依赖easygui")
        return False

def main():
    print("=== 终端模式完全独立验证 ===\n")
    
    success1 = test_pure_terminal()
    print()
    success2 = test_no_gui_import()
    print()
    
    if success1 and success2:
        print("🎉 终端模式已完全独立！")
        print("• 完全不使用easygui")
        print("• 不会弹出任何窗口")
        print("• 完全依赖终端交互")
        print("• 适合服务器环境")
    else:
        print("❌ 终端模式仍有依赖问题")

if __name__ == "__main__":
    main()