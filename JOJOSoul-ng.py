import easygui
import time
import sys
import random
import os

# 游戏版本
VERSION = "1.0.0"


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
            f"纯氧数量: {self.oxygen}\n"
            f"击败怪物: {self.monsters_defeated}"
        )
        print(info)
        # 同时也弹窗显示，体验更好
        easygui.msgbox(info, f"{self.name}的资料")

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

        print(f"🎉 恭喜升级到 {self.level} 级！")
        print("生命上限 +10，攻击力 +2")
        time.sleep(1)


class Game:
    def __init__(self):
        self.player = Player()
        self.lmode = 1.0  # 血量倍率
        self.amode = 1.0  # 攻击倍率
        self.elements = ["火焰", "水", "土地", "暗黑魔法", "闪光"]

    def set_difficulty(self):
        mode = easygui.choicebox(
            "选择难度", "难度选择", ["无限金币版", "简单", "普通", "坤难", "炼狱"]
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
        print(f"\n>>> 开始战斗: {name} <<<")
        time.sleep(1)

        enemy_hp = base_hp * self.lmode
        enemy_atk = base_atk * self.amode

        # 熔岩怪特殊机制：如果倍率是正数代表造成伤害，原代码中熔岩怪火属性是 +，代表回血（反向伤害）
        # 这里为了统一逻辑：multipliers 中正值为对敌人造成伤害倍率，负值为敌人回血倍率

        while True:
            crit = self.get_attack_multiplier()
            choice = easygui.choicebox(
                f"对战 {name} - 选择攻击元素", "战斗中", self.elements
            )
            if not choice:
                continue  # 防止点了取消报错

            # 计算对敌人伤害
            dmg_mult = multipliers.get(choice, 1.0)

            # 特殊处理：原代码中熔岩怪碰到火焰是 Elife = Elife + ... (回血)
            # 我们约定：如果传入的 multiplier 是负数，则代表给敌人回血

            damage = self.player.attack * dmg_mult * crit

            # 原代码逻辑还原：
            # 大部分怪：Elife = Elife - (attck * mult * crit)
            # 熔岩怪火属性：Elife = Elife + (attck * 2 * crit) -> 相当于伤害是 -2.0

            if damage > 0:
                enemy_hp -= damage
                print(f"你使用[{choice}]造成了 {damage:.1f} 点伤害！")
            else:
                enemy_hp -= damage  # 减去负数等于加血
                print(f"你的攻击被吸收了！敌人恢复了 {abs(damage):.1f} 点血量！")

            # 敌人攻击
            self.player.life -= enemy_atk

            time.sleep(1)
            print(f"敌方({name})血量：{enemy_hp:.1f}")
            print(f"我方血量：{self.player.life:.1f}")
            time.sleep(0.5)

            if not self.player.is_alive():
                print("你死了！！！")
                easygui.msgbox("你被打败了...", "游戏结束")
                sys.exit(0)

            if enemy_hp <= 0:
                print("你赢了！！！")
                self.player.coin += reward_coin
                self.player.monsters_defeated += 1

                # 计算经验值
                exp_gain = int(base_hp * 0.1 + base_atk * 2)
                self.player.gain_exp(exp_gain)

                print(f"获得金币: {reward_coin}")
                print(f"获得经验: {exp_gain}")
                break

    def boss_battle(self):
        print("\n>>> 最终战斗: 普奇神父 <<<")
        time.sleep(1)
        enemy_hp = 1000
        enemy_atk = 50
        turn_limit = 12

        print('普奇神父向你靠来:"[MADE IN HEAVEN!]"')

        while True:
            crit = self.get_attack_multiplier()
            if (
                easygui.buttonbox(
                    f"离[天国之时]还有 {turn_limit} [天国之刻]", "Heaven", ["阻止他"]
                )
                is None
            ):
                sys.exit()

            if turn_limit <= 0:
                print("世界重启了，你噶了")
                sys.exit()

            # 1=命中, 2=闪避(除非特殊攻击)
            block = random.randint(1, 2)

            options = self.elements + ["纯氧"]
            choice = easygui.choicebox("选择攻击元素", "决战", options)
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
                    print("你没有足够的纯氧！普奇还是逃了出来。")
                else:
                    print("神父吸入纯氧！")
                    print("隐藏结局：我是安波里欧")
                    time.sleep(2)
                    sys.exit()
            elif block == 2 and choice != "闪光" and choice != "纯氧":
                print("普奇速度过快，你没有打到！")

            # 敌人反击
            # 原版逻辑：life = life - Eattck * block (如果普奇闪避了，伤害翻倍？block是1或2)
            dmg_to_player = enemy_atk * block
            self.player.life -= dmg_to_player
            turn_limit -= 1

            if damage > 0:
                print(f"你造成了 {damage:.1f} 点伤害！")

            print(f"敌方血量：{enemy_hp:.1f} | 我方血量：{self.player.life:.1f}")

            if not self.player.is_alive():
                print("你死了！！！")
                sys.exit()
            elif enemy_hp <= 0:
                if self.player.coin > 1000000000:  # 粗略判断是否作弊版
                    print("普奇：纪狗气死我了")
                else:
                    print("你赢了！！！，恭喜通关！")
                time.sleep(3)
                sys.exit()

    def shop(self):
        while True:
            msg = f"金币剩余: {self.player.coin}"
            choices = [
                "盔甲 [100G, +30HP上限]",
                "剑 [100G, +5伤害]",
                "药水 [50G, 回满HP]",
                "宝箱 [70G, 随机抽奖]",
                "离开商店",
            ]
            x = easygui.choicebox(msg, "商店", choices)

            if not x or x == "离开商店":
                break

            if "盔甲" in x:
                if self.player.coin >= 100:
                    self.player.max_life += 30
                    self.player.coin -= 100
                    print("购买成功：生命上限+30")
                else:
                    self.no_money()
            elif "剑" in x:
                if self.player.coin >= 100:
                    self.player.attack += 5
                    self.player.coin -= 100
                    print("购买成功：伤害+5")
                else:
                    self.no_money()
            elif "药水" in x:
                if self.player.coin >= 50:
                    self.player.heal_full()
                    self.player.coin -= 50
                    print("购买成功：生命已回满")
                else:
                    self.no_money()
            elif "宝箱" in x:
                self.open_chest()

    def no_money(self):
        easygui.msgbox("金币不足！", "错误")

    def open_chest(self):
        if self.player.coin < 70:
            self.no_money()
            return

        self.player.coin -= 70
        outcome = random.randint(1, 5)

        if outcome == 1:
            val = random.randint(-20, 30)
            self.player.max_life += val
            print(f"抽奖结果：生命上限变化 {val}")
        elif outcome == 2:
            val = random.randint(-5, 10)
            self.player.attack += val
            print(f"抽奖结果：伤害变化 {val}")
        elif outcome == 3:
            val = random.randint(-1, 1)
            self.player.crit_max += val
            print(f"抽奖结果：伤害上限倍率变化 {val}")
        elif outcome == 4:
            val = random.randint(0, 1)
            self.player.crit_min += val
            print(f"抽奖结果：伤害下限倍率变化 {val}")
        elif outcome == 5:
            self.player.oxygen += 1
            print("获得了氧气 x1")

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
        }

        try:
            with open("savegame.dat", "w") as f:
                for key, value in save_data.items():
                    f.write(f"{key}:{value}\n")
            print("游戏已保存！")
            easygui.msgbox("游戏已保存！", "保存成功")
        except Exception as e:
            print(f"保存失败: {e}")
            easygui.msgbox(f"保存失败: {e}", "错误")

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

            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False

    def run(self):

        print(f"JOJO Soul v{VERSION}")
        print("作者：YricOTF (Refactored)")
        time.sleep(1)

        # 角色命名
        player_name = easygui.enterbox("请输入你的名字：", "角色创建", default="勇者")
        if player_name:
            self.player.name = player_name

        print(f"欢迎, {self.player.name}!")

        # 检查是否有存档
        if os.path.exists("savegame.dat"):
            if (
                easygui.buttonbox(
                    "发现存档，是否加载？", "加载游戏", ["加载存档", "新游戏"]
                )
                == "加载存档"
            ):
                if self.load_game():
                    print(f"欢迎回来, {self.player.name}！")
                    easygui.msgbox(
                        f"欢迎回来, {self.player.name}！\n等级: {self.player.level}",
                        "加载成功",
                    )
                else:
                    easygui.msgbox("加载失败，开始新游戏", "错误")
            else:
                os.remove("savegame.dat")  # 删除旧存档

        if easygui.buttonbox("是否开始游戏？", choices=("YES", "NO")) == "NO":
            sys.exit()

        self.set_difficulty()

        # 剧情文本
        story = [
            f"{self.player.name}，你降落在这个大陆",
            "这个大陆被普奇神父所控制",
            "他想重启世界",
            "你是阻止他的最后希望",
            "先打怪升级吧，{self.player.name}！",
        ]
        for line in story:
            print(line)
            time.sleep(1)

        while True:
            self.check_stat_anomalies()

            action = easygui.choicebox(
                "选择行动",
                "世界地图",
                [
                    "商店",
                    "丛林",
                    "山洞",
                    "腐化之地",
                    "熔岩地下城",
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
                    {"火焰": 2.0, "水": 0.5, "土地": 0.5, "暗黑魔法": 1.5, "闪光": 1.1},
                )
            elif action == "山洞":
                # 吸血鬼
                self.battle(
                    "吸血鬼",
                    200,
                    18,
                    150,
                    {"火焰": 1.3, "水": 0.5, "土地": 0.5, "暗黑魔法": 1.5, "闪光": 2.1},
                )
            elif action == "腐化之地":
                # 沼泽怪
                self.battle(
                    "沼泽怪",
                    250,
                    17,
                    200,
                    {"火焰": 0.3, "水": 1.5, "土地": 2.5, "暗黑魔法": 1.5, "闪光": 0.1},
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
            elif action == "天国":
                self.boss_battle()


if __name__ == "__main__":
    game = Game()
    game.run()
