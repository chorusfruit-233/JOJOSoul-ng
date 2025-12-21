import sys
import os
import importlib.util
from unittest.mock import patch

# 检查是否在 CI 环境中
IS_CI = os.environ.get("CI", "false").lower() == "true"

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 动态导入模块
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
Player = module.Player
Game = module.Game


class TestCoreLogic:
    """测试核心游戏逻辑，不涉及 GUI"""

    def test_player_creation(self):
        """测试玩家创建"""
        player = Player("测试玩家")
        assert player.name == "测试玩家"
        assert player.level == 1
        assert player.life == 100.0
        assert player.attack == 10.0
        assert player.coin == 100

    def test_player_level_up(self):
        """测试玩家升级"""
        player = Player()
        initial_level = player.level
        initial_attack = player.attack

        # 给予足够经验升级
        player.gain_exp(150)

        assert player.level > initial_level
        assert player.attack > initial_attack
        assert player.life == player.max_life  # 升级应该回满血

    def test_game_initialization(self):
        """测试游戏初始化"""
        game = Game()
        assert game.lmode == 1.0
        assert game.amode == 1.0
        assert len(game.elements) == 5
        assert isinstance(game.player, Player)

    def test_attack_multiplier_range(self):
        """测试攻击倍率在范围内"""
        game = Game()
        game.player.crit_min = 1
        game.player.crit_max = 3

        for _ in range(100):
            multiplier = game.get_attack_multiplier()
            assert 1 <= multiplier <= 3

    def test_stat_anomalies_check(self):
        """测试属性异常检查"""
        game = Game()

        # 测试正常情况
        game.check_stat_anomalies()

        # 测试彩蛋情况
        game.player.crit_max = 1
        game.player.crit_min = 1
        original_coin = game.player.coin
        game.check_stat_anomalies()
        assert game.player.coin > original_coin

    @patch("random.randint")
    def test_open_chest_crit_max_boundary(self, mock_randint):
        """测试宝箱抽奖中crit_max减少到低于crit_min时的边界检查"""
        game = Game()
        game.player.coin = 100
        game.player.crit_min = 5
        game.player.crit_max = 6  # 当前上限比下限高1

        # 模拟抽奖结果：outcome=3 (crit_max修改), val=-1 (减少1)
        mock_randint.side_effect = [
            3,
            -1,
        ]  # 第一个随机数是outcome，第二个是val
        game.open_chest()

        # 验证边界检查生效：crit_max减少到5，不低于crit_min
        assert game.player.crit_max == 5
        assert game.player.crit_min == 5
        assert game.player.crit_min <= game.player.crit_max
        assert game.player.coin == 30  # 100 - 70

    @patch("random.randint")
    def test_open_chest_crit_min_boundary(self, mock_randint):
        """测试宝箱抽奖中crit_min增加到超过crit_max时的边界检查"""
        game = Game()
        game.player.coin = 100
        game.player.crit_min = 5
        game.player.crit_max = 5  # 当前上限等于下限

        # 模拟抽奖结果：outcome=4 (crit_min修改), val=1 (增加1)
        mock_randint.side_effect = [4, 1]  # 第一个随机数是outcome，第二个是val
        game.open_chest()

        # 验证边界检查生效：crit_min增加到6，crit_max同步提升到6
        assert game.player.crit_min == 6
        assert game.player.crit_max == 6  # 上限应同步提升
        assert game.player.crit_min <= game.player.crit_max
        assert game.player.coin == 30  # 100 - 70
