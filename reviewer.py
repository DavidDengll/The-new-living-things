# reviewer.py
class Reviewer:
    def __init__(self, visual_summary, learning_rate=0.1):
        self.visual_chars = set(visual_summary.upper())
        self.bigram_scores = {}
        self.learning_rate = learning_rate

    def score(self, raw_sentence):
        base_score = len(set(raw_sentence).intersection(self.visual_chars))
        learned_bonus = self._evaluate_bigrams(raw_sentence.upper())
        return base_score + learned_bonus

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