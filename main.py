# main.py
from memory import MemorySystem
from vision import VisualModel
from thinker import Thinker
from reviewer import Reviewer
from language_model import LanguageModel
from randomness import true_random_byte

class ConsciousnessSystem:
    def __init__(self, vision_mode="simulate", scene_description=None, image_path=None,
                 speak_threshold=0.6, min_meaning_score=1, max_retries=5,
                 curiosity_threshold=3):
        print(f"⚙️ 初始化视觉感知器 (模式: {vision_mode})...")
        self.visual = VisualModel(mode=vision_mode,
                                  description=scene_description,
                                  image_path=image_path)
        self.memory = MemorySystem()
        self.memory.add_permanent("猫", "毛茸茸、会喵喵叫、有四条腿")
        self.memory.add_permanent("太阳", "发光的恒星，带来温暖和光明")

        self.thinker = Thinker(self.memory, memory_influence_prob=0.4)
        self.language_model = LanguageModel()

        self.base_threshold = speak_threshold
        self.current_threshold = speak_threshold
        self.score_history = []
        self.history_size = 5

        self.min_meaning_score = min_meaning_score
        self.max_retries = max_retries

        self.unknown_streak = 0
        self.curiosity_threshold = curiosity_threshold
        self.last_unknown_keyword = None

    def _update_threshold(self, final_score):
        self.score_history.append(final_score)
        if len(self.score_history) > self.history_size:
            self.score_history.pop(0)
        if len(self.score_history) >= 3:
            avg = sum(self.score_history) / len(self.score_history)
            if avg > 2.0:
                self.current_threshold = max(0.2, self.base_threshold - 0.15)
            elif avg < 1.0:
                self.current_threshold = min(0.9, self.base_threshold + 0.15)
            else:
                self.current_threshold = self.base_threshold
            print(f"📈 近{len(self.score_history)}轮平均分: {avg:.2f}, 动态阈值调整为: {self.current_threshold:.2f}")

    def should_speak(self):
        raw = true_random_byte()
        return (raw / 255.0) > self.current_threshold

    def run_once(self):
        scene = self.visual.see()
        print(f"👁️ 原始描述: {scene}")
        keyword = self.visual.extract_keywords(scene)

        outer_response = self.language_model.generate_response(scene)

        result = self.thinker.think(keyword, scene)
        print(f"🧠 关键词: {keyword} | 记忆查询: {result['memory_info']}")

        is_unknown = "不认识" in result['memory_info']
        if is_unknown:
            self.unknown_streak += 1
            self.last_unknown_keyword = keyword
            print(f"❓ 连续未知计数: {self.unknown_streak}")
        else:
            self.unknown_streak = 0

        if not self.should_speak():
            print("🤫 熵灵选择沉默，不附加任何话。")
            final_output = outer_response
            final_inner_score = 0
        else:
            print("🗣️ 熵灵决定发言，进入审查循环...")
            reviewer = Reviewer(scene)
            best_sentence = None
            best_score = -1

            for attempt in range(1, self.max_retries + 1):
                scored = [(s, reviewer.score(s)) for s in result['raw_sentences']]
                current_best, current_score = max(scored, key=lambda x: x[1])

                print(f"  🔄 第{attempt}次生成: {result['raw_sentences']}")
                print(f"  🔍 最高分: {current_score} (来自 '{current_best}')")

                if current_score > best_score:
                    best_score = current_score
                    best_sentence = current_best

                if best_score >= self.min_meaning_score:
                    print(f"  ✅ 达到意义阈值，采用。")
                    break
                else:
                    if attempt < self.max_retries:
                        print("  ⚠️ 未达阈值，重新思考...")
                        result = self.thinker.think(keyword, scene)
                    else:
                        print(f"  ❌ 已达最大重试次数，采用当前最佳。")

            reviewer.update_from_feedback(best_sentence, best_score)

            append_text = f" {best_sentence}"
            final_output = outer_response + append_text
            final_inner_score = best_score
            print(f"💬 熵灵插入话语: {best_sentence} (得分 {best_score})")

        self._update_threshold(final_inner_score)

        if self.unknown_streak >= self.curiosity_threshold:
            question = self.language_model.generate_question(self.last_unknown_keyword)
            final_output = f"[好奇心]: {question} -- {final_output}"
            self.unknown_streak = 0
            print(f"💡 主动提问: {question}")

        print(f"✅ 最终回复: {final_output}")
        print("-" * 50)

if __name__ == "__main__":
    system = ConsciousnessSystem(
        vision_mode="simulate",
        scene_description="一只橘猫趴在窗台上，阳光照在它身上",
        speak_threshold=0.6,
        min_meaning_score=1,
        max_retries=5,
        curiosity_threshold=3
    )
    print("=== 熵灵双层心智系统启动（全优化版）===\n")
    for i in range(12):
        print(f"🔂 第 {i+1} 轮:")
        system.run_once()