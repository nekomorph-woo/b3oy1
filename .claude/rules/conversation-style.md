# 对话与输出风格

> 第一性原理：输出的唯一目的是让读者用最小认知成本获取信息。装饰是成本，不是价值——每多一个框、一个装饰性 emoji，都是读者要跳过的噪音。

## 语言分工

| 场景 | 语言 |
|------|------|
| 对话、控制台输出、脚本注释、commit message | 简体中文 |
| `.claude/skills/` 仓库维护技能（b3oy1-commit、b3oy1-manage-version 等） | 简体中文 |
| `plugins/*/`（fiber、spin 的分发产物：SKILL.md、agent、hook、plugin.json description、reference） | 英文 |

## 变更摘要

每次改动后给一份摘要。**Why 先行**：第一句说为什么改，不说改了哪个文件——文件是结果，目的才是读者要先知道的。

```
**<动词>** <对象> — <为什么>

- `path/file` — <改动>
- `path/file` — <改动>
```

动词是 leading word，与 commit type 对应，锚定变更性质：

- **Added** — 新增（feat）
- **Changed** — 改行为或结构（refactor / perf）
- **Fixed** — 修复（fix）
- **Removed** — 移除

原则：

- 不用 ASCII 框装饰；只有 before/after 真对比时才用框
- emoji 克制：标记类型/状态，不每行装饰
- 路径写成 `file:line`，可点击
- 影响范围、验证方式只在必要时加一行，不常态堆砌

## 对话原则

- **Why 先行**：先说目的或决策，再说做了什么
- **No ceremony**：信息密度优先，不堆砌格式
- **正面表述**：说「做什么」，不说「不要做什么」——禁止只会让被禁的事更显眼
- **Leading word**：用一个精确的预训练词锚定概念，替代长描述
- **单方真源**：一个意思只在一处定义，不重复
- **可判定完成**：每个步骤给一个能判「做完没」的标准，不写模糊目标
