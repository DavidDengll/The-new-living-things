# classifier.py
from zhipuai import ZhipuAI
from config import ZHIPU_API_KEY, ZHIPU_MODEL_NAME
import json
import re
import hashlib

class Classifier:
    """
    调用大模型做语义分类：分词、词性标注、记忆匹配。
    相同文本不重复调用大模型。
    """

    def __init__(self, memory_system=None):
        if not ZHIPU_API_KEY or ZHIPU_API_KEY == "你的真实API-KEY":
            raise ValueError("请在 config.py 或环境变量中设置有效的 ZHIPU_API_KEY")
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self.model_name = ZHIPU_MODEL_NAME
        self.memory_system = memory_system
        # 分类缓存：{文本哈希: 分类结果}
        self._classify_cache = {}

    def classify(self, text):
        # 检查缓存
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self._classify_cache:
            cached = self._classify_cache[cache_key]
            print(f"📦 使用缓存的分类结果: {cached.get('main_subject', '')}")
            return cached

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
3. 从所有名词中选一个作为"主要描述对象"
4. 如果某个词与已知概念相同或相近，直接使用已知概念中的写法

{known_concepts}

请严格按以下JSON格式返回（不要其他内容）：
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

            json_match = re.search(r'\{[^{}]*"words"\s*:\s*\[.*?\]\s*,\s*"main_subject"\s*:\s*"[^"]*"\s*\}', result_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*?\}', result_text, re.DOTALL)

            if json_match:
                clean_json = json_match.group()
                result = json.loads(clean_json)
                # 存入缓存（最多 50 条）
                if len(self._classify_cache) >= 50:
                    oldest_key = list(self._classify_cache.keys())[0]
                    del self._classify_cache[oldest_key]
                self._classify_cache[cache_key] = result
                return result
            else:
                raise json.JSONDecodeError("未找到有效JSON", result_text, 0)

        except json.JSONDecodeError:
            print(f"⚠️ JSON 解析失败，使用兜底分词")
            result = self._fallback_classify(text)
            if len(self._classify_cache) >= 50:
                oldest_key = list(self._classify_cache.keys())[0]
                del self._classify_cache[oldest_key]
            self._classify_cache[cache_key] = result
            return result
        except Exception as e:
            print(f"❌ 分类失败: {e}")
            result = self._fallback_classify(text)
            return result

    def _fallback_classify(self, text):
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