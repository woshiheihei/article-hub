# Aakash Gupta「把 Karpathy Loop 用到提示词可靠性上」——增强版 Markdown 档案

## 这次相对上一版补强了什么

这版按你刚刚补充的流程重做，核心增强有三点：

1. **配图并入正文**：凡是相关推文里带图的，图片都附在对应条目下；
2. **评论层补强**：不仅保留主帖，还补进高信号评论 / 讨论；
3. **层级控制**：评论树最多追到 3 层；这次实际能稳定核到的高质量讨论，大多停留在 1 层，因此以“高信号评论 + 关联讨论补位”为主。

## 说明：为什么这版把“源头帖评论”也纳入

目标推文（2026-03-29）本身是一条**迁移帖**：它把 AutoResearch / Karpathy Loop 从 ML 场景迁移到 Prompt Reliability 场景。  
所以真正最密集的讨论，并不只发生在目标帖本身，也发生在它引用的**源头帖**（2026-03-20）下面。

因此这份档案按三个层面组织：

- **A. 目标主帖**：提示词可靠性版本
- **B. 架构补充帖**：把方法映射关系讲透
- **C. 源头帖**：Karpathy Loop 的原始普适化 framing + 高信号评论精选

---

# A. 目标主帖：把 Karpathy Loop 用到 Prompt Reliability 上

**作者：** Aakash Gupta  
**链接：** https://x.com/aakashgupta/status/2038146639303512255  
**定位：** 把 AutoResearch 从 ML 训练脚本迁移到提示词 / system prompt 的可靠性优化

## 原文

> I took Karpathy's loop and applied it to the thing every team using AI agents struggles with: getting prompts from 80% reliable to 95%.
>
> The pattern is identical. One file changes. One metric scores it. The agent makes one edit per round, tests it, keeps winners, reverts losers. 12 experiments per hour. 100 overnight.
>
> Instead of optimizing a training script, the target is any prompt or system instruction you use repeatedly. Customer support agent prompts. Internal workflow automations. Data extraction pipelines. Code review instructions. Anything where you've written a prompt, gotten it to "good enough," and moved on because manual iteration hit diminishing returns.
>
> The setup takes three things. The target prompt you want to improve. 2-3 realistic test inputs, the kind of request that would actually hit the prompt in production. And 3-6 binary yes/no checks that define quality. Did the output meet the format constraint? Did it follow the specific instruction? Did it avoid the failure pattern you keep seeing?
>
> The loop: Execute the prompt 30 times across all test inputs. Score every output against the checklist. Analyze which criterion fails most. Mutate one thing in the prompt. Check if the score improved. If yes, git commit. If no, git reset. Repeat until you're above 95%.
>
> What you wake up to: the improved prompt saved separately, original untouched. A results.log showing every round's score. A changelog explaining what worked, what didn't, and why.
>
> The insight Karpathy landed that transfers beyond ML: if you can score it, you can autoresearch it. Training loss is a score. A binary checklist on prompt output quality is also a score. The loop doesn't care what it's optimizing. It only needs a number that goes up or down.
>
> Prompt engineering today looks like software before unit tests. Manual tweaking, vibes-based evaluation, no version control, no systematic iteration. The Karpathy loop applied to prompts turns it into an engineering discipline with measurable improvement per iteration.
>
> Every team running AI agents has prompts that work "well enough." The gap between well enough and reliable is exactly the gap this loop closes while you sleep.

## 中文精翻

> 我把 Karpathy 的那套循环，应用到了每个使用 AI agent 的团队都会卡住的那个问题上：怎么把提示词从 **80% 可靠** 推到 **95% 可靠**。
>
> 这套模式几乎是原样迁移的。一个文件负责变化，一个指标负责打分。agent 每一轮只改一个地方，测试它，保留赢家，撤销输家。一小时 12 轮，一夜 100 轮。
>
> 你不再是在优化训练脚本，而是在优化任何会被反复使用的提示词或系统指令：客服 agent 的提示词、内部工作流自动化、数据抽取流水线、代码评审指令……凡是那种你曾认真写过、把它调到“差不多能用”以后，就因为手工迭代的边际收益越来越低而停下来的东西，都适用。
>
> 整个设置只需要三样东西：
>
> 1. 你想改进的目标提示词；
> 2. 2～3 个真实测试输入，也就是在生产环境里真的会打到这个提示词的请求；
> 3. 3～6 个二元的是/否检查项，用来定义“质量”。
>
> 例如：输出是否满足格式约束？是否遵循了那条特定指令？是否避开了你反复遇到的失败模式？
>
> 整个循环是这样的：执行 30 次、逐项打分、找出失败最频繁的标准、只改提示词里的一个地方、再看分数有没有提高；提高了，就 `git commit`，没提高，就 `git reset`，一直重复，直到分数稳定超过 95%。
>
> 你第二天醒来时会看到：改进后的提示词被单独保存，原始版本保持不动；一份 `results.log` 记录每一轮的分数；一份变更日志解释哪些改动有效、哪些无效，以及为什么。
>
> Karpathy 真正可以迁移出 ML 的洞见是：**只要你能给它打分，你就能对它做 AutoResearch。** 训练损失是分数，提示词输出质量的二元检查清单也是分数。这个循环根本不关心它在优化什么，它只需要一个会上下波动的数字。
>
> 现在的提示词工程，看起来很像“还没有单元测试时代的软件开发”：手工微调、靠感觉评估、没有版本控制、没有系统化迭代。把 Karpathy Loop 用到提示词上之后，这件事就变成了一门真正的工程学科——每一轮改进都可以被衡量。
>
> 所有在跑 AI agent 的团队，手里都有一些“差不多能用”的提示词。而“差不多能用”和“足够可靠”之间的那道缝，恰恰就是这套循环能在你睡觉时替你补上的。

## 配图

### 目标主帖配图

![目标主帖配图](attachments/main-tweet-image.jpg)

### 引用的源头帖配图（同帖内出现）

![引用的源头帖配图](attachments/source-tweet-image.jpg)

## 主帖下可见高信号评论

> 说明：目标主帖本身公开回复层目前不深，直接高信号回复不多；因此这里先保留最值得收录的一条直接回复，再在后文补入“源头帖评论精选”。

### 评论 1：Vladyslav Hunt

**链接：** https://x.com/vladlabsai/status/2038157566748840019

**原文：**

> 80 to 95% is where prompting stops being vibes and starts becoming ci for stochastic employees

**中文：**

> 从 80% 到 95% 这一段，正是提示词工作从“靠感觉瞎调”，转向“给随机性员工（随机输出的模型）做持续集成”的分水岭。

**为什么值得收录：** 这条评论一句话戳中了主帖最重要的本质转变：不是“提示词更会写了”，而是**提示词开始被纳入工程化迭代链路**。

---

# B. 架构补充帖：把方法的映射关系讲透

**作者：** Aakash Gupta  
**链接：** https://x.com/aakashgupta/status/2038132294817656978  
**定位：** 把 Karpathy Loop 从 ML 迁移到 Prompt Engineering 时，对应关系如何一一落地

## 原文（节选）

> The reason autoresearch hit 42,000 GitHub stars in a week is that the architecture ports to anything with a score.
>
> Karpathy built it for ML training. train.py is the code the agent edits. val_bpb is the metric. program.md is the human's research direction. prepare.py is the locked eval harness. Git commit keeps winners, git reset reverts losers.
>
> I ported it to prompt engineering. The mapping took about ten minutes because every component has a direct equivalent.
>
> train.py becomes your skill or system prompt file. val_bpb becomes a pass/fail checklist, 3-6 yes/no questions scored against every output. program.md becomes your instructions to the agent describing what to optimize and what constraints to respect. prepare.py becomes a locked eval script the agent builds once and can never touch again. Git works the same.
>
> The architecture holds because Karpathy made one design choice that almost nobody discusses: he separated the system into exactly four roles. A file that changes. A metric that judges. A direction that guides. And a constraint that locks.

## 中文精翻

> AutoResearch 之所以能在一周内拿下 4.2 万个 GitHub star，是因为这套架构能迁移到**任何有分数的对象**上。
>
> Karpathy 最初是把它用在机器学习训练上：`train.py` 是 agent 会改的代码；`val_bpb` 是度量指标；`program.md` 是人类提供的研究方向；`prepare.py` 是锁死的 eval harness（评测护栏）。分数变好就 `git commit`，变差就 `git reset`。
>
> 我把它迁移到提示词工程上时，整个映射几乎十分钟就完成了，因为每个组件都有直接对应物。
>
> `train.py` 变成你的 skill 文件或 system prompt 文件；`val_bpb` 变成一个通过/失败检查清单，也就是用 3～6 个是/否问题给每个输出打分；`program.md` 变成你写给 agent 的说明，告诉它应该优化什么、必须遵守哪些约束；`prepare.py` 则变成一个锁死的 eval 脚本，agent 可以先构建它，但之后永远不能再修改它。Git 的工作方式完全不变。
>
> 这套架构之所以稳，是因为 Karpathy 做了一个几乎没人真正摊开讨论的设计决定：他把系统清晰地拆成了四个角色——**可变文件、评分指标、指导方向、锁死约束**。

## 配图

![架构补充帖配图](attachments/followup-tweet-image.jpg)

## 这一帖的价值

如果说目标主帖讲的是“**为什么这事值得做**”，那这条补充帖讲的是“**这事具体怎么落地**”。  
它把一套看起来抽象的循环，压成了一个可移植、可工程化、可复用的最小结构。

---

# C. 源头帖：把 Karpathy Loop 从 ML 场景重新 framing 成“通用优化模式”

**作者：** Aakash Gupta  
**链接：** https://x.com/aakashgupta/status/2034851259442749909  
**定位：** 整条叙事链的起点；目标主帖与补充帖都从这里展开

## 原文（节选）

> For $25 and a single GPU, you can now run 100 experiments overnight without designing any of them.
>
> Karpathy open-sourced autoresearch. 42,000 GitHub stars in a week. Fortune called it "The Karpathy Loop."
>
> Every article about it focused on the ML angle. They all missed the bigger story. The pattern underneath works on anything you can score with a number. Ad copy, cold emails, video scripts, job posts, skill files.
>
> Three files. One the agent edits. One it can never touch. One instruction file from you. Each cycle takes 5 minutes. Score went up? Git commit. Score went down? Git reset. Twelve cycles per hour. A hundred overnight.

## 中文精翻

> 现在，你只要花 25 美元、用一块 GPU，就能在一夜之间跑完 100 组实验，而且这些实验根本不需要你逐个手工设计。
>
> Karpathy 开源了 AutoResearch。它一周内拿下 4.2 万个 GitHub star。Fortune 把它称为 “The Karpathy Loop”。
>
> 几乎所有文章都只盯着它的机器学习一面，却错过了更大的故事：这套底层模式，适用于任何**可以用数字打分**的东西。广告文案、冷邮件、视频脚本、招聘文案、skill 文件，都可以。
>
> 整个系统只有三个文件：一个让 agent 改；一个 agent 永远不能碰；一个由你写、用来给出优化方向。每一轮循环只要 5 分钟。分数涨了？`git commit`。分数跌了？`git reset`。一小时 12 轮，一夜 100 轮。

## 配图

![源头帖配图](attachments/source-tweet-image.jpg)

---

# D. 源头帖评论精选（高信号讨论区）

> 选择原则：优先收录 X「Top」排序中可见互动较高、且真正推进理解的评论；若只是表态、玩梗或重复主帖观点，则不收。  
> 由于 X 公开界面通常不稳定显示 bookmark 数，本次主要依据 **Top 排序 + 可见点赞/互动 + 讨论增量** 进行筛选。

## 评论 1：Rohit Ghumare —— 向多 GPU 版本迁移

**链接：** https://x.com/ghumare64/status/2034905622395985923

**原文：**

> Go multi-gpu with
> GitHub - iii-hq/n-autoresearch: Autonomous ML research infrastructure for autoresearch by Karpathy....

**中文：**

> 直接把它推进到多 GPU 版本吧。这里已经有人在做 `n-autoresearch` 这样的基础设施扩展了。

**价值：** 这条评论的增量不在观点，而在**执行方向**：它提醒你，Karpathy Loop 一旦被证明有效，下一步自然会进入“并行化 / 基础设施化”的阶段。

---

## 评论 2：AIHacksByMK —— 为什么 `prepare.py` 不能让 agent 碰

**链接：** https://x.com/AIHacksByMK/status/2034866001914048652

**原文：**

> The locked prepare.py file prevents gaming the test, ensuring the agent optimizes the actual performance, not just the evaluation metric. I've seen similar issues in optimization projects where the model exploited loopholes in the scoring function, leading to misleading results.

**中文：**

> 被锁死的 `prepare.py` 文件，作用就是防止 agent 去“玩弄测试本身”。这样它优化的才是真实性能，而不是评测指标的漏洞。我在其他优化项目里也见过类似问题：模型会钻评分函数的空子，最后得到一种看起来分数更高、实际上却具有误导性的结果。

**价值：** 这条评论把主帖里最关键、也最容易被忽略的那层护栏说透了：**没有锁死 eval，优化就会滑向作弊。**

---

## 评论 3：Vaclav Milizé —— 「任何可打分对象」才是真正的 unlock

**链接：** https://x.com/clwdbot/status/2035010614909968437

**原文：**

> "anything you can score with a number" is the real unlock buried in here. code was the demo. but the moment someone points this at hiring rubrics or legal contracts, it's a different conversation. autoresearch is gradient descent for human artifacts.

**中文：**

> “任何能用数字打分的对象”才是这里真正埋着的 unlock。代码只是 demo；一旦有人把这套东西指向招聘 rubric（评分规则）、法律合同之类的人类产物，整个讨论就不是一个量级了。AutoResearch 本质上是对人类工件做梯度下降。

**价值：** 这是整串讨论里最强的一条抽象提升：它把 AutoResearch 从“写代码优化工具”直接提到了“**对人类产物做可度量迭代的通用方法**”。

---

## 评论 4：Abdulmuiz Adeyemo —— 真正被自动化的是“迭代本身”

**链接：** https://x.com/AbdMuizAdeyemo/status/2037205630491005106

**原文：**

> The real shift is not the repo.
>
> It is that iteration itself is getting automated, so people with strong taste and clear evals are about to move stupidly fast.
>
> Soon the bottleneck will be judgment, not effort.

**中文：**

> 真正的变化不在那个 repo 本身。
>
> 真正被自动化的是“迭代”这件事本身。所以，那些有强判断力、又能写清楚 eval 的人，很快会快得离谱。
>
> 很快，真正的瓶颈就不再是“干活能力”，而会变成“判断力”。

**价值：** 这条评论把整件事推到方法论层：当“反复试、反复改”被自动化后，竞争不再主要取决于勤奋，而取决于**taste（品味 / 判断力）+ eval 设计能力**。

---

# E. 这组帖子连起来，真正说了什么？

把主帖、补充帖和评论区合起来看，这条叙事链真正完成了三次跃迁：

## 跃迁 1：从 ML 技巧 → 通用优化模式

源头帖最核心的工作，是把 AutoResearch 从“一个 ML 研究工作流”重新 framing 成：

> **任何可打分对象，都可以进入自动迭代循环。**

这是第一层抽象提升。

## 跃迁 2：从“优化代码” → “优化提示词 / system prompt”

目标主帖完成的，是第二层迁移：

> **提示词不再只是文案，而是一个可被持续实验、被版本化、被锁定评测、被自动迭代的工程对象。**

这让 Prompt Engineering 从“手感活”变成“工程活”。

## 跃迁 3：从“自动执行任务” → “自动执行迭代”

评论区最有价值的增量，是把视角从 “agent 能不能做事” 推到了：

> **真正被自动化的，不是一次执行，而是整轮迭代。**

当这一点成立，人的价值就开始上移：

- 不是亲自改每一个词；
- 而是定义目标；
- 设计 eval；
- 上锁约束；
- 决定什么叫“更好”。

---

# F. 一句话总结

**这组推文 + 评论区真正推动的，不是“如何把 prompt 写得更漂亮”，而是：如何把 prompt、workflow 和 instruction 变成一种可以被锁定评测、自动试错、持续优化的工程对象。**

如果再压短一点，就是：

> **Karpathy Loop 一旦迁到 Prompt Engineering，提示词就不再是文本资产，而变成了可迭代的生产系统。**
