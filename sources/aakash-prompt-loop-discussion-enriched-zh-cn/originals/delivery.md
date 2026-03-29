# Aakash Gupta：把 Karpathy Loop 用到提示词可靠性上

## 主帖

**作者：** Aakash Gupta  
**时间：** 2026-03-29 14:50  
**链接：** https://x.com/aakashgupta/status/2038146639303512255

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
> Karpathy 真正可以迁移出 ML 的洞见是：**只要你能给它打分，你就能对它做 AutoResearch。** 训练损失是分数，提示词输出质量的二元检查清单也是分数。这个循环根本不关心它在优化什么，它只需要一个会上下波动的数字。
>
> 现在的提示词工程，看起来很像“还没有单元测试时代的软件开发”：手工微调、靠感觉评估、没有版本控制、没有系统化迭代。把 Karpathy Loop 用到提示词上之后，这件事就变成了一门真正的工程学科——每一轮改进都可以被衡量。

![目标主帖配图](attachments/main-tweet-image.jpg)

### 主帖评论精选

#### Vladyslav Hunt · 2026-03-29 15:33

> 80 to 95% is where prompting stops being vibes and starts becoming ci for stochastic employees

中文：

> 从 80% 到 95% 这一段，正是提示词工作从“靠感觉瞎调”，转向“给随机性员工做持续集成”的分水岭。

#### Mia · 2026-03-29 16:02

> this is exactly the gap most teams hit. getting something to work 80% of the time is the easy bit — that last 15% is where projects go to die. the iterative score-and-revert loop is so much more practical than trying to engineer perfect prompts upfront

中文：

> 这正是大多数团队都会撞上的那道坎。把东西做到 80% 能用，其实是容易的；最后那 15%，才是项目真正容易死掉的地方。相比一开始就想把 prompt 一次性设计到完美，这种“评分—回滚—继续迭代”的循环要现实得多。

---

## 补充帖

**作者：** Aakash Gupta  
**时间：** 2026-03-29 13:53  
**链接：** https://x.com/aakashgupta/status/2038132294817656978

> AutoResearch 之所以能在一周内拿下 4.2 万个 GitHub star，是因为这套架构能迁移到**任何有分数的对象**上。
>
> Karpathy 最初是把它用在机器学习训练上：`train.py` 是 agent 会改的代码；`val_bpb` 是度量指标；`program.md` 是人类提供的研究方向；`prepare.py` 是锁死的 eval harness（评测护栏）。分数变好就 `git commit`，变差就 `git reset`。
>
> 我把它迁移到提示词工程上时，整个映射几乎十分钟就完成了，因为每个组件都有直接对应物。
>
> `train.py` 变成你的 skill 文件或 system prompt 文件；`val_bpb` 变成一个通过/失败检查清单，也就是用 3～6 个是/否问题给每个输出打分；`program.md` 变成你写给 agent 的说明，告诉它应该优化什么、必须遵守哪些约束；`prepare.py` 则变成一个锁死的 eval 脚本，agent 可以先构建它，但之后永远不能再修改它。Git 的工作方式完全不变。
>
> 这套架构之所以稳，是因为 Karpathy 做了一个几乎没人真正摊开讨论的设计决定：他把系统清晰地拆成了四个角色——**可变文件、评分指标、指导方向、锁死约束**。

![补充帖配图](attachments/followup-tweet-image.jpg)

### 补充帖评论精选

#### ImL1s · 2026-03-29 14:10

> What's powerful here is the separation of concerns: humans define the direction, agents run the experiments. That's a much more sustainable research loop than trying to automate everything end-to-end. The "score as the universal interface" insight is what makes it generalizable.

中文：

> 这里真正强的地方，是把职责清楚拆开了：人来定义方向，agent 来跑实验。相比试图把一切都端到端自动化，这是一种更可持续的研究循环。真正让它具有普适性的，是“分数作为通用接口”这个洞见。

#### Annabell Schaefer · 2026-03-29 15:34

> 3-6 criteria can be enough, but might get quickly exploited by autoresearch if not exhaustive.

中文：

> 3～6 个标准可能已经够用了，但如果这些标准不够完整，AutoResearch 也会很快开始钻空子。

---

## 源头帖

**作者：** Aakash Gupta  
**时间：** 2026-03-20 12:35  
**链接：** https://x.com/aakashgupta/status/2034851259442749909

> 现在，你只要花 25 美元、用一块 GPU，就能在一夜之间跑完 100 组实验，而且这些实验根本不需要你逐个手工设计。
>
> Karpathy 开源了 AutoResearch。它一周内拿下 4.2 万个 GitHub star。Fortune 把它称为 “The Karpathy Loop”。
>
> 几乎所有文章都只盯着它的机器学习一面，却错过了更大的故事：这套底层模式，适用于任何**可以用数字打分**的东西。广告文案、冷邮件、视频脚本、招聘文案、skill 文件，都可以。
>
> 整个系统只有三个文件：一个让 agent 改；一个 agent 永远不能碰；一个由你写、用来给出优化方向。每一轮循环只要 5 分钟。分数涨了？`git commit`。分数跌了？`git reset`。一小时 12 轮，一夜 100 轮。

![源头帖配图](attachments/source-tweet-image.jpg)

### 源头帖评论精选

#### Rohit Ghumare · 2026-03-20 16:11

> Go multi-gpu with GitHub - iii-hq/n-autoresearch...

中文：

> 直接把它推进到多 GPU 版本吧。这里已经有人在做 `n-autoresearch` 这样的基础设施扩展了。

#### AIHacksByMK · 2026-03-20 13:33

> The locked `prepare.py` file prevents gaming the test, ensuring the agent optimizes the actual performance, not just the evaluation metric.

中文：

> 被锁死的 `prepare.py` 文件，作用就是防止 agent 去玩弄测试本身。这样它优化的才是真实性能，而不是评测指标的漏洞。

#### Vaclav Milizé · 2026-03-20 23:08

> "anything you can score with a number" is the real unlock buried in here. code was the demo. but the moment someone points this at hiring rubrics or legal contracts, it's a different conversation. autoresearch is gradient descent for human artifacts.

中文：

> “任何能用数字打分的对象”才是真正埋着的 unlock。代码只是 demo；一旦有人把这套东西指向招聘 rubric、法律合同之类的人类产物，整个讨论就不是一个量级了。AutoResearch 本质上是对人类工件做梯度下降。

#### Abdulmuiz Adeyemo · 2026-03-27 00:30

> The real shift is not the repo. It is that iteration itself is getting automated... Soon the bottleneck will be judgment, not effort.

中文：

> 真正的变化不在那个 repo 本身。真正被自动化的是“迭代”这件事本身。很快，真正的瓶颈就不再是干活能力，而会变成判断力。

---

## 方法论总结

### 跃迁 1：从 ML 技巧到通用优化模式

> **任何可打分对象，都可以进入自动迭代循环。**

### 跃迁 2：从优化代码到优化提示词 / system prompt

> **提示词不再只是文案，而是一个可被持续实验、可版本化、可锁定评测、可自动迭代的工程对象。**

### 跃迁 3：从自动执行任务到自动执行迭代

> **真正被自动化的，不是一次执行，而是整轮迭代。**

## 一句话总结

> **Karpathy Loop 一旦迁到 Prompt Engineering，提示词就不再是文本资产，而变成了可迭代的生产系统。**
