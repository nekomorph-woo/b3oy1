---
name: setup-wt
description: Set up this repo for the wt plugin — install the throwaway-worktree convention rule (with the lazygit diff-tool ask), exclude the worktree home in .gitignore, and optionally install the wt shell helper. Run once before first use of wt:ops-wt. Produces its own artifacts only; never edits other setup's docs.
disable-model-invocation: true
---

# Setup wt

Scaffold this repo for the worktree layer of the b3oy1 stack. This skill is the **worktree-only** half of repo setup — it installs the convention rule, the `.gitignore` exclude, and (opt-in) the lazygit diff-viewing helper. It does **not** touch anything the other setups own (issue tracker docs, agent-skills index, other `.claude/rules/` files); each artifact it writes is its own.

Complements `setup-b3oy1` (the fiber/spin half): the two are independent — either may run before, after, or without the other. Run this once, before the first `wt:ops-wt` use.

Not every repo needs this. A repo that develops directly on a feature branch, with no `.fiber/worktrees/` home, skips this plugin entirely — the fiber workflow (wayfinder / prototype / implement / tdd) does not depend on worktrees.

## Process

### 1. Install the worktree convention rule

Copy [throwaway-worktree-convention.md](./reference/throwaway-worktree-convention.md) into the repo's `.claude/rules/`. The template carries one placeholder, `{{WORKTREE_DIFF_TOOL_BLOCK}}`, resolved by the lazygit ask in step 3: on opt-in, delete the placeholder line and keep the `## Viewing diffs in a worktree` section that follows it; on decline, delete the placeholder line **and** the whole section.

The copy is **overwrite-as-update**: refresh the file unconditionally on re-run — no diff check, no skip-if-exists, no ask. The template is the source of truth for this one file; nothing else in `.claude/rules/` is touched.

Completion: `.claude/rules/throwaway-worktree-convention.md` exists with the placeholder resolved.

### 2. Exclude the worktree home in `.gitignore`

The convention lives at `.fiber/worktrees/` inside the repo; without a `.gitignore` entry, every worktree directory shows up as untracked in the main working tree. Ensure the exclude is present — **idempotently**: if `.gitignore` already carries `.fiber/worktrees/`, do nothing; otherwise append it. Do not touch any other line of the file.

Completion: `.gitignore` carries a `.fiber/worktrees/` exclude; main `git status` stays clean with worktrees present.

### 3. Ask about the worktree diff tool (lazygit)

The worktree home `.fiber/worktrees/` is gitignored (step 2), so IDEs that treat the repo root as the single project window show no changes for worktrees under it. A lightweight diff tool pointed at a worktree directory closes that gap. Ask the user — a yes/no question — whether to install lazygit as that tool. Before asking, check whether lazygit is already installed (`command -v lazygit`); if it is, ask only about the shell helper + rule section, not the install. On yes:

- **Install lazygit** (skip if already installed). macOS/Linux: `brew install lazygit` (if brew and the download stall on ghcr.io, retry with `HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles`); other package managers: scoop / winget on Windows, or the user's usual one. Verify with `lazygit --version`.
- **Install the shell helper.** Append [worktree-helper.sh](./reference/worktree-helper.sh) (macOS/Linux: function `wt`, append to `~/.zshrc` or `~/.bashrc`) or [worktree-helper.ps1](./reference/worktree-helper.ps1) (Windows: function `wtx` — `wt` collides with Windows Terminal's `wt.exe`, append to PowerShell `$PROFILE`). Replace the `<repo-root>` token in the helper with the repo's absolute path before appending; if a previous `# b3oy1 worktree helper` block already exists in the rc, replace it instead of appending a second copy.
- **Resolve the placeholder** per step 1: the `## Viewing diffs in a worktree` section lands in the installed rule.

On no (or if the user already uses another diff tool), the section drops out of the installed rule entirely — see step 1. The convention's gitignore behavior is unchanged either way.

Completion: the user answered; lazygit is on PATH or explicitly declined; the shell helper is installed or declined.

### 4. Done

Tell the user the wt layer is ready, and what consumes each artifact:

- all agent sessions → `.claude/rules/throwaway-worktree-convention.md` (the layer table routes prototype / research / task tickets to throwaway worktrees, implement / tdd to destination worktrees)
- `wt:ops-wt` → `.fiber/worktrees.md` routing table (created on first use, not here)
- the human's terminal → `wt <slug>` / `wtx <slug>` (lazygit diff viewing, when opted in)

Mention they can edit the rule file directly later. Re-running this skill refreshes the rule from the template (overwrite-as-update) and re-ensures the `.gitignore` exclude (idempotent; the shell-helper block in the rc is likewise replaced, not duplicated).

Completion: every artifact above exists (or is explicitly declined); the user knows the consumption map.

## Out of scope

- **tracker / domain / agent-skills setup** — `setup-b3oy1`'s territory; this skill never writes those files.
- **`.fiber/worktrees.md` seeding** — the routing table is created by `wt:ops-wt` on the first worktree, not by setup.
- **existing worktrees** — migrating or cleaning pre-existing worktrees (e.g. a `.claude/worktrees/` directory) is the convention rule's own instruction to agent sessions, not setup's.
