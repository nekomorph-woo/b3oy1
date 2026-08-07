---
name: b3oy1-distill
description: 蒸馏上游 matt skills 到本仓库——先 dry-run 出 HTML 报告，确认后再 apply 写入。
disable-model-invocation: true
---

# Distill

从上游 `mattpocock/skills` 蒸馏工程 skill 到本仓库。**统一入口，总是先 check**：先 dry-run 看清差异，用户确认后才真正写入。

契合用户全局 `git-working-tree` 规则——覆盖 working tree 前必须先问，dry-run 零副作用正合此意。

## 步骤

### 1. 先 check（dry-run，零写入）

跑：

    python3 scripts/distill.py --check

dry-run 只 clone 上游 + 跑内容检查，**不拷贝、不做路径替换、不写 meta**。产出 `distill-report/distill-check-<yy-MM-dd-HH-ss>.html`（时间戳文件名，入 git 供 commit 追踪；`--check-out` 可改路径）。

完成标准：命令跑完，终端打印出报告的绝对路径；脚本退出码已读到（`0`=无变更 / `2`=有变更 / `1`=bucket 或 extra skill 缺失）。

### 1.5 可选：逐条精细分析（LLM）

dry-run 报告只有总览 + 原始 diff。需要逐段分析（变更点 / 影响 / 变更原由 / 学习要点 / 建议动作）时：

1. 导出分析输入：

       python3 scripts/distill.py --check --analyze-out

   产出 `distill-report/distill-analysis-input.md`——按「独立变更段」切分（hunk 内连续增删行组），含输出规格。
2. **当前执行本 skill 的 LLM 逐段分析**：读分析输入文件，按输出规格产出分析 JSON（逐独立变更段一条，禁止合并）。
3. 合并进报告：

       python3 scripts/distill.py --check --apply-analysis <分析-json-路径>

   详情区段渲染为按 skill 分组的逐段分析形态。

完成标准：报告打开后详情区段是分组卡 + 逐段五字段分析；报告与分析输入都落在 `distill-report/`。

### 2. 交接报告路径

**只打印报告的绝对路径**，不 `open`、不产生副作用。提示用户可自行打开查看。

读终端 summary 行，口头汇报：几个 skill 变更 / 新增 / 删除 / 未变，extra skills 状态。

完成标准：用户拿到 HTML 绝对路径与一句话总览，无需自己翻终端。

### 3. 问是否 apply

明确询问用户是否 apply（执行真正蒸馏）。**未确认不写文件。**

- 用户拒绝 / 想先看报告 → 停在此步，等用户看完 HTML 再决定。
- 退出码 `1`（结构缺失）→ 不询问 apply，直接报告错误，让用户先修 bucket / extra 配置。
- 退出码 `0`（无变更）→ 告知无差异，问是否仍要 apply（通常不需要）。

完成标准：拿到用户显式确认（「apply」/「蒸馏」/「确认」），或已停在等待态。

### 4. 确认后 apply

跑正常蒸馏（无 `--check`）：

    python3 scripts/distill.py

这一步执行拷贝覆盖 + 路径前缀替换 + meta 写入 + agents 清理——**会覆盖 working tree 文件**，所以必须经过第 3 步确认。

完成标准：脚本跑完无 ERROR，meta 已更新；汇报本轮变更（哪些 skill 拷贝 / 哪些路径替换命中 / extra 同步情况）。

### 5. 指向 /b3oy1-commit 收尾

apply 产出的改动（skill 文件 + `DISTILL.meta.json`）需要提交。**指向 `/b3oy1-commit`，不内嵌调用**——commit 的 type / scope / 版本升级判断归 b3oy1-commit。

完成标准：用户知道下一步该跑 `/b3oy1-commit`；本 skill 不越界写 commit。

## 范围边界

只做 **分流 + 调用 + 结果交接**。

- 不解释 `DISTILL.meta.json` 语义——归 `distill.py` 写它。
- 不管上游仓库 `matt_src` 来源——归脚本顶部常量。
- 不内嵌 commit——归 `/b3oy1-commit`。
