import sys
import os
import importlib.util

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
