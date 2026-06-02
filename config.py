# config.py
import os

# ============================================
# API 配置
# ============================================
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "你的真实API-KEY")
ZHIPU_MODEL_NAME = "glm-4.7-flash"

# ============================================
# 发言与审查
# ============================================
SPEAK_THRESHOLD = 0.6        # 发言冲动（0.2=话痨，0.9=沉默）
MIN_MEANING_SCORE = 4        # 念头通过线（0~10，越高越严格）
MAX_RETRIES = 3              # 想不出好话时的重试次数
CURIOSITY_THRESHOLD = 3      # 连续陌生几次后主动提问

# ============================================
# 记忆升级条件
# ============================================
SHORT_TO_LONG_COUNT = 5      # 短期→长期所需的提及次数
LONG_TO_PERMANENT_COUNT = 7  # 长期→永久所需的提及次数

# ============================================
# 视觉模式
# ============================================
VISION_MODE = "keyboard"     # "simulate" / "real" / "keyboard"
SCENE_DESCRIPTION = "一只橘猫趴在窗台上，阳光照在它身上"
IMAGE_PATH = None

# ============================================
# 分类器设置
# ============================================
USE_CLOUD_CLASSIFIER = True  # 是否使用云端大模型做语义分类

# ============================================
# 情绪模型参数
# ============================================
EMOTION_DECAY_RATE = 0.05
EMOTION_SPEAK_ENERGY_COST = 0.03
EMOTION_SILENCE_ENERGY_GAIN = 0.05
EMOTION_LEARN_CURIOSITY_GAIN = 0.1
EMOTION_LEARN_PLEASURE_GAIN = 0.05
EMOTION_UNKNOWN_CURIOSITY_GAIN = 0.15
EMOTION_QUESTION_CURIOSITY_COST = 0.2

# ============================================
# 反驳冲动参数
# ============================================
REJECTION_BONUS_MAX = 0.3
REJECTION_BONUS_PER_STREAK = 0.1
REJECTION_LENIENT_THRESHOLD = 3

# ============================================
# 生成策略概率
# ============================================
MEMORY_INFLUENCE_PROB = 0.4
WORD_INSERT_PROB = 0.3
MOSAIC_PROB = 0.5
HINT_USE_PROB = 0.7