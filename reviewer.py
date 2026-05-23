# reviewer.py
import json
import os

BIGRAM_STATE_FILE = "bigram_scores.json"

class Reviewer:
    def __init__(self, visual_summary, memory_system=None, learning_rate=0.1):
        self.visual_chars = set(visual_summary.upper())
        self.memory_system = memory_system
        self.learning_rate = learning_rate
        # 加载持久化的 bigram 分数
        self.bigram_scores = self._load_bigrams()

    def _load_bigrams(self):
        if os.path.exists(BIGRAM_STATE_FILE):
            try:
                with open(BIGRAM_STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_bigrams(self):
        with open(BIGRAM_STATE_FILE, 'w') as f:
            json.dump(self.bigram_scores, f)

    def score(self, raw_sentence, mood=None):
        base_score = len(set(raw_sentence).intersection(self.visual_chars))
        learned_bonus = self._evaluate_bigrams(raw_sentence.upper())
        memory_bonus = self._memory_match_score(raw_sentence)

        total = base_score + learned_bonus + memory_bonus

        if mood:
            energy = mood.get("energy", 0.5)
            curiosity = mood.get("curiosity", 0.5)
            pleasure = mood.get("pleasure", 0.5)
            if energy < 0.3:
                total -= 0.5
            if curiosity > 0.7:
                total += 0.3
            if pleasure > 0.7:
                total += 0.2
            elif pleasure < 0.3:
                total -= 0.3

        return max(0, total)

    def _memory_match_score(self, raw_sentence):
        if not self.memory_system:
            return 0

        bonus = 0
        sentence_upper = raw_sentence.upper()
        cursor = self.memory_system.conn.cursor()
        cursor.execute("SELECT feature FROM memories")
        rows = cursor.fetchall()

        for row in rows:
            feature = row[0].upper()
            # 修复 break 逻辑：每个 feature 最多匹配一次
            matched = False
            for i in range(len(feature) - 1):
                if matched:
                    break
                for j in range(i + 2, len(feature) + 1):
                    sub = feature[i:j]
                    if sub in sentence_upper:
                        bonus += 3
                        matched = True
                        break  # 跳出内层 j 循环
                # matched 后外层循环会自动 break（通过上面的 if matched）
            # 继续下一个 feature
        return bonus

    def _bigrams(self, text):
        return [(text[i], text[i+1]) for i in range(len(text)-1)]

    def _evaluate_bigrams(self, text):
        pairs = self._bigrams(text)
        if not pairs:
            return 0
        total = 0
        count = 0
        for p in pairs:
            if p in self.bigram_scores:
                total += self.bigram_scores[p]
                count += 1
        if count == 0:
            return 0
        return total / count

    def update_from_feedback(self, sentence, score):
        pairs = self._bigrams(sentence.upper())
        for p in pairs:
            if p not in self.bigram_scores:
                self.bigram_scores[p] = 0
            self.bigram_scores[p] = (1 - self.learning_rate) * self.bigram_scores[p] + self.learning_rate * score
        # 每次更新后持久化
        self._save_bigrams()