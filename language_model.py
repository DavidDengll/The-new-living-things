# language_model.py
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, ZHIPU_MODEL_NAME

class LanguageModel:
    def __init__(self):
        if not ZHIPU_API_KEY or ZHIPU_API_KEY == "你的真实API-KEY":
            raise ValueError("请在 config.py 或环境变量中设置有效的 ZHIPU_API_KEY")
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self.model_name = ZHIPU_MODEL_NAME

    def generate_response(self, visual_summary):
        print(f"⏳ 正在请求大模型 (模型: {self.model_name})...")
        system_prompt = "你是一个观察者，会用简洁、生动的一句话描述你所看到的情景。"
        user_prompt = f"我看到：{visual_summary}"
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7, max_tokens=100
            )
            llm_output = response.choices[0].message.content
            print(f"✅ 大模型回复: {llm_output}")
            return llm_output
        except Exception as e:
            print(f"❌ 调用大模型失败: {e}")
            return "我看着眼前的一切，心中泛起一丝波澜。"

    def generate_question(self, unknown_keyword):
        print(f"❓ 正在生成关于'{unknown_keyword}'的提问...")
        prompt = f"我看到一个不认识的物体叫「{unknown_keyword}」，请用一个好奇的简单问句问我它是什么，只用一句话。"
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8, max_tokens=50
            )
            question = response.choices[0].message.content.strip()
            return question
        except Exception:
            return f"那是什么？「{unknown_keyword}」是什么东西？"