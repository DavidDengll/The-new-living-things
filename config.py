# config.py
import os

# ============================================
# 模型提供商配置（通用 OpenAI 兼容接口）
# ============================================
MODEL_NAME = "glm-4.7-flash"
API_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
API_KEY = os.environ.get("LLM_API_KEY", "你的API-Key")
API_EXTRA_HEADERS = {}

# ============================================
# 发言与审查
# ============================================
SPEAK_THRESHOLD = 0.6
MIN_MEANING_SCORE = 4
MAX_RETRIES = 3
CURIOSITY_THRESHOLD = 3

# ============================================
# 记忆升级条件
# ============================================
SHORT_TO_LONG_COUNT = 5
LONG_TO_PERMANENT_COUNT = 7

# ============================================
# 视觉模式
# ============================================
VISION_MODE = "keyboard"
SCENE_DESCRIPTION = "一只橘猫趴在窗台上，阳光照在它身上"
IMAGE_PATH = None

# ============================================
# 分类器设置
# ============================================
USE_CLOUD_CLASSIFIER = False

# ============================================
# 编码模式选择（双模架构）
# ============================================
# True  : 使用云端大模型编码（效果好，消耗 Token）
# False : 使用本地 sentence-transformers 编码（省钱，GPU 加速）
USE_CLOUD_ENCODER = False              # 默认本地
CLOUD_ENCODER_MODEL = "Agnes-2.0-Flash"  # 云端编码用的模型名

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

# ============================================
# 启动配置校验
# ============================================
def validate_config():
    if API_KEY == "你的API-Key" or API_KEY is None or API_KEY == "":
        raise ValueError(
            "❌ 检测到 API_KEY 未配置！\n"
            "请打开 config.py，将 API_KEY 替换为你自己的密钥，\n"
            "或者设置环境变量 LLM_API_KEY。\n"
            "如果你用的是智谱，去 https://open.bigmodel.cn 注册获取。"
        )
    print("✅ 配置校验通过")