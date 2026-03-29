---
title: "长时运行 agent 的高效 harness（执行框架）"
sourceUrl: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
publishedOn: "2025-11-26"
---

# 长时运行 agent 的高效 harness（执行框架）

agent 在跨越多个 context window 持续工作时，至今仍面临不少挑战。为此，我们借鉴了人类工程师的工作方式，尝试为长时运行 agent 设计一种更有效的 harness（执行框架）。

随着 AI agent 能力持续增强，开发者越来越希望它们承担那些需要连续工作数小时、甚至数天的复杂任务。然而，如何让 agent 在多个 context window 之间稳定、持续地推进工作，仍然是一个尚未解决的问题。

长时运行 agent 的核心难点在于：它们必须以离散会话的方式工作，而每个新会话开始时，都不记得之前发生过什么。你可以把这想象成一个由轮班工程师接力完成的软件项目，但每位新来的工程师都完全不知道上一班发生了什么。由于 context window 有限，而大多数复杂项目又无法在单个 window 内完成，agent 需要一种机制来弥合不同编码会话之间的断层。

我们提出了一套双组件方案，使 [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) 能够跨多个 context window 有效工作：一是 **initializer agent**，负责在第一次运行时搭建环境；二是 **coding agent**，负责在每个会话中持续做出增量进展，同时为下一个会话留下清晰的工作痕迹。相应代码示例见配套的 [quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)。

## 长时运行 agent 问题

Claude Agent SDK 是一个强大且通用的 agent harness，既擅长编程，也适合处理那些需要模型调用工具来收集上下文、规划并执行的任务。它具备诸如 compaction 之类的上下文管理能力，使 agent 能在不耗尽 context window 的前提下持续处理任务。从理论上说，在这样的设定下，agent 应该可以在任意长时间内持续做有价值的工作。

但 compaction 并不足够。开箱即用时，即便是像 Opus 4.5 这样的前沿编程模型，在 Claude Agent SDK 上跨多个 context window 循环运行，如果只收到一个高层级提示，例如“构建一个 [claude.ai](http://claude.ai) 的克隆”，仍然不足以做出一个达到生产质量的 Web 应用。

Claude 的失败主要表现为两种模式。第一，agent 往往试图一次做太多事——本质上是在尝试一把把整个应用做完。这常常导致模型在实现过程中耗尽上下文，于是下一个会话开始时，只能接手一个功能做到一半、且没有文档记录的状态。后续 agent 不得不猜测之前发生了什么，并花费大量时间重新把基础应用修回可运行状态。即使有 compaction，这种情况依然会发生，因为 compaction 并不总能向下一个 agent 传递足够清晰的指令。

第二种失败模式则往往出现在项目后期。当一些功能已经完成后，后续某个 agent 实例会四下查看，发现项目似乎已有进展，于是直接宣告任务完成。

这意味着问题可以拆成两个部分。首先，我们需要搭建一个初始环境，为某个提示所要求的 *全部* 功能打好基础，让 agent 能按步骤、按功能逐项推进。其次，我们应该提示每个 agent 在朝目标做出增量进展的同时，在会话结束时让环境保持在一个“干净状态（clean state）”。这里所谓“干净状态”，指的是那种可以直接合并进主分支的代码状态：没有明显 bug，代码结构清晰、文档完备；总体而言，开发者可以很容易从这个状态开始开发新功能，而不必先清理一堆无关的遗留问题。

在内部实验中，我们通过一个双组件方案来解决这些问题：

1. Initializer agent：第一个 agent 会话会使用一套专门的提示，要求模型完成初始环境搭建，包括编写 `init.sh` 脚本、创建用于记录 agent 行为日志的 `claude-progress.txt` 文件，以及生成一个初始 git commit，用来展示新增了哪些文件。
2. Coding agent：之后的每个会话都要求模型做出增量进展，并留下结构化更新。<sup>1</sup>

这里的关键洞见是：必须让 agent 在拿到全新 context window 后，仍然能够快速理解当前工作状态。实现这一点的关键，就是 `claude-progress.txt` 文件与 git 历史的配合。这些做法的灵感来自我们对高效软件工程师日常工作方式的观察。

## 环境管理

在更新后的 [Claude 4 prompting guide](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#multi-context-window-workflows) 中，我们分享了多 context window 工作流的一些最佳实践，其中包括一种 harness 结构：在“第一个 context window 中使用不同的提示”。这个“不同的提示”要求 initializer agent 搭建好环境，并把未来 coding agent 高效工作所需的所有上下文准备齐全。下面，我们更深入地展开说明，这类环境中的几个关键组件分别是什么。

### 功能清单

为了避免 agent 试图一次性做完整个应用，或者过早认定项目已经完成，我们要求 initializer agent 写出一份全面的功能需求文件，把用户最初的提示扩展成一组具体功能。在 [claude.ai](http://claude.ai) 克隆这个例子里，这意味着要列出 200 多项功能，比如“用户可以打开一个新聊天、输入查询、按下回车，并看到 AI 回复”。这些功能在一开始都会被标记为“failing”，这样后续 coding agent 就能清楚知道“完整功能”到底应该是什么样子。

```json
{
    "category": "functional",
    "description": "New chat button creates a fresh conversation",
    "steps": [
      "Navigate to main interface",
      "Click the 'New Chat' button",
      "Verify a new conversation is created",
      "Check that chat area shows welcome state",
      "Verify conversation appears in sidebar"
    ],
    "passes": false
  }
```

我们要求 coding agent 编辑这个文件时，只能修改 `passes` 字段的状态；同时还会用很强硬的措辞提示它，例如：“删除或修改测试是不可接受的，因为这可能导致功能缺失或留下 bug。” 经过一些实验后，我们最终选择用 JSON 来承载这类信息，因为与 Markdown 文件相比，模型不太会不恰当地改动或覆盖 JSON 文件。

### 增量推进

在有了这套初始环境脚手架之后，下一版 coding agent 就只被要求一次处理一个功能。事实证明，这种增量式方法对于抑制 agent “一口气做太多”的倾向至关重要。

但即便改成增量推进，模型在做出代码修改后，仍然必须把环境留在一个干净状态。在实验中，我们发现，最有效的诱导方式是要求模型把进展提交到 git，并使用具有描述性的 commit message，同时把本轮进展写入进度文件。这样一来，模型就能借助 git 回滚错误的代码修改，并恢复到代码库之前可工作的状态。

这些做法还提高了效率，因为 agent 不再需要花时间猜测先前发生了什么，也不用再把时间浪费在重新修复基础应用上。

### 测试

我们观察到的最后一种主要失败模式，是 Claude 倾向于在没有充分测试的情况下就把某个功能标记为完成。若没有明确提示，Claude 虽然往往会做代码修改，也会通过单元测试或对开发服务器执行 `curl` 命令来做一些测试，但它往往意识不到该功能其实并没有以端到端方式真正跑通。

在构建 Web 应用这个场景下，一旦明确提示 Claude 使用浏览器自动化工具，并像真实用户那样完成全部测试，它在端到端验证功能方面的表现通常就会明显改善。

![Claude 通过 Puppeteer MCP server 测试 claude.ai 克隆时截取的截图。](https://cdn.sanity.io/images/4zrzovbb/website/f94c2257964fb2d623f1e81f874977ebfc0986bc-1920x1080.gif)

Claude 通过 Puppeteer MCP server 测试 claude.ai 克隆时截取的截图。

给 Claude 配备这类测试工具后，性能显著提升，因为 agent 能发现并修复那些仅从代码本身并不容易看出的 bug。

当然，一些问题仍然存在，例如 Claude 的视觉能力存在局限，浏览器自动化工具本身也难以识别所有类型的 bug。举例来说，Claude 无法通过 Puppeteer MCP 看见浏览器原生的 alert 模态框，因此依赖这些模态框的功能往往更容易出错。

## 快速进入状态

在以上这些机制都就位后，每个 coding agent 在开始工作时，都会被提示先执行一组步骤，以便快速摸清当前状态。虽然其中有些步骤很基础，但仍然非常有帮助：

1. *运行 **`pwd`**，确认你当前所在的工作目录。你只能编辑这个目录中的文件。*
2. *阅读 git 日志和进度文件，快速了解最近做了哪些工作。*
3. *阅读功能清单文件，并选择尚未完成、优先级最高的功能开始处理。*

这种做法还能为 Claude 节省一些 token，因为它不必在每个会话里重新摸索该如何测试代码。另一个有帮助的做法，是让 initializer agent 写一个能够启动开发服务器的 `init.sh` 脚本，然后在实现新功能之前，先运行一轮基础的端到端测试。

在 claude.ai 克隆这个例子里，这意味着 agent 每次都会先启动本地开发服务器，再借助 Puppeteer MCP 新建一条聊天、发送一条消息，并接收一个回复。这样一来，Claude 就能迅速发现应用是否被留在了损坏状态，并立即修复已有 bug。相反，如果 agent 一上来就实现新功能，问题很可能只会变得更严重。

综合以上设计，一个典型会话通常会以下面的 assistant 消息开场：

```
[Assistant] 我会先确认当前项目状态，弄清楚我现在面对的是什么。
[Tool Use] <bash - pwd>
[Tool Use] <read - claude-progress.txt>
[Tool Use] <read - feature_list.json>
[Assistant] 接下来我看一下 git log，了解最近的工作内容。
[Tool Use] <bash - git log --oneline -20>
[Assistant] 现在我检查一下是否存在可用于重启服务的 init.sh 脚本。
<启动开发服务器>
[Assistant] 很好。现在我去打开应用，并验证一些基础功能是否仍然正常。
<测试基础功能>
[Assistant] 根据我的验证测试，基础功能运行正常。核心聊天功能、主题切换、会话加载和错误处理都工作良好。接下来我会更全面地查看 tests.json 文件，以了解下一步应该实现什么。
<开始处理一个新功能>
```

**Agent 的失败模式与解决方案**

| **Problem** | **Initializer Agent Behavior** | **Coding Agent Behavior** |
| --- | --- | --- |
| Claude 过早宣告整个项目已经完成。 | 建立功能清单文件：根据输入规格，创建一个结构化 JSON 文件，其中列出端到端功能描述。 | 在每次会话开始时读取功能清单文件。选择一个单独功能开始处理。 |
| Claude 离开时让环境处于带 bug 或进展未文档化的状态。 | 写入初始 git 仓库和进度记录文件。 | 会话开始时先读取进度记录文件和 git commit 日志，并对开发服务器执行一次基础测试，以发现未记录的 bug。会话结束时写入 git commit 和进度更新。 |
| Claude 过早把功能标记为已完成。 | 建立功能清单文件。 | 对所有功能进行自验证。只有在充分测试后，才将功能标记为 “passing”。 |
| Claude 需要花时间摸索如何运行应用。 | 编写能够启动开发服务器的 `init.sh` 脚本。 | 会话开始时先阅读 `init.sh`。 |

对长时运行 AI agent 的四种常见失败模式及对应解法的总结。

## 未来工作

这项研究展示了长时运行 agent harness 中一种可行的解决方案组合，使模型能够跨多个 context window 持续做出增量进展。不过，仍然存在不少开放问题。

最值得注意的是，目前仍不清楚：在跨上下文工作时，是单个通用 coding agent 表现最佳，还是多 agent 架构能够取得更好的效果。看起来很合理的一点是，像 testing agent、质量保障 agent，或者专门负责代码清理的 agent 这样的专用角色，可能会在软件开发生命周期中的某些子任务上做得更好。

此外，这个 demo 当前主要针对全栈 Web 应用开发做了优化。未来一个重要方向，是把这些发现推广到其他领域。很可能其中部分乃至全部经验，都可以应用到其他需要长时运行 agent 任务的场景中，例如科研或金融建模。

### 致谢

本文由 Justin Young 撰写。特别感谢 David Hershey、Prithvi Rajasakeran、Jeremy Hadfield、Naia Bouscal、Michael Tingley、Jesse Mu、Jake Eaton、Marius Buleandara、Maggie Vo、Pedram Navid、Nadine Yasser 和 Alex Notov 所做出的贡献。

这项工作体现了 Anthropic 多个团队的共同努力，正是他们让 Claude 能够以安全方式执行长时程自主软件工程，尤其是 code RL 与 Claude Code 团队。欢迎有兴趣参与这项工作的候选人前往 [anthropic.com/careers](http://anthropic.com/careers) 申请。

### 脚注

1. 在这里，我们之所以把它们称作不同的 agent，仅仅是因为它们收到的初始用户提示不同。除此之外，system prompt、工具集合以及整体 agent harness 都是相同的。
