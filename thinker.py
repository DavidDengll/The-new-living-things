# thinker.py
from randomness import true_random_int, true_random_byte, true_random_bool

class Thinker:
    def __init__(self, memory_system, memory_influence_prob=0.4, word_insert_prob=0.3):
        self.memory = memory_system
        self.memory_influence_prob = memory_influence_prob
        self.word_insert_prob = word_insert_prob

    def _mosaic_generate(self, length):
        """
        词素拼图：从记忆碎片中随机拼接新词。
        不是复制粘贴，也不是纯随机字母。
        """
        fragments = []
        for _ in range(3):  # 取 2~3 个碎片
            frag = self.memory.get_random_fragment(min_len=1, max_len=3)
            if frag:
                fragments.append(frag)

        if not fragments:
            return None  # 记忆库空了，退回兜底

        # 随机排列碎片并拼接
        import random
        random.shuffle(fragments)
        mosaic = "".join(fragments)

        # 截取到目标长度
        if len(mosaic) >= length:
            return mosaic[:length]
        else:
            # 不够长就补随机字母（但主体是记忆碎片）
            padding = "".join(chr(65 + (true_random_byte() % 26)) for _ in range(length - len(mosaic)))
            return mosaic + padding

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
            # 1. 有 hint 时优先用 hint
            if hint and true_random_bool(0.7):
                if len(hint) >= length:
                    raw_sentences.append(hint[:length])
                else:
                    padded = hint + "".join(chr(65 + (true_random_byte() % 26)) for _ in range(length - len(hint)))
                    raw_sentences.append(padded)
                continue

            # 2. 词素拼图：基于记忆碎片拼出新词
            if true_random_bool(0.5):
                mosaic = self._mosaic_generate(length)
                if mosaic:
                    raw_sentences.append(mosaic)
                    continue

            # 3. 整词插入（保留）
            if true_random_bool(self.word_insert_prob):
                fragment = self.memory.get_random_fragment(min_len=2, max_len=6)
                if fragment and len(fragment) >= 2:
                    raw_sentences.append(fragment)
                    continue

            # 4. 兜底：逐字符生成（chr(65+random) 只在记忆完全为空时才到这里）
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
        # 优先词素拼图
        if true_random_bool(0.5):
            mosaic = self._mosaic_generate(length)
            if mosaic:
                return mosaic

        # 兜底
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