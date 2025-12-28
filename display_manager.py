"""
DisplayManager - 统一的游戏显示管理器
支持GUI和终端双模式，可在运行时切换
"""

import sys


class DisplayManager:
    """统一的显示管理器，支持完全独立的GUI和终端模式"""

    def __init__(self, mode="both"):
        """
        初始化显示管理器

        Args:
            mode (str): 显示模式，'gui', 'terminal', 或 'both'
        """
        self.mode = mode
        self.gui_available = False
        self.easygui = None

        # 终端模式下完全不尝试导入easygui，避免触发GUI相关操作
        if mode == "terminal":
            return

        # 只有在需要GUI时才尝试导入easygui
        if mode in ["gui", "both"]:
            try:
                import easygui

                self.easygui = easygui
                self.gui_available = True
            except ImportError:
                if mode == "gui":
                    print(
                        "警告: easygui未安装，GUI功能将无法使用",
                        file=sys.stderr,
                    )

    def set_mode(self, mode):
        """
        设置显示模式

        Args:
            mode (str): 显示模式，'gui', 'terminal', 或 'both'
        """
        if mode == "gui" and not self.gui_available:
            print("警告: easygui不可用，GUI功能将无法使用", file=sys.stderr)
        self.mode = mode

    def get_mode(self):
        """获取当前显示模式"""
        return self.mode

    def use_gui(self):
        """检查是否使用GUI"""
        return self.mode in ["gui", "both"] and self.gui_available

    def use_terminal(self):
        """检查是否使用终端"""
        return (
            self.mode == "terminal"
            or self.mode == "both"
            or (self.mode == "gui" and not self.gui_available)
        )

    def show_message(self, title, message):
        """
        显示消息（根据模式独立显示）

        Args:
            title (str): 消息标题
            message (str): 消息内容
        """
        # GUI显示 - 优先尝试GUI
        if self.use_gui() and self.easygui:
            try:
                self.easygui.msgbox(message, title)
                return  # GUI成功，不输出终端
            except Exception:
                # GUI失败，继续使用终端
                if self.mode == "gui":
                    print(f"GUI失败，切换到终端模式", file=sys.stderr)

        # 终端显示 - GUI不可用或失败时使用
        if self.use_terminal():
            print(f"[{title}] {message}")

    def show_info(self, info):
        """
        显示信息（根据模式显示）

        Args:
            info (str): 信息内容
        """
        # GUI显示 - 优先尝试GUI
        if self.use_gui() and self.easygui:
            try:
                self.easygui.msgbox(info, "信息")
                return  # GUI成功，不输出终端
            except Exception:
                # GUI失败，继续使用终端
                if self.mode == "gui":
                    print(f"GUI失败，切换到终端模式", file=sys.stderr)

        # 终端显示 - GUI不可用或失败时使用
        if self.use_terminal():
            print(info)

    def get_choice(self, title, choices):
        """
        获取用户选择（根据模式独立工作）

        Args:
            title (str): 选择标题
            choices (list): 选择项列表

        Returns:
            str: 用户选择的项目，如果取消则返回None
        """
        # 终端模式 - 完全不接触easygui
        if self.mode == "terminal" or not self.gui_available:
            print(f"\n{title}")
            for i, choice in enumerate(choices):
                print(f"{i+1}. {choice}")
            print("0. 取消")

            while True:
                try:
                    selection = input("请选择（输入数字）: ").strip()
                    if selection == "0":
                        print("已取消选择")
                        return None
                    choice_index = int(selection) - 1
                    if 0 <= choice_index < len(choices):
                        selected = choices[choice_index]
                        print(f"已选择: {selected}")
                        return selected
                    else:
                        print(f"无效选择，请输入0-{len(choices)}之间的数字")
                except ValueError:
                    print("请输入有效数字")
                except KeyboardInterrupt:
                    print("\n用户中断，取消选择")
                    return None

        # GUI模式 - 仅使用GUI
        elif self.mode == "gui" and self.gui_available:
            return self.easygui.choicebox(title, choices=choices)

        # 混合模式 - 先尝试GUI，失败时使用终端
        elif self.mode == "both":
            if self.gui_available:
                try:
                    result = self.easygui.choicebox(title, choices=choices)
                    if result is not None:
                        return result
                except Exception:
                    print("GUI失败，使用终端模式", file=sys.stderr)

            # 终端回退
            print(f"\n{title}")
            for i, choice in enumerate(choices):
                print(f"{i+1}. {choice}")
            print("0. 取消")

            while True:
                try:
                    selection = input("请选择（输入数字）: ").strip()
                    if selection == "0":
                        return None
                    choice_index = int(selection) - 1
                    if 0 <= choice_index < len(choices):
                        return choices[choice_index]
                    else:
                        print(f"无效选择，请输入0-{len(choices)}之间的数字")
                except ValueError:
                    print("请输入有效数字")
                except KeyboardInterrupt:
                    return None

        return None

    def get_yes_no(self, title, message):
        """
        获取是/否选择（根据模式独立工作）

        Args:
            title (str): 对话框标题
            message (str): 询问内容

        Returns:
            bool: True表示是，False表示否
        """
        # 终端模式 - 完全不接触easygui
        if self.mode == "terminal" or not self.gui_available:
            print(f"\n{title}")
            print(f"{message}")

            while True:
                try:
                    choice = input("请选择 (1=是, 2=否): ").strip()
                    if choice in ["1", "y", "yes", "是"]:
                        print("已选择: 是")
                        return True
                    elif choice in ["2", "n", "no", "否"]:
                        print("已选择: 否")
                        return False
                    else:
                        print("请输入 1/2 或 y/n")
                except KeyboardInterrupt:
                    print("\n用户中断，选择否")
                    return False

        # GUI模式 - 仅使用GUI
        elif self.mode == "gui" and self.gui_available:
            result = self.easygui.buttonbox(
                message, title, choices=["是", "否"]
            )
            return result == "是"

        # 混合模式 - 先尝试GUI，失败时使用终端
        elif self.mode == "both":
            if self.gui_available:
                try:
                    result = self.easygui.buttonbox(
                        message, title, choices=["是", "否"]
                    )
                    if result is not None:
                        return result == "是"
                except Exception:
                    print("GUI失败，使用终端模式", file=sys.stderr)

            # 终端回退
            print(f"\n{title}")
            print(f"{message}")

            while True:
                try:
                    choice = input("请选择 (1=是, 2=否): ").strip()
                    if choice in ["1", "y", "yes", "是"]:
                        return True
                    elif choice in ["2", "n", "no", "否"]:
                        return False
                    else:
                        print("请输入 1/2 或 y/n")
                except KeyboardInterrupt:
                    return False

        return False

    def get_input(self, title, prompt):
        """
        获取文本输入（根据模式独立工作）

        Args:
            title (str): 输入框标题
            prompt (str): 输入提示

        Returns:
            str: 用户输入的文本，如果取消则返回None
        """
        # 终端模式 - 完全不接触easygui
        if self.mode == "terminal" or not self.gui_available:
            print(f"\n{title}")
            while True:
                try:
                    result = input(f"{prompt}: ").strip()
                    return result if result else None
                except KeyboardInterrupt:
                    print("\n用户中断，取消输入")
                    return None

        # GUI模式 - 仅使用GUI
        elif self.mode == "gui" and self.gui_available:
            return self.easygui.enterbox(prompt, title)

        # 混合模式 - 先尝试GUI，失败时使用终端
        elif self.mode == "both":
            if self.gui_available:
                try:
                    result = self.easygui.enterbox(prompt, title)
                    if result is not None:
                        return result
                except Exception:
                    print("GUI失败，使用终端模式", file=sys.stderr)

            # 终端回退
            print(f"\n{title}")
            while True:
                try:
                    result = input(f"{prompt}: ").strip()
                    return result if result else None
                except KeyboardInterrupt:
                    return None

        return None

    def show_character_info(self, player_or_info):
        """
        显示角色信息

        Args:
            player_or_info: 玩家对象或信息字符串
        """
        # 如果是字符串，直接显示
        if isinstance(player_or_info, str):
            info = f"=== 角色信息 ===\n{player_or_info}\n================"
        else:
            # 如果是player对象，生成信息
            info = f"""
=== 角色信息 ===
等级: {player_or_info.level}
经验值: {player_or_info.exp}/{player_or_info.exp_needed}
生命值: {player_or_info.life}/{player_or_info.max_life}
攻击力: {player_or_info.attack}
金币: {player_or_info.coin}
暴击倍率: {player_or_info.crit_min}-{player_or_info.crit_max}
氧气数量: {player_or_info.oxygen}
================
"""

        # GUI显示 - 优先尝试GUI
        if self.use_gui() and self.easygui:
            try:
                self.easygui.msgbox(info, "角色信息")
                return  # GUI成功，不输出终端
            except Exception:
                # GUI失败，继续使用终端
                if self.mode == "gui":
                    print(f"GUI失败，切换到终端模式", file=sys.stderr)

        # 终端显示 - GUI不可用或失败时使用
        if self.use_terminal():
            print(info)

    def show_battle_info(self, title, message):
        """
        显示战斗相关信息
        """
        # GUI显示 - 优先尝试GUI
        if self.use_gui() and self.easygui:
            try:
                self.easygui.msgbox(message, title)
                return  # GUI成功，不输出终端
            except Exception:
                # GUI失败，继续使用终端
                if self.mode == "gui":
                    print(f"GUI失败，切换到终端模式", file=sys.stderr)

        # 终端显示 - GUI不可用或失败时使用
        if self.use_terminal():
            print(f"\n=== {title} ===")
            print(message)


# 全局显示管理器实例（默认混合模式）
display_manager = DisplayManager(mode="both")


def get_display_manager():
    """获取全局显示管理器实例"""
    return display_manager


def set_display_mode(mode):
    """设置全局显示模式

    Args:
        mode (str): 'gui', 'terminal', 或 'both'
    """
    display_manager.set_mode(mode)


def get_display_mode():
    """获取当前显示模式"""
    return display_manager.get_mode()
