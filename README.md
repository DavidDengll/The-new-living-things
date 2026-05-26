# 熵灵 (Entropy Sprite)

> 一个由**真随机**驱动的实验性意识模拟系统。
> 它不是普通的聊天程序，而是一个拥有“内核冲动”与“外部语言”的双层心智模型。

## 👤 关于我
我是一名六年级学生，会 C++。因为对意识和随机性感到好奇，我开始动手创造了熵灵。

---

## 🧠 我为什么这样设计

### 人类思考的秘密
我发现，人类思考的过程并不是直接“想”出答案。我们的大脑会先随机冒出很多乱七八糟的念头（就像神经元在自发放电），然后自己给自己打分，把最合适的那个挑出来。这个过程太快了，所以我们平时根本察觉不到。

我就想：能不能用代码模拟这个过程？

### 1. 真随机驱动 — 模拟大脑噪声
我用操作系统硬件熵（或者量子随机数）来决定：
- 要不要“说话”
- 说几句话
- 每句话多长
然后通过随机 ASCII 码生成最原始的“念头”。它无时无刻都在随机——就跟大脑里的神经噪声一样，是“想法”诞生的土壤。

### 2. 自我审查 — 语义级批量审查官
生成的乱码会交给**审核官**。审核官会调用大模型，根据**视觉模型**看到的场景，从语义层面批量判断所有念头是否有意义。

大模型会给每个念头打出 0~10 分的语义关联分数。审核官还会从记忆库中选出一个**与当前场景最相关的概念**，反馈给思考者，指导下一轮念头的生成方向。

所有念头在一次 API 调用中完成批量审查，大幅降低了调用成本。

如果所有念头都低于 4 分 → **思考者**重新生成。如果多次重试仍不通过，取最高分的那句。

**反驳冲动**：当内核的念头连续被审核官否定时，系统会累积“反驳冲动”，并传入审核官。审核官在评分时会对边缘分数更宽容——被否定多了的人，需要一点被理解的空间。

### 3. 情绪模型 — 模拟内在状态
三维情绪系统：
- **精力**：累了就不想说话，休息会恢复
- **好奇心**：好奇时就爱提问，容易插嘴
- **愉悦**：开心时宽容，不开心时挑剔

情绪随时间自然衰减，也被事件影响。好奇心不再只是一个硬编码计数器——当审核官给某个念头打出低分时（说明“完全不理解”），好奇心会自然增长。情绪不仅影响审核官打分，还会直接影响发言冲动。

**反驳冲动**：当内核的念头连续被审核官否定时，系统会累积“反驳冲动”，临时提高发言概率。这避免了“越被否定越沉默”的单向趋近，让熵灵在被打压时反而更有表达欲。

### 4. 视觉感知 — 环境的输入
用 GPT 或 GLM 等多模态模型作为“眼睛”。看到画面后，用不超过 15 个字简短描述，作为审核官判断的依据。

### 5. 记忆系统 — 遗忘与巩固
三层记忆，模仿人脑的海马体和皮层：
- **短期记忆**：一天删一次
- **长期记忆**：一年删一次
- **永久记忆**：永远不删
一天内被连续提及 5 次 → 短期升长期；一年内被提 7 次 → 长期升永久。

**记忆持久化**：所有记忆用 SQLite 存在硬盘上，关机重启不丢失。

**记忆影响内核**：思考者生成念头时，有四层生成策略（按优先级）：
1. **hint 引导**：审核官反馈的“最相关记忆概念”作为方向
2. **词素拼图**：从记忆碎片中随机拼接新词（不是复制粘贴，是重组创作）
3. **整词插入**：从记忆库取完整片段
4. **兜底随机**：`chr(65+random)` 只在记忆库完全为空时才启用

记忆不再是被动的仓库，而是通过审核官的中转和碎片重组，真正参与了“想法”的生成。

### 6. 本地兜底 — 断网也能说话
大模型（GLM-4.7-Flash）是“主声道”。如果 API 不可用，内置本地兜底回复，根据当前情绪给出不同反应。

### 7. 沉默时的内心闪过
当内核决定不说话时，它仍会生成一个简短念头交给审核官判断。如果语义上有意义，附在回答末尾（如“内心一闪：猫”）；如果无意义，只留下一个低调的“（…）”。无意义的念头不影响发言阈值，但会累积反驳冲动和好奇心。

---

## 🧱 模块说明
| 文件 | 功能 |
|------|------|
| `randomness.py` | 从操作系统熵池提取真随机数 |
| `memory.py` | 三层记忆系统（SQLite 持久化，名称-特征结构，自动升级） |
| `emotion.py` | 情绪模型（精力/好奇/愉悦，随时间衰减，事件触发，状态保存） |
| `vision.py` | 视觉模型（支持模拟文字/真实图片多模态） |
| `thinker.py` | 思考者，四层生成策略（hint引导→词素拼图→整词插入→兜底随机） |
| `reviewer.py` | 语义审查官，批量审查念头，支持反驳冲动，返回最相关记忆概念 |
| `language_model.py` | 大模型外壳 + 本地兜底输出 + 好奇心提问 |
| `main.py` | 主系统，整合所有模块 |

---

## ⚙️ 快速开始
1. 克隆本仓库
2. 安装依赖：`pip install zhipuai`
3. 在 [智谱AI开放平台](https://open.bigmodel.cn/) 申请免费 API Key
4. 把 Key 填进 `config.py`
5. 运行：`python main.py`

> SQLite 是 Python 自带模块，无需额外安装。情绪状态和记忆都会自动保存到本地文件，下次启动时自动加载。

---

## 🔄 自我优化机制
1. **情绪影响发言冲动**：好奇高更容易开口，精力低更倾向于沉默
2. **反驳冲动**：连续被否时反而更想说，且审核官会适当宽容
3. **好奇心自然增长**：审核官打出低分时好奇心自动上升
4. **批量语义审查**：一次 API 调用判断所有念头，大幅降低成本
5. **审查官引导记忆方向**：返回的关联概念作为 hint 传给下一轮生成
6. **词素拼图**：从记忆碎片中随机拼接新词，不是复制粘贴
7. **动态发言阈值**：说得好就多开口，说得差就沉默
8. **特征自更新**：对事物的认识随观察越来越精准
9. **好奇心提问**：连续遇到陌生事物会主动发问
10. **情绪演化**：精力、好奇、愉悦随时间变化
11. **状态持久化**：记忆和情绪在关机后不丢失
12. **本地兜底**：API 不可用时仍能输出
13. **沉默内心闪过**：不说话时内核仍有念头产生，过审后以“内心一闪”形式出现

---

## 📌 关于代码
这个项目是我和 DeepSeek 结对编程做的——我出想法和架构，DeepSeek 帮我写代码。
代码可能写得不太好（我才六年级，也没钱充值），但我觉得这个思路本身有意思。各位大佬可以不看我的代码，把它当做一个灵感参考，自己去实现。

---

## 🔬 与现有项目的区别
市面上有使用量子随机数的项目，有三层记忆系统，也有 LLM 自我审查技术。但熵灵是**第一个将这些技术有机组合**为一个模拟意识生成闭环的系统：真随机生成原始念头 → 批量语义审查并反馈关联记忆 → 记忆碎片拼图引导下一轮生成方向 → 情绪和反驳冲动影响发言与审查 → 记忆固化 → 自主决定表达（包括沉默时的内心闪过）。它不是现有任何项目的复制品，而是一个全新的组合实验。

---

## 📄 许可
MIT License

---

# English

# Entropy Sprite

> An experimental consciousness simulation driven by **true randomness**.
> It is not a typical chatbot but a dual-layer mind model with an "inner impulse" and an "outer language."

## 👤 About Me
I'm a 6th-grade student. I can write C++ code. I built Entropy Sprite because I got curious about consciousness and randomness.

---

## 🧠 Why I Designed It This Way

### How Human Thinking Actually Works
I realized that when we think, our brain doesn't just produce a perfectly formed idea. First, neurons fire randomly and generate a bunch of messy thoughts. Then, our brain scores them and picks the best one. This happens so fast we don't notice it.

So I thought: what if I could simulate this process in code?

### 1. True Randomness Engine — Simulating Neural Noise
I used hardware entropy from the OS (or quantum random numbers) to decide:
- Whether to "speak"
- How many sentences to say
- How long each sentence is
Then raw "thoughts" are generated from random ASCII characters. It's always random — just like neural noise in our brains, the soil where ideas grow.

### 2. Semantic Batch Reviewer — Meaning-Based Censorship
The random strings are sent to a **Reviewer**, which calls a large language model to batch-judge all thoughts on a 0–10 scale based on the scene from the **Vision Model**.

All thoughts are evaluated in a single API call, significantly reducing costs.

The Reviewer also selects the **most relevant memory concept** from the memory bank and feeds it back to the Thinker as a hint for the next round.

If all thoughts score below 4 → the **Thinker** retries. If multiple retries still fail, the highest-scoring one is chosen.

**Rebuttal Impulse**: When thoughts are repeatedly rejected, the system passes the rebuttal streak to the Reviewer, which becomes slightly more lenient on borderline scores — because someone who's been shut down repeatedly deserves a little understanding.

### 3. Emotion Model — Simulating Internal States
A three-dimensional emotion system:
- **Energy**: When tired, prefers silence; rest restores it
- **Curiosity**: When curious, asks more questions and interrupts more often
- **Pleasure**: When happy, more forgiving; when unhappy, pickier

Emotions decay over time and are affected by events. Curiosity grows naturally when the Reviewer gives low scores. Emotions influence both the Reviewer's tolerance and the impulse to speak.

**Rebuttal Impulse**: When the kernel's thoughts are repeatedly rejected, the system accumulates a rebuttal impulse, temporarily increasing speech probability. This avoids the one-way drift toward silence.

### 4. Vision Perception — Input from the Environment
Multimodal models like GPT or GLM act as its "eyes," describing scenes in under 15 words for the Reviewer to use as context.

### 5. Memory System — Forgetting and Consolidation
Three-layer memory inspired by the hippocampus and cortex:
- **Short-term** – cleared daily
- **Long-term** – cleared yearly
- **Permanent** – never forgotten
5 recalls in one day → upgrade to long-term. 7 recalls in one year → upgrade to permanent.

**Persistent Memory**: All memories stored in SQLite on disk, surviving shutdowns.

**Memory-Influenced Kernel**: The Thinker has a four-tier generation strategy (by priority):
1. **Hint-guided**: Uses the Reviewer's "most relevant memory concept" as direction
2. **Morpheme Mosaic**: Randomly splices memory fragments into new words (recombination, not copy-paste)
3. **Whole-word insertion**: Takes complete fragments from memory
4. **Fallback random**: `chr(65+random)` only activates when the memory bank is completely empty

Memory is no longer a passive warehouse — through the Reviewer's relay and fragment recombination, it genuinely participates in shaping thought generation.

### 6. Local Fallback — Speaking When Offline
The LLM (GLM-4.7-Flash) is the "main voice channel." If the API is unavailable, built-in fallback responses adjust based on current mood.

### 7. Silent Inner Murmur
When the kernel decides not to speak, it still generates a brief thought for Reviewer judgment. If semantically meaningful, it's appended (e.g., "inner murmur: meow"). If meaningless, a quiet "(…)" remains. Meaningless thoughts accumulate rebuttal impulse and curiosity.

---

## 🧱 Module Overview
| File | Function |
|------|----------|
| `randomness.py` | Extracts true random numbers from OS entropy pool |
| `memory.py` | Three-layer memory system (SQLite persistence, auto-upgrade) |
| `emotion.py` | Emotion model (energy/curiosity/pleasure, time decay, state saving) |
| `vision.py` | Vision model (simulated text / real image multimodal) |
| `thinker.py` | Thinker, four-tier generation (hint→mosaic→whole-word→fallback random) |
| `reviewer.py` | Semantic batch reviewer, rebuttal-aware, returns most relevant memory concept |
| `language_model.py` | LLM shell + local fallback + curiosity questions |
| `main.py` | Main system, integrates all modules |

---

## ⚙️ Quick Start
1. Clone this repo
2. Install dependencies: `pip install zhipuai`
3. Get a free API Key from [ZhipuAI Open Platform](https://open.bigmodel.cn/)
4. Put your Key in `config.py`
5. Run: `python main.py`

> SQLite is built-in. Emotion state and memories are automatically saved locally and loaded on startup.

---

## 🔄 Self-Optimization Mechanisms
1. **Emotion-driven speak impulse**: Curiosity increases speech likelihood, fatigue reduces it
2. **Rebuttal impulse**: Repeated rejection triggers stronger speech urge, Reviewer becomes more lenient
3. **Natural curiosity growth**: Low Reviewer scores automatically increase curiosity
4. **Batch semantic review**: All thoughts judged in one API call, drastically reducing cost
5. **Reviewer-guided memory direction**: Returned related concepts serve as hints for next-round generation
6. **Morpheme mosaic**: Randomly splices memory fragments into new words, not copy-paste
7. **Dynamic speak threshold**: Speaks more when saying good things, goes silent when saying nonsense
8. **Feature self-updating**: Understanding of concepts refines with each observation
9. **Curiosity-driven questioning**: Actively asks about repeatedly unfamiliar things
10. **Emotion evolution**: Energy, curiosity, and pleasure change over time
11. **State persistence**: Memories and emotions survive shutdowns
12. **Local fallback**: Outputs even when API is unavailable
13. **Silent inner murmur**: Kernel thoughts persist even when silent, appear if meaningful

---

## 📌 A Note on the Code
I built this project through pair programming with DeepSeek — I came up with the ideas and architecture, and DeepSeek helped me write the code.
The code might be rough (I'm only in 6th grade and don't have money for premium tools), but I hope the idea itself is interesting. Feel free to ignore my code and just use the concept as inspiration.

---

## 🔬 How This Differs From Existing Projects
Entropy Sprite is **the first to organically combine** true random thought generation, batch semantic review with memory concept feedback, memory fragment mosaic guiding generation direction, emotion and rebuttal impulse affecting both speech and review, memory consolidation, and autonomous expression (including silent inner murmurs) into a single closed-loop consciousness simulation system.

---

## 📄 License
MIT License

### 1. 安装
```bash
git clone https://github.com/DavidDengll/The-new-living-things.git
cd The-new-living-things
pip install zhipuai
2. 获取 API Key
访问 智谱AI开放平台 注册并完成实名认证。

在控制台创建 API Key。

打开 config.py，填入 Key：

python
ZHIPU_API_KEY = "sk-你的key"
3. 运行
bash
python main.py
4. 自定义配置
所有可调参数集中在 config.py，无需修改其他源代码：

参数	默认值	说明
SPEAK_THRESHOLD	0.6	发言冲动（0.2=话痨，0.9=沉默）
MIN_MEANING_SCORE	4	念头通过线（0~10）
MAX_RETRIES	5	重试次数
SHORT_TO_LONG_COUNT	5	短期→长期所需提及次数
LONG_TO_PERMANENT_COUNT	7	长期→永久所需提及次数
视觉模式切换（修改 config.py）：

模拟模式（默认）：VISION_MODE = "simulate"，修改 SCENE_DESCRIPTION 换场景

真实图片：VISION_MODE = "real"，设置 IMAGE_PATH = "photo.jpg"（需要多模态额度）

5. 故障排查
现象	可能原因	解决方法
No module named 'zhipuai'	                    未安装依赖	 执行 pip install zhipuai
提示 API Key 无效	                             Key 未填写或格式错误	检查 config.py 中 Key 是否以 sk- 开头
长时间无响应或超时	网络无法访问智谱 API	       检查网络连接，尝试 ping api.zhipuai.cn
数据库报错	文件损坏或被占用	                  关闭其他使用该数据库的程序；如仍不行，备份后删除 entropy_memory.db 重新运行
真实图片模式无输出	图片路径错误或没有多模态额度	确认图片在项目目录下，且智谱账户有 glm-4v 的可用额度

## 各位也可以自己调节一下你想要改的东西