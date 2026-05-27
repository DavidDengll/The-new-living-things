# language_model.py
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, ZHIPU_MODEL_NAME
import random
import time

class LanguageModel:
    def __init__(self):
        if not ZHIPU_API_KEY or ZHIPU_API_KEY == "你的真实API-KEY":
            raise ValueError("请在 config.py 或环境变量中设置有效的 ZHIPU_API_KEY")
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self.model_name = ZHIPU_MODEL_NAME
        self.fallback_templates = [
            "我看着眼前的一切，陷入了沉思。",
            "今天的感觉有点不一样。",
            "嗯……有意思。",
            "我需要再观察一会儿。",
            "这个世界总是充满意外。"
        ]

    def generate_response(self, visual_summary, mood=None):
        print(f"⏳ 正在请求大模型...")
        system_prompt = "你是一个观察者，会用简洁、生动的一句话描述你所看到的情景。"
        user_prompt = f"我看到：{visual_summary}"

        # 最多重试2次
        for retry in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=100
                )
                llm_output = response.choices[0].message.content

                if llm_output and llm_output.strip():
                    llm_output = llm_output.strip()
                    print(f"✅ 大模型回复: {llm_output}")
                    return llm_output
                else:
                    print(f"⚠️ 大模型返回空内容 (第{retry+1}次)，尝试重试...")
                    time.sleep(0.5)  # 等半秒再重试

            except Exception as e:
                print(f"❌ 大模型调用失败 (第{retry+1}次): {e}")
                time.sleep(0.5)

        # 所有重试都失败，用本地兜底
        print(f"⚠️ 大模型全部重试失败，使用本地兜底")
        return self._fallback_output(mood)

    def generate_question(self, unknown_keyword):
        prompt = f"我看到一个不认识的物体叫「{unknown_keyword}」，请用一个好奇的简单问句问我它是什么，只用一句话。"
        for retry in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=50
                )
                question = response.choices[0].message.content
                if question and question.strip():
                    return question.strip()
                else:
                    time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        return f"那是什么？「{unknown_keyword}」是什么东西？"

    def _fallback_output(self, mood=None):
        if mood:
            energy = mood.get("energy", 0.5)
            curiosity = mood.get("curiosity", 0.5)
            if energy < 0.3:
                return "嗯……（有点累，不想多说话）"
            if curiosity > 0.7:
                return "嗯？那是什么？让我看看……"
        return random.choice(self.fallback_templates)