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

### 2. 自我审查 — 模拟前额叶的筛选
生成的乱码会交给一个叫**审核官**的 Agent，让它结合**视觉模型**看到的场景和**情绪状态**，判断这些话有没有意义。
- 如果全是废话 → 让**思考者**重新想。重试时，上次最佳句子的尾部会作为“引导”传给思考者，让下一次生成更有方向感，而不是纯随机抽卡。
- 如果有意义 → 排个序，挑最好的那句
审核官不仅看乱码和视觉场景的字母匹配，还会检查乱码中是否包含了**记忆库里的真实词语**。如果内核的念头碰巧说出了一个记忆中的词（比如“喵”），即使和视觉字母不重合，也会被加分。审核官学到的字母组合权重（bigram）会被持久化保存，下次启动继续生效，不再是“金鱼的记忆”。

### 3. 情绪模型 — 模拟内在状态
我给它加入了三维情绪系统：
- **精力**：累了就不想说话，休息会恢复
- **好奇心**：好奇时就爱提问，容易插嘴
- **愉悦**：开心时宽容，不开心时挑剔
情绪会随时间自然衰减，也会被事件影响（说了话消耗精力，学到新东西增加好奇心和愉悦）。情绪不仅影响审核官打分，还会直接影响发言冲动——好奇心高时更容易开口，精力低时更倾向于沉默。每次关机的情绪会被保存，下次启动继续演化。

### 4. 视觉感知 — 环境的输入
我用 GPT 或 GLM 等多模态模型作为它的“眼睛”。看到画面后，用不超过 15 个字简短描述，再交给审核官做判断。环境成了它“思考”的依据，就像我们用眼睛看见世界，才知道该说什么。

### 5. 记忆系统 — 遗忘与巩固
我给它做了三层记忆，模仿人脑的海马体和皮层：
- **短期记忆**：一天删一次（像临时记住的电话号码）
- **长期记忆**：一年删一次（像学会的公式，不复习就会忘）
- **永久记忆**：永远不删（像自己的名字，一辈子忘不掉）
如果短期记忆在一天内被连续提了 5 次，就升级为长期；长期记忆在一年内被提了 7 次，就升级为永久。这就跟复习知识一样，反复提及才能记住。

**记忆持久化**：所有记忆用 SQLite 数据库存在硬盘上，关机重启也不会丢失。三层结构、升级规则、特征自更新全部保留。

**记忆影响内核**：思考者生成乱码时，有一定概率直接从记忆库中抽取**整词片段**（2~6个字）插入到念头里。比如记忆里有“会喵喵叫”，念头里可能直接出现“喵喵”。记忆不再只是被动的仓库，它真正参与了“想法”的生成。

### 6. 本地兜底 — 断网也能说话
大模型（GLM-4.7-Flash）是它的“主声道”，但如果 API 不可用（断网、额度用完），它不会变哑巴。内置了本地兜底回复，还会根据当前情绪给出不同的反应。

### 7. 沉默时的内心闪过
当内核决定不说话时，它依然会生成一个简短的念头（“内心一闪”），交给审核官判断。如果这个念头有意义，就会附在回答末尾（如“内心一闪：猫”）；如果无意义，就默默丢弃，只输出正常回答——而且不会因为被毙掉就降低阈值，避免了“越被否越想说”的反直觉逻辑。这样内核永远不会完全隐身，只是在大多数时候选择了安静，或者在说出来之前被审核官毙掉了。

---

## 🧱 模块说明
| 文件 | 功能 |
|------|------|
| `randomness.py` | 从操作系统熵池提取真随机数 |
| `memory.py` | 三层记忆系统（SQLite 持久化，名称-特征结构，自动升级） |
| `emotion.py` | 情绪模型（精力/好奇/愉悦，随时间衰减，事件触发，状态保存） |
| `vision.py` | 视觉模型（支持模拟文字/真实图片多模态） |
| `thinker.py` | 思考者，支持整词插入和重试引导生成 |
| `reviewer.py` | 审核官，打分受情绪和记忆匹配双重影响，bigram 权重持久化 |
| `language_model.py` | 大模型外壳 + 本地兜底输出 |
| `main.py` | 主系统，情绪纳入发言冲动，沉默被否不降阈值 |

---

## ⚙️ 快速开始
1. 克隆本仓库
2. 安装依赖：`pip install zhipuai`
3. 在 [智谱AI开放平台](https://open.bigmodel.cn/) 申请免费 API Key
4. 把 Key 填进 `config.py`
5. 运行：`python main.py`

> SQLite 是 Python 自带模块，无需额外安装。情绪状态、记忆和审核官学习权重都会自动保存到本地文件，下次启动时自动加载。

---

## 🔄 自我优化机制
1. **情绪影响发言冲动**：好奇心高更容易开口，精力低更倾向于沉默，不再纯随机抛硬币
2. **重试引导生成**：审核不通过时，上次最佳句尾作为引导传给思考者，下次生成更有方向
3. **动态发言阈值**：说得好就多开口，说得差就沉默；沉默被否不降阈值
4. **记忆整词插入**：内核怪话里会偶尔出现记忆中的完整词语，而非只取单个字母
5. **记忆匹配审核**：审核官不仅看字母重合，还会检查乱码是否包含记忆中的真实内容
6. **审查官持久化学习**：好的字母组合权重保存到文件，下次启动继续生效
7. **特征自更新**：对事物的认识随观察越来越精准
8. **好奇心提问**：连续遇到陌生事物会主动发问
9. **情绪演化**：精力、好奇、愉悦随时间变化，影响审查和发言行为
10. **状态持久化**：记忆和情绪在关机后不丢失，启动继续演化
11. **本地兜底**：API 不可用时仍能输出，不会变哑巴
12. **沉默内心闪过**：不主动说话时，内核仍有念头产生，过审后以“内心一闪”形式出现

---

## 📌 关于代码
这个项目是我和 DeepSeek 结对编程做的——我出想法和架构，DeepSeek 帮我写代码。
代码可能写得不太好（我才六年级，也没钱充值），但我觉得这个思路本身有意思。各位大佬可以不看我的代码，把它当做一个灵感参考，自己去实现。

---

## 🔬 与现有项目的区别
市面上有使用量子随机数的项目，有三层记忆系统，也有 LLM 自我审查技术。但熵灵是**第一个将这些技术有机组合**为一个模拟意识生成闭环的系统：真随机生成原始念头 → 记忆影响生成内容 → 情绪影响发言冲动和审查 → 重试引导改进 → 记忆匹配辅助筛选 → 记忆固化 → 自主决定表达（包括沉默时的内心闪过）。它不是现有任何项目的复制品，而是一个全新的组合实验。

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

### 2. Self-Censorship — Simulating the Prefrontal Cortex
The random strings are sent to a **Reviewer** agent, which checks them against what the **Vision Model** is seeing and the current **emotional state**.
- If all of them are nonsense → the **Thinker** tries again. During retries, the tail of the previous best sentence is passed as a "hint" to guide the next generation, making it more directional than pure random sampling.
- If there's a meaningful one → it picks the best
The Reviewer doesn't just check letter overlap with the visual scene. It also checks whether the random sentence contains **real words from the memory bank**. Learned bigram weights are persisted to disk, so they survive restarts — no more "goldfish memory."

### 3. Emotion Model — Simulating Internal States
I built a three-dimensional emotion system:
- **Energy**: When tired, it prefers silence; rest restores it
- **Curiosity**: When curious, it asks more questions and interrupts more often
- **Pleasure**: When happy, it's more forgiving; when unhappy, it's pickier
Emotions decay naturally over time and are also affected by events. Emotions not only influence the Reviewer's scoring but also directly affect the impulse to speak — high curiosity makes speech more likely, low energy tilts toward silence. Emotions are saved on shutdown and continue evolving on the next startup.

### 4. Vision Perception — Input from the Environment
I connected it to multimodal models like GPT or GLM as its "eyes." The model describes what it sees in under 15 words, and that description goes to the Reviewer. The environment shapes its thoughts, just like we rely on our senses to know what to say.

### 5. Memory System — Forgetting and Consolidation
I built a three-layer memory system, inspired by the hippocampus and cortex:
- **Short-term** – cleared daily (like a phone number you just looked up)
- **Long-term** – cleared yearly (like a formula you learned but might forget)
- **Permanent** – never forgotten (like your own name)
If a short-term memory is recalled 5 times in one day, it upgrades to long-term. If a long-term memory is recalled 7 times in one year, it becomes permanent.

**Persistent Memory**: All memories are stored in a SQLite database on disk, surviving shutdowns and restarts.

**Memory-Influenced Kernel**: When the Thinker generates random thoughts, there's a chance it will pull **whole word fragments** (2-6 characters) directly from the memory bank. Memory is no longer just a passive warehouse — it genuinely participates in idea generation.

### 6. Local Fallback — Speaking Even When Offline
The LLM (GLM-4.7-Flash) is its "main voice channel," but if the API is unavailable, built-in fallback responses take over, adjusted by current mood.

### 7. Silent Inner Murmur
When the kernel decides not to speak, it still generates a brief thought ("inner murmur") for Reviewer judgment. If meaningful, it's appended (e.g., "inner murmur: meow"). If meaningless, it's silently discarded — and being rejected doesn't lower the speak threshold, avoiding the counterintuitive "the more you're shut down, the more you want to speak" logic.

---

## 🧱 Module Overview
| File | Function |
|------|----------|
| `randomness.py` | Extracts true random numbers from OS entropy pool |
| `memory.py` | Three-layer memory system (SQLite persistence, auto-upgrade) |
| `emotion.py` | Emotion model (energy/curiosity/pleasure, time decay, state saving) |
| `vision.py` | Vision model (simulated text / real image multimodal) |
| `thinker.py` | Thinker, whole-word insertion and retry hint guidance |
| `reviewer.py` | Reviewer, mood and memory-matching scoring, persisted bigram weights |
| `language_model.py` | LLM shell + local fallback output |
| `main.py` | Main system, emotion-driven speak impulse, silent rejection doesn't lower threshold |

---

## ⚙️ Quick Start
1. Clone this repo
2. Install dependencies: `pip install zhipuai`
3. Get a free API Key from [ZhipuAI Open Platform](https://open.bigmodel.cn/)
4. Put your Key in `config.py`
5. Run: `python main.py`

---

## 🔄 Self-Optimization Mechanisms
1. **Emotion-driven speak impulse**: High curiosity increases speech likelihood, low energy favors silence
2. **Retry hint guidance**: Failed reviews pass the best sentence tail as a hint for smarter regeneration
3. **Dynamic speak threshold**: Speaks more when saying good things, goes silent when saying nonsense; rejected murmurs don't affect it
4. **Whole-word memory insertion**: Kernel output occasionally contains complete words from memory
5. **Memory-matching review**: Reviewer checks both letter overlap and memory content
6. **Persistent reviewer learning**: Bigram weights saved to disk, surviving restarts
7. **Feature self-updating**: Concept understanding refines with each observation
8. **Curiosity-driven questioning**: Actively asks about repeatedly unfamiliar things
9. **Emotion evolution**: Energy, curiosity, pleasure change over time
10. **State persistence**: Memories and emotions survive shutdowns
11. **Local fallback**: Outputs even when API is unavailable
12. **Silent inner murmur**: Kernel thoughts persist even when silent, appear if meaningful

---

## 📌 A Note on the Code
I built this project through pair programming with DeepSeek — I came up with the ideas and architecture, and DeepSeek helped me write the code.
The code might be rough (I'm only in 6th grade and don't have money for premium tools), but I hope the idea itself is interesting. Feel free to ignore my code and just use the concept as inspiration.

---

## 🔬 How This Differs From Existing Projects
Entropy Sprite is **the first to organically combine** true random thought generation, memory-influenced content, emotion-driven speak impulse and review, retry hint guidance, memory-matching filtering, memory consolidation, and autonomous expression (including silent inner murmurs) into a single closed-loop consciousness simulation system.

---

## 📄 License
MIT License