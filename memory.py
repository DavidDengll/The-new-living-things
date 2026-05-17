# memory.py
import datetime
import random

class MemorySystem:
    def __init__(self):
        self.store = []

    @staticmethod
    def _today():
        return datetime.date.today()

    @staticmethod
    def _same_day(d1, d2):
        return d1 == d2

    @staticmethod
    def _same_year(d1, d2):
        return d1.year == d2.year

    def _cleanup(self):
        today = self._today()
        kept = []
        for mem in self.store:
            level = mem["level"]
            created = mem["created"]
            if level == "permanent":
                kept.append(mem)
            elif level == "long":
                if self._same_year(created, today):
                    kept.append(mem)
                else:
                    print(f"🧹 长期记忆过期删除: {mem['name']}")
            elif level == "short":
                if self._same_day(created, today):
                    kept.append(mem)
                else:
                    print(f"🧹 短期记忆过期删除: {mem['name']}")
        self.store = kept

    def search(self, keyword, new_feature=None):
        self._cleanup()
        today = self._today()
        for mem in self.store:
            if mem["name"] == keyword:
                last_date = mem.get("last_mentioned_date")
                if last_date and self._same_day(last_date, today):
                    mem["mentioned_count"] += 1
                else:
                    mem["mentioned_count"] = 1
                mem["last_mentioned_date"] = today
                self._try_upgrade(mem)
                if new_feature:
                    self._update_feature(mem, new_feature)
                return mem["feature"]
        return None

    def _try_upgrade(self, mem):
        if mem["level"] == "short" and mem["mentioned_count"] >= 5:
            mem["level"] = "long"
            mem["mentioned_count"] = 0
            print(f"⬆️ 升级：短期 → 长期: {mem['name']}")
        elif mem["level"] == "long" and mem["mentioned_count"] >= 7:
            mem["level"] = "permanent"
            mem["mentioned_count"] = 0
            print(f"⬆️ 升级：长期 → 永久: {mem['name']}")

    def _update_feature(self, mem, new_desc):
        old_words = mem["feature"].replace("，", " ").replace("。", " ").split()
        new_words = new_desc.replace("，", " ").replace("。", " ").split()
        all_words = old_words + new_words
        freq = {}
        for w in all_words:
            freq[w] = freq.get(w, 0) + 1
        top_words = sorted(freq, key=freq.get, reverse=True)[:5]
        mem["feature"] = "、".join(top_words)
        print(f"🔄 特征更新: {mem['name']} → {mem['feature']}")

    def get_random_fragment(self):
        candidates = [m for m in self.store if m["level"] in ("permanent", "long")]
        if not candidates:
            candidates = self.store
        if not candidates:
            return ""
        mem = random.choice(candidates)
        feat = mem["feature"]
        max_start = max(0, len(feat) - 1)
        start = random.randint(0, max_start)
        end = min(start + random.randint(1, 4), len(feat))
        return feat[start:end]

    def add_short(self, name, feature):
        for mem in self.store:
            if mem["name"] == name and mem["level"] == "permanent":
                return
        mem = {
            "name": name,
            "feature": feature,
            "level": "short",
            "created": self._today(),
            "mentioned_count": 0,
            "last_mentioned_date": None
        }
        self.store.append(mem)
        print(f"📝 新短期记忆: {name}（特征: {feature}）")

    def add_permanent(self, name, feature):
        mem = {
            "name": name,
            "feature": feature,
            "level": "permanent",
            "created": self._today(),
            "mentioned_count": 0,
            "last_mentioned_date": None
        }
        self.store.append(mem)
        print(f"🧬 永久记忆植入: {name}（特征: {feature}）")