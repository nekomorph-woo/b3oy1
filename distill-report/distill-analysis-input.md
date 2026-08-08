# 蒸馏分析输入（dry-run · vs 上次 meta ed37663c）

对以下每个 content_changed 的 diff 文件，按「独立变更段」（连续增删行组）逐段分析。
**由谁分析**：当前执行 /b3oy1-distill skill 的 LLM 会话（非脚本内嵌）。
**匹配约束**：`file` 必须与下方文件标题精确一致（含 ` · ` 分隔）；`label` 必须与段序号
精确一致（`变更 1`、`变更 2`…）。LLM 输出顺序无关，按这两字段机械配对。

产出 JSON 数组，每条对应一个变更段：

```json
[{"file": "<bucket>/<skill> · <rel>", "label": "变更 N",
  "summary": "(可选)文件级一行概览", "point": "变更点", "impact": "影响评估",
  "why": "变更原由", "learn": "学习要点", "action": "建议动作", "detail": "动作说明"}
]
```

输出规格：
```text
对每个「独立变更段」（连续增删行组）产出以下 JSON：

- summary  变更摘要（可选，文件级一行概览，多段文件建议提供）
- point    变更点——这段 diff 具体改了什么，指向具体内容，不空泛
- impact   影响评估——对 b3oy1 本地（目录约定 / 替换规则 / 流程 / 产物）的具体影响；无影响要明说「无影响」
- why      变更原由——上游为什么这么改：动机、要解决的问题、对读者的收益。禁止编造——
           基于 diff 内容与 skill 目的合理推断，推断处标注；无法推断时明说「无法从 diff 推断」
- learn    学习要点——从这段变更可学到什么：可迁移的规则 / 理念 / 写法，供 b3oy1 蒸馏者吸收
- action   建议动作——采纳 / 检查规则 / 忽略，附一句说明

要求：
1. 每条基于实际 diff 行撰写，禁止泛泛而谈
2. why 必须结合 skill 的目的与读者视角推断动机
3. learn 要具体、可迁移——能落到 b3oy1 的实践或文档中
4. 同一 hunk 窗口内多个独立变更段分别分析，禁止合并
```

---
## engineering/ask-matt · SKILL.md（32 行变更）
### 变更 1 · @@ -14,13 +14,13 @@
```diff
 
-1. **`/grill-with-docs`** — sharpen the idea by interview. Start here when you **have a codebase**: it's stateful, retaining what it learns in `.fiber/CONTEXT.md` and ADRs. (No codebase? Use `/grill-me` — see Standalone. Both run the same `/grilling` primitive; `grill-with-docs` is the one that leaves a paper trail.)
-2. **Branch — can you settle every question in conversation?** If a question needs a runnable answer (state, business logic, a UI you have to see), detour through a prototype, bridged by **`/handoff`** in both directions (see Crossing sessions):
+1. **`/grill-with-docs`** — sharpen the idea by interview. Start here whenever you are **working in a working directory**: it's stateful, retaining what it learns in `.fiber/CONTEXT.md` and ADRs. (No working directory? Use `/grill-me` — see Standalone. Both run the same `/grilling` primitive; `grill-with-docs` is the one that leaves a paper trail, which makes it the better of the two whenever a repo is there to leave it in.)
+2. **Branch — can you settle every question in conversation?** If a question needs a runnable answer (state, business logic, a UI you have to see), detour through a prototype, bridged by **`/handoff`** in both directions (a prototype lives in its own directory, which is exactly what `/handoff` is for — see Phase boundaries):
    - **`/handoff`** out, then open a fresh session against that file,
```
→ 为 `变更 1` 产出一条分析（file=`engineering/ask-matt · SKILL.md`、label=`变更 1`）。

### 变更 2 · @@ -14,13 +14,13 @@
```diff
 3. **Branch — is this a multi-session build?**
-   - **Yes** → **`/to-spec`** (turn the thread into a spec), then **`/to-tickets`** to split it into tracer-bullet tickets, each declaring its **blocking edges**. On a local tracker that's one file per ticket under `.fiber/.scratch/<feature>/issues/`, worked blockers-first by hand; on a real tracker the edges become native blocking links, so any ticket whose blockers are done can be grabbed — kick off **`/implement`** per ticket, **clearing context between each one**.
+   - **Yes** → **`/to-spec`** (turn the thread into a spec), then **`/to-tickets`** to split it into tracer-bullet tickets, each declaring its **blocking edges**. On a local tracker that's one file per ticket under `.fiber/.scratch/<feature>/issues/`, worked blockers-first by hand; on a real tracker the edges become native blocking links, so any ticket whose blockers are done can be grabbed — kick off **`/implement`** per ticket, **`/clear`ing context between each one**. Each ticket is self-contained, so the last one's context is disposable.
    - **No** → **`/implement`** right here, in the same context window.
```
→ 为 `变更 2` 产出一条分析（file=`engineering/ask-matt · SKILL.md`、label=`变更 2`）。

### 变更 3 · @@ -29,7 +29,7 @@
```diff
 
-The limit on this is the **[smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**: the window (~120k tokens on state-of-the-art models) within which the model still reasons sharply. If a session approaches it before `/to-tickets`, don't push on degraded — `/handoff` and continue in a fresh thread.
+The limit on this is the **[smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**: the window (~150k tokens on state-of-the-art models) within which the model still reasons sharply. If a session approaches it before `/to-tickets`, don't push on degraded — `/compact` at the nearest phase boundary and carry on (see Phase boundaries).
 
```
→ 为 `变更 3` 产出一条分析（file=`engineering/ask-matt · SKILL.md`、label=`变更 3`）。

### 变更 4 · @@ -58,20 +58,32 @@
```diff
 
-## Crossing sessions
+## Phase boundaries
 
```
→ 为 `变更 4` 产出一条分析（file=`engineering/ask-matt · SKILL.md`、label=`变更 4`）。

### 变更 5 · @@ -58,20 +58,32 @@
```diff
 
-- **`/handoff`** — when a thread is full or you need to branch off (e.g. into a `/prototype` session), this compacts the conversation into a markdown file. You don't continue in place — you **open a new session and reference that file** to carry the context across. It's the bridge between context windows, in either direction. Use it when you want a **fresh session** but need the **current conversation preserved**.
-- **`/compact`** (built-in) — stay in the **same conversation**, letting the earlier turns be summarized. Use it at **intentional breaks between phases**, when you don't mind losing the verbatim history. Don't compact mid-phase — the agent can lose its way. `/handoff` forks; `/compact` continues.
+A **phase** is a chunk of work inside a session — the grilling, the implementation, the QA. At the **boundary** between two of them you have five options, and picking between them is the fuzziest decision in this whole map:
+
+- **Continue** — stay put. Costs nothing, loses nothing.
+- **`/clear`** — empty the window, when nothing here matters to what's next.
+- **`/handoff`** — write a portable markdown file. Narrow: only for a **new harness**, a **new directory**, a **colleague**, or forking a side task **mid-phase**. What it buys is portability.
+- **Subagent** — send a tightly-scoped task to its own window and get a report back.
+- **`/compact`** — compress this context and seed a fresh session with it. The **default**, at the bottom of the tree rather than the first reach.
+
+Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) for the ordered tree — the five questions, the reasoning behind each branch, and why the primary-source cost makes **Continue** the one to rule out first. Make the decision **at** a boundary; mid-phase, continue or split the rest into subagents.
 
```
→ 为 `变更 5` 产出一条分析（file=`engineering/ask-matt · SKILL.md`、label=`变更 5`）。

### 变更 6 · @@ -58,20 +58,32 @@
```diff
 
-- **`/grill-me`** — the same relentless interview as `/grill-with-docs`, but for when you have **no codebase**. Stateless: it saves nothing locally, builds no `.fiber/CONTEXT.md`. Reach for it to sharpen any plan or design that doesn't live in a repo.
-- **`/prototype`** — a small, throwaway program that answers one design question: does this state model feel right, or what should this UI look like. Throwaway from day one — keep the answer, delete the code. It's the detour in step 2 of the main flow, but reach for it any time a design question is hard to settle on paper.
+- **`/grill-me`** — the same relentless interview as `/grill-with-docs`, but **stateless**: it saves nothing locally and builds no `.fiber/CONTEXT.md`. Reach for it when you are **not working in a working directory** — sharpening a plan, a design, a piece of writing, anything with no repo under it. If you are in a working directory, use `/grill-with-docs` instead: it runs the same interview and leaves a paper trail, so it is strictly the better one.
+- **`/grilling`** — the interview primitive itself: rounds, the frontier, facts are the agent's job and decisions are yours. `/grill-me` and `/grill-with-docs` are the two named ways in, and `/triage`, `/wayfinder` and `/improve-codebase-architecture` all run it internally. Reach for it directly only when you want the interview with no wrapper around it.
+- **`/resolving-merge-conflicts`** — work an in-progress merge or rebase conflict hunk by hunk, resolving by **intent** traced to each side's primary source rather than by picking lines, then finish the operation. It never runs `--abort`. Standalone and off every flow: reach for it when you are already mid-conflict.
+- **`/prototype`** — a small, throwaway program that answers one design question: does this state model feel right, or what should this UI look like. Throwaway is a constraint on how the code is written, not a promise to destroy it: the answer folds into the real code, and the prototype itself is kept as a **primary source** on a `prototype/<name>` branch out of main, pointed at from the implementation issue. It's the detour in step 2 of the main flow, but reach for it any time a design question is hard to settle on paper.
 - **`/research`** — delegate reading legwork to a **background agent**: it investigates a question against **primary sources**, then leaves a cited Markdown file in the repo. Keep working while it reads. The file it produces is something to take *into* the main flow at `/grill-with-docs` — research feeds the thinking, it doesn't replace it.
```
→ 为 `变更 6` 产出一条分析（file=`engineering/ask-matt · SKILL.md`、label=`变更 6`）。

### 变更 7 · @@ -58,20 +58,32 @@
```diff
 - **`/research`** — delegate reading legwork to a **background agent**: it investigates a question against **primary sources**, then leaves a cited Markdown file in the repo. Keep working while it reads. The file it produces is something to take *into* the main flow at `/grill-with-docs` — research feeds the thinking, it doesn't replace it.
+- **`/to-questionnaire`** — when the thing blocking you isn't in your head or the codebase but in **someone else's**, this writes them a questionnaire to fill in. It's the inverse of `/grill-me`: instead of interviewing you about the subject, it interviews you about the **send** — who it's going to, what you need back — and aims the questions at the gap. What comes back is material for `/grill-with-docs` or `/to-spec`.
+- **`/wizard`** — for the steps only a **human** can take: provisioning infrastructure, setting up credentials or CI secrets, clicking through an unfamiliar third-party dashboard, running a one-off migration or cutover. It generates an interactive bash script that opens each URL, captures each value, and writes it into `.env` and GitHub secrets — so the procedure stops being something you re-explain to an agent every time. Model-invoked, so the agent reaches for it the moment it hits a wall only you can pass. If the agent could just do it itself, it should; this is for where a human is genuinely in the loop.
+- **`/wait-what`** — the corrective for a message that didn't land. Use it mid-conversation, inside any other skill, and the agent re-pitches what it just said with the context you were missing, in plain English, using the `.fiber/CONTEXT.md` vocabulary. It works after the fact; `/grill-with-docs` is the upfront cure, because a shared language agreed early is what stops the jargon arriving at all.
 - **`/teach`** — learn a concept over multiple sessions, using the current directory as a stateful workspace.
```
→ 为 `变更 7` 产出一条分析（file=`engineering/ask-matt · SKILL.md`、label=`变更 7`）。

### 变更 8 · @@ -58,20 +58,32 @@
```diff
 - **`/teach`** — learn a concept over multiple sessions, using the current directory as a stateful workspace.
-- **`/writing-great-skills`** — reference for writing and editing skills well.
+- **`/writing-for-agents`** — reference for writing documents agents consume: skills, AGENTS.md, pointed-at docs.
 
```
→ 为 `变更 8` 产出一条分析（file=`engineering/ask-matt · SKILL.md`、label=`变更 8`）。

---
## engineering/code-review · SKILL.md（8 行变更）
### 变更 1 · @@ -1,12 +1,12 @@
```diff
 name: code-review
-description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/PRD asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
+description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
 ---
```
→ 为 `变更 1` 产出一条分析（file=`engineering/code-review · SKILL.md`、label=`变更 1`）。

### 变更 2 · @@ -1,12 +1,12 @@
```diff
 - **Standards** — does the code conform to this repo's documented coding standards?
-- **Spec** — does the code faithfully implement the originating issue / PRD / spec?
+- **Spec** — does the code faithfully implement the originating issue / spec?
 
```
→ 为 `变更 2` 产出一条分析（file=`engineering/code-review · SKILL.md`、label=`变更 2`）。

### 变更 3 · @@ -28,7 +28,7 @@
```diff
 2. A path the user passed as an argument.
-3. A PRD/spec file under `docs/`, `specs/`, or `.fiber/.scratch/` matching the branch name or feature.
+3. A spec file under `docs/`, `specs/`, or `.fiber/.scratch/` matching the branch name or feature.
 4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".
```
→ 为 `变更 3` 产出一条分析（file=`engineering/code-review · SKILL.md`、label=`变更 3`）。

### 变更 4 · @@ -56,8 +56,6 @@
```diff
 ### 4. Spawn both sub-agents in parallel
-
-Send a single message with two `Agent` tool calls. Use the `general-purpose` subagent for both.
 
```
→ 为 `变更 4` 产出一条分析（file=`engineering/code-review · SKILL.md`、label=`变更 4`）。

---
## engineering/codebase-design · DESIGN-IT-TWICE.md（2 行变更）
### 变更 1 · @@ -18,7 +18,7 @@
```diff
 
-Spawn 3+ sub-agents in parallel using the Agent tool. Each must produce a **radically different** interface for the deepened module.
+Spawn 3+ sub-agents in parallel. Each must produce a **radically different** interface for the deepened module.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/codebase-design · DESIGN-IT-TWICE.md`、label=`变更 1`）。

---
## engineering/diagnosing-bugs · SKILL.md（10 行变更）
### 变更 1 · @@ -8,6 +8,12 @@
```diff
 When exploring the codebase, read `.fiber/CONTEXT.md` (if it exists) to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.
+
+## Redact
+
+This skill has you show commands, outputs and captured artifacts. **Redact every secret first** — write `<REDACTED>` in its place. Build loops against env vars, so the credential stays in the environment rather than in what you show. Captured artifacts carry auth headers: quote only the lines that carry the signal.
+
+If the redacted output is not enough to diagnose the bug, say so and ask the user.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/diagnosing-bugs · SKILL.md`、label=`变更 1`）。

### 变更 2 · @@ -46,11 +52,11 @@
```diff
 
-Stop and say so explicitly. List what you tried. Ask the user for: (a) access to whatever environment reproduces it, (b) a captured artifact (HAR file, log dump, core dump, screen recording with timestamps), or (c) permission to add temporary production instrumentation. Do **not** proceed to hypothesise without a loop.
+Stop and say so explicitly. List what you tried. Ask the user for: (a) access to whatever environment reproduces it, (b) a redacted captured artifact (HAR file, log dump, core dump, screen recording with timestamps), or (c) permission to add temporary production instrumentation. Do **not** proceed to hypothesise without a loop.
 
```
→ 为 `变更 2` 产出一条分析（file=`engineering/diagnosing-bugs · SKILL.md`、label=`变更 2`）。

### 变更 3 · @@ -46,11 +52,11 @@
```diff
 
-Phase 1 is done when the loop is **tight** and **red-capable**: you can name **one command** — a script path, a test invocation, a curl — that you have **already run at least once** (paste the invocation and its output), and that is:
+Phase 1 is done when the loop is **tight** and **red-capable**: you can name **one command** — a script path, a test invocation, a curl — that you have **already run at least once** (show the invocation and its output, redacted), and that is:
 
```
→ 为 `变更 3` 产出一条分析（file=`engineering/diagnosing-bugs · SKILL.md`、label=`变更 3`）。

---
## engineering/improve-codebase-architecture · SKILL.md（2 行变更）
### 变更 1 · @@ -24,7 +24,7 @@
```diff
 
-Then use the Agent tool with `subagent_type=Explore` to walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:
+Then spawn a sub-agent to walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/improve-codebase-architecture · SKILL.md`、label=`变更 1`）。

---
## engineering/prototype · LOGIC.md（64 行变更）
### 变更 1 · @@ -1,13 +1,15 @@
```diff
 
-A tiny interactive terminal app that lets the user drive a state model by hand. Use this when the question is about **business logic, state transitions, or data shape** — the kind of thing that looks reasonable on paper but only feels wrong once you push it through real cases.
+A single, self-contained HTML file — a **shareable demo** — that lets anyone drive a state model by clicking buttons. Use this when the question is about **business logic, state transitions, or data shape** — the kind of thing that looks reasonable on paper but only feels wrong once you push it through real cases.
+
+Because it's one file with nothing to install, you can hand it to a non-developer — a designer, a PM, a domain expert — and let them feel the model for themselves. So it speaks their language, not the code's.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 1`）。

### 变更 2 · @@ -1,13 +1,15 @@
```diff
 - "I want to feel out what the API should look like before writing it."
-- Anything where the user wants to **press buttons and watch state change**.
+- Anything where someone wants to **press buttons and watch state change**.
 
```
→ 为 `变更 2` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 2`）。

### 变更 3 · @@ -15,17 +17,11 @@
```diff
 
-Before writing code, write down what state model and what question you're prototyping. One paragraph, in the prototype's README or a comment at the top of the file. A logic prototype that answers the wrong question is pure waste — make the question explicit so it can be checked later, whether the user is watching now or returning to it AFK.
+Before writing code, write down what state model and what question you're prototyping. One paragraph, at the top of the demo (in a visible intro, not just a comment). A logic prototype that answers the wrong question is pure waste — make the question explicit so it can be checked later, whether the user is watching now or returning to it AFK.
 
```
→ 为 `变更 3` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 3`）。

### 变更 4 · @@ -15,17 +17,11 @@
```diff
 
-### 2. Pick the language
+### 2. Isolate the logic in a portable module
 
```
→ 为 `变更 4` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 4`）。

### 变更 5 · @@ -15,17 +17,11 @@
```diff
 
-Use whatever the host project uses. If the project has no obvious runtime (e.g. a docs repo), ask.
-
-Match the project's existing conventions for tooling — don't add a new package manager or runtime just for the prototype.
-
-### 3. Isolate the logic in a portable module
-
-Put the actual logic — the bit that's answering the question — behind a small, pure interface that could be lifted out and dropped into the real codebase later. The TUI around it is throwaway; the logic module shouldn't be.
+Put the actual logic — the bit that's answering the question — in a single `<script>` block written as a small, pure module that could be lifted out and dropped into the real codebase later. The page around it is throwaway; this module isn't.
 
```
→ 为 `变更 5` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 5`）。

### 变更 6 · @@ -34,46 +30,38 @@
```diff
 
-Pick whichever shape best fits the question being asked, *not* whichever is easiest to wire to a TUI. Keep it pure: no I/O, no terminal code, no `console.log` for control flow. The TUI imports it and calls into it; nothing flows the other direction.
+Pick whichever shape best fits the question being asked, *not* whichever is easiest to wire to a page. Keep it pure: no DOM, no `document`, no button handlers reaching inside it. The page calls into it; nothing flows the other direction. This is what makes the prototype useful past its own lifetime: once the question's answered, the validated reducer / machine / function set lifts into the real module on its own.
 
```
→ 为 `变更 6` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 6`）。

### 变更 7 · @@ -34,46 +30,38 @@
```diff
 
-This is what makes the prototype useful past its own lifetime: when the question's been answered, the validated reducer / machine / function set can be lifted into the real module on its own.
+### 3. Build the shareable HTML file
 
```
→ 为 `变更 7` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 7`）。

### 变更 8 · @@ -34,46 +30,38 @@
```diff
 
-### 4. Build the smallest TUI that exposes the state
+One file, plain HTML/CSS/JS — no framework, no bundler, no server, everything inline so it opens by double-click and survives being emailed around. Anyone should be able to run it by opening it.
 
```
→ 为 `变更 8` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 8`）。

### 变更 9 · @@ -34,46 +30,38 @@
```diff
 
-Build it as a **lightweight TUI** — on every tick, clear the screen (`console.clear()` / `print("\033[2J\033[H")` / equivalent) and re-render the whole frame. The user should always see one stable view, not an ever-growing scrollback.
+Write it for a non-developer. Every label is in **domain language**, not code — buttons and state read like the business, not the reducer. Explain in plain words what's happening.
 
```
→ 为 `变更 9` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 9`）。

### 变更 10 · @@ -34,46 +30,38 @@
```diff
 
-Each frame has two parts, in this order:
+Lay it out with a clean hierarchy, top to bottom:
 
```
→ 为 `变更 10` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 10`）。

### 变更 11 · @@ -34,46 +30,38 @@
```diff
 
-1. **Current state**, pretty-printed and diff-friendly (one field per line, or formatted JSON). Use **bold** for field names or section headers and **dim** for less important context (timestamps, IDs, derived values). Native ANSI escape codes are fine — `\x1b[1m` bold, `\x1b[2m` dim, `\x1b[0m` reset. No need to pull in a styling library unless one is already in the project.
-2. **Keyboard shortcuts**, listed at the bottom: `[a] add user  [d] delete user  [t] tick clock  [q] quit`. Bold the key, dim the description, or vice-versa — whatever reads cleanly.
+1. **Title and one-line explanation** of what this demo lets you explore (the question from step 1).
+2. **Current state** — the full relevant state, rendered as a readable panel (labelled fields, not a raw JSON dump), re-rendered after every click so the change is visible. Where it helps a non-developer follow, call out what just changed.
+3. **Free-play buttons** — one button per action, always available, so anyone can poke at the model in any order. Each click dispatches its action and re-renders the state.
+4. **Guided walkthroughs** — a set of **scenarios**, one per tab. Each tab holds a short plain-language description of the scenario — the situation it sets up and what to watch for — and underneath it, the ordered **buttons to press** for that scenario. Each step is a real button: clicking it performs that action and moves to the next step. Starting a walkthrough resets to a known initial state so the scenario runs the same way every time.
 
```
→ 为 `变更 11` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 11`）。

### 变更 12 · @@ -34,46 +30,38 @@
```diff
 
-Behaviour:
+Choose scenarios that demonstrate the awkward cases — the happy path, a tricky edge case, an attempt at something that should be illegal — the ones hard to reason about on paper.
 
```
→ 为 `变更 12` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 12`）。

### 变更 13 · @@ -34,46 +30,38 @@
```diff
 
-1. **Initialise state** — a single in-memory object/struct. Render the first frame on start.
-2. **Read one keystroke (or one line)** at a time, dispatch to a handler that mutates state.
-3. **Re-render** the full frame after every action — don't append, replace.
-4. **Loop until quit.**
+Keep it beautiful but restrained: clean typography, generous spacing, one accent colour. No animations, no gimmicks — nothing that competes with the state and the buttons.
 
```
→ 为 `变更 13` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 13`）。

### 变更 14 · @@ -34,46 +30,38 @@
```diff
 
-The whole frame should fit on one screen.
+### 4. Hand it over
 
```
→ 为 `变更 14` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 14`）。

### 变更 15 · @@ -34,46 +30,38 @@
```diff
 
-### 5. Make it runnable in one command
+Send them the file, or open it for them. They'll click through the walkthroughs and free-play whenever they get to it; the interesting moments are when they say "wait, that shouldn't be possible" or "huh, I assumed X would be different" — those are the bugs in the _idea_, which is the whole point. If they want new actions or a new scenario, add them. Prototypes evolve.
 
```
→ 为 `变更 15` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 15`）。

### 变更 16 · @@ -34,46 +30,38 @@
```diff
 
-Add a script to the project's existing task runner (`package.json` scripts, `Makefile`, `justfile`, `pyproject.toml`). The user should run `pnpm run <prototype-name>` or equivalent — never need to remember a path.
+### 5. Capture the answer and the prototype
 
```
→ 为 `变更 16` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 16`）。

### 变更 17 · @@ -34,46 +30,38 @@
```diff
 
-If the host project has no task runner, just put the command at the top of the prototype's README.
-
-### 6. Hand it over
-
-Give the user the run command. They'll drive it themselves; the interesting moments are when they say "wait, that shouldn't be possible" or "huh, I assumed X would be different" — those are the bugs in the _idea_, which is the whole point. If they want new actions added, add them. Prototypes evolve.
-
-### 7. Capture the answer and the prototype
-
-Once the prototype has answered its question, capture the answer, then capture the prototype the way the [SKILL](SKILL.md) describes. The logic-specific mapping: the validated reducer / machine / function set lifts into the real module (the decision, absorbed); the TUI shell rides along to the throwaway branch that keeps the prototype as a primary source.
+Once the prototype has answered its question, capture the answer, then capture the prototype the way the [SKILL](SKILL.md) describes. The logic-specific mapping: the validated reducer / machine / function set lifts into the real module (the decision, absorbed); the HTML shell rides along to the throwaway branch that keeps the prototype as a primary source — and being one self-contained file, it stays trivially re-runnable there.
 
```
→ 为 `变更 17` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 17`）。

### 变更 18 · @@ -34,46 +30,38 @@
```diff
 - **Don't add tests.** A prototype that needs tests is no longer a prototype.
-- **Don't wire it to the real database.** Use an in-memory store unless the question is specifically about persistence.
+- **Don't wire it to the real database.** Use in-memory state unless the question is specifically about persistence.
 - **Don't generalise.** No "what if we wanted to support X later." The prototype answers one question.
```
→ 为 `变更 18` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 18`）。

### 变更 19 · @@ -34,46 +30,38 @@
```diff
 - **Don't generalise.** No "what if we wanted to support X later." The prototype answers one question.
-- **Don't blur the logic and the TUI together.** If the reducer / state machine references `console.log`, prompts, or terminal escape codes, it's no longer portable. Keep the TUI as a thin shell over a pure module.
-- **Don't ship the TUI shell into production.** The shell is optimised for being driven by hand from a terminal. The logic module behind it is the bit worth keeping.
+- **Don't blur the logic and the page together.** If the pure module references the DOM, `document`, or button handlers, it's no longer liftable. Keep the page as a thin shell over a pure module.
+- **Don't reach for a framework, bundler, or server.** One file the recipient double-clicks; a React app or a dev server defeats "shareable".
+- **Don't ship the HTML shell into production.** The page is optimised for being clicked through by hand. The logic module behind it is the bit worth keeping.
```
→ 为 `变更 19` 产出一条分析（file=`engineering/prototype · LOGIC.md`、label=`变更 19`）。

---
## engineering/prototype · SKILL.md（4 行变更）
### 变更 1 · @@ -11,7 +11,7 @@
```diff
 
-- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a tiny interactive terminal app that pushes the state machine through cases that are hard to reason about on paper.
+- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file — free-play buttons plus tabbed guided walkthroughs — that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
 - **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.
```
→ 为 `变更 1` 产出一条分析（file=`engineering/prototype · SKILL.md`、label=`变更 1`）。

### 变更 2 · @@ -19,7 +19,7 @@
```diff
 1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious — but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
-2. **One command to run.** Whatever the project's existing task runner supports — `pnpm <name>`, `python <path>`, `bun <path>`, etc. The user must be able to start it without thinking.
+2. **Trivial to run.** A UI prototype starts from one command in the project's task runner — `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
 3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE — wipe me" name.
```
→ 为 `变更 2` 产出一条分析（file=`engineering/prototype · SKILL.md`、label=`变更 2`）。

---
## engineering/setup-matt-pocock-skills · SKILL.md（2 行变更）
### 变更 1 · @@ -37,7 +37,7 @@
```diff
 
-> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-tickets`, `triage`, `to-spec`, and `qa` read from and write to it — they need to know whether to call `gh issue create`, write a markdown file under `.fiber/.scratch/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.
+> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-tickets`, `triage`, and `to-spec` read from and write to it — they need to know whether to call `gh issue create`, write a markdown file under `.fiber/.scratch/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/setup-matt-pocock-skills · SKILL.md`、label=`变更 1`）。

---
## engineering/setup-matt-pocock-skills · issue-tracker-github.md（2 行变更）
### 变更 1 · @@ -1,6 +1,6 @@
```diff
 
-Issues and PRDs for this repo live as GitHub issues. Use the `gh` CLI for all operations.
+Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/setup-matt-pocock-skills · issue-tracker-github.md`、label=`变更 1`）。

---
## engineering/setup-matt-pocock-skills · issue-tracker-gitlab.md（2 行变更）
### 变更 1 · @@ -1,6 +1,6 @@
```diff
 
-Issues and PRDs for this repo live as GitLab issues. Use the [`glab`](https://gitlab.com/gitlab-org/cli) CLI for all operations.
+Issues and specs for this repo live as GitLab issues. Use the [`glab`](https://gitlab.com/gitlab-org/cli) CLI for all operations.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/setup-matt-pocock-skills · issue-tracker-gitlab.md`、label=`变更 1`）。

---
## engineering/setup-matt-pocock-skills · issue-tracker-local.md（2 行变更）
### 变更 1 · @@ -1,6 +1,6 @@
```diff
 
-Issues and specs (you may know a spec as a PRD) for this repo live as markdown files in `.fiber/.scratch/`.
+Issues and specs for this repo live as markdown files in `.fiber/.scratch/`.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/setup-matt-pocock-skills · issue-tracker-local.md`、label=`变更 1`）。

---
## engineering/tdd · SKILL.md（2 行变更）
### 变更 1 · @@ -23,6 +23,8 @@
```diff
 
+When the shape of that interface is itself in question — how deep the module is, where the seam belongs, what the interface should expose — use the `/codebase-design` skill for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.
+
 ## Anti-patterns
```
→ 为 `变更 1` 产出一条分析（file=`engineering/tdd · SKILL.md`、label=`变更 1`）。

---
## engineering/to-spec · SKILL.md（2 行变更）
### 变更 1 · @@ -4,7 +4,7 @@
```diff
 
-This skill takes the current conversation context and codebase understanding and produces a spec (you may know this document as a PRD). Do NOT interview the user — just synthesize what you already know.
+This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview the user — just synthesize what you already know.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/to-spec · SKILL.md`、label=`变更 1`）。

---
## engineering/triage · SKILL.md（2 行变更）
### 变更 1 · @@ -73,7 +73,7 @@
```diff
 
-4. **Grill (if needed).** If the request needs fleshing out, run the `/grilling` and `/domain-modeling` skills together — grill it into shape one question at a time, sharpening domain terms and updating `.fiber/CONTEXT.md`/ADRs inline as decisions land.
+4. **Grill (if needed).** If the request needs fleshing out, run the `/grilling` and `/domain-modeling` skills together — grill it into shape a round of questions at a time, sharpening domain terms and updating `.fiber/CONTEXT.md`/ADRs inline as decisions land.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/triage · SKILL.md`、label=`变更 1`）。

---
## engineering/wayfinder · SKILL.md（8 行变更）
### 变更 1 · @@ -14,7 +14,7 @@
```diff
 
-Every map and ticket is an issue, so it has a **name** — its title. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish — a name wraps its link — but they ride *inside* the name, never stand in for it.
+Every map and ticket is an issue, so it has a **name** — its title. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish — a name wraps its link — but they ride _inside_ the name, never stand in for it.
 
```
→ 为 `变更 1` 产出一条分析（file=`engineering/wayfinder · SKILL.md`、label=`变更 1`）。

### 变更 2 · @@ -72,12 +72,12 @@
```diff
 
-Every ticket is either **HITL** — human in the loop, worked *with* a human who speaks for themselves — or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).
+Every ticket is either **HITL** — human in the loop, worked _with_ a human who speaks for themselves — or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).
 
```
→ 为 `变更 2` 产出一条分析（file=`engineering/wayfinder · SKILL.md`、label=`变更 2`）。

### 变更 3 · @@ -72,12 +72,12 @@
```diff
 - **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to — an outline, a rough take, a stub, or UI/logic code via the /prototype skill. Links the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question.
-- **Grilling** (HITL): Conversation via the /grilling and /domain-modeling skills, one question at a time. The default case.
-- **Task** (HITL or AFK): Manual work that must happen before a *decision* can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that *does* rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.
+- **Grilling** (HITL): Conversation. The default case. Always invoke the /grilling and /domain-modeling skills.
+- **Task** (HITL or AFK): Manual work that must happen before a _decision_ can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that _does_ rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.
 
```
→ 为 `变更 3` 产出一条分析（file=`engineering/wayfinder · SKILL.md`、label=`变更 3`）。

---
## productivity/grilling · SKILL.md（18 行变更）
### 变更 1 · @@ -3,10 +3,20 @@
```diff
 
-Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.
+Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.
 
```
→ 为 `变更 1` 产出一条分析（file=`productivity/grilling · SKILL.md`、label=`变更 1`）。

### 变更 2 · @@ -3,10 +3,20 @@
```diff
 
-Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.
+Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.
 
```
→ 为 `变更 2` 产出一条分析（file=`productivity/grilling · SKILL.md`、label=`变更 2`）。

### 变更 3 · @@ -3,10 +3,20 @@
```diff
 
-If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.
+Each question should be formatted like so:
 
```
→ 为 `变更 3` 产出一条分析（file=`productivity/grilling · SKILL.md`、label=`变更 3`）。

### 变更 4 · @@ -3,10 +3,20 @@
```diff
 
-Do not act on it until I confirm we have reached a shared understanding.
+```
+❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>
+
+➡️ <your recommended answer>
+```
+
+Each round the user answers reshapes the tree — settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.
+
+Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it — don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report — ask the rest of the frontier now. The _decisions_ are the user's — put each to them and wait.
+
+The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
```
→ 为 `变更 4` 产出一条分析（file=`productivity/grilling · SKILL.md`、label=`变更 4`）。
