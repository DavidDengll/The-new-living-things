# vision.py
import base64
import os
from config import ZHIPU_API_KEY

class VisualModel:
    def __init__(self, mode="simulate", description=None, image_path=None):
        self.mode = mode
        self.description = description or "一只橘猫趴在窗台上，阳光照在它身上"
        self.image_path = image_path
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
            desc = response.choices[0].message.content.strip()
            print(f"👁️ 视觉模型看到: {desc}")
            return desc
        except Exception as e:
            print(f"❌ 视觉识别失败: {e}")
            return self.description

    def extract_keywords(self, description):
        words = description.replace("，", " ").replace("。", " ").split()
        return words[0] if words else "未知"