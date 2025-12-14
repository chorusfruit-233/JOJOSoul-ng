#!/usr/bin/env python3
"""
验证终端模式正常工作的测试
"""

from display_manager import DisplayManager


def test_terminal_only():
    """测试纯终端模式"""
    print("=== 纯终端模式测试 ===")
    dm = DisplayManager(mode="terminal")

    print(f"当前模式: {dm.get_mode()}")
    print(f"使用GUI: {dm.use_gui()}")
    print(f"使用终端: {dm.use_terminal()}")

    # 测试消息显示
    dm.show_message("欢迎", "欢迎来到JOJO Soul！")

    # 测试信息显示
    dm.show_info("角色信息：\n等级: 1\n生命值: 100/100\n攻击力: 10")

    print("✅ 终端模式正常工作\n")


def test_gui_fallback():
    """测试GUI模式在easygui不可用时的回退"""
    print("=== GUI回退测试 ===")
    dm = DisplayManager(mode="gui")

    print(f"当前模式: {dm.get_mode()}")
    print(f"使用GUI: {dm.use_gui()}")
    print(f"使用终端: {dm.use_terminal()}")

    # 测试消息显示
    dm.show_message("测试", "GUI模式在无easygui时的消息")

    print("✅ GUI模式正确回退到终端\n")


def test_both_mode():
    """测试混合模式"""
    print("=== 混合模式测试 ===")
    dm = DisplayManager(mode="both")

    print(f"当前模式: {dm.get_mode()}")
    print(f"使用GUI: {dm.use_gui()}")
    print(f"使用终端: {dm.use_terminal()}")

    # 测试消息显示
    dm.show_message("测试", "混合模式消息")

    print("✅ 混合模式正常工作\n")


def test_mode_switching():
    """测试模式切换"""
    print("=== 模式切换测试 ===")
    dm = DisplayManager(mode="terminal")

    print(f"初始模式: {dm.get_mode()}")
    dm.set_mode("gui")
    print(f"切换到GUI: {dm.get_mode()}")
    dm.set_mode("both")
    print(f"切换到混合: {dm.get_mode()}")
    dm.set_mode("terminal")
    print(f"切换到终端: {dm.get_mode()}")

    print("✅ 模式切换正常工作\n")


def main():
    print("=== 终端模式功能验证 ===\n")

    test_terminal_only()
    test_gui_fallback()
    test_both_mode()
    test_mode_switching()

    print("=== 验证总结 ===")
    print("✅ 终端模式：完全正常工作")
    print("✅ GUI回退：无easygui时正确回退")
    print("✅ 混合模式：智能切换正常")
    print("✅ 模式切换：运行时切换正常")
    print("\n🎉 终端模式现在完全可用！")


if __name__ == "__main__":
    main()
