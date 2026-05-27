# config.py
import os

# ============================================
# API 配置
# ============================================
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "sk-6996b71a04f84c73a1d1c7741e22b2d7.c4MoGypYMEONUouA")
ZHIPU_MODEL_NAME = "glm-4.7-flash"

# ============================================
# 发言与审查
# ============================================
SPEAK_THRESHOLD = 0.6        # 发言冲动（0.2=话痨，0.9=沉默）
MIN_MEANING_SCORE = 4        # 念头通过线（0~10，越高越严格）
MAX_RETRIES = 3              # 想不出好话时的重试次数（降低以加快速度）
CURIOSITY_THRESHOLD = 3      # 连续陌生几次后主动提问

# ============================================
# 记忆升级条件
# ============================================
SHORT_TO_LONG_COUNT = 5      # 短期→长期所需的提及次数
LONG_TO_PERMANENT_COUNT = 7  # 长期→永久所需的提及次数

# ============================================
# 视觉模式
# "simulate" = 固定场景描述
# "real"     = 真实图片（需要多模态额度）
# "keyboard" = 键盘输入场景描述
# ============================================
VISION_MODE = "keyboard"     # 默认改为键盘输入模式
SCENE_DESCRIPTION = "一只橘猫趴在窗台上，阳光照在它身上"
IMAGE_PATH = None            # 真实图片模式时填写，如 "photo.jpg"

# ============================================
# 情绪模型参数
# ============================================
EMOTION_DECAY_RATE = 0.05    # 每小时情绪衰减比例
EMOTION_SPEAK_ENERGY_COST = 0.03   # 每次发言消耗的精力
EMOTION_SILENCE_ENERGY_GAIN = 0.05 # 沉默时恢复的精力
EMOTION_LEARN_CURIOSITY_GAIN = 0.1 # 学到新东西时好奇心的增长
EMOTION_LEARN_PLEASURE_GAIN = 0.05 # 学到新东西时愉悦的增长
EMOTION_UNKNOWN_CURIOSITY_GAIN = 0.15 # 连续陌生时好奇心的增长
EMOTION_QUESTION_CURIOSITY_COST = 0.2 # 提问后好奇心的下降

# ============================================
# 反驳冲动参数
# ============================================
REJECTION_BONUS_MAX = 0.3    # 连续被否时发言概率的最大提升
REJECTION_BONUS_PER_STREAK = 0.1  # 每次被否的概率提升
REJECTION_LENIENT_THRESHOLD = 3   # 审核官开始宽容的连续被否次数

# ============================================
# 生成策略概率
# ============================================
MEMORY_INFLUENCE_PROB = 0.4  # 单字符记忆影响的概率
WORD_INSERT_PROB = 0.3       # 整词插入的概率
MOSAIC_PROB = 0.5            # 词素拼图的概率
HINT_USE_PROB = 0.7          # 使用 hint 的概率