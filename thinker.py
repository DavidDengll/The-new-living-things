# thinker.py
from randomness import true_random_int, true_random_byte, true_random_bool

class Thinker:
    def __init__(self, memory_system, memory_influence_prob=0.4, word_insert_prob=0.3):
        self.memory = memory_system
        self.memory_influence_prob = memory_influence_prob
        self.word_insert_prob = word_insert_prob

    def think(self, keyword, visual_summary, hint=None):
        found = self.memory.search(keyword, new_feature=visual_summary)
        if found:
            memory_info = f'记得"{keyword}"：{found}'
        else:
            memory_info = f'不认识"{keyword}"，这是什么？'
            self.memory.add_short(name=keyword, feature=visual_summary)

        num_sentences = true_random_int(1, 3)
        sentence_lengths = [true_random_int(3, 8) for _ in range(num_sentences)]

        raw_sentences = []
        for length in sentence_lengths:
            # 如果有 hint（上次最佳句子的尾部），优先使用它作为生成基础
            if hint and true_random_bool(0.7):  # 70% 概率直接使用 hint 片段
                # 取 hint 的前 length 个字符（如果不足则补随机字符）
                if len(hint) >= length:
                    raw_sentences.append(hint[:length])
                else:
                    padded = hint + "".join(chr(65 + (true_random_byte() % 26)) for _ in range(length - len(hint)))
                    raw_sentences.append(padded)
                continue

            # 原有的整词插入或逐字符生成逻辑
            if true_random_bool(self.word_insert_prob):
                fragment = self.memory.get_random_fragment(min_len=2, max_len=6)
                if fragment and len(fragment) >= 2:
                    raw_sentences.append(fragment)
                    continue

            chars = []
            for _ in range(length):
                if true_random_bool(self.memory_influence_prob):
                    fragment = self.memory.get_random_fragment(min_len=1, max_len=1)
                    if fragment:
                        chars.append(fragment[0])
                        continue
                char_code = 65 + (true_random_byte() % 26)
                chars.append(chr(char_code))
            raw_sentences.append("".join(chars))

        return {
            "keyword": keyword,
            "memory_info": memory_info,
            "raw_sentences": raw_sentences,
        }

    def generate_raw_thought(self, length=5):
        chars = []
        for _ in range(length):
            if true_random_bool(self.memory_influence_prob):
                fragment = self.memory.get_random_fragment(min_len=1, max_len=1)
                if fragment:
                    chars.append(fragment[0])
                    continue
            char_code = 65 + (true_random_byte() % 26)
            chars.append(chr(char_code))
        return "".join(chars)