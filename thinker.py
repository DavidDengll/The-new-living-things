# thinker.py
from randomness import true_random_int, true_random_byte, true_random_bool
from config import MEMORY_INFLUENCE_PROB, WORD_INSERT_PROB, MOSAIC_PROB, HINT_USE_PROB, ZHIPU_API_KEY, ZHIPU_MODEL_NAME
import random
import time
import datetime
import re
import json

class Thinker:
    def __init__(self, memory_system, memory_influence_prob=None, word_insert_prob=None):
        self.memory = memory_system
        self.memory_influence_prob = memory_influence_prob if memory_influence_prob is not None else MEMORY_INFLUENCE_PROB
        self.word_insert_prob = word_insert_prob if word_insert_prob is not None else WORD_INSERT_PROB
        from zhipuai import ZhipuAI
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self._search_cache = {}

    def _web_search(self, keyword):
        today = datetime.date.today().isoformat()
        if keyword in self._search_cache:
            if self._search_cache[keyword] == today:
                print(f"📦 今日已搜索过「{keyword}」，跳过")
                return []
        print(f"🌐 正在联网搜索: {keyword}")
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                search_results = list(ddgs.text(keyword, max_results=3))
                for r in search_results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    if body:
                        results.append(f"{title}: {body}")
            if results:
                self._search_cache[keyword] = today
                print(f"✅ 搜索到 {len(results)} 条结果")
                return results
            else:
                print(f"⚠️ 搜索无结果")
                return []
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []

    def _learn_and_answer(self, keyword, search_results, question=""):
        """一次大模型调用，同时完成总结和解答"""
        if not search_results:
            return {"summary": None, "answer": None}

        print(f"📝 正在联网学习并解答...")
        search_text = "\n".join(search_results[:3])

        if question and question.strip():
            prompt = f"""我搜索了「{keyword}」，以下是搜索结果：
{search_text}

请完成两个任务：
1. 用一句话（不超过15个字）总结「{keyword}」的核心特征
2. 回答以下问题：{question}

请严格按以下JSON格式返回（不要其他内容）：
{{"summary":"一句话特征总结","answer":"问题的完整解答（含推理过程）"}}"""
        else:
            prompt = f"""我搜索了「{keyword}」，以下是搜索结果：
{search_text}

请用一句话（不超过15个字）总结「{keyword}」的核心特征。

请严格按以下JSON格式返回（不要其他内容）：
{{"summary":"一句话特征总结","answer":""}}"""

        try:
            response = self.client.chat.completions.create(
                model=ZHIPU_MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            result_text = response.choices[0].message.content.strip()
            result_text = re.sub(r'^```(?:json)?\s*\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)

            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                summary = result.get("summary", "")
                answer = result.get("answer", "")
                if summary:
                    print(f"📝 学习结果: {summary}")
                if answer:
                    print(f"💡 附带解答: {answer[:120]}...")
                return {"summary": summary, "answer": answer}

            print(f"⚠️ JSON 解析失败，当作纯文本")
            return {"summary": result_text[:100], "answer": result_text}

        except Exception as e:
            print(f"❌ 学习解答失败: {e}")
            return {"summary": None, "answer": None}

    def _mosaic_generate(self, length):
        fragments = []
        for _ in range(3):
            frag = self.memory.get_random_fragment(min_len=1, max_len=3)
            if frag:
                fragments.append(frag)
        if not fragments:
            return None
        random.shuffle(fragments)
        mosaic = "".join(fragments)
        if len(mosaic) >= length:
            return mosaic[:length]
        else:
            padding = "".join(chr(65 + (true_random_byte() % 26)) for _ in range(length - len(mosaic)))
            return mosaic + padding

    def think(self, keyword, visual_summary, hint=None, question="", skip_thoughts=False):
        # ===== 第一部分：记忆查询 + 联网学习（始终执行） =====
        found = self.memory.search(keyword)
        if found:
            memory_info = f'记得"{keyword}"：{found}'
            thinker_answer = None
        else:
            memory_info = f'不认识"{keyword}"，正在学习...'
            search_results = self._web_search(keyword)
            if search_results:
                result = self._learn_and_answer(keyword, search_results, question)
                summary = result.get("summary")
                thinker_answer = result.get("answer")
                if summary:
                    self.memory.add_short(name=keyword, feature=summary)
                    memory_info = f'学到新知识"{keyword}"：{summary}（来自网络搜索）'
                    found = summary
                else:
                    self.memory.add_short(name=keyword, feature=visual_summary)
                    memory_info = f'不认识"{keyword}"，用场景描述暂存'
                    thinker_answer = None
            else:
                self.memory.add_short(name=keyword, feature=visual_summary)
                memory_info = f'不认识"{keyword}"，用场景描述暂存（联网无结果）'
                thinker_answer = None

        # ===== 第二部分：如果跳过念头生成，直接返回 =====
        if skip_thoughts:
            return {
                "keyword": keyword,
                "memory_info": memory_info,
                "raw_sentences": [],
                "thinker_answer": thinker_answer,
            }

        # ===== 第三部分：四层生成策略（原有逻辑） =====
        num_sentences = true_random_int(1, 2)
        sentence_lengths = [true_random_int(3, 8) for _ in range(num_sentences)]

        raw_sentences = []
        for length in sentence_lengths:
            if hint and true_random_bool(HINT_USE_PROB):
                if len(hint) >= length:
                    raw_sentences.append(hint[:length])
                else:
                    padded = hint + "".join(chr(65 + (true_random_byte() % 26)) for _ in range(length - len(hint)))
                    raw_sentences.append(padded)
                continue

            if true_random_bool(MOSAIC_PROB):
                mosaic = self._mosaic_generate(length)
                if mosaic:
                    raw_sentences.append(mosaic)
                    continue

            if true_random_bool(self.word_insert_prob):
                fragment = self.memory.get_random_fragment(min_len=2, max_len=6)
                if fragment and len(fragment) >= 2:
                    raw_sentences.append(fragment)
                    continue

            chars = []
            for _ in range(length):
                if true_random_bool(self.memory_influence_prob):
                    fragment = self.memory.get_random_fragment(min_len=1, max_len=1)
                    if fragment:
                        chars.append(fragment[0])
                        continue
                char_code = 65 + (true_random_byte() % 26)
                chars.append(chr(char_code))
            raw_sentences.append("".join(chars))

        return {
            "keyword": keyword,
            "memory_info": memory_info,
            "raw_sentences": raw_sentences,
            "thinker_answer": thinker_answer,
        }

    def generate_raw_thought(self, length=5):
        if true_random_bool(MOSAIC_PROB):
            mosaic = self._mosaic_generate(length)
            if mosaic:
                return mosaic
        chars = []
        for _ in range(length):
            if true_random_bool(self.memory_influence_prob):
                fragment = self.memory.get_random_fragment(min_len=1, max_len=1)
                if fragment:
                    chars.append(fragment[0])
                    continue
            char_code = 65 + (true_random_byte() % 26)
            chars.append(chr(char_code))
        return "".join(chars)