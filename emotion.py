# emotion.py
import datetime
import json
import os

EMOTION_STATE_FILE = "emotion_state.json"

class Emotion:
    def __init__(self):
        # 精力：0 (疲惫) - 1 (精力充沛)
        self.energy = 0.7
        # 好奇心：0 (漠不关心) - 1 (极度好奇)
        self.curiosity = 0.5
        # 愉悦：0 (沮丧) - 1 (非常开心)
        self.pleasure = 0.5

        self.last_update = datetime.datetime.now().isoformat()
        self.load_state()

    def update(self, event_type=None):
        """随时间自然衰减，并根据事件调整"""
        now = datetime.datetime.now()
        last = datetime.datetime.fromisoformat(self.last_update)
        elapsed_hours = (now - last).total_seconds() / 3600.0

        # 自然衰减：每小时衰减 5%
        decay = 0.05 * elapsed_hours
        self.energy = max(0.0, self.energy - decay)
        self.curiosity = max(0.1, self.curiosity - decay * 0.5)
        self.pleasure = max(0.1, self.pleasure - decay * 0.3)

        # 事件调节
        if event_type == "speak":
            self.energy -= 0.03   # 说话消耗精力
            self.curiosity = min(1.0, self.curiosity + 0.02)
        elif event_type == "silence":
            self.energy = min(1.0, self.energy + 0.05)  # 休息恢复
        elif event_type == "learn_new":
            self.curiosity = min(1.0, self.curiosity + 0.1)
            self.pleasure = min(1.0, self.pleasure + 0.05)
        elif event_type == "unknown_streak":
            self.curiosity = min(1.0, self.curiosity + 0.15)
            self.energy -= 0.02
        elif event_type == "question_asked":
            self.curiosity -= 0.2  # 提问后好奇心暂时满足
            self.pleasure = min(1.0, self.pleasure + 0.05)

        # 约束在 0~1
        self.energy = max(0.0, min(1.0, self.energy))
        self.curiosity = max(0.0, min(1.0, self.curiosity))
        self.pleasure = max(0.0, min(1.0, self.pleasure))

        self.last_update = now.isoformat()
        self.save_state()

    def get_state(self):
        return {
            "energy": self.energy,
            "curiosity": self.curiosity,
            "pleasure": self.pleasure
        }

    def save_state(self):
        with open(EMOTION_STATE_FILE, 'w') as f:
            json.dump({
                "energy": self.energy,
                "curiosity": self.curiosity,
                "pleasure": self.pleasure,
                "last_update": self.last_update
            }, f)

    def load_state(self):
        if os.path.exists(EMOTION_STATE_FILE):
            with open(EMOTION_STATE_FILE, 'r') as f:
                data = json.load(f)
                self.energy = data.get("energy", self.energy)
                self.curiosity = data.get("curiosity", self.curiosity)
                self.pleasure = data.get("pleasure", self.pleasure)
                self.last_update = data.get("last_update", self.last_update)