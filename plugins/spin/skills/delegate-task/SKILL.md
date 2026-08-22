---
name: delegate-task
description: Package one change task into a self-contained handoff document plus a paste-ready kickoff prompt, hand it to a clean external session for execution, then verify the result mechanically. User-invoked — the user decides what leaves the main session; the model never ships work out on its own initiative.
disable-model-invocation: true
---

# Delegate task

Move one bounded change task out of the main session. The main session writes **what** to change and **how to prove it changed**; a clean external session does the reading and typing. The main session keeps its context hot for decisions; the executor starts fresh, unburdened, and fast.

The executor works from a document, never from conversation memory; acceptance is mechanical, never vibes. Every step below enforces those two properties.

One concern per handoff. Bundling unrelated changes makes acceptance ambiguous and rework expensive; independent tasks travel as separate handoffs.

## Process

### 1. Survey the boundary

Confirm with the user:

- Which changes belong to this handoff — files and logic points — and what is explicitly out of scope.
- Which repos and branches are affected.
- Logic that must survive verbatim: per-region/per-environment differences, env-var branches, hand-tuned behavior.

Then grep/read every affected file and build the change list from code facts, not memory.

Completion: every file to be touched appears in the list, and the user confirms the boundary has no gaps.

### 2. Write the handoff document

Output to `.fiber/delegate-task/<slug>.md` (slug from task semantics). Every section must be executable by an agent with **zero** project background — assume it knows nothing; whatever it needs gets a path:

- **Background** — one paragraph: why, current state, constraints.
- **Inputs** — every file, doc, spec, or DDL the executor must read, as paths.
- **Change list** — grouped by repo or layer, one row per file: `file | change`. Files carrying preserved logic get a **manual merge** mark stating what to keep and what to change.
- **Acceptance criteria** — mechanically decidable only: greppable residue assertions ("no `String userId` remains anywhere under src/"), build commands, test commands with named baselines. No "looks right".
- **Pitfalls** — files not to touch, easily missed corners, naming and null-handling conventions.

Completion: every listed file carries a concrete change description; every criterion is mechanically checkable; a zero-background agent could execute the whole thing without asking a clarifying question.

### 3. Self-check before release

Three checks, each closing a failure mode observed in real delegations:

- **Consistency** — no two requirements contradict. Classic slip: a zero-diff zone plus a required touch-up inside it. Resolve contradictions in the document, or grant an explicit narrow exception ("comment-only edits allowed in X").
- **Closure** — every file the toolchain forces along is in the change list: tests that break compilation when their subject changes, forced imports, generated code. Walk the expected compile/test errors mentally against the list once.
- **Feasible fences** — play each prohibition against reality: if "don't touch X" collides with a test that cannot go green without touching X, the executor is trapped between two unsatisfiable orders. Fix the fence or authorize the exception explicitly.

Completion: all three checks pass; every conflict found is resolved inside the document, not left to the executor's judgment.

### 4. Generate the kickoff prompt

Emit one paste-ready block for the fresh session: the absolute path to the handoff document (its first action must be reading it), the affected repos with branches, the execution order when steps depend on each other, and the completion boundary — run tests or not, report back how.

Every kickoff prompt closes with the no-commit rule: **do not run `git commit` — complete all changes, report back, and wait.** Committing is the main session's call, made only after acceptance passes.

Completion: pasted cold, the new session's first move is reading the document — not asking what any of this is.

### 5. Accept and route findings

Verify the returned work against the document's own criteria. For anything beyond trivial, spawn a dedicated read-only sub-agent as verifier — diff against the change list for missing and out-of-bounds edits, run every greppable assertion, run builds/tests against baselines — reporting findings without fixing them. Keeping verification out-of-context protects the main session's headroom.

Route what comes back:

- **Small flaws** (a style slip, a stale comment) → fix inline in the main session now.
- **Structural misses** (wrong shape, missing piece) → write an incremental handoff and re-delegate; never let the main session silently absorb a redesign.

Completion: every acceptance criterion passes or is routed; the user confirms the result.
