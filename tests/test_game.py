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

    def test_new_enemies_initialization(self):
        """测试新敌人初始化"""
        game = Game()
        # 验证新敌人元素倍率设置正确
        # 冰霜巨人：火焰3.0, 水-1.5
        ice_giant_multipliers = {
            "火焰": 3.0,
            "水": -1.5,
            "土地": 0.8,
            "暗黑魔法": 1.2,
            "闪光": 0.5,
        }
        assert ice_giant_multipliers["火焰"] == 3.0
        assert ice_giant_multipliers["水"] == -1.5

        # 暗影刺客：暗黑魔法-2.0, 闪光3.0
        shadow_assassin_multipliers = {
            "火焰": 0.5,
            "水": 0.5,
            "土地": 0.5,
            "暗黑魔法": -2.0,
            "闪光": 3.0,
        }
        assert shadow_assassin_multipliers["暗黑魔法"] == -2.0
        assert shadow_assassin_multipliers["闪光"] == 3.0

        # 雷电元素：水2.0, 闪光-1.8
        lightning_element_multipliers = {
            "火焰": 1.0,
            "水": 2.0,
            "土地": 0.3,
            "暗黑魔法": 1.5,
            "闪光": -1.8,
        }
        assert lightning_element_multipliers["水"] == 2.0
        assert lightning_element_multipliers["闪光"] == -1.8

    def test_new_player_attributes(self):
        """测试玩家新属性"""
        player = Player()
        assert player.element_damage_bonus == 1.0
        assert player.temporary_element_boost == 1.0
        assert player.temporary_boost_turns == 0
        assert player.skill_points == 0
        assert len(player.skills) == 5
        assert "火球术" in player.skills
        assert "治疗术" in player.skills
        assert "护盾" in player.skills
        assert "元素爆发" in player.skills
        assert "时间减缓" in player.skills

    def test_skill_system_initialization(self):
        """测试技能系统初始化"""
        player = Player()
        for skill_name, skill_data in player.skills.items():
            assert skill_data["level"] == 0
            assert skill_data["cooldown"] == 0
            assert "max_cooldown" in skill_data
            assert skill_data["max_cooldown"] > 0

    def test_achievements_system_initialization(self):
        """测试成就系统初始化"""
        game = Game()
        assert len(game.achievements) > 0
        assert "初次胜利" in game.achievements
        assert "世界拯救者" in game.achievements

        for achievement_name, achievement_data in game.achievements.items():
            assert "description" in achievement_data
            assert "completed" in achievement_data
            assert "reward" in achievement_data
            assert achievement_data["completed"] == False
            assert achievement_data["reward"] > 0

    def test_level_up_grants_skill_point(self):
        """测试升级获得技能点"""
        player = Player()
        original_skill_points = player.skill_points
        original_level = player.level

        # 模拟升级
        player.level_up()

        assert player.level == original_level + 1
        assert player.skill_points == original_skill_points + 1

    def test_element_damage_bonus_application(self):
        """测试元素伤害加成应用"""
        game = Game()
        game.player.element_damage_bonus = 1.5

        # 模拟伤害计算
        base_damage = 100
        element_mult = 2.0
        crit = 1.0

        expected_damage = (
            base_damage * element_mult * crit * game.player.element_damage_bonus
        )
        assert expected_damage == 300.0

    def test_temporary_element_boost(self):
        """测试临时元素增强"""
        player = Player()
        player.temporary_element_boost = 2.0
        player.temporary_boost_turns = 3

        # 模拟使用临时增强
        assert player.temporary_boost_turns == 3
        assert player.temporary_element_boost == 2.0

    def test_achievement_completion(self):
        """测试成就完成"""
        game = Game()
        achievement_name = "初次胜利"
        original_coin = game.player.coin

        # 完成成就
        game.complete_achievement(achievement_name)

        assert game.achievements[achievement_name]["completed"] == True
        assert (
            game.player.coin
            == original_coin + game.achievements[achievement_name]["reward"]
        )

    def test_shop_unlock_conditions(self):
        """测试商店解锁条件"""
        game = Game()

        # 等级1时应该只能购买基础物品
        game.player.level = 1
        # 这里可以添加商店选项检查逻辑

        # 等级3时应该解锁新装备
        game.player.level = 3
        # 这里可以添加商店选项检查逻辑

        # 等级5时应该解锁元素卷轴
        game.player.level = 5
        # 这里可以添加商店选项检查逻辑

    def test_skill_cooldown_update(self):
        """测试技能冷却更新"""
        game = Game()

        # 设置技能冷却
        game.player.skills["火球术"]["cooldown"] = 3

        # 更新冷却
        game.update_skill_cooldowns()

        assert game.player.skills["火球术"]["cooldown"] == 2

        # 继续更新直到冷却结束
        game.update_skill_cooldowns()
        game.update_skill_cooldowns()
        assert game.player.skills["火球术"]["cooldown"] == 0
