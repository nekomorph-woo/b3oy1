# b3oy1 skill 与 rule 分发

本 repo 构建 b3oy1 skill 栈以及随栈下发的 rule。本 glossary 锁定一套用语，区分「下发到每个采用 repo 的」与「只属于某一个 repo 的」。

## Rule

**分布式规则**:
随 skill 栈的 setup 流程（`setup-b3oy1`，worktree 约定则经 `wt:setup-wt`）下发、对每个采用 b3oy1 栈的 repo 都生效的 rule。英文撰写，跨 repo 通用。
_避免_: 模板规则、默认规则、共享规则

**本 repo 专属规则**:
为某一个 repo 的具体上下文撰写的 rule（如本 repo 自己的 `conversation-style.md`），不下发。与同主题的分布式规则共存时，因更具体而优先。
_避免_: 本地规则、自定义规则、项目规则

**对话与输出风格**:
b3oy1 栈关于 agent session 说话与排版的 canonical 约定；以 `b3oy1-conversation-style` 规则下发，规则正文是单一真源，本条只命名概念。
_避免_: 输出风格、语气、语调
