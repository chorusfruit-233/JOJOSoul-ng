import time
import sys
import random
import os

from display_manager import DisplayManager

# 游戏版本
VERSION = "2.0.0"


class Player:
    def __init__(self, name="勇者"):
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
        # 使用DisplayManager同时显示终端和GUI
        from display_manager import get_display_manager
        display = get_display_manager()
        display.show_info(info)
        if display.is_gui_enabled():
            display.show_message("角色信息", info)
        from display_manager import get_display_manager
        display = get_display_manager()
        display.show_message(f"{self.name}的资料", info)

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
        upgrade_msg = f"🎉 恭喜升级到 {self.level} 级！\n生命上限 +10，攻击力 +2，技能点 +1"
        
        # 由于Player类在创建时可能还没有display_manager，使用简单的print
        print("生命上限 +10，攻击力 +2，技能点 +1")
        time.sleep(1)
        
        # 尝试使用display_manager（如果可用）
        try:
            from display_manager import get_display_manager
            display = get_display_manager()
            display.show_message("升级", f"🎉 恭喜升级到 {self.level} 级！")
        except:
            pass


class Game:
    def __init__(self):
        self.player = Player()
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
        }

    def set_difficulty(self):
        mode = self.display.get_choice(
            "选择难度",
            ["无限金币版", "简单", "普通", "坤难", "炼狱"],
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
            self.lmode, self.amode = 1.3, 1.3
        elif mode == "炼狱":
            self.lmode, self.amode = 1.5, 1.5

    def check_stat_anomalies(self):
        # 检查并修复属性异常（原代码中的彩蛋/Bug修复逻辑）
        if self.player.crit_max == self.player.crit_min:
            print("恭喜你发现彩蛋！奖励810金币！")
            self.player.coin += 810
            self.player.crit_max, self.player.crit_min = 2, 0
        elif self.player.crit_max <= 0 or self.player.crit_min < 0:
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

        # 熔岩怪特殊机制：如果倍率是正数代表造成伤害，原代码中熔岩怪火属性是 +，代表回血（反向伤害）
        # 这里为了统一逻辑：multipliers 中正值为对敌人造成伤害倍率，负值为敌人回血倍率

        while True:
            crit = self.get_attack_multiplier()
            choice = self.display.get_choice(f"对战 {name} - 选择攻击元素", self.elements)
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
                    print("元素增强效果已结束！")

            damage = self.player.attack * dmg_mult * crit * total_element_bonus

            # 原代码逻辑还原：
            # 大部分怪：Elife = Elife - (attck * mult * crit)
            # 熔岩怪火属性：Elife = Elife + (attck * 2 * crit) -> 相当于伤害是 -2.0

            if damage > 0:
                enemy_hp -= damage
                self.display.show_battle_info("攻击", f"你使用[{choice}]造成了 {damage:.1f} 点伤害！")
            else:
                enemy_hp -= damage  # 减去负数等于加血
                absorb_info = f"你的攻击被吸收了！敌人恢复了 {abs(damage):.1f} 点血量！"
                if self.display.use_gui():
                    self.display.show_battle_info("攻击被吸收", absorb_info)
                else:
                    print(absorb_info)

            # 敌人攻击
            self.player.life -= enemy_atk

            time.sleep(1)
            # 显示战斗血量信息
            battle_info = f"敌方({name})血量：{enemy_hp:.1f}\n我方血量：{self.player.life:.1f}"
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
                sys.exit(0)

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
                    from display_manager import get_display_manager
                    display = get_display_manager()
                    display.show_message("成就解锁", "🏆 成就解锁：雪山征服者！")
                elif (
                    name == "暗影刺客"
                    and not self.achievements["暗影克星"]["completed"]
                ):
                    from display_manager import get_display_manager
                    display = get_display_manager()
                    display.show_message("成就解锁", "🏆 成就解锁：暗影克星！")
                    self.complete_achievement("暗影克星")
                    display.show_message("成就解锁", "🏆 成就解锁：风暴掌控者！")
                elif name in ["石像守卫", "古代法师", "神殿骑士"]:
                    # 检查是否击败了所有神殿敌人
                    temple_enemies_defeated = getattr(
                        self, "temple_enemies_defeated", []
                    )
                    if name not in temple_enemies_defeated:
                        temple_enemies_defeated.append(name)
                        self.temple_enemies_defeated = temple_enemies_defeated

                    if (
                        len(self.temple_enemies_defeated) >= 3
                        and not self.achievements["神殿英雄"]["completed"]
                    ):
                        self.complete_achievement("神殿英雄")
                        from display_manager import get_display_manager
                        display = get_display_manager()
                        display.show_message("成就解锁", "🏆 成就解锁：神殿英雄！")

                # 检查一般成就
                self.check_achievements()
                break

    def boss_battle(self):
        self.display.show_battle_info("最终战斗", "普奇神父")
        time.sleep(1)
        enemy_hp = 1000
        enemy_atk = 50
        turn_limit = 12

        print('普奇神父向你靠来:"[MADE IN HEAVEN!]"')

        while True:
            crit = self.get_attack_multiplier()
            if not self.display.get_yes_no(
                "Heaven",
                f"离[天国之时]还有 {turn_limit} [天国之刻]，是否阻止他？"
            ):
                sys.exit()

            if turn_limit <= 0:
                print("世界重启了，你噶了")
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
                    msg = "你没有足够的纯氧！普奇还是逃了出来。"
                    if self.display.use_gui():
                        self.display.show_message("纯氧不足", msg)
                    else:
                        print(msg)
                else:
                    msg1 = "神父吸入纯氧！"
                    msg2 = "隐藏结局：我是安波里欧"
                    if self.display.use_gui():
                        self.display.show_message("隐藏结局", f"{msg1}\n{msg2}")
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
                self.display.show_battle_info("攻击", f"你造成了 {damage:.1f} 点伤害！")

            # 显示Boss战血量信息
            boss_battle_info = f"敌方血量：{enemy_hp:.1f} | 我方血量：{self.player.life:.1f}"
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
                        self.display.show_message("成就解锁", "🏆 成就解锁：世界拯救者！")
                
                # 显示胜利信息
                if self.display.use_gui():
                    self.display.show_message("游戏通关", victory_msg)
                
                time.sleep(3)
                sys.exit()

    def shop(self):
        while True:
            msg = f"金币剩余: {self.player.coin}"
            # 根据玩家等级解锁新物品
            choices = [
                "盔甲 [100G, +30HP上限]",
                "剑 [100G, +5伤害]",
                "药水 [50G, 回满HP]",
                "宝箱 [70G, 随机抽奖]",
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
            x = self.display.get_choice("商店", choices)

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
            elif "魔法袍" in x:
                if self.player.coin >= 200:
                    self.player.element_damage_bonus += 0.15
                    self.player.coin -= 200
                    self.display.show_message("购买成功", "元素伤害+15%")
                    # 检查元素大师成就
                    if not self.achievements["元素大师"]["completed"]:
                        self.complete_achievement("元素大师")
                        self.display.show_message("成就解锁", "🏆 成就解锁：元素大师！")
                else:
                    self.no_money()
            elif "力量护符" in x:
                if self.player.coin >= 150:
                    self.player.crit_min += 3
                    self.player.coin -= 150
                    self.display.show_message("购买成功", "伤害下限倍率+3")
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
                f"{element_choice}伤害临时提升100%，持续3回合！"
            )

    def skill_menu(self):
        """技能菜单"""
        while True:
            msg = f"技能点: {self.player.skill_points}\n\n"
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

            choice = self.display.get_choice("技能系统", skill_list)
            if not choice or choice == "返回":
                break

            # 提取技能名称
            skill_name = choice.split(" Lv.")[0]
            if skill_name in self.player.skills:
                self.manage_skill(skill_name)

    def manage_skill(self, skill_name):
        """管理单个技能"""
        skill = self.player.skills[skill_name]

        # 技能描述
        descriptions = {
            "火球术": "造成50点火焰伤害，无视元素倍率",
            "治疗术": "恢复50%最大生命值",
            "护盾": "下回合受到伤害减半",
            "元素爆发": "所有元素伤害倍率x2，持续3回合",
            "时间减缓": "敌人下回合无法攻击",
        }

        msg = f"{skill_name} (等级: {skill['level']})\n\n"
        msg += f"描述: {descriptions.get(skill_name, '未知技能')}\n"
        msg += f"冷却时间: {skill['max_cooldown']}回合\n"
        msg += f"当前冷却: {skill['cooldown']}回合\n\n"

        if skill["level"] == 0:
            msg += "学习此技能需要1个技能点"
            choices = ["学习技能", "返回"]
        else:
            msg += "升级技能需要1个技能点"
            choices = ["升级技能", "使用技能", "返回"]

        action = self.display.get_choice(f"{skill_name}管理", choices)
        if not action or action == "返回":
            return

        if action == "学习技能" or action == "升级技能":
            if self.player.skill_points >= 1:
                self.player.skill_points -= 1
                skill["level"] += 1
                from display_manager import get_display_manager
                display = get_display_manager()
                display.show_message("技能升级", f"{skill_name}升级到Lv.{skill['level']}！")

                # 检查技能新手成就
                if not self.achievements["技能新手"]["completed"]:
                    self.complete_achievement("技能新手")
                    display.show_message("成就解锁", "🏆 成就解锁：技能新手！")
            else:
                display.show_message("错误", "技能点不足！")
        elif action == "使用技能":
            if skill["cooldown"] > 0:
                self.display.show_message("错误", "技能还在冷却中！")
            else:
                self.use_skill(skill_name)

    def use_skill(self, skill_name):
        """使用技能"""
        skill = self.player.skills[skill_name]

        if skill_name == "火球术":
            damage = 50 * skill["level"]
            self.display.show_battle_info("火球术", f"造成{damage}点火焰伤害！")
            return damage
        elif skill_name == "治疗术":
            heal_amount = self.player.max_life * 0.5 * skill["level"]
            self.player.life = min(
                self.player.life + heal_amount, self.player.max_life
            )
            self.display.show_battle_info("治疗", f"治疗术恢复了{heal_amount:.1f}点生命值！")
            return 0
        elif skill_name == "护盾":
            self.display.show_battle_info("护盾", "护盾激活！下回合受到伤害减半！")
            self.player.shield_active = True
            return 0
        elif skill_name == "元素爆发":
            self.player.element_damage_bonus *= 2.0
            self.display.show_battle_info("元素爆发", "所有元素伤害倍率x2，持续3回合！")
            return 0
        elif skill_name == "时间减缓":
            self.display.show_battle_info("时间减缓", "敌人下回合无法攻击！")
            self.player.time_slow_active = True
            return 0

        # 设置冷却
        skill["cooldown"] = skill["max_cooldown"]
        return 0

    def update_skill_cooldowns(self):
        """更新技能冷却"""
        for skill_name, skill_data in self.player.skills.items():
            if skill_data["cooldown"] > 0:
                skill_data["cooldown"] -= 1

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

        # 显示新完成的成就
        if newly_completed:
            achievement_names = "、".join(newly_completed)
            from display_manager import get_display_manager
            display = get_display_manager()
            display.show_info(f"🏆 成就解锁：{achievement_names}！")
            display.show_message("成就系统", f"🏆 成就解锁：\n{achievement_names}")

    def complete_achievement(self, achievement_name):
        """完成成就并发放奖励"""
        if achievement_name in self.achievements:
            achievement = self.achievements[achievement_name]
            if not achievement["completed"]:
                achievement["completed"] = True
                self.player.coin += achievement["reward"]
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
            from display_manager import get_display_manager
            display = get_display_manager()
            display.show_info(f"抽奖结果：生命上限变化 {val}")
            display.show_message("宝箱抽奖", f"抽奖结果：生命上限变化 {val}")
        elif outcome == 2:
            val = random.randint(-5, 10)
            self.player.attack += val
            from display_manager import get_display_manager
            display = get_display_manager()
            display.show_info(f"抽奖结果：伤害变化 {val}")
        elif outcome == 3:
            val = random.randint(-1, 1)
            self.player.crit_max += val
            from display_manager import get_display_manager
            display = get_display_manager()
            display.show_info(f"抽奖结果：伤害上限倍率变化 {val}")
        elif outcome == 4:
            val = random.randint(0, 1)
            self.player.crit_min += val
            from display_manager import get_display_manager
            display = get_display_manager()
            display.show_info(f"抽奖结果：伤害下限倍率变化 {val}")
        elif outcome == 5:
            self.player.oxygen += 1
            from display_manager import get_display_manager
            display = get_display_manager()
            display.show_info("获得了氧气 x1")

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
            with open("savegame.dat", "w") as f:
                for key, value in save_data.items():
                    f.write(f"{key}:{value}\n")
            print("游戏已保存！")
            self.display.show_message("保存成功", "游戏已保存！")
        except Exception as e:
            print(f"保存失败: {e}")
            self.display.show_message("错误", f"保存失败: {e}")

    def load_game(self):
        """加载游戏"""
        try:
            if not os.path.exists("savegame.dat"):
                return False

            save_data = {}
            with open("savegame.dat", "r") as f:
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
            print(f"加载失败: {e}")
            return False

    def run(self):
        # 显示模式选择（仅在启动时显示一次）
        if not hasattr(self, '_mode_selected'):
            # 优先尝试GUI模式，如果GUI不可用才回退到终端模式选择
            from display_manager import DisplayManager
            
            # 先尝试GUI模式
            try:
                import easygui
                mode_choices = [
                    "GUI模式 (图形界面)",
                    "终端模式 (命令行界面)", 
                    "混合模式 (优先GUI，失败时使用终端)"
                ]
                
                selection = easygui.choicebox(
                    "JOJO Soul - 显示模式选择\n\n请选择您偏好的显示模式：",
                    "选择显示模式",
                    choices=mode_choices
                )
                
                if selection == "GUI模式 (图形界面)":
                    selected_mode = 'gui'
                elif selection == "终端模式 (命令行界面)":
                    selected_mode = 'terminal'
                elif selection == "混合模式 (优先GUI，失败时使用终端)":
                    selected_mode = 'both'
                else:
                    selected_mode = 'both'  # 默认混合模式
            except:
                # GUI不可用，使用终端模式选择
                mode_choices = [
                    "GUI模式 (图形界面)",
                    "终端模式 (命令行界面)", 
                    "混合模式 (优先GUI，失败时使用终端)"
                ]
                
                print("=== JOJO Soul - 显示模式选择 ===")
                print("请选择您偏好的显示模式：")
                for i, choice in enumerate(mode_choices):
                    print(f"{i+1}. {choice}")
                
                selected_mode = 'both'  # 默认值
                while True:
                    try:
                        selection = input("请输入选择 (1-3，默认为3): ").strip()
                        if not selection:
                            selection = "3"
                        
                        if selection == "1":
                            selected_mode = 'gui'
                            print("已选择：GUI模式")
                            break
                        elif selection == "2":
                            selected_mode = 'terminal'
                            print("已选择：终端模式")
                            break
                        elif selection == "3":
                            selected_mode = 'both'
                            print("已选择：混合模式")
                            break
                        else:
                            print("无效选择，请输入1-3")
                    except KeyboardInterrupt:
                        print("\n使用默认混合模式")
                        selected_mode = 'both'
                        break
                    except ValueError:
                        print("请输入有效数字")
            
            # 现在根据用户选择创建DisplayManager
            self.display = DisplayManager(mode=selected_mode)
            
            # 显示当前模式信息
            if self.display.use_gui():
                self.display.show_message("显示模式", f"当前显示模式: {self.display.get_mode()}")
            else:
                print(f"当前显示模式: {self.display.get_mode()}")
                print("=== 开始游戏 ===\n")
            
            # 标记已选择模式，避免重复显示
            self._mode_selected = True
        else:
            # 如果已经选择过模式，确保display已初始化
            if self.display is None:
                from display_manager import DisplayManager
                self.display = DisplayManager(mode='both')

        print(f"JOJO Soul v{VERSION}")
        print("作者：YricOTF (Refactored)")
        time.sleep(1)

        # 角色命名
        player_name = self.display.get_input(
            "角色创建", "请输入你的名字："
        )
        if player_name:
            self.player.name = player_name
            self.display.show_message("欢迎", f"欢迎, {self.player.name}!")
        else:
            self.player.name = "勇者"
            self.display.show_message("欢迎", f"欢迎, {self.player.name}!")

    

                        # 检查是否有存档
            if os.path.exists("savegame.dat"):
                if self.display.get_choice("加载游戏", ["加载存档", "新游戏"]) == "加载存档":
                    if self.load_game():
                        print(f"欢迎回来, {self.player.name}!")
                        self.display.show_message("加载成功", f"欢迎回来, {self.player.name}!\n等级: {self.player.level}")
                    else:
                        self.display.show_message("错误", "加载失败，开始新游戏")
                else:
                    os.remove("savegame.dat")  # 删除旧存档

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
                self.battle(
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
                self.battle(
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
                # 沼泽怪
                self.battle(
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
                self.battle(
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
                    self.display.show_message("等级不足", "需要达到5级才能进入雪山！")
                    continue
                # 冰霜巨人
                self.battle(
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
                    easygui.msgbox(
                        "需要先击败腐化之地的沼泽怪才能进入！", "条件不足"
                    )
                    continue
                # 暗影刺客
                self.battle(
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
                    easygui.msgbox(
                        "需要先击败熔岩地下城的熔岩怪才能进入！", "条件不足"
                    )
                    continue
                # 雷电元素
                self.battle(
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
                    self.display.show_message("等级不足", "需要达到8级才能进入古代神殿！")
                    continue
                # 随机选择一个高级敌人
                enemy_choice = self.display.get_choice(
                    "选择挑战的敌人",
                    ["石像守卫", "古代法师", "神殿骑士"],
                )
                if enemy_choice == "石像守卫":
                    self.battle(
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
                    self.battle(
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
                    self.battle(
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
            elif action == "天国":
                self.boss_battle()


if __name__ == "__main__":
    game = Game()
    game.run()
