#!/usr/bin/env python3
"""
测试DisplayManager的独立模式功能
"""

from display_manager import DisplayManager


def test_gui_mode():
    print("=== 测试GUI模式 ===")
    dm = DisplayManager(mode="gui")
    print(f"当前模式: {dm.get_mode()}")
    print(f"使用GUI: {dm.use_gui()}")
    print(f"使用终端: {dm.use_terminal()}")
    print()


def test_terminal_mode():
    print("=== 测试终端模式 ===")
    dm = DisplayManager(mode="terminal")
    print(f"当前模式: {dm.get_mode()}")
    print(f"使用GUI: {dm.use_gui()}")
    print(f"使用终端: {dm.use_terminal()}")

    # 测试终端显示
    dm.show_message("测试", "这是纯终端模式的消息")

    # 测试终端选择（模拟）
    print("\n在交互环境中，这里会显示选择菜单")
    choices = ["选项1", "选项2", "选项3"]
    print(f"选择项: {choices}")
    print("用户需要输入数字进行选择")
    print()


def test_both_mode():
    print("=== 测试混合模式 ===")
    dm = DisplayManager(mode="both")
    print(f"当前模式: {dm.get_mode()}")
    print(f"使用GUI: {dm.use_gui()}")
    print(f"使用终端: {dm.use_terminal()}")

    # 测试混合显示
    dm.show_message("测试", "这是混合模式的消息")
    print()


def test_mode_switching():
    print("=== 测试模式切换 ===")
    dm = DisplayManager(mode="terminal")

    print(f"初始模式: {dm.get_mode()}")
    dm.set_mode("gui")
    print(f"切换后模式: {dm.get_mode()}")
    dm.set_mode("both")
    print(f"再次切换后模式: {dm.get_mode()}")
    print()


def main():
    print("=== DisplayManager独立模式测试 ===\n")

    test_gui_mode()
    test_terminal_mode()
    test_both_mode()
    test_mode_switching()

    print("=== 测试总结 ===")
    print("1. GUI模式：仅使用GUI界面，适合图形环境")
    print("2. 终端模式：仅使用终端界面，适合命令行环境")
    print("3. 混合模式：优先GUI，失败时回退到终端")
    print("4. 模式切换：运行时可以动态切换显示模式")
    print("\n用户可以根据需要选择合适的模式，每种模式都能提供完整的游戏体验！")


if __name__ == "__main__":
    main()
