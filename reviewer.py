# reviewer.py
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, ZHIPU_MODEL_NAME

class Reviewer:
    """
    语义审查官：调用大模型判断念头是否与场景相关。
    替代旧版的字母匹配、bigram权重、记忆子串匹配。
    """

    def __init__(self, visual_summary, memory_system=None):
        self.visual_summary = visual_summary
        self.memory_system = memory_system
        if not ZHIPU_API_KEY or ZHIPU_API_KEY == "你的真实API-KEY":
            raise ValueError("请在 config.py 或环境变量中设置有效的 ZHIPU_API_KEY")
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self.model_name = ZHIPU_MODEL_NAME

    def judge(self, raw_sentence):
        """
        判断一个念头是否和当前场景有语义关联。
        返回 (分数 0~10, 解释)
        """
        print(f"⚖️ 审查官正在判断: '{raw_sentence}'")

        system_prompt = """你是一个严格但公正的语义审查官。
你的任务是判断一个"内心念头"（可能包含随机字母、词语碎片或记忆片段）是否和当前看到的场景有语义关联。
请给出0~10的整数分数，以及一句话解释。

评分标准：
- 0分：完全无关，纯随机乱码（如"KJDM"、"ABX"）
- 1~3分：有微弱关联（比如包含场景中某个字的拼音首字母，或碰巧撞上了一个字）
- 4~6分：有一定关联（包含与场景相关的词汇、概念或情感）
- 7~9分：明确相关（直接说出了场景中的物体、动作、颜色或感受）
- 10分：完美契合（精准而生动地描述了场景的某个核心元素）

请严格按以下格式回复（不要多说任何额外内容）：
分数|解释"""

        user_prompt = f"当前场景：{self.visual_summary}\n内心念头：{raw_sentence}"

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=80
            )
            result = response.choices[0].message.content.strip()

            if "|" in result:
                parts = result.split("|", 1)
                score = float(parts[0].strip())
                explanation = parts[1].strip()
            else:
                import re
                numbers = re.findall(r'\d+', result)
                score = float(numbers[0]) if numbers else 0
                explanation = result

            score = max(0, min(10, score))
            print(f"✅ 审查结果: {score}/10 - {explanation}")
            return score, explanation

        except Exception as e:
            print(f"❌ 审查失败: {e}，回退到默认分数0")
            return 0, "审查失败，默认驳回"

    def judge_batch(self, raw_sentences):
        """
        批量判断多个念头，返回 [(句子, 分数, 解释), ...]
        """
        results = []
        for sentence in raw_sentences:
            score, explanation = self.judge(sentence)
            results.append((sentence, score, explanation))
        return results