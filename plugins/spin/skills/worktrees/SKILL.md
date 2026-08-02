---
name: worktrees
description: Manage git worktrees in the .fiber/worktrees/ home — create (git worktree add + register the routing table), list (read .fiber/worktrees.md), clean (deregister the row + git worktree remove). Use when a worktree needs creating for a ticket, locating an existing one, or removing after resolve / PR merge.
---

# Worktrees

Operational entry point for the worktree convention (`.claude/rules/throwaway-worktree-convention.md` — the rule file is the single source of truth; this skill executes it). Every worktree lives at `.fiber/worktrees/<slug>/` inside the repo, registered in `.fiber/worktrees.md`.

## Create

Create a worktree for a ticket and register it.

1. **Check the routing table first** (task-granularity reuse): read `.fiber/worktrees.md` — if the same unfinished task already has a worktree, reuse it; do not create a second one. One worktree per unfinished task.
2. **Ask before forking a dirty branch.** If the current branch has uncommitted work, ask the user how to proceed (per the git-working-tree rule) — never commit or stash uncommitted user work on its own.
3. **Create**: `git worktree add .fiber/worktrees/<slug>/ -b <branch>`, forked from the current local branch (throwaway) or the integration branch (destination) per the convention.
4. **Register**: append one row to `.fiber/worktrees.md` — ticket, absolute worktree path, branch name, status.

Completion: the worktree exists, is registered in the routing table, and a new session can find it.

## List

Show the routing table — the ticket → path → branch mapping, the semantic layer `git worktree list` does not have.

1. Read `.fiber/worktrees.md` and render its rows.
2. Optionally cross-check against `git worktree list` for drift (registered but removed, or existing but unregistered).

Completion: the user sees which ticket lives in which directory on which branch.

## Clean

Remove a worktree and its registration — called on resolve (throwaway) or PR merge (destination).

1. **Deregister first**: delete the row from `.fiber/worktrees.md`.
2. **Verify clean**: if the worktree holds uncommitted work, ask the user — save it (stash / commit) before removing, never delete uncommitted work.
3. **Remove**: `git worktree remove .fiber/worktrees/<slug>/`, then delete the branch if its reference job is done (per the convention: throwaway branch kept while `implement` works, deleted when the destination lands).

Completion: the worktree directory is gone, the branch is deleted or kept per the convention, and the routing table no longer references it.

## Out of scope

- **Creating worktrees outside `.fiber/worktrees/`** — the home directory is the convention; this skill does not create elsewhere.
- **Claude Code worktrees** — `EnterWorktree` and `.claude/worktrees/` are forbidden by the convention; this skill is git-native only.
- **Merging** — the convention's integration-branch flow (`feature → A → main`) is executed by the workstream, not by this skill.
