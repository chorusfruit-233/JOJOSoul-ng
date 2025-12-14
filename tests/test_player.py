import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 动态导入模块
import importlib.util

spec = importlib.util.spec_from_file_location(
    "JOJOSoul",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "JOJOSoul-ng.py"
    ),
)
module = importlib.util.module_from_spec(spec)
sys.modules["JOJOSoul"] = module
spec.loader.exec_module(module)
Player = module.Player


class TestPlayer:
    def test_player_initialization(self):
        """测试玩家初始化"""
        player = Player()
        assert player.name == "勇者"
        assert player.life == 100.0
        assert player.max_life == 100.0
        assert player.attack == 10.0
        assert player.coin == 100
        assert player.crit_max == 2
        assert player.crit_min == 0
        assert player.oxygen == 0
        assert player.level == 1
        assert player.exp == 0
        assert player.exp_to_next == 100
        assert player.monsters_defeated == 0

    def test_is_alive(self):
        """测试玩家存活状态"""
        player = Player()
        assert player.is_alive() is True

        player.life = 0
        assert player.is_alive() is False

        player.life = -10
        assert player.is_alive() is False

    def test_heal_full(self):
        """测试完全恢复生命值"""
        player = Player()
        player.life = 50.0
        player.heal_full()
        assert player.life == player.max_life

    def test_show_stats(self, capsys):
        """测试显示角色信息"""
        player = Player()
        player.show_stats()
        captured = capsys.readouterr()
        assert "角色: 勇者" in captured.out
        assert "等级: 1" in captured.out
        assert "生命值: 100.0/100.0" in captured.out
        assert "伤害: 10.0" in captured.out
        assert "金币: 100" in captured.out
        assert "伤害倍率: 0x - 2x" in captured.out
        assert "纯氧数量: 0" in captured.out
        assert "击败怪物: 0" in captured.out

    def test_gain_exp(self):
        """测试经验值获得"""
        player = Player()
        player.gain_exp(50)
        assert player.exp == 50
        assert player.level == 1

        # 测试升级
        player.gain_exp(60)
        assert player.level == 2
        assert player.exp == 10  # 110 - 100
        assert player.exp_to_next == 150  # 100 * 1.5
        assert player.max_life == 110  # 100 + 10
        assert player.attack == 12  # 10 + 2
