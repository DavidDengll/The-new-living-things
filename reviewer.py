# reviewer.py
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, ZHIPU_MODEL_NAME

class Reviewer:
    """
    语义审查官：调用大模型批量判断念头是否与场景相关。
    """

    def __init__(self, visual_summary, memory_system=None):
        self.visual_summary = visual_summary
        self.memory_system = memory_system
        if not ZHIPU_API_KEY or ZHIPU_API_KEY == "你的真实API-KEY":
            raise ValueError("请在 config.py 或环境变量中设置有效的 ZHIPU_API_KEY")
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self.model_name = ZHIPU_MODEL_NAME

    def judge_batch(self, raw_sentences, rejection_streak=0):
        """
        批量判断多个念头。
        返回 [(句子, 分数, 解释, 最相关概念), ...]
        rejection_streak: 连续被否次数，影响审核官的宽容度。
        """
        if not raw_sentences:
            return []

        # 获取记忆库中的概念供审核官参考
        memory_context = ""
        if self.memory_system:
            cursor = self.memory_system.conn.cursor()
            cursor.execute("SELECT name, feature FROM memories WHERE level IN ('permanent','long') ORDER BY RANDOM() LIMIT 8")
            rows = cursor.fetchall()
            if rows:
                memory_context = "已知的概念：\n" + "\n".join([f"- {r[0]}：{r[1]}" for r in rows])

        # 构建念头列表
        sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(raw_sentences)])

        # 反驳冲动提示
        rejection_hint = ""
        if rejection_streak >= 3:
            rejection_hint = f"注意：发言者已连续被否定 {rejection_streak} 次，可能带有反驳或证明自己的情绪。请对边缘分数稍微宽容（+1分范围内）。"
        elif rejection_streak >= 1:
            rejection_hint = f"注意：发言者已连续被否定 {rejection_streak} 次。"

        system_prompt = f"""你是一个严格但公正的语义审查官。
你的任务是批量判断多个"内心念头"是否和当前看到的场景有语义关联。

对每个念头，给出：
1. 0~10的整数分数
2. 一句话解释
3. 从已知概念中选一个最相关的概念名（如果没有就写"无"）

评分标准：
- 0分：完全无关，纯随机乱码
- 1~3分：有微弱关联
- 4~6分：有一定关联
- 7~9分：明确相关
- 10分：完美契合

{rejection_hint}

{memory_context}

请严格按以下格式回复，每个念头三行，念头之间用---分隔：
念头序号|分数
解释
最相关概念
---
念头序号|分数
解释
最相关概念"""

        user_prompt = f"当前场景：{self.visual_summary}\n待审查的念头：\n{sentences_text}"

        print(f"⚖️ 批量审查 {len(raw_sentences)} 个念头...")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            result = response.choices[0].message.content.strip()
            return self._parse_batch_result(result, raw_sentences)

        except Exception as e:
            print(f"❌ 批量审查失败: {e}，回退到默认分数0")
            return [(s, 0, "审查失败", "") for s in raw_sentences]

    def _parse_batch_result(self, result_text, raw_sentences):
        """解析批量审查结果"""
        blocks = result_text.split("---")
        results = []
        for i, sentence in enumerate(raw_sentences):
            if i < len(blocks):
                block = blocks[i].strip()
                lines = block.split("\n")
                if len(lines) >= 3:
                    # 第一行：念头序号|分数
                    score_line = lines[0].strip()
                    if "|" in score_line:
                        score = float(score_line.split("|")[1].strip())
                    else:
                        import re
                        nums = re.findall(r'\d+', score_line)
                        score = float(nums[0]) if nums else 0
                    explanation = lines[1].strip()
                    related_concept = lines[2].strip()
                    if related_concept == "无":
                        related_concept = ""
                elif len(lines) >= 2:
                    score = float(lines[0].strip()) if lines[0].strip().isdigit() else 0
                    explanation = lines[1].strip() if len(lines) > 1 else ""
                    related_concept = ""
                else:
                    score = 0
                    explanation = "解析失败"
                    related_concept = ""
            else:
                score = 0
                explanation = "未返回结果"
                related_concept = ""

            score = max(0, min(10, score))
            results.append((sentence, score, explanation, related_concept))

        return results

    def judge(self, raw_sentence, rejection_streak=0):
        """单个念头的判断（内部调用 judge_batch）"""
        results = self.judge_batch([raw_sentence], rejection_streak)
        if results:
            _, score, explanation, concept = results[0]
            print(f"✅ 审查结果: {score}/10 - {explanation} | 关联概念: {concept}")
            return score, explanation, concept
        return 0, "审查失败", ""