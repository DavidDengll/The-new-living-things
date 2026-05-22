# main.py
from memory import MemorySystem
from vision import VisualModel
from thinker import Thinker
from reviewer import Reviewer
from language_model import LanguageModel
from emotion import Emotion
from randomness import true_random_byte
import datetime

class ConsciousnessSystem:
    def __init__(self, vision_mode="simulate", scene_description=None, image_path=None,
                 speak_threshold=0.6, min_meaning_score=1, max_retries=5,
                 curiosity_threshold=3):
        print(f"⚙️ 初始化视觉感知器...")
        self.visual = VisualModel(mode=vision_mode,
                                  description=scene_description,
                                  image_path=image_path)
        # 记忆系统（SQLite 持久化）
        self.memory = MemorySystem()
        # 植入初始永久记忆（只在首次运行时生效，后续不会重复添加，需检查已存在）
        self._seed_initial_memories()

        self.thinker = Thinker(self.memory, memory_influence_prob=0.4)
        self.language_model = LanguageModel()
        self.emotion = Emotion()

        # 动态阈值
        self.base_threshold = speak_threshold
        self.current_threshold = speak_threshold
        self.score_history = []
        self.history_size = 5

        self.min_meaning_score = min_meaning_score
        self.max_retries = max_retries

        self.unknown_streak = 0
        self.curiosity_threshold = curiosity_threshold
        self.last_unknown_keyword = None

    def _seed_initial_memories(self):
        """只在记忆库为空时植入先天永久记忆"""
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
            print(f"📈 动态阈值: {self.current_threshold:.2f}")

    def should_speak(self):
        raw = true_random_byte()
        return (raw / 255.0) > self.current_threshold

    def run_once(self):
        # 更新情绪（自然衰减）
        self.emotion.update()
        mood = self.emotion.get_state()

        # 1. 视觉感知
        scene = self.visual.see()
        print(f"👁️ 看到: {scene}")
        keyword = self.visual.extract_keywords(scene)

        # 2. 大模型生成回答（兜底已内嵌）
        outer_response = self.language_model.generate_response(scene, mood)

        # 3. 思考者生成
        result = self.thinker.think(keyword, scene)
        print(f"🧠 记忆查询: {result['memory_info']}")

        is_unknown = "不认识" in result['memory_info']
        if is_unknown:
            self.unknown_streak += 1
            self.last_unknown_keyword = keyword
            self.emotion.update("unknown_streak")
        else:
            self.unknown_streak = 0
            self.emotion.update("learn_new")

        # 4. 发言决策
        if not self.should_speak():
            print("🤫 沉默")
            self.emotion.update("silence")
            final_output = outer_response
            final_inner_score = 0
        else:
            print("🗣️ 发言")
            self.emotion.update("speak")
            reviewer = Reviewer(scene)
            best_sentence = None
            best_score = -1

            for attempt in range(1, self.max_retries + 1):
                scored = [(s, reviewer.score(s, mood)) for s in result['raw_sentences']]
                current_best, current_score = max(scored, key=lambda x: x[1])
                print(f"  🔄 {attempt}: {result['raw_sentences']} 最高分 {current_score}")
                if current_score > best_score:
                    best_score = current_score
                    best_sentence = current_best
                if best_score >= self.min_meaning_score:
                    break
                else:
                    if attempt < self.max_retries:
                        result = self.thinker.think(keyword, scene)

            reviewer.update_from_feedback(best_sentence, best_score)
            append_text = f" {best_sentence}"
            final_output = outer_response + append_text
            final_inner_score = best_score
            print(f"💬 插入: {best_sentence}")

        # 动态阈值更新
        self._update_threshold(final_inner_score)

        # 好奇心提问
        if self.unknown_streak >= self.curiosity_threshold:
            question = self.language_model.generate_question(self.last_unknown_keyword)
            final_output = f"[好奇心] {question} -- {final_output}"
            self.unknown_streak = 0
            self.emotion.update("question_asked")

        print(f"✅ 最终回复: {final_output}")
        print(f"📊 情绪状态: {mood}")
        print("-" * 50)

    def close(self):
        self.memory.close()
        self.emotion.save_state()

if __name__ == "__main__":
    system = ConsciousnessSystem(
        vision_mode="simulate",
        scene_description="一只橘猫趴在窗台上，阳光照在它身上",
        speak_threshold=0.6,
        min_meaning_score=1,
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