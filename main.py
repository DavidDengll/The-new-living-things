# main.py
from memory import MemorySystem
from vision import VisualModel
from thinker import Thinker
from reviewer import Reviewer
from language_model import LanguageModel
from emotion import Emotion
from randomness import true_random_byte
from config import (
    SPEAK_THRESHOLD, MIN_MEANING_SCORE, MAX_RETRIES, CURIOSITY_THRESHOLD,
    VISION_MODE, SCENE_DESCRIPTION, IMAGE_PATH,
    REJECTION_BONUS_MAX, REJECTION_BONUS_PER_STREAK, USE_CLOUD_CLASSIFIER
)
import random

if USE_CLOUD_CLASSIFIER:
    from classifier import Classifier

class ConsciousnessSystem:
    def __init__(self, vision_mode=None, scene_description=None, image_path=None,
                 speak_threshold=None, min_meaning_score=None, max_retries=None,
                 curiosity_threshold=None):
        print(f"⚙️ 初始化视觉感知器 (模式: {vision_mode or VISION_MODE})...")

        self.memory = MemorySystem()
        self._seed_initial_memories()

        self.classifier = None
        if USE_CLOUD_CLASSIFIER:
            self.classifier = Classifier(memory_system=self.memory)

        self.visual = VisualModel(
            mode=vision_mode if vision_mode is not None else VISION_MODE,
            description=scene_description if scene_description is not None else SCENE_DESCRIPTION,
            image_path=image_path if image_path is not None else IMAGE_PATH,
            classifier=self.classifier
        )

        self.thinker = Thinker(self.memory)
        self.language_model = LanguageModel()
        self.emotion = Emotion()

        self.base_threshold = speak_threshold if speak_threshold is not None else SPEAK_THRESHOLD
        self.current_threshold = self.base_threshold
        self.score_history = []
        self.history_size = 5

        self.min_meaning_score = min_meaning_score if min_meaning_score is not None else MIN_MEANING_SCORE
        self.max_retries = max_retries if max_retries is not None else MAX_RETRIES

        self.unknown_streak = 0
        self.curiosity_threshold = curiosity_threshold if curiosity_threshold is not None else CURIOSITY_THRESHOLD
        self.last_unknown_keyword = None

        self.rejection_streak = 0

        # 审查缓存
        self.review_cache = {}

    def _seed_initial_memories(self):
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
        if final_score == 0:
            return
        if final_score < 0:
            self.current_threshold = min(0.9, self.current_threshold + 0.05)
            print(f"📈 动态阈值（惩罚）: {self.current_threshold:.2f}")
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

    def _get_cached_review(self, scene, sentence):
        import hashlib
        scene_key = hashlib.md5(scene.encode()).hexdigest()[:8]
        if scene_key in self.review_cache:
            if sentence in self.review_cache[scene_key]:
                cached = self.review_cache[scene_key][sentence]
                print(f"📦 使用缓存审查结果: {cached[0]}/10")
                return cached
        return None

    def _set_cached_review(self, scene, sentence, score, explanation, concept):
        import hashlib
        scene_key = hashlib.md5(scene.encode()).hexdigest()[:8]
        if scene_key not in self.review_cache:
            self.review_cache[scene_key] = {}
            if len(self.review_cache) > 5:
                oldest_key = list(self.review_cache.keys())[0]
                del self.review_cache[oldest_key]
        self.review_cache[scene_key][sentence] = (score, explanation, concept)

    def run_once(self):
        self.emotion.update()
        mood = self.emotion.get_state()

        scene = self.visual.see()
        print(f"👁️ 看到: {scene}")

        keywords = self.visual.extract_keywords(scene)
        main_subject = self.visual.get_main_subject(scene)
        print(f"🔑 关键词: {keywords} | 主要对象: {main_subject}")

        primary_keyword = main_subject if main_subject and main_subject != "未知" else (keywords[0] if keywords else "未知")

        outer_response = self.language_model.generate_response(scene, mood)

        result = self.thinker.think(primary_keyword, scene, hint=None)
        print(f"🧠 记忆查询: {result['memory_info']}")

        is_unknown = "不认识" in result['memory_info']
        if is_unknown:
            self.unknown_streak += 1
            self.last_unknown_keyword = primary_keyword
            self.emotion.update("unknown_streak")
        else:
            self.unknown_streak = 0
            self.emotion.update("learn_new")

        rejection_bonus = min(REJECTION_BONUS_MAX, self.rejection_streak * REJECTION_BONUS_PER_STREAK)

        if not self.should_speak(mood, rejection_bonus):
            print("🤫 沉默")
            self.emotion.update("silence")
            inner_murmur = self.thinker.generate_raw_thought(length=random.randint(3, 7))

            cached = self._get_cached_review(scene, inner_murmur)
            if cached:
                murmur_score, murmur_reason, _ = cached
            else:
                reviewer = Reviewer(scene, memory_system=self.memory)
                murmur_score, murmur_reason, _ = reviewer.judge(inner_murmur, rejection_streak=self.rejection_streak)
                self._set_cached_review(scene, inner_murmur, murmur_score, murmur_reason, "")

            if murmur_score >= self.min_meaning_score:
                final_output = f"（内心一闪：{inner_murmur}）"
                final_inner_score = murmur_score
                print(f"💭 内心闪过有意义: {inner_murmur} (得分 {murmur_score}/10)")
                self._update_threshold(final_inner_score)
                self.rejection_streak = 0
            else:
                final_output = "（…）"
                final_inner_score = -1
                self.rejection_streak += 1
                self._update_threshold(final_inner_score)
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
                current_result = self.thinker.think(primary_keyword, scene, hint=hint)

                judge_results = []
                uncached_sentences = []
                for s in current_result['raw_sentences']:
                    cached = self._get_cached_review(scene, s)
                    if cached:
                        judge_results.append((s, cached[0], cached[1], cached[2]))
                    else:
                        uncached_sentences.append(s)

                if uncached_sentences:
                    new_results = reviewer.judge_batch(
                        uncached_sentences,
                        rejection_streak=self.rejection_streak
                    )
                    for s, score, explanation, concept in new_results:
                        self._set_cached_review(scene, s, score, explanation, concept)
                        judge_results.append((s, score, explanation, concept))

                best_in_batch = None
                best_in_batch_score = -1
                best_in_batch_concept = ""
                for s, score, explanation, concept in judge_results:
                    if score > best_in_batch_score:
                        best_in_batch_score = score
                        best_in_batch = s
                        best_in_batch_concept = concept

                current_best = best_in_batch
                current_score = best_in_batch_score
                current_concept = best_in_batch_concept

                print(f"  🔄 {attempt}: {current_result['raw_sentences']} 最高分 {current_score}")

                if current_score > best_score:
                    best_score = current_score
                    best_sentence = current_best
                    best_concept = current_concept
                    if best_concept and best_concept.strip():
                        hint = best_concept.strip()
                    else:
                        hint = None

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
    system = ConsciousnessSystem()
    print("=== 熵灵双层心智系统启动 ===\n")
    print("💡 提示：每轮请输入场景描述，输入 Ctrl+C 退出程序。\n")
    try:
        for i in range(50):
            print(f"🔂 第 {i+1} 轮:")
            system.run_once()
    except KeyboardInterrupt:
        print("\n👋 程序被中断，正在保存状态...")
    finally:
        system.close()