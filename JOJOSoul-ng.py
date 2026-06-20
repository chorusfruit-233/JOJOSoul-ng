import time
import sys
import random
import os
import platform
from pathlib import Path

# 游戏版本
VERSION = "2.3.0"


def get_save_path() -> Path:
    """
    获取跨平台的存档文件路径

    Returns:
        Path: 存档文件的完整路径
    """
    system = platform.system()

    if system == "Windows":
        # Windows: %APPDATA%\JOJOSoul\savegame.dat
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        save_dir = Path(appdata) / "JOJOSoul"
    elif system == "Darwin":
        # macOS: ~/Library/Application Support/JOJOSoul/savegame.dat
        save_dir = Path.home() / "Library" / "Application Support" / "JOJOSoul"
    else:
        # Linux/Unix: ~/.josoul/savegame.dat
        save_dir = Path.home() / ".josoul"

    # 确保目录存在
    save_dir.mkdir(parents=True, exist_ok=True)

    return save_dir / "savegame.dat"


class Player:
    def __init__(self, name="勇者", display=None):
        self.name = name
        self.life = 100.0
        self.max_life = 100.0
        self.attack = 10.0
        self.coin = 100
        self.crit_max = 2  # aup
        self.crit_min = 0  # adown
        self.oxygen = 0  # O2
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        self.monsters_defeated = 0
        # 新增属性
        self.element_damage_bonus = 1.0  # 元素伤害倍率加成
        self.temporary_element_boost = 1.0  # 临时元素伤害增强
        self.temporary_boost_turns = 0  # 临时增强剩余回合数
        # 技能系统
        self.skill_points = 0  # 技能点
        self.skills = {
            "火球术": {"level": 0, "cooldown": 0, "max_cooldown": 3},
            "治疗术": {"level": 0, "cooldown": 0, "max_cooldown": 4},
            "护盾": {"level": 0, "cooldown": 0, "max_cooldown": 5},
            "元素爆发": {"level": 0, "cooldown": 0, "max_cooldown": 6},
            "时间减缓": {"level": 0, "cooldown": 0, "max_cooldown": 8},
        }
        # 技能状态
        self.shield_active = False  # 护盾状态
        self.time_slow_active = False  # 时间减缓状态
        # 显示管理器
        self.display = display

    def is_alive(self):
        return self.life > 0

    def heal_full(self):
        self.life = self.max_life

    def show_stats(self):
        info = (
            f"角色: {self.name}\n"
            f"等级: {self.level} (经验: {self.exp}/{self.exp_to_next})\n"
            f"生命值: {self.life:.1f}/{self.max_life:.1f}\n"
            f"伤害: {self.attack:.1f}\n"
            f"金币: {self.coin}\n"
            f"伤害倍率: {self.crit_min}x - {self.crit_max}x\n"
            f"元素伤害加成: {self.element_damage_bonus:.2f}x\n"
            f"技能点: {self.skill_points}\n"
            f"纯氧数量: {self.oxygen}\n"
            f"击败怪物: {self.monsters_defeated}"
        )
        if self.temporary_boost_turns > 0:
            info += (
                f"\n临时元素增强: {self.temporary_element_boost:.2f}x "
                f"(剩余{self.temporary_boost_turns}回合)"
            )
        # 使用 self.display 显示信息
        if self.display:
            self.display.show_message("角色信息", info)
        else:
            # 如果没有display，使用全局display_manager作为回退
            from display_manager import get_display_manager

            display = get_display_manager()
            display.show_message("角色信息", info)

    def gain_exp(self, amount):
        """获得经验值并升级"""
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.level_up()

    def level_up(self):
        """升级"""
        self.level += 1
        self.exp -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)

        # 升级奖励
        self.max_life += 10
        self.life = self.max_life  # 升级回满血
        self.attack += 2
        self.skill_points += 1  # 每次升级获得1个技能点

        # 升级信息
        if self.display:
            self.display.show_message(
                "升级",
                f"🎉 恭喜升级到 {self.level} 级！\n"
                f"生命上限 +10，攻击力 +2，技能点 +1",
            )
            time.sleep(1)
        else:
            # 如果display不可用，使用简单的print（终端模式）
            print("生命上限 +10，攻击力 +2，技能点 +1")
            time.sleep(1)


class Game:
    def __init__(self):
        self.player = Player(display=None)  # 先创建Player，display稍后设置
        self.display = None  # 延迟初始化，在run方法中根据用户选择创建
        self.lmode = 1.0  # 血量倍率
        self.amode = 1.0  # 攻击倍率
        self.elements = ["火焰", "水", "土地", "暗黑魔法", "闪光"]
        # 成就系统
        self.achievements = {
            "初次胜利": {
                "description": "击败第一个敌人",
                "completed": False,
                "reward": 50,
            },
            "小有成就": {
                "description": "击败10个敌人",
                "completed": False,
                "reward": 200,
            },
            "怪物猎人": {
                "description": "击败50个敌人",
                "completed": False,
                "reward": 1000,
            },
            "富有之人": {
                "description": "拥有1000金币",
                "completed": False,
                "reward": 100,
            },
            "大富翁": {
                "description": "拥有10000金币",
                "completed": False,
                "reward": 500,
            },
            "等级大师": {
                "description": "达到10级",
                "completed": False,
                "reward": 300,
            },
            "传奇勇者": {
                "description": "达到20级",
                "completed": False,
                "reward": 1000,
            },
            "元素大师": {
                "description": "购买魔法袍",
                "completed": False,
                "reward": 150,
            },
            "技能新手": {
                "description": "学习第一个技能",
                "completed": False,
                "reward": 100,
            },
            "技能大师": {
                "description": "所有技能达到3级",
                "completed": False,
                "reward": 800,
            },
            "技能专家": {
                "description": "单个技能达到10级",
                "completed": False,
                "reward": 500,
            },
            "技能宗师": {
                "description": "所有技能达到10级",
                "completed": False,
                "reward": 2000,
            },
            "技能收藏家": {
                "description": "学习所有5个技能",
                "completed": False,
                "reward": 300,
            },
            "雪山征服者": {
                "description": "击败冰霜巨人",
                "completed": False,
                "reward": 300,
            },
            "暗影克星": {
                "description": "击败暗影刺客",
                "completed": False,
                "reward": 350,
            },
            "风暴掌控者": {
                "description": "击败雷电元素",
                "completed": False,
                "reward": 400,
            },
            "神殿英雄": {
                "description": "击败古代神殿所有敌人",
                "completed": False,
                "reward": 800,
            },
            "世界拯救者": {
                "description": "击败普奇神父",
                "completed": False,
                "reward": 2000,
            },
            "无尽新手": {
                "description": "无尽模式达到10波",
                "completed": False,
                "reward": 500,
            },
            "无尽勇士": {
                "description": "无尽模式达到50波",
                "completed": False,
                "reward": 2000,
            },
            "无尽王者": {
                "description": "无尽模式达到100波",
                "completed": False,
                "reward": 5000,
            },
            "无尽传奇": {
                "description": "无尽模式达到200波",
                "completed": False,
                "reward": 10000,
            },
        }
        # 无尽模式状态变量
        self.endless_wave = 0  # 当前波数
        self.endless_difficulty = 1.0  # 难度乘数（每波增加）
        self.endless_high_score = 0  # 最高分（击败敌人总数）
        # 古代神殿击败敌人记录（用于神殿英雄成就）
        self.temple_enemies_defeated = []

    def set_difficulty(self):
        if self.display is None:
            # 终端模式下的简单选择
            print("=== 选择难度 ===")
            print("1. 无限金币版")
            print("2. 简单")
            print("3. 普通")
            print("4. 坤难")
            print("5. 炼狱")
            print("6. 地狱")
            while True:
                choice = input("请输入选择 (1-6): ").strip()
                if choice == "1":
                    mode = "无限金币版"
                    break
                elif choice == "2":
                    mode = "简单"
                    break
                elif choice == "3":
                    mode = "普通"
                    break
                elif choice == "4":
                    mode = "坤难"
                    break
                elif choice == "5":
                    mode = "炼狱"
                    break
                elif choice == "6":
                    mode = "地狱"
                    break
                else:
                    print("无效选择，请重新输入")
        else:
            mode = self.display.get_choice(
                "选择难度",
                ["无限金币版", "简单", "普通", "坤难", "炼狱", "地狱"],
            )
            if not mode:
                sys.exit()

        if mode == "无限金币版":
            self.player.coin = 1145141919810
        elif mode == "简单":
            self.lmode, self.amode = 0.7, 0.8
        elif mode == "普通":
            self.lmode, self.amode = 1.0, 1.0
        elif mode == "坤难":
            self.lmode, self.amode = 1.5, 1.6
        elif mode == "炼狱":
            self.lmode, self.amode = 2.0, 2.2
        elif mode == "地狱":
            self.lmode, self.amode = 2.5, 2.8

    def check_stat_anomalies(self):
        # 检查并修复属性异常（原代码中的彩蛋/Bug修复逻辑）
        if self.player.crit_max == self.player.crit_min:
            if self.display:
                self.display.show_message(
                    "彩蛋发现", "恭喜你发现彩蛋！奖励810金币！"
                )
            else:
                print("恭喜你发现彩蛋！奖励810金币！")
            self.player.coin += 810
            self.player.crit_max, self.player.crit_min = 2, 0
        elif self.player.crit_min > self.player.crit_max:
            if self.display:
                self.display.show_message(
                    "属性异常", "属性异常：伤害下限大于上限，已恢复"
                )
            else:
                print("属性异常：伤害下限大于上限，已恢复")
            self.player.crit_max, self.player.crit_min = 2, 0
        elif self.player.crit_max <= 0 or self.player.crit_min < 0:
            if self.display:
                self.display.show_message("属性异常", "属性异常，已恢复")
            else:
                print("属性异常，已恢复")
            self.player.crit_max, self.player.crit_min = 2, 0

    def get_attack_multiplier(self):
        return random.randint(self.player.crit_min, self.player.crit_max)

    def battle(self, name, base_hp, base_atk, reward_coin, multipliers):
        """
        通用的战斗函数
        multipliers: 字典，key为元素名，value为伤害倍率（正数扣血，负数回血）
        """
        self.display.show_battle_info("战斗开始", f"开始战斗: {name}")
        time.sleep(1)

        enemy_hp = base_hp * self.lmode
        enemy_atk = base_atk * self.amode

        # 战斗开始时重置技能状态
        self.player.shield_active = False
        self.player.time_slow_active = False

        # 熔岩怪特殊机制：如果倍率是正数代表造成伤害，原代码中熔岩怪火属性是 +，代表回血（反向伤害）
        # 这里为了统一逻辑：multipliers 中正值为对敌人造成伤害倍率，负值为敌人回血倍率

        while True:
            # 每回合更新技能冷却
            self.update_skill_cooldowns()

            # 自动使用技能
            skill_damage = self.auto_use_skills(enemy_atk, enemy_hp)
            if skill_damage > 0:
                enemy_hp -= skill_damage
                self.display.show_battle_info(
                    "技能伤害", f"技能造成 {skill_damage} 点伤害！"
                )
                # 检查敌人是否被技能击败
                if enemy_hp <= 0:
                    break

            crit = self.get_attack_multiplier()
            choice = self.display.get_choice(
                f"对战 {name} - 选择攻击元素", self.elements
            )
            if not choice:
                continue  # 防止点了取消报错

            # 计算对敌人伤害
            dmg_mult = multipliers.get(choice, 1.0)

            # 特殊处理：原代码中熔岩怪碰到火焰是 Elife = Elife + ... (回血)
            # 我们约定：如果传入的 multiplier 是负数，则代表给敌人回血

            # 应用元素伤害加成
            total_element_bonus = self.player.element_damage_bonus
            # 应用临时增强效果
            if self.player.temporary_boost_turns > 0:
                total_element_bonus *= self.player.temporary_element_boost
                self.player.temporary_boost_turns -= 1
                if self.player.temporary_boost_turns == 0:
                    self.player.temporary_element_boost = 1.0
                    self.display.show_info("元素增强效果已结束！")

            damage = self.player.attack * dmg_mult * crit * total_element_bonus

            # 原代码逻辑还原：
            # 大部分怪：Elife = Elife - (attck * mult * crit)
            # 熔岩怪火属性：Elife = Elife + (attck * 2 * crit) -> 相当于伤害是 -2.0

            if damage > 0:
                enemy_hp -= damage
                self.display.show_battle_info(
                    "攻击", f"你使用[{choice}]造成了 {damage:.1f} 点伤害！"
                )
            else:
                enemy_hp -= damage  # 减去负数等于加血
                absorb_info = (
                    f"你的攻击被吸收了！敌人恢复了 {abs(damage):.1f} 点血量！"
                )
                if self.display.use_gui():
                    self.display.show_battle_info("攻击被吸收", absorb_info)
                else:
                    print(absorb_info)

            # 敌人攻击
            # 检查时间减缓效果：敌人跳过攻击
            if (
                self.player.time_slow_active
                and self.player.time_slow_active > 0
            ):
                self.display.show_battle_info(
                    "时间减缓",
                    f"敌人被减缓时间，跳过攻击！（剩余{self.player.time_slow_active}回合）",
                )
                self.player.time_slow_active -= 1  # 减少剩余回合数
                # 如果时间减缓仍然有效，完全跳过敌人攻击
                if self.player.time_slow_active > 0:
                    # 时间减缓仍然有效，敌人不攻击，直接进入下一回合
                    pass
                else:
                    # 时间减缓效果结束
                    self.player.time_slow_active = False
                    self.display.show_battle_info(
                        "时间减缓", "时间减缓效果已结束！"
                    )
                # 无论时间减缓是否结束，只要这一回合时间减缓生效，就跳过敌人攻击
                # 继续显示战斗信息，但不执行伤害计算
            else:
                # 没有时间减缓效果，执行正常攻击逻辑
                # 检查护盾效果
                actual_damage = enemy_atk
                if self.player.shield_active and isinstance(
                    self.player.shield_active, dict
                ):
                    # 处理护盾效果
                    shield_data = self.player.shield_active
                    reduction = shield_data.get("reduction", 0.5)
                    actual_damage = enemy_atk * reduction
                    shield_type = shield_data.get("type", "normal")
                    # 更新护盾类型映射，包含所有类型
                    type_display_map = {
                        "normal": "普通护盾",
                        "strong": "强力护盾",
                        "super": "超强护盾",
                        "legendary": "传奇护盾",
                        "epic": "史诗护盾",
                    }
                    type_display = type_display_map.get(shield_type, "护盾")
                    self.display.show_battle_info(
                        type_display,
                        f"{type_display}生效！伤害减为{int(reduction * 100)}%："
                        f"{actual_damage:.1f}",
                    )
                    # 减少护盾剩余回合数
                    shield_data["turns"] -= 1
                    if shield_data["turns"] <= 0:
                        self.player.shield_active = False  # 护盾效果结束
                        self.display.show_battle_info(
                            "护盾", "护盾效果已消失！"
                        )

                # 应用伤害
                self.player.life -= actual_damage
                if actual_damage > 0:
                    self.display.show_battle_info(
                        "敌人攻击", f"敌人造成{actual_damage:.1f}点伤害！"
                    )

            time.sleep(1)
            # 显示战斗血量信息
            battle_info = (
                f"敌方({name})血量：{enemy_hp:.1f}\n"
                f"我方血量：{self.player.life:.1f}"
            )
            if self.display.use_gui():
                self.display.show_battle_info("战斗状态", battle_info)
            else:
                print(f"敌方({name})血量：{enemy_hp:.1f}")
                print(f"我方血量：{self.player.life:.1f}")
            time.sleep(0.5)

            if not self.player.is_alive():
                if not self.display.use_gui():
                    print("你死了！！！")
                self.display.show_message("游戏结束", "你被打败了...")
                return False  # 返回False表示玩家死亡

            if enemy_hp <= 0:
                if not self.display.use_gui():
                    print("你赢了！！！")
                self.player.coin += reward_coin
                self.player.monsters_defeated += 1

                # 计算经验值
                exp_gain = int(base_hp * 0.1 + base_atk * 2)
                self.player.gain_exp(exp_gain)

                # 显示奖励信息
                reward_info = f"获得金币: {reward_coin}\n获得经验: {exp_gain}"
                if self.display.use_gui():
                    self.display.show_message("战斗胜利", reward_info)
                else:
                    print(f"获得金币: {reward_coin}")
                    print(f"获得经验: {exp_gain}")

                # 检查特定敌人成就
                if (
                    name == "冰霜巨人"
                    and not self.achievements["雪山征服者"]["completed"]
                ):
                    self.complete_achievement("雪山征服者")
                    self.display.show_message(
                        "成就解锁", "🏆 成就解锁：雪山征服者！"
                    )
                elif (
                    name == "暗影刺客"
                    and not self.achievements["暗影克星"]["completed"]
                ):
                    self.complete_achievement("暗影克星")
                    self.display.show_message(
                        "成就解锁", "🏆 成就解锁：暗影克星！"
                    )
                elif (
                    name == "雷电元素"
                    and not self.achievements["风暴掌控者"]["completed"]
                ):
                    self.complete_achievement("风暴掌控者")
                    self.display.show_message(
                        "成就解锁", "🏆 成就解锁：风暴掌控者！"
                    )
                elif name in ["石像守卫", "古代法师", "神殿骑士"]:
                    # 检查是否击败了所有神殿敌人
                    if name not in self.temple_enemies_defeated:
                        self.temple_enemies_defeated.append(name)

                    if (
                        len(self.temple_enemies_defeated) >= 3
                        and not self.achievements["神殿英雄"]["completed"]
                    ):
                        self.complete_achievement("神殿英雄")
                        self.display.show_message(
                            "成就解锁", "🏆 成就解锁：神殿英雄！"
                        )

                # 检查一般成就
                self.check_achievements()
                break
        return True  # 战斗胜利

    def _battle_or_die(self, *args, **kwargs):
        """战斗包装方法：玩家死亡时显示游戏结束并返回主菜单。

        恢复少量生命值避免死亡状态影响后续菜单操作，
        行为与 endless_mode 中的死亡处理保持一致。
        """
        result = self.battle(*args, **kwargs)
        if result is False:
            # 玩家死亡，恢复生命值并返回主菜单
            self.player.life = max(1.0, self.player.life)
            self.display.show_message(
                "游戏结束",
                "你被打败了，但命运给了你重来的一次机会...\n已返回主菜单。",
            )
        return result

    def boss_battle(self):
        self.display.show_battle_info("最终战斗", "普奇神父")
        time.sleep(1)
        enemy_hp = 1000
        enemy_atk = 50
        turn_limit = 12

        self.display.show_battle_info(
            "Boss登场", '普奇神父向你靠来:"[MADE IN HEAVEN!]"'
        )

        # 战斗开始时重置技能状态（与普通战斗保持一致）
        self.player.shield_active = False
        self.player.time_slow_active = False

        while True:
            # 每回合更新技能冷却
            self.update_skill_cooldowns()

            crit = self.get_attack_multiplier()
            if not self.display.get_yes_no(
                "Heaven",
                f"离[天国之时]还有 {turn_limit} [天国之刻]，是否阻止他？",
            ):
                sys.exit()

            if turn_limit <= 0:
                self.display.show_message("游戏结束", "世界重启了，你噶了")
                sys.exit()

            # 1=命中, 2=闪避(除非特殊攻击)
            block = random.randint(1, 2)

            options = self.elements + ["纯氧"]
            choice = self.display.get_choice("选择攻击元素", options)
            if not choice:
                continue

            damage = 0

            # 还原原版复杂的判定逻辑
            if block == 1:
                # 普奇没有闪避，普通元素生效
                mult_map = {
                    "火焰": 0.1,
                    "水": 0.5,
                    "土地": 0.5,
                    "暗黑魔法": 2.5,
                    "闪光": 0.0,
                }
                mult = mult_map.get(choice, 0)
                damage = self.player.attack * mult * crit
                enemy_hp -= damage

            # 下面这些 elif 在原版代码中位于 block==1 的外部，意味着即使 block=2 (闪避)，这些攻击也生效
            if choice == "闪光":
                # 闪光总是生效
                damage = self.player.attack * 10.1 * crit
                enemy_hp -= damage
            elif choice == "纯氧":
                if self.player.oxygen < 5:
                    msg1 = "你没有足够的纯氧！普奇还是逃了出来。"
                    if self.display.use_gui():
                        self.display.show_message("纯氧不足", msg1)
                    else:
                        print(msg1)
                else:
                    msg1 = "神父吸入纯氧！"
                    msg2 = "隐藏结局：我是安波里欧"
                    if self.display.use_gui():
                        self.display.show_message(
                            "隐藏结局", f"{msg1}\n{msg2}"
                        )
                    else:
                        print(msg1)
                        print(msg2)
                    time.sleep(2)
                    sys.exit()
            elif block == 2 and choice != "闪光" and choice != "纯氧":
                msg = "普奇速度过快，你没有打到！"
                if self.display.use_gui():
                    self.display.show_battle_info("攻击落空", msg)
                else:
                    print(msg)

            # 敌人反击
            # 原版逻辑：life = life - Eattck * block (如果普奇闪避了，伤害翻倍？block是1或2)
            dmg_to_player = enemy_atk * block
            self.player.life -= dmg_to_player
            turn_limit -= 1

            if damage > 0:
                self.display.show_battle_info(
                    "攻击", f"你造成了 {damage:.1f} 点伤害！"
                )

            # 显示Boss战血量信息
            boss_battle_info = (
                f"敌方血量：{enemy_hp:.1f} | 我方血量：{self.player.life:.1f}"
            )
            if self.display.use_gui():
                self.display.show_battle_info("Boss战状态", boss_battle_info)
            else:
                print(boss_battle_info)

            if not self.player.is_alive():
                if not self.display.use_gui():
                    print("你死了！！！")
                sys.exit()
            elif enemy_hp <= 0:
                if self.player.coin > 1000000000:  # 粗略判断是否作弊版
                    if not self.display.use_gui():
                        print("普奇：纪狗气死我了")
                    victory_msg = "普奇：纪狗气死我了"
                else:
                    if not self.display.use_gui():
                        print("你赢了！！！，恭喜通关！")
                    victory_msg = "你赢了！！！，恭喜通关！"
                    # 检查世界拯救者成就
                    if not self.achievements["世界拯救者"]["completed"]:
                        self.complete_achievement("世界拯救者")
                        self.display.show_message(
                            "成就解锁", "🏆 成就解锁：世界拯救者！"
                        )

                # 显示胜利信息
                if self.display.use_gui():
                    self.display.show_message("游戏通关", victory_msg)
                else:
                    print(victory_msg)

                time.sleep(2)

                # 询问是否进入无尽模式
                if self.display.get_yes_no(
                    "游戏通关",
                    "恭喜你击败了普奇神父！\n是否要挑战无尽模式？\n（无尽模式：敌人会越来越强，挑战你的极限）",
                ):
                    # 进入无尽模式
                    self.endless_mode()
                else:
                    # 返回主菜单
                    self.display.show_message(
                        "返回主菜单", "返回主菜单继续冒险..."
                    )
                    return

    def endless_mode(self):
        """
        无尽模式：敌人会越来越强，挑战玩家的极限
        """
        self.display.show_message(
            "无尽模式",
            "欢迎来到无尽模式！\n敌人会越来越强，挑战你的极限！\n每波敌人都会变得更强大，看看你能坚持多久！",
        )

        # 重置无尽模式状态（如果之前有）
        self.endless_wave = 0
        self.endless_difficulty = 1.0

        # 无尽模式敌人池（名称, 基础HP, 基础攻击, 金币奖励, 元素倍率字典）
        enemy_pool = [
            (
                "熔岩怪",
                150,
                15,
                100,
                {
                    "火焰": -2.0,
                    "水": 2.0,
                    "土地": 1.0,
                    "暗黑魔法": 0.5,
                    "闪光": 1.5,
                },
            ),
            (
                "冰霜巨人",
                200,
                20,
                150,
                {
                    "火焰": 2.0,
                    "水": -2.0,
                    "土地": 1.0,
                    "暗黑魔法": 1.0,
                    "闪光": 1.0,
                },
            ),
            (
                "暗影刺客",
                120,
                25,
                120,
                {
                    "火焰": 1.0,
                    "水": 1.0,
                    "土地": 1.0,
                    "暗黑魔法": 2.0,
                    "闪光": 3.0,
                },
            ),
            (
                "雷电元素",
                180,
                22,
                140,
                {
                    "火焰": 1.0,
                    "水": 1.5,
                    "土地": -2.0,
                    "暗黑魔法": 1.0,
                    "闪光": 2.0,
                },
            ),
            (
                "石像守卫",
                250,
                18,
                160,
                {
                    "火焰": 1.5,
                    "水": 1.0,
                    "土地": 0.5,
                    "暗黑魔法": 1.0,
                    "闪光": 1.0,
                },
            ),
            (
                "古代法师",
                130,
                30,
                130,
                {
                    "火焰": 1.5,
                    "水": 1.5,
                    "土地": 1.5,
                    "暗黑魔法": 2.5,
                    "闪光": 1.5,
                },
            ),
            (
                "神殿骑士",
                300,
                25,
                200,
                {
                    "火焰": 1.0,
                    "水": 1.0,
                    "土地": 1.0,
                    "暗黑魔法": 1.0,
                    "闪光": 1.0,
                },
            ),
            (
                "时空扭曲者",
                280,
                32,
                350,
                {
                    "火焰": 1.2,
                    "水": 1.2,
                    "土地": 1.2,
                    "暗黑魔法": 1.8,
                    "闪光": 1.8,
                },
            ),
            (
                "神圣护卫",
                380,
                42,
                500,
                {
                    "火焰": 1.0,
                    "水": 1.0,
                    "土地": 1.0,
                    "暗黑魔法": 1.0,
                    "闪光": 2.5,
                },
            ),
            (
                "深渊吞噬者",
                420,
                38,
                450,
                {
                    "火焰": 1.5,
                    "水": 1.5,
                    "土地": 1.5,
                    "暗黑魔法": 2.0,
                    "闪光": 1.0,
                },
            ),
            (
                "混沌元素",
                250,
                28,
                300,
                {
                    "火焰": 1.5,
                    "水": 1.5,
                    "土地": 1.5,
                    "暗黑魔法": 1.5,
                    "闪光": 1.5,
                },
            ),
        ]

        while True:
            self.endless_wave += 1
            # 每5波难度增加一次
            if self.endless_wave % 5 == 0:
                self.endless_difficulty += 0.2
                self.display.show_message(
                    "难度提升",
                    f"第{self.endless_wave}波完成！难度提升！\n"
                    f"当前难度倍率: {self.endless_difficulty:.1f}x",
                )

            # 随机选择敌人
            enemy = random.choice(enemy_pool)
            name, base_hp, base_atk, base_coin, multipliers = enemy

            # 应用难度倍率
            scaled_hp = base_hp * self.endless_difficulty
            scaled_atk = base_atk * self.endless_difficulty
            scaled_coin = int(
                base_coin * self.endless_difficulty * 0.8
            )  # 金币奖励稍低

            # 显示波次信息
            wave_info = (
                f"第 {self.endless_wave} 波\n"
                f"敌人: {name}\n"
                f"难度倍率: {self.endless_difficulty:.1f}x\n"
                f"敌人血量: {scaled_hp:.0f} | 敌人攻击: {scaled_atk:.0f}\n"
                f"击败奖励: {scaled_coin} 金币"
            )
            self.display.show_message("无尽模式波次", wave_info)

            # 询问是否继续（允许玩家退出）
            if not self.display.get_yes_no(
                "无尽模式",
                f"准备迎战第{self.endless_wave}波敌人：{name}！\n是否继续？",
            ):
                self.display.show_message(
                    "退出无尽模式",
                    f"你坚持到了第{self.endless_wave}波！\n返回主菜单。",
                )
                # 更新最高分
                if self.endless_wave - 1 > self.endless_high_score:
                    self.endless_high_score = self.endless_wave - 1
                    self.display.show_message(
                        "新纪录",
                        f"新的无尽模式最高分：{self.endless_high_score}波！",
                    )
                # 检查无尽模式成就
                self.check_endless_achievements()
                return

            # 进行战斗
            battle_result = self.battle(
                name, scaled_hp, scaled_atk, scaled_coin, multipliers
            )

            # 检查战斗结果（False表示玩家死亡）
            if battle_result is False:
                # 玩家死亡，结束无尽模式
                self.display.show_message(
                    "无尽模式结束",
                    f"你在第{self.endless_wave}波被击败了！\n最终分数：{self.endless_wave}波",
                )
                # 更新最高分
                if self.endless_wave > self.endless_high_score:
                    self.endless_high_score = self.endless_wave
                    self.display.show_message(
                        "新纪录",
                        f"新的无尽模式最高分：{self.endless_high_score}波！",
                    )
                # 恢复玩家生命值（避免死亡状态影响主菜单）
                self.player.life = max(
                    1.0, self.player.life
                )  # 确保生命值至少为1
                # 检查无尽模式成就
                self.check_endless_achievements()
                # 等待一下
                time.sleep(2)
                # 返回主菜单
                return

            # 战斗胜利，显示波次完成
            self.display.show_message(
                "波次完成", f"第{self.endless_wave}波胜利！\n准备下一波..."
            )
            time.sleep(1)

            # 每10波恢复生命值
            if self.endless_wave % 10 == 0:
                heal_amount = self.player.max_life * 0.3  # 恢复30%最大生命值
                self.player.life = min(
                    self.player.max_life, self.player.life + heal_amount
                )
                self.display.show_message(
                    "恢复", f"每10波恢复！生命值恢复{heal_amount:.0f}点。"
                )

    def shop(self):
        while True:
            # 根据玩家等级解锁新物品
            choices = [
                "盔甲 [100G, +30HP上限]",
                "剑 [100G, +5伤害]",
                "药水 [50G, 回满HP]",
                "宝箱 [70G, 随机抽奖]",
                "技能点 [200G, +1技能点]",
                "技能全满 [100000G, 所有技能升至10级]",
            ]

            # 等级3解锁新装备
            if self.player.level >= 3:
                choices.extend(
                    [
                        "魔法袍 [200G, +15%元素伤害]",
                        "力量护符 [150G, +3伤害下限倍率]",
                        "守护盾 [180G, +50HP上限]",
                        "经验药水 [80G, +100经验值]",
                    ]
                )

            # 等级5解锁高级道具
            if self.player.level >= 5:
                choices.append("元素卷轴 [120G, 临时增强元素伤害]")

            choices.append("离开商店")
            x = self.display.get_choice(
                f"商店 (金币: {self.player.coin})", choices
            )

            if not x or x == "离开商店":
                break

            if "盔甲" in x:
                if self.player.coin >= 100:
                    self.player.max_life += 30
                    self.player.coin -= 100
                    self.display.show_message("购买成功", "生命上限+30")
                else:
                    self.no_money()
            elif "剑" in x:
                if self.player.coin >= 100:
                    self.player.attack += 5
                    self.player.coin -= 100
                    self.display.show_message("购买成功", "伤害+5")
                else:
                    self.no_money()
            elif x == "药水 [50G, 回满HP]":
                if self.player.coin >= 50:
                    self.player.heal_full()
                    self.player.coin -= 50
                    self.display.show_message("购买成功", "生命已回满")
                else:
                    self.no_money()
            elif "宝箱" in x:
                self.open_chest()
            elif "技能点" in x:
                if self.player.coin >= 200:
                    self.player.skill_points += 1
                    self.player.coin -= 200
                    self.display.show_message("购买成功", "获得1个技能点！")
                else:
                    self.no_money()
            elif "技能全满" in x:
                self.upgrade_all_skills_to_max()
            elif "魔法袍" in x:
                if self.player.coin >= 200:
                    self.player.element_damage_bonus += 0.15
                    self.player.coin -= 200
                    self.display.show_message("购买成功", "元素伤害+15%")
                    # 检查元素大师成就
                    if not self.achievements["元素大师"]["completed"]:
                        self.complete_achievement("元素大师")
                        self.display.show_message(
                            "成就解锁", "🏆 成就解锁：元素大师！"
                        )
                else:
                    self.no_money()
            elif "力量护符" in x:
                if self.player.coin >= 150:
                    # 计算增加后的新下限
                    new_crit_min = self.player.crit_min + 3
                    # 如果新下限超过当前上限，先提升上限
                    if new_crit_min > self.player.crit_max:
                        self.player.crit_max = new_crit_min
                    self.player.crit_min = new_crit_min
                    self.player.coin -= 150
                    self.display.show_message(
                        "购买成功", "伤害下限倍率+3，伤害上限已同步提升"
                    )
                else:
                    self.no_money()
            elif "守护盾" in x:
                if self.player.coin >= 180:
                    self.player.max_life += 50
                    self.player.coin -= 180
                    self.display.show_message("购买成功", "生命上限+50")
                else:
                    self.no_money()
            elif x == "经验药水 [80G, +100经验值]":
                if self.player.coin >= 80:
                    self.player.gain_exp(100)
                    self.player.coin -= 80
                    self.display.show_message("购买成功", "获得100经验值")
                else:
                    self.no_money()
            elif "元素卷轴" in x:
                if self.player.coin >= 120:
                    self.use_element_scroll()
                else:
                    self.no_money()

    def no_money(self):
        self.display.show_message("错误", "金币不足！")

    def upgrade_all_skills_to_max(self):
        """将所有技能升级到10级"""
        if self.player.coin < 100000:
            self.no_money()
            return False

        # 确认购买
        confirm_msg = "花费100000金币将所有技能升级到10级？\n\n"
        skills_upgraded = 0
        for skill_name, skill_data in self.player.skills.items():
            if skill_data["level"] < 10:
                skills_upgraded += 1
                confirm_msg += (
                    f"{skill_name}: Lv.{skill_data['level']} → Lv.10\n"
                )

        if skills_upgraded == 0:
            self.display.show_message("提示", "所有技能都已达到10级！")
            return False

        if not self.display.get_yes_no("确认购买", confirm_msg):
            return False

        # 扣除金币并升级所有技能
        self.player.coin -= 100000
        skills_actually_upgraded = 0

        for skill_name, skill_data in self.player.skills.items():
            if skill_data["level"] < 10:

                skill_data["level"] = 10
                skills_actually_upgraded += 1

        # 显示成功信息
        success_msg = (
            f"花费100000金币将所有技能升级到10级！\n"
            f"升级了{skills_actually_upgraded}个技能。"
        )
        self.display.show_message("购买成功", success_msg)

        # 检查技能相关成就
        self.check_skill_achievements()

        return True

    def check_skill_achievements(self):
        """检查技能相关成就（单独调用，便于重用）"""
        # 检查技能新手成就（如果还有未完成的）
        skills_learned = sum(
            1 for skill in self.player.skills.values() if skill["level"] > 0
        )
        if (
            skills_learned >= 1
            and not self.achievements["技能新手"]["completed"]
        ):
            self.complete_achievement("技能新手")

        # 检查技能大师成就（所有技能达到3级）
        if all(skill["level"] >= 3 for skill in self.player.skills.values()):
            if not self.achievements["技能大师"]["completed"]:
                self.complete_achievement("技能大师")

        # 检查技能专家成就（单个技能达到10级）
        max_skill_level = max(
            skill["level"] for skill in self.player.skills.values()
        )
        if (
            max_skill_level >= 10
            and not self.achievements["技能专家"]["completed"]
        ):
            self.complete_achievement("技能专家")

        # 检查技能宗师成就（所有技能达到10级）
        if all(skill["level"] >= 10 for skill in self.player.skills.values()):
            if not self.achievements["技能宗师"]["completed"]:
                self.complete_achievement("技能宗师")

        # 检查技能收藏家成就（学习所有5个技能）
        if (
            skills_learned >= 5
            and not self.achievements["技能收藏家"]["completed"]
        ):
            self.complete_achievement("技能收藏家")

    def use_element_scroll(self):
        """使用元素卷轴，临时增强元素伤害"""
        self.player.coin -= 120

        element_choice = self.display.get_choice("元素卷轴", self.elements)
        if element_choice:
            self.player.temporary_element_boost = 2.0  # 2倍伤害
            self.player.temporary_boost_turns = 3  # 持续3回合
            self.display.show_info(
                f"元素卷轴使用成功：{element_choice}伤害临时提升100%，持续3回合！"
            )
            self.display.show_message(
                "元素卷轴效果",
                f"{element_choice}伤害临时提升100%，持续3回合！",
            )

    def skill_menu(self):
        """技能菜单"""
        while True:
            skill_list = []
            for skill_name, skill_data in self.player.skills.items():
                cooldown_status = (
                    "就绪"
                    if skill_data["cooldown"] == 0
                    else f"冷却中({skill_data['cooldown']}回合)"
                )
                skill_list.append(
                    f"{skill_name} Lv.{skill_data['level']} "
                    f"[{cooldown_status}]"
                )

            skill_list.append("返回")

            choice = self.display.get_choice(
                f"技能系统 (技能点: {self.player.skill_points})", skill_list
            )
            if not choice or choice == "返回":
                break

            # 提取技能名称
            skill_name = choice.split(" Lv.")[0]
            if skill_name in self.player.skills:
                self.manage_skill(skill_name)

    def manage_skill(self, skill_name):
        """管理单个技能"""
        skill = self.player.skills[skill_name]

        # 技能描述（根据等级变化）
        descriptions = {
            "火球术": "造成火焰伤害，无视元素倍率（每级提升伤害，每级减少冷却，Lv1:40伤害, Lv10:230伤害）",
            "治疗术": (
                "恢复生命值，可突破生命值上限（每级提升治疗量，每级减少冷却，"
                "Lv1:40%最大生命值, Lv10:220%最大生命值）"
            ),
            "护盾": (
                "减少受到的伤害（每级提升减伤效果，每级减少冷却，"
                "Lv1:伤害减半1回合, Lv10:伤害减为5%4回合）"
            ),
            "元素爆发": (
                "提升元素伤害（每级提升加成效果和持续时间，每级减少冷却，"
                "Lv1:+50%3回合, Lv10:+300%6回合）"
            ),
            "时间减缓": "减缓敌人行动（每级增加跳过回合数，每级减少冷却，Lv1:跳过1回合, Lv10:跳过8回合）",
        }

        # 显示技能信息
        info = (
            f"{skill_name} (等级: {skill['level']})\n\n"
            f"描述: {descriptions.get(skill_name, '未知技能')}\n"
            f"冷却时间: {skill['max_cooldown']}回合\n"
            f"当前冷却: {skill['cooldown']}回合\n\n"
        )

        if skill["level"] == 0:
            info += "学习此技能需要1个技能点\n"
            choices = ["学习技能", "返回"]
        elif skill["level"] >= 10:
            info += "技能已达到最大等级（10级）\n"
            choices = ["使用技能", "返回"]
        else:
            info += "升级技能需要1个技能点\n"
            choices = ["升级技能", "使用技能", "返回"]

        self.display.show_info(info)

        action = self.display.get_choice(f"{skill_name}管理", choices)
        if not action or action == "返回":
            return

        if action == "学习技能" or action == "升级技能":
            # 检查技能是否已达到最大等级
            if skill["level"] >= 10:
                self.display.show_message(
                    "错误", "技能已达到最大等级（10级），无法继续升级！"
                )
                return

            if self.player.skill_points >= 1:
                self.player.skill_points -= 1
                skill["level"] += 1
                self.display.show_message(
                    "技能升级", f"{skill_name}升级到Lv.{skill['level']}！"
                )

                # 检查技能新手成就
                if not self.achievements["技能新手"]["completed"]:
                    self.complete_achievement("技能新手")
                    self.display.show_message(
                        "成就解锁", "🏆 成就解锁：技能新手！"
                    )
            else:
                self.display.show_message("错误", "技能点不足！")
        elif action == "使用技能":
            if skill["cooldown"] > 0:
                self.display.show_message("错误", "技能还在冷却中！")
            else:
                self.use_skill(skill_name)

    def use_skill(self, skill_name):
        """使用技能"""
        skill = self.player.skills[skill_name]

        # 检查技能是否已学习（等级>0）
        if skill["level"] == 0:
            self.display.show_message("错误", "技能尚未学习！")
            return 0

        # 检查冷却
        if skill["cooldown"] > 0:
            self.display.show_message("错误", "技能还在冷却中！")
            return 0

        damage = 0  # 默认伤害为0
        skill_level = skill["level"]

        if skill_name == "火球术":
            # 火球术：等级1=40, 等级2=70, 等级3=95, 等级4=115, 等级5=130
            # 等级6=150, 等级7=170, 等级8=190, 等级9=210, 等级10=230
            base_damages = {
                1: 40,
                2: 70,
                3: 95,
                4: 115,
                5: 130,
                6: 150,
                7: 170,
                8: 190,
                9: 210,
                10: 230,
            }
            damage = base_damages.get(skill_level, 40)
            self.display.show_battle_info(
                "火球术", f"造成{damage}点火焰伤害！"
            )
        elif skill_name == "治疗术":
            # 治疗术：等级1=40%, 等级2=65%, 等级3=85%, 等级4=100%, 等级5=120%
            # 等级6=140%, 等级7=160%, 等级8=180%, 等级9=200%, 等级10=220%
            heal_percentages = {
                1: 0.4,
                2: 0.65,
                3: 0.85,
                4: 1.0,
                5: 1.2,
                6: 1.4,
                7: 1.6,
                8: 1.8,
                9: 2.0,
                10: 2.2,
            }
            heal_percent = heal_percentages.get(skill_level, 0.4)
            heal_amount = self.player.max_life * heal_percent
            self.player.life = self.player.life + heal_amount
            self.display.show_battle_info(
                "治疗",
                f"治疗术恢复了{heal_amount:.1f}点生命值！当前生命值：{self.player.life:.1f}",
            )
        elif skill_name == "护盾":
            # 护盾：等级1-2=伤害减半1回合，等级3=伤害减为40%1回合
            # 等级4=伤害减为30%2回合，等级5=伤害减为20%2回合
            # 等级6=伤害减为15%2回合，等级7=伤害减为10%2回合
            # 等级8=伤害减为10%3回合，等级9=伤害减为5%3回合，等级10=伤害减为5%4回合
            if skill_level >= 8:
                # 等级8-10：史诗护盾
                reduction = 0.1 if skill_level == 8 else 0.05
                turns = 3 if skill_level <= 9 else 4
                shield_type = "史诗护盾"
                self.display.show_battle_info(
                    "护盾",
                    f"{shield_type}激活！下{turns}回合伤害减为{int(reduction * 100)}%！",
                )
                self.player.shield_active = {
                    "type": "epic",
                    "reduction": reduction,
                    "turns": turns,
                }
            elif skill_level >= 6:
                # 等级6-7：传奇护盾
                reduction = 0.15 if skill_level == 6 else 0.1
                shield_type = "传奇护盾"
                self.display.show_battle_info(
                    "护盾",
                    f"{shield_type}激活！下2回合伤害减为{int(reduction * 100)}%！",
                )
                self.player.shield_active = {
                    "type": "legendary",
                    "reduction": reduction,
                    "turns": 2,
                }
            elif skill_level >= 4:
                # 等级4-5：超强护盾，持续2回合
                reduction = 0.3 if skill_level == 4 else 0.2
                shield_type = "超强护盾"
                self.display.show_battle_info(
                    "护盾",
                    f"{shield_type}激活！下2回合伤害减为{int(reduction * 100)}%！",
                )
                self.player.shield_active = {
                    "type": "super",
                    "reduction": reduction,
                    "turns": 2,
                }
            elif skill_level == 3:
                self.display.show_battle_info(
                    "护盾", "强力护盾激活！下回合伤害减为40%！"
                )
                self.player.shield_active = {
                    "type": "strong",
                    "reduction": 0.4,
                    "turns": 1,
                }
            else:
                self.display.show_battle_info(
                    "护盾", "护盾激活！下回合受到伤害减半！"
                )
                self.player.shield_active = {
                    "type": "normal",
                    "reduction": 0.5,
                    "turns": 1,
                }
        elif skill_name == "元素爆发":
            # 元素爆发：等级1=+50%, 等级2=+80%, 等级3=+100%, 等级4=+120%, 等级5=+150%持续4回合
            # 等级6=+180%持续4回合，等级7=+210%持续4回合，等级8=+240%持续5回合，等级9=+270%持续5回合，等级10=+300%持续6回合
            boost_values = {
                1: 0.5,
                2: 0.8,
                3: 1.0,
                4: 1.2,
                5: 1.5,
                6: 1.8,
                7: 2.1,
                8: 2.4,
                9: 2.7,
                10: 3.0,
            }
            boost = boost_values.get(skill_level, 0.5)
            self.player.temporary_element_boost = 1.0 + boost
            # 设置持续回合数：1-3级=3回合，4-7级=4回合，8-10级=5回合，10级额外增加1回合
            if skill_level >= 10:
                self.player.temporary_boost_turns = 6
            elif skill_level >= 8:
                self.player.temporary_boost_turns = 5
            elif skill_level >= 4:
                self.player.temporary_boost_turns = 4
            else:
                self.player.temporary_boost_turns = 3
            self.display.show_battle_info(
                "元素爆发",
                f"元素爆发！所有元素伤害提升{int(boost * 100)}%，"
                f"持续{self.player.temporary_boost_turns}回合！",
            )
        elif skill_name == "时间减缓":
            # 时间减缓：等级1-2=跳过1回合，等级3-4=跳过2回合，等级5=跳过3回合
            # 等级6=跳过4回合，等级7=跳过5回合，等级8=跳过6回合，等级9=跳过7回合，等级10=跳过8回合
            if skill_level <= 2:
                skip_turns = 1
            elif skill_level <= 4:
                skip_turns = 2
            elif skill_level == 5:
                skip_turns = 3
            elif skill_level == 6:
                skip_turns = 4
            elif skill_level == 7:
                skip_turns = 5
            elif skill_level == 8:
                skip_turns = 6
            elif skill_level == 9:
                skip_turns = 7
            else:  # 等级10
                skip_turns = 8
            self.display.show_battle_info(
                "时间减缓", f"时间减缓！敌人跳过{skip_turns}回合攻击！"
            )
            self.player.time_slow_active = skip_turns

        # 设置冷却时间（每次升级都有冷却缩减）
        base_cooldown = skill["max_cooldown"]

        # 基础冷却缩减：每级减少0.15回合
        level_reduction = skill_level * 0.15

        # 5级额外奖励：额外减少0.5回合
        if skill_level >= 5:
            level_reduction += 0.5

        # 10级额外奖励：再额外减少0.5回合
        if skill_level >= 10:
            level_reduction += 0.5

        # 计算实际冷却（四舍五入，最低为1回合）
        actual_cooldown = max(1, round(base_cooldown - level_reduction))
        skill["cooldown"] = actual_cooldown

        # 显示冷却信息（仅在冷却减少时显示）
        if actual_cooldown < base_cooldown:
            reduction_amount = base_cooldown - actual_cooldown
            self.display.show_battle_info(
                "技能冷却",
                f"技能冷却减少{reduction_amount}回合！当前冷却：{actual_cooldown}回合",
            )

        return damage

    def update_skill_cooldowns(self):
        """更新技能冷却"""
        for skill_name, skill_data in self.player.skills.items():
            if skill_data["cooldown"] > 0:
                skill_data["cooldown"] -= 1

    def auto_use_skills(self, enemy_atk, enemy_hp):
        """
        根据战斗条件自动使用技能
        Args:
            enemy_atk: 敌人攻击力
            enemy_hp: 敌人当前血量
        Returns:
            int: 技能造成的总伤害
        """
        total_damage = 0
        life_percent = self.player.life / self.player.max_life

        # 检查每个技能是否可用
        for skill_name, skill_data in self.player.skills.items():
            # 技能未学习或冷却中则跳过
            if skill_data["level"] == 0 or skill_data["cooldown"] > 0:
                continue

            if skill_name == "治疗术":
                # 生命值低于40%时使用治疗术
                if life_percent < 0.4:
                    self.display.show_battle_info(
                        "自动技能", "自动使用治疗术！"
                    )
                    # use_skill会处理冷却，这里直接调用
                    self.use_skill(skill_name)

            elif skill_name == "护盾":
                # 敌人攻击力较高时使用护盾（攻击力大于玩家生命值的20%）
                if (
                    enemy_atk > self.player.max_life * 0.2
                    and not self.player.shield_active
                ):
                    self.display.show_battle_info("自动技能", "自动使用护盾！")
                    self.use_skill(skill_name)

            elif skill_name == "火球术":
                # 敌人血量较高时使用火球术（血量大于玩家攻击力的5倍）
                if enemy_hp > self.player.attack * 5:
                    self.display.show_battle_info(
                        "自动技能", "自动使用火球术！"
                    )
                    damage = self.use_skill(skill_name)
                    total_damage += damage

            elif skill_name == "元素爆发":
                # 元素伤害加成较低时使用（当前加成小于1.5倍）
                if self.player.element_damage_bonus < 1.5:
                    self.display.show_battle_info(
                        "自动技能", "自动使用元素爆发！"
                    )
                    self.use_skill(skill_name)

            elif skill_name == "时间减缓":
                # 时间减缓触发条件：敌人攻击力较高或玩家生命值较低时使用
                # 条件1：敌人攻击力大于玩家攻击力的1.5倍
                # 条件2：玩家生命值低于70%
                # 条件3：敌人攻击力大于玩家最大生命值的25%（危险情况）
                condition1 = enemy_atk > self.player.attack * 1.5
                condition2 = life_percent < 0.7
                condition3 = enemy_atk > self.player.max_life * 0.25

                if condition1 or condition2 or condition3:
                    self.display.show_battle_info(
                        "自动技能", "自动使用时间减缓！"
                    )
                    self.use_skill(skill_name)

        return total_damage

    def check_achievements(self):
        """检查并触发成就"""
        newly_completed = []

        # 检查各类成就条件
        if (
            self.player.monsters_defeated >= 1
            and not self.achievements["初次胜利"]["completed"]
        ):
            self.complete_achievement("初次胜利")
            newly_completed.append("初次胜利")

        if (
            self.player.monsters_defeated >= 10
            and not self.achievements["小有成就"]["completed"]
        ):
            self.complete_achievement("小有成就")
            newly_completed.append("小有成就")

        if (
            self.player.monsters_defeated >= 50
            and not self.achievements["怪物猎人"]["completed"]
        ):
            self.complete_achievement("怪物猎人")
            newly_completed.append("怪物猎人")

        if (
            self.player.coin >= 1000
            and not self.achievements["富有之人"]["completed"]
        ):
            self.complete_achievement("富有之人")
            newly_completed.append("富有之人")

        if (
            self.player.coin >= 10000
            and not self.achievements["大富翁"]["completed"]
        ):
            self.complete_achievement("大富翁")
            newly_completed.append("大富翁")

        if (
            self.player.level >= 10
            and not self.achievements["等级大师"]["completed"]
        ):
            self.complete_achievement("等级大师")
            newly_completed.append("等级大师")

        if (
            self.player.level >= 20
            and not self.achievements["传奇勇者"]["completed"]
        ):
            self.complete_achievement("传奇勇者")
            newly_completed.append("传奇勇者")

        # 检查技能相关成就
        skills_learned = sum(
            1 for skill in self.player.skills.values() if skill["level"] > 0
        )
        if (
            skills_learned >= 1
            and not self.achievements["技能新手"]["completed"]
        ):
            self.complete_achievement("技能新手")
            newly_completed.append("技能新手")

        if (
            all(skill["level"] >= 3 for skill in self.player.skills.values())
            and not self.achievements["技能大师"]["completed"]
        ):
            self.complete_achievement("技能大师")
            newly_completed.append("技能大师")

        # 检查技能专家：任意单个技能达到10级
        if (
            any(skill["level"] >= 10 for skill in self.player.skills.values())
            and not self.achievements["技能专家"]["completed"]
        ):
            self.complete_achievement("技能专家")
            newly_completed.append("技能专家")

        # 检查技能宗师：所有技能达到10级
        if (
            all(skill["level"] >= 10 for skill in self.player.skills.values())
            and not self.achievements["技能宗师"]["completed"]
        ):
            self.complete_achievement("技能宗师")
            newly_completed.append("技能宗师")

        # 检查技能收藏家：学习所有5个技能
        if (
            all(skill["level"] > 0 for skill in self.player.skills.values())
            and not self.achievements["技能收藏家"]["completed"]
        ):
            self.complete_achievement("技能收藏家")
            newly_completed.append("技能收藏家")

        # 显示新完成的成就
        if newly_completed:
            achievement_names = "、".join(newly_completed)
            if self.display:
                self.display.show_message(
                    "成就系统", f"🏆 成就解锁：{achievement_names}！"
                )
            else:
                print(f"🏆 成就解锁：{achievement_names}！")

    def complete_achievement(self, achievement_name):
        """完成成就并发放奖励"""
        if achievement_name in self.achievements:
            achievement = self.achievements[achievement_name]
            if not achievement["completed"]:
                achievement["completed"] = True
                self.player.coin += achievement["reward"]
                # 使用 self.display 显示成就完成信息
                if self.display:
                    self.display.show_message(
                        "成就完成",
                        f"成就完成：{achievement_name}，"
                        f"奖励{achievement['reward']}金币！",
                    )
                else:
                    print(
                        f"成就完成：{achievement_name}，"
                        f"奖励{achievement['reward']}金币！"
                    )

    def show_achievements(self):
        """显示成就列表"""
        msg = "成就列表\n\n"
        completed_count = 0

        for name, data in self.achievements.items():
            status = "✅" if data["completed"] else "❌"
            msg += (
                f"{status} {name}: {data['description']} "
                f"(奖励: {data['reward']}金币)\n"
            )
            if data["completed"]:
                completed_count += 1

        msg += f"\n完成进度: {completed_count}/{len(self.achievements)}"
        self.display.show_message("成就系统", msg)

    def open_chest(self):
        if self.player.coin < 70:
            self.no_money()
            return

        self.player.coin -= 70
        outcome = random.randint(1, 5)

        if outcome == 1:
            val = random.randint(-20, 30)
            self.player.max_life += val
            if self.display:
                self.display.show_info(f"抽奖结果：生命上限变化 {val}")
                self.display.show_message(
                    "宝箱抽奖", f"抽奖结果：生命上限变化 {val}"
                )
        elif outcome == 2:
            val = random.randint(-5, 10)
            self.player.attack += val
            if self.display:
                self.display.show_info(f"抽奖结果：伤害变化 {val}")
        elif outcome == 3:
            val = random.randint(-1, 1)
            self.player.crit_max += val
            # 确保crit_max不小于crit_min
            if self.player.crit_max < self.player.crit_min:
                self.player.crit_max = self.player.crit_min
            if self.display:
                self.display.show_info(f"抽奖结果：伤害上限倍率变化 {val}")
        elif outcome == 4:
            val = random.randint(0, 1)
            self.player.crit_min += val
            # 确保crit_min不超过crit_max
            if self.player.crit_min > self.player.crit_max:
                self.player.crit_max = self.player.crit_min
            if self.display:
                self.display.show_info(f"抽奖结果：伤害下限倍率变化 {val}")
        elif outcome == 5:
            self.player.oxygen += 1
            if self.display:
                self.display.show_info("获得了氧气 x1")

        time.sleep(1)

    def save_game(self):
        """保存游戏"""
        save_data = {
            "name": self.player.name,
            "life": self.player.life,
            "max_life": self.player.max_life,
            "attack": self.player.attack,
            "coin": self.player.coin,
            "crit_max": self.player.crit_max,
            "crit_min": self.player.crit_min,
            "oxygen": self.player.oxygen,
            "level": self.player.level,
            "exp": self.player.exp,
            "exp_to_next": self.player.exp_to_next,
            "monsters_defeated": self.player.monsters_defeated,
            "lmode": self.lmode,
            "amode": self.amode,
            "element_damage_bonus": self.player.element_damage_bonus,
            "temporary_element_boost": (self.player.temporary_element_boost),
            "temporary_boost_turns": self.player.temporary_boost_turns,
            "skill_points": self.player.skill_points,
            "endless_high_score": self.endless_high_score,
            "temple_enemies_defeated": ",".join(self.temple_enemies_defeated),
        }

        # 保存技能数据
        for skill_name, skill_data in self.player.skills.items():
            save_data[f"skill_{skill_name}_level"] = skill_data["level"]
            save_data[f"skill_{skill_name}_cooldown"] = skill_data["cooldown"]

        # 保存成就数据
        for achievement_name, achievement_data in self.achievements.items():
            save_data[f"achievement_{achievement_name}"] = achievement_data[
                "completed"
            ]

        try:
            save_file = get_save_path()
            with open(save_file, "w") as f:
                for key, value in save_data.items():
                    f.write(f"{key}:{value}\n")
            self.display.show_message("保存成功", "游戏已保存！")
        except Exception as e:
            self.display.show_message("错误", f"保存失败: {e}")

    def load_game(self):
        """加载游戏"""
        try:
            save_file = get_save_path()
            if not save_file.exists():
                return False

            save_data = {}
            with open(save_file, "r") as f:
                for line in f:
                    if ":" in line:
                        key, value = line.strip().split(":", 1)
                        save_data[key] = value

            # 恢复玩家数据
            self.player.name = save_data.get("name", "勇者")
            self.player.life = float(save_data.get("life", 100))
            self.player.max_life = float(save_data.get("max_life", 100))
            self.player.attack = float(save_data.get("attack", 10))
            self.player.coin = int(save_data.get("coin", 100))
            self.player.crit_max = int(save_data.get("crit_max", 2))
            self.player.crit_min = int(save_data.get("crit_min", 0))
            self.player.oxygen = int(save_data.get("oxygen", 0))
            self.player.level = int(save_data.get("level", 1))
            self.player.exp = int(save_data.get("exp", 0))
            self.player.exp_to_next = int(save_data.get("exp_to_next", 100))
            monsters_defeated = int(save_data.get("monsters_defeated", 0))
            self.player.monsters_defeated = monsters_defeated
            self.lmode = float(save_data.get("lmode", 1.0))
            self.amode = float(save_data.get("amode", 1.0))
            # 新增属性
            self.player.element_damage_bonus = float(
                save_data.get("element_damage_bonus", 1.0)
            )
            self.player.temporary_element_boost = float(
                save_data.get("temporary_element_boost", 1.0)
            )
            self.player.temporary_boost_turns = int(
                save_data.get("temporary_boost_turns", 0)
            )
            self.player.skill_points = int(save_data.get("skill_points", 0))

            # 恢复无尽模式最高分
            self.endless_high_score = int(
                save_data.get("endless_high_score", 0)
            )
            # 恢复古代神殿击败记录
            temple_str = save_data.get("temple_enemies_defeated", "")
            self.temple_enemies_defeated = (
                [e for e in temple_str.split(",") if e] if temple_str else []
            )

            # 加载技能数据
            for skill_name in self.player.skills.keys():
                self.player.skills[skill_name]["level"] = int(
                    save_data.get(f"skill_{skill_name}_level", 0)
                )
                self.player.skills[skill_name]["cooldown"] = int(
                    save_data.get(f"skill_{skill_name}_cooldown", 0)
                )

            # 加载成就数据
            for achievement_name in self.achievements.keys():
                self.achievements[achievement_name]["completed"] = (
                    save_data.get(f"achievement_{achievement_name}", "False")
                    == "True"
                )

            return True
        except Exception as e:
            if self.display:
                self.display.show_message("错误", f"加载失败: {e}")
            else:
                print(f"加载失败: {e}")
            return False

    def run(self):
        # 显示模式选择（仅在启动时显示一次）
        if not hasattr(self, "_mode_selected"):
            # 检查命令行参数
            selected_mode = None
            import sys

            if "--terminal" in sys.argv or "-t" in sys.argv:
                selected_mode = "terminal"
            elif "--gui" in sys.argv or "-g" in sys.argv:
                selected_mode = "gui"
            elif "--both" in sys.argv or "-b" in sys.argv:
                selected_mode = "both"

            # 如果没有命令行参数，显示模式选择界面
            if selected_mode is None:
                # 优先尝试GUI模式，如果GUI不可用才回退到终端模式选择
                # 先尝试GUI模式
                try:
                    import easygui

                    mode_choices = [
                        "GUI模式 (图形界面)",
                        "终端模式 (命令行界面)",
                        "混合模式 (优先GUI，失败时使用终端)",
                    ]

                    selection = easygui.choicebox(
                        "JOJO Soul - 显示模式选择\n\n请选择您偏好的显示模式：",
                        "选择显示模式",
                        choices=mode_choices,
                    )

                    if selection == "GUI模式 (图形界面)":
                        selected_mode = "gui"
                    elif selection == "终端模式 (命令行界面)":
                        selected_mode = "terminal"
                    elif selection == "混合模式 (优先GUI，失败时使用终端)":
                        selected_mode = "both"
                    else:
                        selected_mode = "both"  # 默认混合模式
                except Exception:
                    # GUI不可用，使用终端模式选择
                    mode_choices = [
                        "GUI模式 (图形界面)",
                        "终端模式 (命令行界面)",
                        "混合模式 (优先GUI，失败时使用终端)",
                    ]

                    print("=== JOJO Soul - 显示模式选择 ===")
                    print("请选择您偏好的显示模式：")
                    for i, choice in enumerate(mode_choices):
                        print(f"{i + 1}. {choice}")

                    selected_mode = "both"  # 默认值
                    while True:
                        try:
                            selection = input(
                                "请输入选择 (1-3，默认为3): "
                            ).strip()
                            if not selection:
                                selection = "3"

                            if selection == "1":
                                selected_mode = "gui"
                                print("已选择：GUI模式")
                                break
                            elif selection == "2":
                                selected_mode = "terminal"
                                print("已选择：终端模式")
                                break
                            elif selection == "3":
                                selected_mode = "both"
                                print("已选择：混合模式")
                                break
                            else:
                                print("无效选择，请输入1-3")
                        except KeyboardInterrupt:
                            print("\n使用默认混合模式")
                            selected_mode = "both"
                            break
                        except ValueError:
                            print("请输入有效数字")

            # 现在根据用户选择创建DisplayManager
            from display_manager import DisplayManager

            self.display = DisplayManager(mode=selected_mode)
            # 将 display 设置到 player 对象上
            self.player.display = self.display

            # 显示当前模式信息
            if self.display.use_gui():
                self.display.show_message(
                    "显示模式", f"当前显示模式: {self.display.get_mode()}"
                )
            else:
                print(f"当前显示模式: {self.display.get_mode()}")
                print("=== 开始游戏 ===\n")

            # 标记已选择模式，避免重复显示
            self._mode_selected = True
        else:
            # 如果已经选择过模式，确保display已初始化
            if self.display is None:
                from display_manager import DisplayManager

                self.display = DisplayManager(mode="both")

        self.display.show_message(
            "JOJO Soul", f"JOJO Soul v{VERSION}\n作者：YricOTF (Refactored)"
        )
        time.sleep(1)

        # 角色命名
        player_name = self.display.get_input("角色创建", "请输入你的名字：")
        if player_name:
            self.player.name = player_name
            self.display.show_message("欢迎", f"欢迎, {self.player.name}!")
        else:
            self.player.name = "勇者"
            self.display.show_message("欢迎", f"欢迎, {self.player.name}!")

        # 检查是否有存档
        save_file = get_save_path()
        if save_file.exists():
            if (
                self.display.get_choice("加载游戏", ["加载存档", "新游戏"])
                == "加载存档"
            ):
                if self.load_game():
                    self.display.show_message(
                        "加载成功",
                        f"欢迎回来, {self.player.name}!\n等级: {self.player.level}",
                    )
                else:
                    self.display.show_message("错误", "加载失败，开始新游戏")
            else:
                save_file.unlink()  # 删除旧存档

        if not self.display.get_yes_no("开始游戏", "是否开始游戏？"):
            sys.exit()

        self.set_difficulty()

        # 剧情文本
        story = [
            f"{self.player.name}，你降落在这个大陆",
            "这个大陆被普奇神父所控制",
            "他想重启世界",
            "你是阻止他的最后希望",
            f"先打怪升级吧，{self.player.name}！",
        ]

        # 在GUI模式下，将剧情合并显示
        if self.display.use_gui():
            story_text = "\n".join(story)
            self.display.show_message("剧情", story_text)
        else:
            # 终端模式逐行显示
            for line in story:
                print(line)
                time.sleep(1)

        while True:
            self.check_stat_anomalies()

            action = self.display.get_choice(
                "选择行动",
                [
                    "商店",
                    "技能系统",
                    "成就系统",
                    "丛林",
                    "山洞",
                    "腐化之地",
                    "熔岩地下城",
                    "雪山",
                    "暗影遗迹",
                    "风暴高地",
                    "古代神殿",
                    "时空裂隙",
                    "天国前哨",
                    "混沌领域",
                    "天国",
                    "角色资料",
                    "保存游戏",
                    "退出游戏",
                ],
            )

            if not action or action == "退出游戏":
                sys.exit()

            if action == "商店":
                self.shop()
            elif action == "技能系统":
                self.skill_menu()
            elif action == "成就系统":
                self.show_achievements()
            elif action == "角色资料":
                self.player.show_stats()
            elif action == "保存游戏":
                self.save_game()
            elif action == "丛林":
                # 树妖：火x2, 水x0.5...
                self._battle_or_die(
                    "树妖",
                    120,
                    random.randint(4, 10),
                    100,
                    {
                        "火焰": 2.0,
                        "水": 0.5,
                        "土地": 0.5,
                        "暗黑魔法": 1.5,
                        "闪光": 1.1,
                    },
                )
            elif action == "山洞":
                # 吸血鬼
                self._battle_or_die(
                    "吸血鬼",
                    200,
                    18,
                    150,
                    {
                        "火焰": 1.3,
                        "水": 0.5,
                        "土地": 0.5,
                        "暗黑魔法": 1.5,
                        "闪光": 2.1,
                    },
                )
            elif action == "腐化之地":
                # 25%概率出现高级变种深渊吞噬者，否则为普通沼泽怪
                if random.random() < 0.25:
                    # 深渊吞噬者
                    self._battle_or_die(
                        "深渊吞噬者",
                        420,
                        38,
                        450,
                        {
                            "火焰": 1.8,
                            "水": -1.2,
                            "土地": 0.2,
                            "暗黑魔法": 2.8,
                            "闪光": 0.8,
                        },
                    )
                else:
                    # 沼泽怪
                    self._battle_or_die(
                        "沼泽怪",
                        250,
                        17,
                        200,
                        {
                            "火焰": 0.3,
                            "水": 1.5,
                            "土地": 2.5,
                            "暗黑魔法": 1.5,
                            "闪光": 0.1,
                        },
                    )
            elif action == "熔岩地下城":
                # 熔岩怪：注意这里火是-2.0(回血)，原代码逻辑复现
                self._battle_or_die(
                    "熔岩怪",
                    150,
                    12,
                    0,
                    {
                        "火焰": -2.0,
                        "水": 2.5,
                        "土地": 1.5,
                        "暗黑魔法": 0.5,
                        "闪光": 0.1,
                    },
                )
            elif action == "雪山":
                # 需要等级5解锁
                if self.player.level < 5:
                    self.display.show_message(
                        "等级不足", "需要达到5级才能进入雪山！"
                    )
                    continue
                # 冰霜巨人
                self._battle_or_die(
                    "冰霜巨人",
                    300,
                    25,
                    250,
                    {
                        "火焰": 3.0,
                        "水": -1.5,
                        "土地": 0.8,
                        "暗黑魔法": 1.2,
                        "闪光": 0.5,
                    },
                )
            elif action == "暗影遗迹":
                # 需要击败沼泽怪解锁
                if self.player.monsters_defeated < 3:
                    self.display.show_message(
                        "条件不足", "需要先击败腐化之地的沼泽怪才能进入！"
                    )
                    continue
                # 暗影刺客
                self._battle_or_die(
                    "暗影刺客",
                    180,
                    30,
                    300,
                    {
                        "火焰": 0.5,
                        "水": 0.5,
                        "土地": 0.5,
                        "暗黑魔法": -2.0,
                        "闪光": 3.0,
                    },
                )
            elif action == "风暴高地":
                # 需要击败熔岩怪解锁
                if self.player.monsters_defeated < 4:
                    self.display.show_message(
                        "条件不足", "需要先击败熔岩地下城的熔岩怪才能进入！"
                    )
                    continue
                # 雷电元素
                self._battle_or_die(
                    "雷电元素",
                    220,
                    28,
                    280,
                    {
                        "火焰": 1.0,
                        "水": 2.0,
                        "土地": 0.3,
                        "暗黑魔法": 1.5,
                        "闪光": -1.8,
                    },
                )
            elif action == "古代神殿":
                # 需要等级8解锁
                if self.player.level < 8:
                    self.display.show_message(
                        "等级不足", "需要达到8级才能进入古代神殿！"
                    )
                    continue
                # 随机选择一个高级敌人
                enemy_choice = self.display.get_choice(
                    "选择挑战的敌人",
                    ["石像守卫", "古代法师", "神殿骑士"],
                )
                if enemy_choice == "石像守卫":
                    self._battle_or_die(
                        "石像守卫",
                        350,
                        35,
                        400,
                        {
                            "火焰": 0.5,
                            "水": 0.5,
                            "土地": -1.5,
                            "暗黑魔法": 0.8,
                            "闪光": 2.5,
                        },
                    )
                elif enemy_choice == "古代法师":
                    self._battle_or_die(
                        "古代法师",
                        280,
                        40,
                        450,
                        {
                            "火焰": 2.0,
                            "水": -2.0,
                            "土地": 1.5,
                            "暗黑魔法": 3.0,
                            "闪光": 0.1,
                        },
                    )
                elif enemy_choice == "神殿骑士":
                    self._battle_or_die(
                        "神殿骑士",
                        400,
                        30,
                        500,
                        {
                            "火焰": 1.5,
                            "水": 1.0,
                            "土地": 2.0,
                            "暗黑魔法": -1.0,
                            "闪光": 1.8,
                        },
                    )
            elif action == "时空裂隙":
                # 需要击败古代神殿任意敌人解锁
                if self.player.monsters_defeated < 5:
                    self.display.show_message(
                        "条件不足",
                        "需要先击败古代神殿的任意敌人才能进入时空裂隙！",
                    )
                    continue
                # 时空扭曲者
                self._battle_or_die(
                    "时空扭曲者",
                    280,
                    32,
                    350,
                    {
                        "火焰": 0.3,
                        "水": 0.3,
                        "土地": 0.3,
                        "暗黑魔法": -2.5,
                        "闪光": 3.5,
                    },
                )
            elif action == "天国前哨":
                # 需要等级10解锁
                if self.player.level < 10:
                    self.display.show_message(
                        "等级不足", "需要达到10级才能进入天国前哨！"
                    )
                    continue
                # 神圣护卫
                self._battle_or_die(
                    "神圣护卫",
                    380,
                    42,
                    500,
                    {
                        "火焰": 1.2,
                        "水": 1.2,
                        "土地": 1.2,
                        "暗黑魔法": 0.1,
                        "闪光": 2.5,
                    },
                )
            elif action == "混沌领域":
                # 需要完成"元素大师"成就解锁
                if not self.achievements["元素大师"]["completed"]:
                    self.display.show_message(
                        "条件不足", "需要完成'元素大师'成就才能进入混沌领域！"
                    )
                    continue
                # 混沌元素 - 随机属性
                base_hp = random.randint(200, 400)
                base_atk = random.randint(20, 40)
                reward_coin = random.randint(300, 600)

                # 随机元素倍率（每回合变化在battle中处理较复杂，这里使用固定随机倍率）
                multipliers = {
                    "火焰": random.uniform(0.5, 3.0),
                    "水": random.uniform(0.5, 3.0),
                    "土地": random.uniform(0.5, 3.0),
                    "暗黑魔法": random.uniform(0.5, 3.0),
                    "闪光": random.uniform(0.5, 3.0),
                }

                self.display.show_message(
                    "混沌领域",
                    f"遇到混沌元素！\n血量: {base_hp}, 攻击: {base_atk}, "
                    f"金币: {reward_coin}",
                )

                # 战斗后给予双倍经验奖励（通过修改exp_gain在battle中实现较复杂，这里先简单处理）
                # 保存原始battle调用，战斗胜利后手动增加经验
                original_monsters_defeated = self.player.monsters_defeated

                self._battle_or_die(
                    "混沌元素",
                    base_hp,
                    base_atk,
                    reward_coin,
                    multipliers,
                )

                # 如果怪物被击败（monsters_defeated增加）
                if self.player.monsters_defeated > original_monsters_defeated:
                    # 计算基础经验并加倍
                    base_exp = int(base_hp * 0.1 + base_atk * 2)
                    extra_exp = base_exp  # 双倍经验 = 额外增加100%
                    self.player.gain_exp(extra_exp)
                    self.display.show_message(
                        "混沌奖励",
                        f"混沌元素被击败！获得额外{extra_exp}经验值！",
                    )
            elif action == "天国":
                self.boss_battle()

    def check_endless_achievements(self):
        """检查无尽模式相关成就"""
        # 使用无尽模式最高分进行检查
        if (
            self.endless_high_score >= 10
            and not self.achievements["无尽新手"]["completed"]
        ):
            self.complete_achievement("无尽新手")
        if (
            self.endless_high_score >= 50
            and not self.achievements["无尽勇士"]["completed"]
        ):
            self.complete_achievement("无尽勇士")
        if (
            self.endless_high_score >= 100
            and not self.achievements["无尽王者"]["completed"]
        ):
            self.complete_achievement("无尽王者")
        if (
            self.endless_high_score >= 200
            and not self.achievements["无尽传奇"]["completed"]
        ):
            self.complete_achievement("无尽传奇")


if __name__ == "__main__":
    game = Game()
    game.run()
