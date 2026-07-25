---
name: setup-b3oy1
description: Set up this repo for the b3oy1 skill stack — orchestrate the matt-pocock setup, then relocate the agent-skills index and install the b3oy1-specific rules (tracker body safety, wayfinder planning discipline). Run once before first use of the workflow skills.
disable-model-invocation: true
---

# Setup b3oy1

Scaffold this repo for the b3oy1 skill stack. This is an **orchestration** layer on top of `setup-matt-pocock-skills` — it runs the matt setup flow, then applies the four b3oy1-specific deltas that the base setup does not cover.

Run once, before the first wayfinder / distill / commit cycle.

## What the base setup gives you

`setup-matt-pocock-skills` already scaffolds: issue tracker choice, triage label vocabulary, domain doc layout, and an `## Agent skills` index block. **Reuse that flow — do not copy its logic.** Reach for it as the first step, then layer the deltas below.

## Process

### 1. Run the base setup

Invoke the `setup-matt-pocock-skills` flow (or its outcome): explore the repo, present findings, take the user through Sections A / B / C, confirm, and write `.fiber/docs/agents/issue-tracker.md`, `.fiber/docs/agents/domain.md`, and (if `triage` is installed) `.fiber/docs/agents/triage-labels.md`.

Stop the base setup **before** it writes the `## Agent skills` index block — step 2 relocates where that block lands.

Completion: the three `.fiber/docs/agents/*.md` files exist; the user has confirmed tracker / label / domain choices.

### 2. Relocate the agent-skills index

The base setup writes the `## Agent skills` block into `CLAUDE.md` (or `AGENTS.md`). b3oy1 keeps the root agent-instruction file lean and moves the index to its own rule file.

Write the block to **`.claude/rules/agent-skills.md`** instead, using the same block body the base setup produces.

Then, if a `## Agent skills` block already exists in `CLAUDE.md` / `AGENTS.md`, **replace it in place** with a one-line pointer:

    ## Agent skills

    See `.claude/rules/agent-skills.md`.

If the block does not yet exist in the root file, do not add one — the rule file is the single source.

Completion: `.claude/rules/agent-skills.md` holds the full index; `CLAUDE.md` / `AGENTS.md` has at most a one-line pointer, never a duplicate block.

### 3. Install the tracker body-safety rule

Copy [tracker-index-edit.md](./tracker-index-edit.md) to the user project's `.claude/rules/tracker-index-edit.md`.

This makes the map / tracker-index overwrite hazard (a `gh issue edit --body-file` on a stale snapshot destroys concurrent edits) a distributed hard rule — re-fetch before edit, prefer surgical operations.

Completion: `.claude/rules/tracker-index-edit.md` exists with the re-fetch discipline.

### 4. Install the wayfinder planning-discipline rule

Copy [wayfinder-no-encroachment.md](./wayfinder-no-encroachment.md) to the user project's `.claude/rules/wayfinder-no-encroachment.md`.

This pins the "plan, don't do" seam: frontier / grilling / hand-off tickets hand off to the implementation workstream rather than writing destination code. It is a soft, attention-based constraint (independent file, repeated with the wayfinder skill body) — the user accepted it as soft, with a PreToolUse hook as the upgrade path if it fails.

Completion: `.claude/rules/wayfinder-no-encroachment.md` exists with the seam and fallback principle.

### 5. Inject sub-issue discipline into the issue tracker doc

Open `.fiber/docs/agents/issue-tracker.md` (written in step 1) and ensure the sub-issue discipline is present. The base seed already describes three tiers; b3oy1 tightens the top tier.

Append (or merge into the Wayfinding section) this overlay:

> **Sub-issue discipline.** When the tracker is GitHub, the ticket↔map relationship is expressed with **native sub-issues** — that is the canonical, UI-visible representation. Wire every child as a sub-issue of the map at creation; keep the sub-issue graph consistent as tickets are added or closed. The map body's task list and the child's `Part of #<map>` line are **fallbacks** for trackers without sub-issues, not a substitute on GitHub.

Do **not** edit the fiber seed template (`plugins/fiber/skills/setup-matt-pocock-skills/issue-tracker-*.md`) — the overlay lives in the generated doc only.

Completion: `.fiber/docs/agents/issue-tracker.md` carries the sub-issue discipline; the fiber seed is untouched.

### 6. Done

Tell the user the stack is ready, and which skills consume each artifact:

- `wayfinder`, `to-tickets`, `triage` → `.fiber/docs/agents/*.md`
- all agent sessions → `.claude/rules/agent-skills.md` (index), `.claude/rules/tracker-index-edit.md` (body safety), `.claude/rules/wayfinder-no-encroachment.md` (planning seam)

Mention they can edit any of these files directly later. Re-running this skill is only needed to switch trackers or restart from scratch.

Completion: every artifact listed above exists; the user knows the consumption map.

## Out of scope

- **marketplace registration** — this skill is bundled with the `spin` plugin but is **not** registered in `marketplace.json`. Version bumps go through `/b3oy1-manage-version`.
- **dogfood migration of this repo's own `CLAUDE.md` block** — separate task.
- **editing fiber seed templates** — the deltas are orchestration overlays, never edits to `plugins/fiber/**`.
