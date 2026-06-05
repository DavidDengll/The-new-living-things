# test_virtual.py
import sys
import os
import time
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from virtual_env import VirtualEnvironment
from main import ConsciousnessSystem
from config import *

class VirtualTestRunner:
    def __init__(self, grid_size=5, max_rounds=100, sleep_sec=0.2, use_local_response=False):
        self.env = VirtualEnvironment(size=grid_size)
        self.system = ConsciousnessSystem()
        # 替换视觉方法
        self.system.visual.see = self.env.see
        self.system.visual.mode = "virtual"
        self.max_rounds = max_rounds
        self.sleep_sec = sleep_sec
        self.round = 0

        # 可选：省掉语言模型的调用，用本地模板（大幅降成本）
        if use_local_response:
            from language_model import LanguageModel
            class MockLanguageModel(LanguageModel):
                def generate_response(self, visual_summary, mood=None):
                    return "[本地] 我看到了一些东西。"
            self.system.language_model = MockLanguageModel()

    def run(self):
        print("=" * 60)
        print("🧠 熵灵虚拟环境自动测试启动")
        print(f"   网格大小: {self.env.size}×{self.env.size}")
        print(f"   最大轮数: {self.max_rounds}")
        print(f"   初始位置: {self.env.agent_pos}")
        print(f"   休眠间隔: {self.sleep_sec}s")
        print("=" * 60)

        while self.round < self.max_rounds:
            self.round += 1
            print(f"\n🔂 第 {self.round} 轮")
            print("-" * 40)

            self.system.run_once()
            state = self.env.get_state()
            agent = state["agent"]
            items = state["items"]
            last_output = getattr(self.system, "last_final_output", "")

            self._print_grid(agent, items)

            if last_output:
                print(f"💬 熵灵: {last_output[:200]}")

            emo = self.system.emotion.get_state()
            print(f"📊 精力:{emo['energy']:.2f} 好奇:{emo['curiosity']:.2f} 愉悦:{emo['pleasure']:.2f}")

            history = state.get("history", [])
            if history:
                print(f"📋 最近动作:")
                for h in history[-3:]:
                    print(f"   {h}")

            # 显示背包
            inv = self.env.get_inventory()
            if inv:
                print(f"🎒 背包: {', '.join(inv)}")

            time.sleep(self.sleep_sec)

        print("\n" + "=" * 60)
        print("✅ 测试完成")
        print(f"   总轮数: {self.round}")
        print(f"   最终位置: {self.env.agent_pos}")
        print(f"   剩余物品: {len(self.env.items)}")
        print(f"   背包物品: {self.env.get_inventory()}")
        print("=" * 60)
        self.system.close()

    def _print_grid(self, agent, items):
        size = self.env.size
        item_map = {}
        for item in items:
            # 显示物品名的前两个字符，避免首字歧义
            name_display = item["name"][:2] if len(item["name"]) >= 2 else item["name"] + " "
            item_map[(item["x"], item["y"])] = name_display

        print(f"┌{'───' * size}┐")
        for y in range(size):
            row = "│"
            for x in range(size):
                if [x, y] == [agent["x"], agent["y"]]:
                    row += "🤖 "
                elif (x, y) in item_map:
                    row += f"{item_map[(x, y)]} "
                else:
                    row += "·  "
            row += "│"
            print(row)
        print(f"└{'───' * size}┘")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=50, help="测试轮数")
    parser.add_argument("--interval", type=float, default=0.2, help="每轮休眠秒数")
    parser.add_argument("--local", action="store_true", help="使用本地回复（省API）")
    args = parser.parse_args()

    runner = VirtualTestRunner(max_rounds=args.rounds, sleep_sec=args.interval, use_local_response=args.local)
    try:
        runner.run()
    except KeyboardInterrupt:
        print("\n👋 手动中断")
    finally:
        runner.system.close()