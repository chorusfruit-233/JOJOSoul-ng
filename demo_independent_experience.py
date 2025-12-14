#!/usr/bin/env python3
"""
演示DisplayManager的独立模式完整体验
"""

from display_manager import DisplayManager

def demo_terminal_experience():
    """演示纯终端模式的完整体验"""
    print("=== 纯终端模式演示 ===")
    dm = DisplayManager(mode='terminal')
    
    # 模拟游戏中的各种交互
    dm.show_message("欢迎", "欢迎来到JOJO Soul世界！")
    
    # 角色创建
    name = dm.get_input("角色创建", "请输入你的角色名称")
    if name:
        dm.show_message("角色信息", f"角色 {name} 创建成功！")
    
    # 商店选择
    items = ["经验药水 [80G, +100经验值]", "药水 [50G, 回满HP]", "剑 [100G, +5伤害]"]
    choice = dm.get_choice("商店", items)
    if choice:
        dm.show_message("购买成功", f"你购买了 {choice}")
    
    # 战斗选择
    elements = ["火焰", "水", "土地", "暗黑魔法", "闪光"]
    element = dm.get_choice("战斗", ["选择攻击元素"] + elements)
    if element:
        dm.show_message("战斗", f"你使用了 {element} 攻击！")
    
    # 确认对话框
    if dm.get_yes_no("确认", "是否保存游戏？"):
        dm.show_message("保存", "游戏已保存！")
    
    print("终端模式演示完成\n")

def demo_gui_experience():
    """演示纯GUI模式的完整体验"""
    print("=== GUI模式演示 ===")
    dm = DisplayManager(mode='gui')
    
    print("在GUI模式下，所有交互都通过图形界面进行：")
    print("- 消息通过弹窗显示")
    print("- 选择通过下拉菜单进行")
    print("- 输入通过输入框进行")
    print("- 确认通过按钮进行")
    print("用户无需查看终端，完全通过GUI操作\n")

def demo_both_experience():
    """演示混合模式的完整体验"""
    print("=== 混合模式演示 ===")
    dm = DisplayManager(mode='both')
    
    print("在混合模式下：")
    print("- 优先使用GUI界面")
    print("- 终端同步显示信息")
    print("- GUI失败时自动回退到终端")
    print("- 提供最佳的用户体验\n")

def main():
    print("=== JOJO Soul 独立显示模式演示 ===\n")
    
    demo_terminal_experience()
    demo_gui_experience() 
    demo_both_experience()
    
    print("=== 总结 ===")
    print("✅ 终端模式：完整的命令行体验，适合服务器环境")
    print("✅ GUI模式：完整的图形界面体验，适合桌面环境")
    print("✅ 混合模式：智能切换，提供最佳体验")
    print("\n用户可以根据环境和个人喜好选择合适的模式，")
    print("每种模式都能提供完整的游戏体验！")

if __name__ == "__main__":
    main()