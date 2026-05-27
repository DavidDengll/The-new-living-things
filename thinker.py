# thinker.py
from randomness import true_random_int, true_random_byte, true_random_bool
from config import MEMORY_INFLUENCE_PROB, WORD_INSERT_PROB, MOSAIC_PROB, HINT_USE_PROB

class Thinker:
    def __init__(self, memory_system, memory_influence_prob=None, word_insert_prob=None):
        self.memory = memory_system
        self.memory_influence_prob = memory_influence_prob if memory_influence_prob is not None else MEMORY_INFLUENCE_PROB
        self.word_insert_prob = word_insert_prob if word_insert_prob is not None else WORD_INSERT_PROB

    def _mosaic_generate(self, length):
        fragments = []
        for _ in range(3):
            frag = self.memory.get_random_fragment(min_len=1, max_len=3)
            if frag:
                fragments.append(frag)
        if not fragments:
            return None
        import random
        random.shuffle(fragments)
        mosaic = "".join(fragments)
        if len(mosaic) >= length:
            return mosaic[:length]
        else:
            padding = "".join(chr(65 + (true_random_byte() % 26)) for _ in range(length - len(mosaic)))
            return mosaic + padding

    def think(self, keyword, visual_summary, hint=None):
        found = self.memory.search(keyword, new_feature=visual_summary)
        if found:
            memory_info = f'记得"{keyword}"：{found}'
        else:
            memory_info = f'不认识"{keyword}"，这是什么？'
            self.memory.add_short(name=keyword, feature=visual_summary)

        num_sentences = true_random_int(1, 2)
        sentence_lengths = [true_random_int(3, 8) for _ in range(num_sentences)]

        raw_sentences = []
        for length in sentence_lengths:
            if hint and true_random_bool(HINT_USE_PROB):
                if len(hint) >= length:
                    raw_sentences.append(hint[:length])
                else:
                    padded = hint + "".join(chr(65 + (true_random_byte() % 26)) for _ in range(length - len(hint)))
                    raw_sentences.append(padded)
                continue

            if true_random_bool(MOSAIC_PROB):
                mosaic = self._mosaic_generate(length)
                if mosaic:
                    raw_sentences.append(mosaic)
                    continue

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
        if true_random_bool(MOSAIC_PROB):
            mosaic = self._mosaic_generate(length)
            if mosaic:
                return mosaic
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