# memory.py
import sqlite3
import datetime
import random
import os

DB_PATH = "entropy_memory.db"

class MemorySystem:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                feature TEXT,
                level TEXT NOT NULL DEFAULT 'short',
                created TEXT NOT NULL,
                mentioned_count INTEGER DEFAULT 0,
                last_mentioned_date TEXT
            )
        ''')
        self.conn.commit()

    @staticmethod
    def _today():
        return datetime.date.today().isoformat()

    @staticmethod
    def _same_day(d1, d2):
        return d1 == d2

    @staticmethod
    def _same_year(d1, d2):
        return d1[:4] == d2[:4]

    def _cleanup(self):
        today = self._today()
        cursor = self.conn.cursor()
        # 清理短期记忆
        cursor.execute("DELETE FROM memories WHERE level='short' AND created != ?", (today,))
        # 清理长期记忆（年份不同）
        cursor.execute("DELETE FROM memories WHERE level='long' AND substr(created,1,4) != ?", (today[:4],))
        self.conn.commit()
        if cursor.rowcount > 0:
            print(f"🧹 过期记忆已清理")

    def search(self, keyword, new_feature=None):
        self._cleanup()
        today = self._today()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE name=?", (keyword,))
        row = cursor.fetchone()
        if row:
            mem = {
                "id": row[0], "name": row[1], "feature": row[2],
                "level": row[3], "created": row[4],
                "mentioned_count": row[5], "last_mentioned_date": row[6]
            }
            last_date = mem["last_mentioned_date"]
            if last_date and self._same_day(last_date, today):
                mem["mentioned_count"] += 1
            else:
                mem["mentioned_count"] = 1
            mem["last_mentioned_date"] = today

            # 特征更新
            if new_feature:
                self._update_feature(mem, new_feature)

            # 检查升级
            self._try_upgrade(mem)

            # 写回数据库
            cursor.execute("""
                UPDATE memories SET mentioned_count=?, last_mentioned_date=?, feature=?, level=?
                WHERE id=?
            """, (mem["mentioned_count"], mem["last_mentioned_date"], mem["feature"], mem["level"], mem["id"]))
            self.conn.commit()
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
        cursor = self.conn.cursor()
        cursor.execute("SELECT feature FROM memories WHERE level IN ('permanent','long') ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT feature FROM memories ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
        if not row:
            return ""
        feat = row[0]
        max_start = max(0, len(feat) - 1)
        start = random.randint(0, max_start)
        end = min(start + random.randint(1, 4), len(feat))
        return feat[start:end]

    def add_short(self, name, feature):
        # 永久记忆同名不添加
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM memories WHERE name=? AND level='permanent'", (name,))
        if cursor.fetchone():
            return
        today = self._today()
        cursor.execute("INSERT INTO memories (name, feature, level, created) VALUES (?,?,?,?)",
                       (name, feature, 'short', today))
        self.conn.commit()
        print(f"📝 新短期记忆: {name}（特征: {feature}）")

    def add_permanent(self, name, feature):
        today = self._today()
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO memories (name, feature, level, created) VALUES (?,?,?,?)",
                       (name, feature, 'permanent', today))
        self.conn.commit()
        print(f"🧬 永久记忆植入: {name}（特征: {feature}）")

    def close(self):
        self.conn.close()