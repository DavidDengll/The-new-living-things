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
        system_prompt = "你是一个观察者，会用简洁、生动的一句话描述你所看到的情景。一定要回复，不要留空。"
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

                # 检查 response 是否有效
                if response and response.choices and len(response.choices) > 0:
                    llm_output = response.choices[0].message.content
                    # 确保不是 None
                    if llm_output is not None:
                        llm_output = llm_output.strip()
                        if llm_output:  # 非空字符串
                            print(f"✅ 大模型回复: {llm_output}")
                            return llm_output

                print(f"⚠️ 大模型返回空内容 (第{retry+1}次)，尝试重试...")
                time.sleep(1)  # 等1秒再重试

            except Exception as e:
                print(f"❌ 大模型调用失败 (第{retry+1}次): {e}")
                time.sleep(1)

        # 所有重试都失败，用本地兜底
        print(f"⚠️ 大模型全部重试失败，使用本地兜底")
        fallback = self._fallback_output(mood)
        # 确保兜底也不是空字符串
        if not fallback or not fallback.strip():
            fallback = "我看到了，但不知道该说什么。"
        print(f"📝 兜底回复: {fallback}")
        return fallback

    def generate_question(self, unknown_keyword):
        prompt = f"我看到一个不认识的物体叫「{unknown_keyword}」，请用一个好奇的简单问句问我它是什么，只用一句话。一定要回复，不要留空。"
        for retry in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=50
                )
                if response and response.choices and len(response.choices) > 0:
                    question = response.choices[0].message.content
                    if question is not None:
                        question = question.strip()
                        if question:
                            return question
                time.sleep(1)
            except Exception:
                time.sleep(1)

        # 兜底问题
        fallback_question = f"那是什么？「{unknown_keyword}」是什么东西？"
        print(f"📝 兜底提问: {fallback_question}")
        return fallback_question

    def _fallback_output(self, mood=None):
        """确保一定返回非空字符串"""
        if mood:
            energy = mood.get("energy", 0.5)
            curiosity = mood.get("curiosity", 0.5)
            if energy < 0.3:
                return "嗯……（有点累，不想多说话）"
            if curiosity > 0.7:
                return "嗯？那是什么？让我看看……"

        # 随机选一个模板，确保不是空字符串
        template = random.choice(self.fallback_templates)
        if not template or not template.strip():
            template = "我看着眼前的一切，心中泛起一丝波澜。"
        return template