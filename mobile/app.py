"""
JOJO Soul 移动端主应用
基于 BeeWare/Toga 框架
"""

import sys
import os

# 添加父目录到路径，以便导入游戏代码
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from mobile.display_manager_mobile import get_mobile_display_manager


class JOJOSoulApp(toga.App):
    """JOJO Soul 移动端应用"""

    def startup(self):
        """应用启动"""
        # 设置主窗口
        self.main_window = toga.MainWindow(title=self.formal_name)

        # 创建移动端显示管理器
        self.display = get_mobile_display_manager(self)

        # 创建主界面
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # 添加标题
        title_label = toga.Label(
            "JOJO Soul",
            style=Pack(font_size=24, padding=(0, 10))
        )
        box.add(title_label)

        # 添加开始按钮
        start_button = toga.Button(
            "开始游戏",
            on_press=self.start_game,
            style=Pack(padding=10)
        )
        box.add(start_button)

        # 添加退出按钮
        exit_button = toga.Button(
            "退出",
            on_press=self.exit_app,
            style=Pack(padding=10)
        )
        box.add(exit_button)

        # 设置主窗口内容
        self.main_window.content = box

        # 显示主窗口
        self.main_window.show()

    def start_game(self, widget):
        """开始游戏"""
        # TODO: 启动游戏
        # 这里需要导入并运行游戏
        # 注意：需要修改游戏代码以支持移动端显示管理器
        self.main_window.info_dialog(
            "提示",
            "移动端游戏功能正在开发中..."
        )

    def exit_app(self, widget):
        """退出应用"""
        self.exit()


def main():
    """主函数"""
    return JOJOSoulApp()


if __name__ == "__main__":
    app = main()
    app.main_loop()