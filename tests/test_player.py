import sys
import os
import pytest

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
        if IS_CI:
            # CI 环境中跳过 GUI 相关测试
            pytest.skip("跳过 CI 环境中的 GUI 测试")

        # 设置显示模式为终端，确保测试有输出
        from display_manager import set_display_mode, get_display_manager

        original_mode = get_display_manager().get_mode()
        try:
            set_display_mode("terminal")
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
        finally:
            set_display_mode(original_mode)

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

    def test_new_attributes_initialization(self):
        """测试新属性初始化"""
        player = Player()
        assert player.element_damage_bonus == 1.0
        assert player.temporary_element_boost == 1.0
        assert player.temporary_boost_turns == 0
        assert player.skill_points == 0
        assert len(player.skills) == 5
        assert player.shield_active is False
        assert player.time_slow_active is False

    def test_skill_points_on_level_up(self):
        """测试升级获得技能点"""
        player = Player()
        original_points = player.skill_points

        # 升级一次
        player.level_up()
        assert player.skill_points == original_points + 1

        # 再次升级
        player.exp = player.exp_to_next
        player.level_up()
        assert player.skill_points == original_points + 2

    def test_skills_structure(self):
        """测试技能结构"""
        player = Player()

        expected_skills = ["火球术", "治疗术", "护盾", "元素爆发", "时间减缓"]
        assert list(player.skills.keys()) == expected_skills

        for skill_name, skill_data in player.skills.items():
            assert "level" in skill_data
            assert "cooldown" in skill_data
            assert "max_cooldown" in skill_data
            assert skill_data["level"] == 0
            assert skill_data["cooldown"] == 0
            assert skill_data["max_cooldown"] > 0

    def test_element_damage_bonus(self):
        """测试元素伤害加成"""
        player = Player()

        # 默认加成应该是1.0
        assert player.element_damage_bonus == 1.0

        # 增加加成
        player.element_damage_bonus = 1.5
        assert player.element_damage_bonus == 1.5

    def test_temporary_element_boost(self):
        """测试临时元素增强"""
        player = Player()

        # 默认应该是1.0，0回合
        assert player.temporary_element_boost == 1.0
        assert player.temporary_boost_turns == 0

        # 设置临时增强
        player.temporary_element_boost = 2.0
        player.temporary_boost_turns = 3
        assert player.temporary_element_boost == 2.0
        assert player.temporary_boost_turns == 3

    def test_shield_and_time_slow_status(self):
        """测试护盾和时间减缓状态"""
        player = Player()

        # 默认状态应该是False
        assert player.shield_active is False
        assert player.time_slow_active is False

        # 激活护盾
        player.shield_active = True
        assert player.shield_active is True

        # 激活时间减缓
        player.time_slow_active = True
        assert player.time_slow_active is True

    def test_show_stats_includes_new_attributes(self, capsys):
        """测试显示信息包含新属性"""
        if IS_CI:
            # CI 环境中跳过 GUI 相关测试
            pytest.skip("跳过 CI 环境中的 GUI 测试")

        # 设置显示模式为终端，确保测试有输出
        from display_manager import set_display_mode, get_display_manager

        original_mode = get_display_manager().get_mode()
        try:
            set_display_mode("terminal")
            player = Player()
            player.show_stats()
            captured = capsys.readouterr()
            assert "元素伤害加成: 1.00x" in captured.out
            assert "技能点: 0" in captured.out
        finally:
            set_display_mode(original_mode)

    def test_show_stats_with_temporary_boost(self, capsys):
        """测试显示临时增强状态"""
        if IS_CI:
            # CI 环境中跳过 GUI 相关测试
            pytest.skip("跳过 CI 环境中的 GUI 测试")

        # 设置显示模式为终端，确保测试有输出
        from display_manager import set_display_mode, get_display_manager

        original_mode = get_display_manager().get_mode()
        try:
            set_display_mode("terminal")
            player = Player()
            player.temporary_element_boost = 2.0
            player.temporary_boost_turns = 3
            player.show_stats()
            captured = capsys.readouterr()
            assert "临时元素增强: 2.00x (剩余3回合)" in captured.out
        finally:
            set_display_mode(original_mode)
