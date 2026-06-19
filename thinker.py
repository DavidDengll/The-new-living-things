# thinker.py
from randomness import true_random_int, true_random_byte, true_random_bool
from config import MEMORY_INFLUENCE_PROB, WORD_INSERT_PROB, MOSAIC_PROB, HINT_USE_PROB, ZHIPU_API_KEY, ZHIPU_MODEL_NAME
import random
import time
import datetime
import re

class Thinker:
    def __init__(self, memory_system, memory_influence_prob=None, word_insert_prob=None):
        self.memory = memory_system
        self.memory_influence_prob = memory_influence_prob if memory_influence_prob is not None else MEMORY_INFLUENCE_PROB
        self.word_insert_prob = word_insert_prob if word_insert_prob is not None else WORD_INSERT_PROB
        from zhipuai import ZhipuAI
        self.client = ZhipuAI(api_key=ZHIPU_API_KEY)
        self._search_cache = {}

    def _web_search(self, keyword):
        """联网搜索，一天内相同关键词只搜一次"""
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
        """
        一次大模型调用，同时完成总结和解答。
        使用纯文本格式（总结：... 答案：...）避免 JSON 解析失败。
        """
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

请按以下格式回复：
总结：（你的总结）
答案：（你的答案）"""
        else:
            prompt = f"""我搜索了「{keyword}」，以下是搜索结果：
{search_text}

请用一句话（不超过15个字）总结「{keyword}」的核心特征。

请按以下格式回复：
总结：（你的总结）"""

        try:
            response = self.client.chat.completions.create(
                model=ZHIPU_MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            result_text = response.choices[0].message.content
            if result_text is None:
                print(f"⚠️ 大模型返回 None")
                return {"summary": None, "answer": None}

            result_text = result_text.strip()
            if not result_text:
                print(f"⚠️ 大模型返回空内容")
                return {"summary": None, "answer": None}

            # 解析纯文本格式
            summary = ""
            answer = ""
            summary_match = re.search(r'总结[：:]\s*(.*)', result_text)
            answer_match = re.search(r'答案[：:]\s*(.*)', result_text)
            if summary_match:
                summary = summary_match.group(1).strip()
                print(f"📝 学习结果: {summary}")
            if answer_match:
                answer = answer_match.group(1).strip()
                print(f"💡 附带解答: {answer[:120]}...")

            # 如果解析失败，尝试把整段文本当作总结
            if not summary and not answer:
                print(f"⚠️ 格式解析失败，使用原始文本作为总结")
                summary = result_text[:100]

            return {"summary": summary, "answer": answer}

        except Exception as e:
            print(f"❌ 学习解答失败: {e}")
            return {"summary": None, "answer": None}

    def _mosaic_generate(self, length):
        """从记忆碎片中拼接新词"""
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
        """
        主思考方法。
        - 先查记忆，不认识则联网搜索并学习。
        - 如果 skip_thoughts=True，则不生成随机念头（仅用于解答者已附带答案的情况）。
        """
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

            # 兜底：纯随机字母
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
        """生成一个简短的原始念头（用于沉默时的内心闪过）"""
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