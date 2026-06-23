# reviewer.py
from model_provider import get_provider
from config import REJECTION_LENIENT_THRESHOLD
import re

class Reviewer:
    def __init__(self, visual_summary, memory_system=None):
        self.visual_summary = visual_summary
        self.memory_system = memory_system
        self.provider = get_provider()

    def judge_batch(self, raw_sentences, rejection_streak=0):
        if not raw_sentences:
            return []

        memory_context = ""
        if self.memory_system:
            keywords = [w.strip() for w in self.visual_summary.replace("，", " ").replace("。", " ").split() if len(w.strip()) >= 1]
            related_memories = []
            for kw in keywords[:3]:
                cursor = self.memory_system.conn.cursor()
                cursor.execute(
                    "SELECT name, feature FROM memories WHERE (name LIKE ? OR feature LIKE ?) AND level IN ('permanent','long') LIMIT 3",
                    (f"%{kw}%", f"%{kw}%")
                )
                rows = cursor.fetchall()
                for r in rows:
                    if r not in related_memories:
                        related_memories.append(r)
            if related_memories:
                memory_context = "相关的已知概念：\n" + "\n".join([f"- {r[0]}：{r[1]}" for r in related_memories[:8]])

        sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(raw_sentences)])

        rejection_hint = ""
        if rejection_streak >= REJECTION_LENIENT_THRESHOLD:
            rejection_hint = f"注意：发言者已连续被否定 {rejection_streak} 次，可能带有反驳或证明自己的情绪。请对边缘分数稍微宽容（+1分范围内）。"
        elif rejection_streak >= 1:
            rejection_hint = f"注意：发言者已连续被否定 {rejection_streak} 次。"

        system_prompt = f"""你是一个严格但公正的语义审查官。
你的任务是批量判断多个"内心念头"是否和当前看到的场景有语义关联。

对每个念头，给出：
1. 0~10的整数分数
2. 一句话解释
3. 从相关概念中选一个最相关的概念名（如果没有就写"无"）

评分标准：
- 0分：完全无关，纯随机乱码
- 1~3分：有微弱关联
- 4~6分：有一定关联
- 7~9分：明确相关
- 10分：完美契合

{rejection_hint}

{memory_context}

请严格按以下格式回复（每个念头三行，念头之间用---分隔）：
念头序号|分数
解释
最相关概念
---
念头序号|分数
解释
最相关概念"""

        user_prompt = f"当前场景：{self.visual_summary}\n待审查的念头：\n{sentences_text}"

        print(f"⚖️ 批量审查 {len(raw_sentences)} 个念头...")

        prompt_length = len(system_prompt) + len(user_prompt) + len(sentences_text)
        estimated_tokens = prompt_length // 2 + 200
        max_tokens = min(800, max(200, estimated_tokens))

        try:
            result = self.provider.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=max_tokens
            )
            if not result:
                print("❌ 批量审查：大模型返回空")
                return [(s, 0, "审查失败", "") for s in raw_sentences]
            print(f"📝 审查官原始返回:\n{result}")
            return self._parse_batch_result(result, raw_sentences)
        except Exception as e:
            print(f"❌ 批量审查失败: {e}，回退到默认分数0")
            return [(s, 0, "审查失败", "") for s in raw_sentences]

    def _parse_batch_result(self, result_text, raw_sentences):
        results = []
        blocks = result_text.split("---")
        if len(blocks) < len(raw_sentences):
            blocks = result_text.split("\n\n")

        for i, sentence in enumerate(raw_sentences):
            score = 0
            explanation = "解析失败"
            related_concept = ""
            if i < len(blocks):
                block = blocks[i].strip()
                lines = [l.strip() for l in block.split("\n") if l.strip()]
                for line in lines:
                    if "|" in line and any(c.isdigit() for c in line):
                        parts = line.split("|")
                        for part in parts:
                            nums = re.findall(r'\d+', part)
                            if nums:
                                score = float(nums[0])
                                break
                    elif line.isdigit() and len(line) <= 2:
                        score = float(line)
                    elif "分" in line and any(c.isdigit() for c in line):
                        nums = re.findall(r'\d+', line)
                        if nums:
                            score = float(nums[0])
                    elif len(line) > 3 and not line.startswith("念头"):
                        if explanation == "解析失败":
                            explanation = line
                    if line != lines[0] and line not in ["无", "解析失败"] and len(line) <= 10:
                        if related_concept == "" and line != explanation:
                            related_concept = line
                if score == 0 and len(lines) > 0:
                    nums = re.findall(r'\d+', lines[0])
                    if nums:
                        score = float(nums[0])
                        if len(lines) > 1:
                            explanation = lines[1]
                        if len(lines) > 2:
                            related_concept = lines[2]
                if related_concept == "无":
                    related_concept = ""
            score = max(0, min(10, score))
            results.append((sentence, score, explanation, related_concept))
        return results

    def judge(self, raw_sentence, rejection_streak=0):
        results = self.judge_batch([raw_sentence], rejection_streak)
        if results:
            _, score, explanation, concept = results[0]
            print(f"✅ 审查结果: {score}/10 - {explanation} | 关联概念: {concept}")
            return score, explanation, concept
        return 0, "审查失败", ""