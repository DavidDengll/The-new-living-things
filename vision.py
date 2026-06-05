# vision.py
import base64
import os
from config import ZHIPU_API_KEY, USE_CLOUD_CLASSIFIER
import jieba

class VisualModel:
    def __init__(self, mode="simulate", description=None, image_path=None, classifier=None):
        self.mode = mode
        self.description = description or "一只橘猫趴在窗台上，阳光照在它身上"
        self.image_path = image_path
        self.classifier = classifier if USE_CLOUD_CLASSIFIER else None
        if self.mode == "real":
            if not ZHIPU_API_KEY or ZHIPU_API_KEY == "你的真实API-KEY":
                raise ValueError("真实模式需要有效的 ZHIPU_API_KEY")
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
            print("✅ 多模态视觉模型已连接（真实模式）")

    def see(self):
        if self.mode == "simulate":
            return self.description
        elif self.mode == "real":
            return self._real_see()
        elif self.mode == "keyboard":
            return self._keyboard_see()
        else:
            raise ValueError(f"未知视觉模式: {self.mode}")

    def _real_see(self):
        if not self.image_path or not os.path.exists(self.image_path):
            raise FileNotFoundError(f"图片不存在: {self.image_path}")
        with open(self.image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        print(f"🖼️ 正在观察图片: {self.image_path} ...")
        try:
            response = self.client.chat.completions.create(
                model="glm-4v",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": "请简单描述这张图片里的主要物体或场景，只返回一句话，不超过15个字。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]}],
                temperature=0.3, max_tokens=50
            )
            desc = response.choices[0].message.content
            if desc:
                desc = desc.strip()
            else:
                desc = self.description
            print(f"👁️ 视觉模型看到: {desc}")
            return desc
        except Exception as e:
            print(f"❌ 视觉识别失败: {e}")
            return self.description

    def _keyboard_see(self):
        text = input("⌨️ 请输入场景描述：").strip()
        if not text:
            text = self.description
            print(f"👁️ 使用默认场景: {text}")
        return text

    def extract_keywords(self, description):
        if self.classifier and USE_CLOUD_CLASSIFIER:
            try:
                keywords = self.classifier.extract_keywords(description, max_keywords=5)
                if keywords:
                    return keywords
            except Exception as e:
                print(f"⚠️ 云端分类失败，使用 jieba 分词: {e}")
        skip_words = {
            "一只", "一个", "一条", "一张", "一片", "这个", "那个", "这些", "那些",
            "的", "了", "在", "是", "有", "和", "与", "它", "他", "她", "我", "你",
            "着", "被", "把", "从", "到", "上", "中", "下", "里", "外", "都", "也", "很", "就", "还",
            "这", "那", "什么", "怎么", "为什么",
            "上面", "下面", "里面", "外面", "旁边", "前面", "后面",
            "非常", "特别", "比较", "更", "最", "太",
            "正在", "已经", "马上", "刚才", "现在",
        }
        words = jieba.lcut(description)
        keywords = [w for w in words if w.strip() and w not in skip_words]
        if not keywords:
            return ["未知"]
        return keywords[:5]

    def get_main_subject(self, description):
        if self.classifier and USE_CLOUD_CLASSIFIER:
            try:
                return self.classifier.get_main_subject(description)
            except:
                pass
        keywords = self.extract_keywords(description)
        if keywords:
            return keywords[0]
        return "未知"