"""
移动端显示管理器 - 基于 Toga GUI 框架
"""

import sys


class MobileDisplayManager:
    """移动端显示管理器"""

    def __init__(self, app=None):
        """
        初始化移动端显示管理器

        Args:
            app: Toga 应用实例
        """
        self.app = app
        self.mode = "mobile"
        self.gui_available = True
        self.current_window = None

    def set_mode(self, mode):
        """设置显示模式（移动端固定为 mobile）"""
        # 移动端固定使用 mobile 模式
        self.mode = "mobile"

    def get_mode(self):
        """获取当前显示模式"""
        return self.mode

    def use_gui(self):
        """移动端始终使用 GUI"""
        return True

    def use_terminal(self):
        """移动端不使用终端"""
        return False

    def show_message(self, title, message):
        """
        显示消息对话框

        Args:
            title (str): 消息标题
            message (str): 消息内容
        """
        # TODO: 使用 Toga 创建消息对话框
        # 示例代码（需要导入 toga）:
        # from toga import Box, Label, Button
        # self._show_dialog(title, message)
        print(f"[{title}] {message}")

    def show_info(self, info):
        """
        显示信息

        Args:
            info (str): 信息内容
        """
        # TODO: 使用 Toga 显示信息
        print(info)

    def get_choice(self, title, choices):
        """
        获取用户选择

        Args:
            title (str): 选择标题
            choices (list): 选择项列表

        Returns:
            str: 用户选择的项目
        """
        # TODO: 使用 Toga 创建选择列表
        # 示例代码:
        # from toga import Selection
        # selection = Selection(items=choices)
        # return selection.value
        return choices[0] if choices else None

    def get_yes_no(self, title, message):
        """
        获取是/否选择

        Args:
            title (str): 对话框标题
            message (str): 询问内容

        Returns:
            bool: True表示是，False表示否
        """
        # TODO: 使用 Toga 创建确认对话框
        # 示例代码:
        # from toga import ConfirmationDialog
        # dialog = ConfirmationDialog(title, message)
        # return dialog.result
        return True

    def get_input(self, title, prompt):
        """
        获取文本输入

        Args:
            title (str): 输入框标题
            prompt (str): 输入提示

        Returns:
            str: 用户输入的文本
        """
        # TODO: 使用 Toga 创建输入对话框
        # 示例代码:
        # from toga import TextInput
        # input_field = TextInput(placeholder=prompt)
        # return input_field.value
        return "勇者"

    def show_battle_info(self, title, message):
        """
        显示战斗相关信息

        Args:
            title (str): 标题
            message (str): 消息内容
        """
        # TODO: 使用 Toga 显示战斗信息
        print(f"\n=== {title} ===")
        print(message)

    def _show_dialog(self, title, message):
        """显示对话框（内部方法）"""
        # TODO: 实现 Toga 对话框
        pass


# 创建全局移动端显示管理器实例
mobile_display_manager = None


def get_mobile_display_manager(app=None):
    """获取全局移动端显示管理器实例"""
    global mobile_display_manager
    if mobile_display_manager is None:
        mobile_display_manager = MobileDisplayManager(app)
    return mobile_display_manager


def set_mobile_display_manager(display_manager):
    """设置全局移动端显示管理器"""
    global mobile_display_manager
    mobile_display_manager = display_manager