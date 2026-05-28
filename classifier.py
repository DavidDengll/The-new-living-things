# classifier.py
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, ZHIPU_MODEL_NAME
import json

class Classifier:
    """
    调用大模型做语义分类：分词、词性标注、记忆匹配。
    """

    def __init__(self, memory_system=None):
        if not ZHIPU_API_KEY or ZHIPU_API_KEY == "你的真实API-KEY":
            raise ValueError("请在 config.py 或环境变量中设置有效的 ZHIPU_API_KEY")
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self.model_name = ZHIPU_MODEL_NAME
        self.memory_system = memory_system

    def classify(self, text):
        known_concepts = ""
        if self.memory_system:
            cursor = self.memory_system.conn.cursor()
            cursor.execute("SELECT name FROM memories WHERE level IN ('permanent','long') LIMIT 10")
            rows = cursor.fetchall()
            if rows:
                known_concepts = "已知概念：" + "、".join([r[0] for r in rows])

        system_prompt = f"""你是一个中文语义分析专家。
请对给定的文本进行分词和分类。

规则：
1. 把文本拆成有意义的词或短语（2-4个字优先）
2. 标注每个词的词性：名词、动词、形容词、其他
3. 从所有名词中选一个作为"主要描述对象"（通常是第一个名词，或最重要的那个）
4. 如果某个词与已知概念相同或相近，直接使用已知概念中的写法

{known_concepts}

请严格按以下JSON格式返回（不要输出其他内容）：
{{"words":[{{"word":"词1","type":"名词"}},{{"word":"词2","type":"动词"}}],"main_subject":"主要描述对象"}}"""

        user_prompt = f"文本：{text}"

        print(f"🔍 正在分类: {text}")

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
            result_text = response.choices[0].message.content.strip()
            print(f"📝 分类原始返回: {result_text}")

            # 尝试清理 JSON（去掉可能的代码块标记）
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                result_text = "\n".join(lines[1:-1])

            result = json.loads(result_text)
            return result

        except json.JSONDecodeError:
            print(f"⚠️ JSON 解析失败，尝试修复...")
            return self._fallback_classify(text)
        except Exception as e:
            print(f"❌ 分类失败: {e}")
            return self._fallback_classify(text)

    def _fallback_classify(self, text):
        """分类失败时的兜底方案：按标点拆词"""
        words = []
        for sep in "，。！？、；： ":
            text = text.replace(sep, " ")
        segments = text.split()
        for seg in segments:
            if seg.strip():
                words.append({"word": seg.strip(), "type": "名词"})

        main_subject = words[0]["word"] if words else "未知"
        return {"words": words, "main_subject": main_subject}

    def extract_keywords(self, text, max_keywords=5):
        result = self.classify(text)
        words = result.get("words", [])

        keywords = []
        for w in words:
            if w["type"] in ("名词", "形容词"):
                keywords.append(w["word"])

        if len(keywords) < max_keywords:
            for w in words:
                if w["word"] not in keywords:
                    keywords.append(w["word"])
                    if len(keywords) >= max_keywords:
                        break

        return keywords[:max_keywords]

    def get_main_subject(self, text):
        result = self.classify(text)
        return result.get("main_subject", "未知")