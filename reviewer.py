# reviewer.py
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, ZHIPU_MODEL_NAME

class Reviewer:
    """
    语义审查官：调用大模型判断念头是否与场景相关。
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
        返回 (分数 0~10, 解释, 最相关记忆概念)
        """
        print(f"⚖️ 审查官正在判断: '{raw_sentence}'")

        # ✅ 获取记忆库中所有概念名，供审核官选择最相关的
        memory_hint = ""
        if self.memory_system:
            cursor = self.memory_system.conn.cursor()
            cursor.execute("SELECT name, feature FROM memories WHERE level IN ('permanent','long') ORDER BY RANDOM() LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                memory_hint = "已知的概念：\n" + "\n".join([f"- {r[0]}：{r[1]}" for r in rows])

        system_prompt = f"""你是一个严格但公正的语义审查官。
你的任务是判断一个"内心念头"（可能包含随机字母、词语碎片或记忆片段）是否和当前看到的场景有语义关联。
请给出0~10的整数分数，以及一句话解释。

评分标准：
- 0分：完全无关，纯随机乱码（如"KJDM"、"ABX"）
- 1~3分：有微弱关联
- 4~6分：有一定关联
- 7~9分：明确相关
- 10分：完美契合

另外，请从以下已知概念中，选一个**与当前场景最相关的概念名**（只写概念名，不要解释）。
{memory_hint}

请严格按以下格式回复（三行，不要多说）：
分数
解释
最相关概念"""

        user_prompt = f"当前场景：{self.visual_summary}\n内心念头：{raw_sentence}"

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            result = response.choices[0].message.content.strip()
            lines = result.split("\n")
            if len(lines) >= 3:
                score = float(lines[0].strip())
                explanation = lines[1].strip()
                related_concept = lines[2].strip()
            elif len(lines) >= 2:
                score = float(lines[0].strip())
                explanation = lines[1].strip()
                related_concept = ""
            else:
                import re
                numbers = re.findall(r'\d+', result)
                score = float(numbers[0]) if numbers else 0
                explanation = result
                related_concept = ""

            score = max(0, min(10, score))
            print(f"✅ 审查结果: {score}/10 - {explanation} | 关联概念: {related_concept}")
            return score, explanation, related_concept

        except Exception as e:
            print(f"❌ 审查失败: {e}，回退到默认分数0")
            return 0, "审查失败，默认驳回", ""

    def judge_batch(self, raw_sentences):
        results = []
        for sentence in raw_sentences:
            score, explanation, concept = self.judge(sentence)
            results.append((sentence, score, explanation, concept))
        return results