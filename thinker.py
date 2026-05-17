# thinker.py
from randomness import true_random_int, true_random_byte, true_random_bool

class Thinker:
    def __init__(self, memory_system, memory_influence_prob=0.4):
        self.memory = memory_system
        self.memory_influence_prob = memory_influence_prob

    def think(self, keyword, visual_summary):
        found = self.memory.search(keyword, new_feature=visual_summary)
        if found:
            memory_info = f"记得“{keyword}”：{found}"
        else:
            memory_info = f"不认识“{keyword}”，这是什么？"
            self.memory.add_short(name=keyword, feature=visual_summary)

        num_sentences = true_random_int(1, 3)
        sentence_lengths = [true_random_int(3, 8) for _ in range(num_sentences)]

        raw_sentences = []
        for length in sentence_lengths:
            chars = []
            for _ in range(length):
                if true_random_bool(self.memory_influence_prob):
                    fragment = self.memory.get_random_fragment()
                    if fragment:
                        chars.append(fragment[0] if fragment else chr(65 + (true_random_byte() % 26)))
                        continue
                char_code = 65 + (true_random_byte() % 26)
                chars.append(chr(char_code))
            raw_sentences.append("".join(chars))

        return {
            "keyword": keyword,
            "memory_info": memory_info,
            "raw_sentences": raw_sentences,
        }