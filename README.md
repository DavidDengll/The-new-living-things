# 熵灵 (Entropy Sprite)

> 一个由**真随机**驱动的实验性意识模拟系统。
> 它不是普通的聊天程序，而是一个拥有“内核冲动”与“外部语言”的双层心智模型。

## 👤 关于我
我是一名六年级学生。因为对意识和随机性感到好奇，我开始动手创造了熵灵。

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
生成的乱码会交给一个叫**审核官**的 Agent，让它结合**视觉模型**看到的场景，判断这些话有没有意义。
- 如果全是废话 → 让**思考者**重新想，直到想出有意义的话为止
- 如果有意义 → 排个序，挑最好的那句
这就像我们的大脑在说话之前，会先“毙掉”无数不合时宜的念头。

### 3. 视觉感知 — 环境的输入
我用 GPT 或 GLM 等多模态模型作为它的“眼睛”。看到画面后，用不超过 15 个字简短描述，再交给审核官做判断。环境成了它“思考”的依据，就像我们用眼睛看见世界，才知道该说什么。

### 4. 记忆系统 — 遗忘与巩固
我给它做了三层记忆，模仿人脑的海马体和皮层：
- **短期记忆**：一天删一次（像临时记住的电话号码）
- **长期记忆**：一年删一次（像学会的公式，不复习就会忘）
- **永久记忆**：永远不删（像自己的名字，一辈子忘不掉）
如果短期记忆在一天内被连续提了 5 次，就升级为长期；长期记忆在一年内被提了 7 次，就升级为永久。这就跟复习知识一样，反复提及才能记住。

---

## ⚙️ 怎么跑起来
1. 克隆这个仓库
2. 安装依赖：`pip install zhipuai`
3. 去 [智谱AI开放平台](https://open.bigmodel.cn/) 申请免费 API Key
4. 把 Key 填进 `config.py`
5. 运行：`python main.py`

---

## 📌 关于代码
这个项目是我和 AI 结对编程做的——我出想法和架构，AI 帮我写代码。
代码可能写得不太好（我才六年级，也没钱充值），但我觉得这个思路本身有意思。各位大佬可以不看我的代码，把它当做一个灵感参考，自己去实现。

## 📄 许可
MIT License

#English:

# Entropy Sprite

> An experimental consciousness simulation driven by **true randomness**.
> It is not a typical chatbot but a dual-layer mind model with an "inner impulse" and an "outer language."

## 👤 About Me
I'm a 6th-grade student. I built Entropy Sprite because I got curious about consciousness and randomness.

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
The random strings are sent to a **Reviewer** agent, which checks them against what the **Vision Model** is seeing.
- If all of them are nonsense → the **Thinker** tries again until something meaningful comes out
- If there's a meaningful one → it picks the best
This is exactly how our brain silences countless bad ideas before we open our mouth.

### 3. Vision Perception — Input from the Environment
I connected it to multimodal models like GPT or GLM as its "eyes." The model describes what it sees in under 15 words, and that description goes to the Reviewer. The environment shapes its thoughts, just like we rely on our senses to know what to say.

### 4. Memory System — Forgetting and Consolidation
I built a three-layer memory system, inspired by the hippocampus and cortex:
- **Short-term** – cleared daily (like a phone number you just looked up)
- **Long-term** – cleared yearly (like a formula you learned but might forget)
- **Permanent** – never forgotten (like your own name)
If a short-term memory is recalled 5 times in one day, it upgrades to long-term. If a long-term memory is recalled 7 times in one year, it becomes permanent. It's just like studying — you need repetition to truly remember.

---

## ⚙️ How to Run It
1. Clone this repo
2. Install dependencies: `pip install zhipuai`
3. Get a free API Key from [ZhipuAI Open Platform](https://open.bigmodel.cn/)
4. Put your Key in `config.py`
5. Run: `python main.py`

---

## 📌 A Note on the Code
I built this project through pair programming with AI — I came up with the ideas and architecture, and the AI helped me write the code.
The code might be rough (I'm only in 6th grade and don't have money for premium tools), but I hope the idea itself is interesting. Feel free to ignore my code and just use the concept as inspiration.

## 📄 License
MIT License