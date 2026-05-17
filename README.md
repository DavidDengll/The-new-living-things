# 熵灵 (Entropy Sprite)

> 一个由**真随机**驱动的实验性意识模拟系统。
> 它不是普通的聊天程序，而是一个拥有“内核冲动”与“外部语言”的双层心智模型。

## 👤 关于我
我是一名六年级学生。因为对意识和随机性感到好奇，我开始动手创造了熵灵。

---

## 🧠 我的设计思路

### 1. 真随机驱动
我用操作系统硬件熵（或者量子随机数）来决定：
- 要不要“说话”
- 说几句话
- 每句话多长
然后通过随机 ASCII 码生成最原始的“念头”。它无时无刻都在随机——就跟大脑里的噪声一样。

### 2. 自我审查
生成的乱码会交给一个叫**审核官**的 Agent，让它结合**视觉模型**看到的场景，判断这些话有没有意义。
- 如果全是废话 → 让**思考者**重新想，直到想出有意义的话为止
- 如果有意义 → 排个序，挑最好的那句

### 3. 视觉感知
我用 GPT 或 GLM 等多模态模型作为它的“眼睛”。看到画面后，用不超过 15 个字简短描述，再交给审核官做判断。

### 4. 记忆系统
我给熵灵做了三层记忆：
- **短期记忆**：一天删一次
- **长期记忆**：一年删一次
- **永久记忆**：永远不删
如果短期记忆在一天内被连续提了 5 次，就升级为长期；长期记忆在一年内被提了 7 次，就升级为永久。这些数字都可以自己调。

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

## 🧠 How I Designed It

### 1. True Randomness Engine
I used hardware entropy from the OS (or quantum random numbers) to decide:
- Whether to "speak"
- How many sentences to say
- How long each sentence is
Then raw "thoughts" are generated from random ASCII characters. It's always random, just like neural noise in our brains.

### 2. Self-Censorship
The random strings are sent to a **Reviewer** agent, which checks them against what the **Vision Model** is seeing.
- If all of them are nonsense → the **Thinker** tries again until something meaningful comes out
- If there's a meaningful one → it picks the best

### 3. Vision Perception
I connected it to multimodal models like GPT or GLM as its "eyes." The model describes what it sees in under 15 words, and that description goes to the Reviewer.

### 4. Memory System
I built a three-layer memory system, like human memory:
- **Short-term** – cleared daily
- **Long-term** – cleared yearly
- **Permanent** – never forgotten
If a short-term memory is recalled 5 times in one day, it upgrades to long-term. If a long-term memory is recalled 7 times in one year, it becomes permanent. All the numbers are adjustable.

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