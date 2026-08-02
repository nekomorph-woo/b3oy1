# bad bad boy1

> 仓库 slug `b3oy1`，读作 **bad bad boy1**。

轻量决策 + 可验证 loop 的工程 skill 集。核心 skill 蒸馏自 [mattpocock/skills](https://github.com/mattpocock/skills)（grill / spec / tickets / seam），封装成两个可即装的 Claude Code 插件。

远端：<https://github.com/nekomorph-woo/b3oy1>

## 一、为什么需要它

### 1. 这是什么

一个 Claude Code 插件市集，内含两个插件：**fiber**（22 个工程 skill）和 **spin**（外围支撑工具）。

核心主张：AI 编码的失败，根因不是模型不够强，而是**错位、冗长、不工作、泥潭化**这四个工程问题没被纪律化地解决。fiber 把这些纪律打包成 skill，让你在真实工程里反复使用，而不是 vibe coding。

### 2. 四个失败模式

| 问题 | 根因 | fiber 的回应 |
|------|------|--------------|
| 代理没做你想要的 | **错位**——你与代理之间有沟通鸿沟 | grill：开工前逐分支追问 |
| 代理过于冗长 | 开发者与领域专家语言不通，代理用 20 词说 1 词 | 共享语言（`CONTEXT.md` + ADR） |
| 代码不工作 | 反馈循环缺失 | 红-绿-重构 TDD + 诊断循环 |
| 代码变成一团泥 | 代理加速编码，也加速软件熵增 | 关心代码设计（deep module） |

共享语言的收益是持续复利。matt 给的例子——同样一个 bug：

- **之前**：「当课程中某个章节被变为 real（即在文件系统中获得位置）时存在问题」
- **之后**：「materialization cascade 存在问题」

这种简洁会在每一次会话里反复省下 token 与误解。

### 3. matt skills 的好处、流程与实践

以下叙事大幅参考 matt 原始 README，因为这套 skill 的灵魂属于他。

#### 3.1 四类问题与对应 skill

**问题 1：代理没做你想要的事**

最常见的软件失败模式是错位。你和代理之间隔着一道沟通鸿沟。解法是 grill——让代理在动手前，沿着决策树每个分支逐个追问你，每问都附上推荐答案。

- `/grill-me`——非代码场景
- `/grill-with-docs`——相同质询，同时构建领域模型，更新 `CONTEXT.md` 和 ADR

**问题 2：代理过于冗长**

开发者与领域专家说不同的语言。代理被丢进项目后只能自己摸索术语，于是用 20 个词表达 1 个词。解法是建立 ubiquitous language——一份帮代理解码项目术语的文档。

- `/domain-modeling`——主动构建并锐化项目领域模型

**问题 3：代码不工作**

哪怕你和代理对「做什么」达成一致，代理仍可能产出坏代码。这时要审视的是**反馈循环**：静态类型、浏览器访问、自动化测试。红-绿-重构是核心。

- `/tdd`——鼓励红-绿-重构，区分好测试与坏测试
- `/diagnosing-bugs`——把最佳调试实践封装成简单循环

**问题 4：代码变成一团泥**

代理极大加速编码，也以前所未有的速度加速软件熵增。解法是采用全新的 AI 驱动开发姿态：**关心代码设计**。

- `/to-spec`——出规范前先问你涉及哪些模块
- `/improve-codebase-architecture`——扫描代码库寻找深化机会，生成 HTML 报告，建议每几天跑一次
- `/codebase-design`——设计深度模块的共享原则与词汇表

#### 3.2 skill 的分类原则

skill 按调用者分两类：

- **用户调用型**：只能手动输入（如 `/grill-me`）触发，负责编排
- **模型调用型**：可手动触发，也可由代理自动触发，封装可复用的纪律

铁律：用户调用型 skill 可以调用模型调用型，但绝不会调用另一个用户调用型。这让编排层与纪律层保持干净分层。

#### 3.3 一段典型工作流

从想法到上线，一次完整的 fiber 流程长这样：

```
grill-with-docs  →  to-spec  →  to-tickets  →  implement  →  code-review
   (对齐决策)       (拆模块)     (tracer-bullet)   (TDD 落地)     (双轴审查)
```

1. `/grill-with-docs`——逐分支追问，把模糊需求逼成明确决策，同时沉淀 `CONTEXT.md`
2. `/to-spec`——把对齐后的对话转成规范，明确涉及哪些模块
3. `/to-tickets`——把规范拆成 tracer-bullet 式票据，先打通端到端骨架
4. `/implement`——按票据红-绿-重构地落地
5. `/code-review`——沿「标准」与「规范」双轴审查变更

每一步都有可验证的产物落盘，下一步读上一步的输出——这就是「可验证 loop」。

## 二、fiber 与 spin 的理念

### 4. fiber 哲学

fiber 把决策视作**纤维**：每条决策都是一根细而韧的丝，多根编织成稳固的工程织物。四条原则：

- **决策纤维**——一次只解一个决策，沿依赖树推进，不跳跃、不并行猜测
- **可验证 loop**——每步都有可判「做完没」的产物，下一步读上一步
- **grill 主动施压**——开工前逼问到底，宁可多问一句，不赌一次错位
- **轻量持久追溯**——产物统一落 `.fiber/` 命名空间，文档只记决策不写叙事

`.fiber/` 是这一切的物理载体：

```
.fiber/
├── CONTEXT.md          # 共享语言（领域模型）
├── CONTEXT-MAP.md      # 多上下文时的索引（monorepo）
├── docs/adr/           # 架构决策记录
├── docs/agents/        # 给代理读的配置（tracker / labels / domain layout）
├── worktrees.md        # worktree 路由表（ticket → 路径 → 分支）
├── worktrees/          # 工作树家目录（throwaway 与 destination 分层）
└── .scratch/           # 本地票据归宿（若选 local tracker）
```

**与上游 matt 的关键差异**：matt 的 skill 会把文档散落在仓库根目录（`CONTEXT.md`、`docs/adr/`、`docs/agents/`、`.scratch/` 各占一处）。

fiber 把这些**全部收敛到 `.fiber/` 一个目录下**——根目录保持干净，所有决策产物有唯一入口、可整体追溯、可一键忽略。

issue tracker 的默认值不预设——`/setup-matt-pocock-skills` 跟随用户的设置意图：本地 markdown、GitHub、GitLab 三者一视同仁。

它由仓库信号（`git remote`、已有 `.fiber/.scratch/`）推断后与用户确认，用户想要哪种就是哪种。

`/setup-matt-pocock-skills` 是这一切的入口：跑一次，它探索你的仓库、推荐答案、确认后写入 `.fiber/docs/agents/*.md`，其余工程 skill 才知道去哪读配置。

### 5. spin 哲学

spin 是 fiber 的**外围支撑层**——不直接编码、不直接决策，但让 fiber 工作流跑得起来、维护得下去。

边界很清晰：

- **fiber** = 工程纪律（grill / spec / tickets / TDD / review / domain）
- **spin** = 支撑工具（提交、初始化、工作树、写作、侦查）

spin 目前含 6 个 skill：`snap`（纯变更提交）与 `worktrees`（工作树创建与清理）让日常开发顺畅运转；

`setup-b3oy1`（本仓库 skill 栈初始化）、`setup-ship`（为消费项目生成 ship skill）负责初始化；`recon`（口头侦查报告）与 `edit-article`（本文档就是用它写的）辅助理解与写作。

spin 不与 fiber 抢地盘：凡是「编排骨架 + 可复用纪律」归 fiber，凡是「让这套体系运转和维护的胶水」归 spin。

## 三、结构与维护

### 6. 仓库结构

```
b3oy1/
├── .claude-plugin/marketplace.json   # 市集清单（fiber + spin）
├── plugins/
│   ├── fiber/                        # 22 个 matt 蒸馏 skill
│   │   ├── .claude-plugin/{plugin.json, DISTILL.meta.json}
│   │   ├── skills/                   # 每个 skill 一个目录
│   │   └── reference/matt/LICENSE    # 上游 MIT 许可
│   └── spin/                         # 支撑工具，6 个 skill
│       ├── .claude-plugin/plugin.json
│       └── skills/                   # edit-article / recon / setup-b3oy1 / setup-ship / snap / worktrees
└── scripts/
    ├── distill.py                    # 跟上游重新蒸馏
    └── test_distill.py               # 蒸馏逻辑测试
```

### 7. 安装与蒸馏

**安装市集**：

```bash
claude plugin marketplace add nekomorph-woo/b3oy1   # 或本地路径
claude plugin install fiber@b3oy1
claude plugin install spin@b3oy1
```

首次使用 fiber 工程类 skill 前，跑一次 `/setup-matt-pocock-skills` 生成 `.fiber/docs/agents/*.md`。

**跟上游重新蒸馏**（matt 更新后同步）：

```bash
python3 scripts/distill.py
```

蒸馏是 **config 驱动 + 全局路径前缀替换**，幂等可复跑（`scripts/test_distill.py` 守护关键逻辑）：

- 只改 `setup` skill 本体 + 2 个 seed template 的路径（→ `.fiber/`）
- 其余 21 个 skill 的 `.md` 原样拷贝，文件名全保留
- 白名单 bucket：`engineering` / `productivity`（matt 新增目录默认不取）
- skill 灵魂不动，只做机械安全的路径替换：正文连续路径走字面量前缀替换；ASCII 目录树走路径重写（展平节点路径 → 应用前缀规则 → 重建树）
- 树重写的规则设计见 `.fiber/docs/adr/0001-distill-tree-rewrite.md`

版本与 hash 追溯记在 `plugins/fiber/.claude-plugin/DISTILL.meta.json`——上游 commit、每个 skill 的 hash、蒸馏日期、策略说明都在里面，方便审计「改了什么、为什么改」。

### 8. 致谢

fiber 的 22 个工程 skill 蒸馏自 [mattpocock/skills](https://github.com/mattpocock/skills)（MIT），skill 的灵魂、四问题叙事、分类原则全部归属 Matt Pocock。spin 的 `edit-article` 同样来自 matt。

（其源在 matt 的 personal bucket。）本仓库自己做的是：收敛到统一 `.fiber/` 命名空间、setup 入口意图驱动、配上 spin 支撑层。

本仓库同样采用 **MIT** 协议，见根目录 `LICENSE`。上游 matt 的原始许可文件保留在 `plugins/fiber/reference/matt/LICENSE`。
