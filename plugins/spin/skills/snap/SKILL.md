---
name: snap
description: Write one conventional-commit message for the staged diff and commit it, linking any issue the conversation already references.
---

# Snap

Write one conventional-commit message for the staged diff, then commit. Link any issue the conversation already references.

Snap serves any project. It detects the commit language from the repo's own history and rules, and infers `type` / `scope` from the paths touched. It does not bump versions or run project-specific release flow — pair it with a project-level skill when a commit must also version something.

## Process

### 1. Read the staged diff

Run `git diff --cached --stat` and `git diff --cached`. From the result pick a **type** and a **scope**.

Completion: every staged file maps to one type and one scope.

### 2. Detect the commit language

Pick the language for `description`, in priority order:

1. The language of the last 5 commit messages.
2. The language of the project's rule file (`CLAUDE.md` / `AGENTS.md`).
3. English.

Completion: one language is chosen before the message is written.

### 3. Write the message

Format:

    <type>(<scope>): <description>

- `description` in the detected language, single line, imperative.
- States the behavior that changed, not the files touched.

Completion: one line says what behavior changed.

### 4. Link issues already in context

Scan the conversation for issue signals. **No signal → append no footer, ask nothing.**

| Signal | Example |
|--------|---------|
| `#<n>` in the user's message | "fixes #42", "links #7 and #13" |
| issue URL | `https://github.com/owner/repo/issues/42` |
| an issue created earlier this session | its number is in context |
| the draft message already cites one | `description` carries `#<n>` |

On match, collect every number and append a footer:

    Closes #42, closes #13

`Closes` is the keyword — GitHub and GitLab both accept `Closes` / `Fixes` / `Resolves`.

Completion: every issue referenced in context is cited, or the message has no footer.

### 5. Commit and summarize

`git commit` with the message. Print a short summary: the type and scope chosen, any linked issues, and how many commits sit ahead of `origin`.

Completion: the commit exists; the summary states the type, scope, any linked issues, and the count of commits ahead of `origin`.

## type

Infer from what the change does.

| type | when |
|------|------|
| feat | new file / function / capability |
| fix | bug fix |
| docs | docs only |
| style | formatting, no logic change |
| refactor | restructure, behavior unchanged |
| perf | performance |
| test | tests |
| chore | build / tooling / deps |
| ci | CI config |

## scope

Infer from the primary path touched; multiple paths → the dominant one.

| path | scope |
|------|-------|
| `src/**/<area>/**` | the area, e.g. `auth`, `api` |
| `tests/**` / `**/*.test.*` | test |
| `docs/**` | docs |
| `package.json` / `*.lock` | deps |
| `.github/workflows/**` | ci |
| root config files | config |
| unclear | the project name, or `core` |
