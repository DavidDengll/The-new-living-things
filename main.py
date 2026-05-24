# main.py
from memory import MemorySystem
from vision import VisualModel
from thinker import Thinker
from reviewer import Reviewer
from language_model import LanguageModel
from emotion import Emotion
from randomness import true_random_byte
import datetime
import random

class ConsciousnessSystem:
    def __init__(self, vision_mode="simulate", scene_description=None, image_path=None,
                 speak_threshold=0.6, min_meaning_score=4, max_retries=5,
                 curiosity_threshold=3):
        print(f"⚙️ 初始化视觉感知器...")
        self.visual = VisualModel(mode=vision_mode,
                                  description=scene_description,
                                  image_path=image_path)
        self.memory = MemorySystem()
        self._seed_initial_memories()

        self.thinker = Thinker(self.memory, memory_influence_prob=0.4)
        self.language_model = LanguageModel()
        self.emotion = Emotion()

        self.base_threshold = speak_threshold
        self.current_threshold = speak_threshold
        self.score_history = []
        self.history_size = 5

        self.min_meaning_score = min_meaning_score
        self.max_retries = max_retries

        self.unknown_streak = 0
        self.curiosity_threshold = curiosity_threshold
        self.last_unknown_keyword = None

        self.rejection_streak = 0

    def _seed_initial_memories(self):
        """
        只在记忆库为空时植入先天永久记忆。
        使用 name=概念名, feature=特征描述 的统一格式。
        与 memory.search(name) 和 reviewer.judge 返回的 related_concept 保持一致。
        """
        import sqlite3
        conn = sqlite3.connect("entropy_memory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        if count == 0:
            self.memory.add_permanent("猫", "毛茸茸、会喵喵叫、有四条腿")
            self.memory.add_permanent("太阳", "发光的恒星，带来温暖和光明")
        conn.close()

    def _update_threshold(self, final_score):
        if final_score <= 0:
            return
        self.score_history.append(final_score)
        if len(self.score_history) > self.history_size:
            self.score_history.pop(0)
        if len(self.score_history) >= 3:
            avg = sum(self.score_history) / len(self.score_history)
            if avg > 7.0:
                self.current_threshold = max(0.2, self.base_threshold - 0.15)
            elif avg < 3.0:
                self.current_threshold = min(0.9, self.base_threshold + 0.15)
            else:
                self.current_threshold = self.base_threshold
            print(f"📈 动态阈值: {self.current_threshold:.2f}")

    def should_speak(self, mood, rejection_bonus=0.0):
        curiosity = mood.get("curiosity", 0.5)
        energy = mood.get("energy", 0.5)
        adjusted = self.current_threshold - (curiosity - 0.5) * 0.4 + (0.5 - energy) * 0.3 - rejection_bonus
        adjusted = max(0.05, min(0.95, adjusted))
        raw = true_random_byte()
        return (raw / 255.0) > adjusted

    def run_once(self):
        self.emotion.update()
        mood = self.emotion.get_state()

        scene = self.visual.see()
        print(f"👁️ 看到: {scene}")
        keyword = self.visual.extract_keywords(scene)

        outer_response = self.language_model.generate_response(scene, mood)

        # ✅ 初始 think 不传 hint（第一轮没有审核官反馈）
        result = self.thinker.think(keyword, scene, hint=None)
        print(f"🧠 记忆查询: {result['memory_info']}")

        is_unknown = "不认识" in result['memory_info']
        if is_unknown:
            self.unknown_streak += 1
            self.last_unknown_keyword = keyword
            self.emotion.update("unknown_streak")
        else:
            self.unknown_streak = 0
            self.emotion.update("learn_new")

        rejection_bonus = min(0.3, self.rejection_streak * 0.1)

        if not self.should_speak(mood, rejection_bonus):
            print("🤫 沉默")
            self.emotion.update("silence")

            inner_murmur = self.thinker.generate_raw_thought(length=random.randint(3, 7))
            reviewer = Reviewer(scene, memory_system=self.memory)
            murmur_score, murmur_reason, _ = reviewer.judge(inner_murmur)

            if murmur_score >= self.min_meaning_score:
                final_output = f"{outer_response}（内心一闪：{inner_murmur}）"
                final_inner_score = murmur_score
                print(f"💭 内心闪过有意义: {inner_murmur} (得分 {murmur_score}/10)")
                self._update_threshold(final_inner_score)
                self.rejection_streak = 0
            else:
                final_output = f"{outer_response}（…）"
                final_inner_score = 0
                self.rejection_streak += 1
                curiosity_boost = (10 - murmur_score) / 20
                self.emotion.curiosity = min(1.0, self.emotion.curiosity + curiosity_boost)
                print(f"💭 内心闪过无意义: {inner_murmur} ({murmur_reason}) | 反驳冲动+1 | 好奇+{curiosity_boost:.2f}")
        else:
            print("🗣️ 发言")
            self.emotion.update("speak")
            reviewer = Reviewer(scene, memory_system=self.memory)
            best_sentence = None
            best_score = -1
            best_concept = ""
            hint = None

            for attempt in range(1, self.max_retries + 1):
                # ✅ 用审核官返回的 related_concept 作为 hint 传给下一轮 think
                current_result = self.thinker.think(keyword, scene, hint=hint)
                scored = []
                for s in current_result['raw_sentences']:
                    semantic_score, _, related_concept = reviewer.judge(s)
                    scored.append((s, semantic_score, related_concept))
                current_best, current_score, current_concept = max(scored, key=lambda x: x[1])
                print(f"  🔄 {attempt}: {current_result['raw_sentences']} 最高分 {current_score}")

                if current_score > best_score:
                    best_score = current_score
                    best_sentence = current_best
                    best_concept = current_concept
                    # ✅ 优先用审核官返回的最相关记忆概念，其次用最佳句子尾部
                    if best_concept and best_concept.strip():
                        hint = best_concept.strip()
                    elif len(best_sentence) >= 2:
                        hint = best_sentence[-2:]
                    else:
                        hint = best_sentence

                if best_score >= self.min_meaning_score:
                    print(f"  ✅ 达到意义阈值，停止重试")
                    break
                else:
                    if attempt < self.max_retries:
                        print("  ⚠️ 分数过低，尝试基于 hint 重新生成...")
                    else:
                        print(f"  ❌ 已达最大重试次数，采用当前最佳。")

            append_text = f" {best_sentence}"
            final_output = outer_response + append_text
            final_inner_score = best_score
            print(f"💬 插入: {best_sentence}")
            self._update_threshold(final_inner_score)
            self.rejection_streak = 0

        if self.unknown_streak >= self.curiosity_threshold:
            question = self.language_model.generate_question(self.last_unknown_keyword)
            final_output = f"[好奇心] {question} -- {final_output}"
            self.unknown_streak = 0
            self.emotion.update("question_asked")

        print(f"✅ 最终回复: {final_output}")
        print(f"📊 情绪状态: {mood} | 反驳冲动: {self.rejection_streak}")
        print("-" * 50)

    def close(self):
        self.memory.close()
        self.emotion.save_state()

if __name__ == "__main__":
    system = ConsciousnessSystem(
        vision_mode="simulate",
        scene_description="一只橘猫趴在窗台上，阳光照在它身上",
        speak_threshold=0.6,
        min_meaning_score=4,
        max_retries=5,
        curiosity_threshold=3
    )
    print("=== 熵灵双层心智系统启动 ===\n")
    try:
        for i in range(12):
            print(f"🔂 第 {i+1} 轮:")
            system.run_once()
    finally:
        system.close()