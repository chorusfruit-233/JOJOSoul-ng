import sys
import os
from unittest.mock import patch

# 检查是否在 CI 环境中
IS_CI = os.environ.get("CI", "false").lower() == "true"

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 动态导入模块
import importlib.util

spec = importlib.util.spec_from_file_location(
    "JOJOSoul",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "JOJOSoul-ng.py",
    ),
)
module = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(module)
except Exception as e:
    print(f"模块加载失败: {e}")
    raise
Game = module.Game
Player = module.Player


class TestGame:
    def test_game_initialization(self):
        """测试游戏初始化"""
        game = Game()
        assert game.lmode == 1.0
        assert game.amode == 1.0
        assert game.elements == ["火焰", "水", "土地", "暗黑魔法", "闪光"]
        assert isinstance(game.player, Player)

    def test_get_attack_multiplier(self):
        """测试获取攻击倍率"""
        game = Game()
        game.player.crit_min = 1
        game.player.crit_max = 3

        # 测试多次获取倍率，应该在范围内
        for _ in range(100):
            multiplier = game.get_attack_multiplier()
            assert 1 <= multiplier <= 3

    def test_check_stat_anomalies(self, capsys):
        """测试属性异常检查"""
        game = Game()

        # 测试正常情况
        game.check_stat_anomalies()
        captured = capsys.readouterr()
        assert captured.out == ""

        # 测试彩蛋情况
        game.player.crit_max = 1
        game.player.crit_min = 1
        original_coin = game.player.coin
        game.check_stat_anomalies()
        captured = capsys.readouterr()
        assert "恭喜你发现彩蛋！奖励810金币！" in captured.out
        assert game.player.coin == original_coin + 810
        assert game.player.crit_max == 2
        assert game.player.crit_min == 0

        # 测试异常情况
        game.player.crit_max = -1
        game.player.crit_min = 0
        game.check_stat_anomalies()
        captured = capsys.readouterr()
        assert "属性异常，已恢复" in captured.out
        assert game.player.crit_max == 2
        assert game.player.crit_min == 0

    @patch("easygui.choicebox")
    @patch("sys.exit")  # Mock sys.exit 避免测试时退出
    def test_set_difficulty(self, mock_choicebox, mock_exit):
        """测试难度设置"""
        game = Game()

        # 测试无限金币版
        mock_choicebox.return_value = "无限金币版"
        game.set_difficulty()
        assert game.player.coin == 1145141919810

        # 测试简单难度
        mock_choicebox.return_value = "简单"
        game.set_difficulty()
        assert game.lmode == 0.7
        assert game.amode == 0.8

        # 测试普通难度
        mock_choicebox.return_value = "普通"
        game.set_difficulty()
        assert game.lmode == 1.0
        assert game.amode == 1.0

        # 测试坤难难度
        mock_choicebox.return_value = "坤难"
        game.set_difficulty()
        assert game.lmode == 1.3
        assert game.amode == 1.3

        # 测试炼狱难度
        mock_choicebox.return_value = "炼狱"
        game.set_difficulty()
        assert game.lmode == 1.5
        assert game.amode == 1.5
