---
name: suggest-tickets-bag
description: After to-tickets slices a spec into tickets, restate every ticket in one plain-language line (what user-visible behavior it builds, which spec section it maps to), then suggest how they group into implementation bags. A bag is a merge proposal — a confirmed bag becomes ONE work order (one AFK batch, one report), not N tickets wearing a label. Reason stated for every bag AND every ticket kept standalone. Invoked by the model right after a to-tickets run; output goes to the console for the user to judge.
---

# Suggest tickets bag

Review the tickets that `to-tickets` just created, and suggest how they group into **bags** — and a bag is a **merge proposal**, not a grouping view.

A confirmed bag becomes **one work order**: one AFK batch, one report, one review (see `afk-implement`). Its member tickets stop being individually tracked deliverables and become the bag's internal steps. The test of a useful suggestion: it changes how many things get created, tracked, and reviewed. Thirty thin tickets becoming five work orders is the win; thirty tickets wearing five labels is decoration. If the next step you propose is still "create the tickets as sliced", the bagging failed.

The skill exists because over-sliced tickets are the fuel for reviewer fatigue: thirty thin tickets reviewed one by one drain the human far faster than five well-shaped bags. Grouping happens **before** the fatigue, at slice time, when merging is still free.

## Process

### 1. Read the fresh batch

Collect the tickets `to-tickets` just created — titles, acceptance criteria, and blocking edges.

Completion: every ticket from the run is in hand, with its acceptance criteria read.

### 2. Restate each ticket in plain language

Ticket wording straight out of `to-tickets` is often opaque — the user scans the batch and cannot tell what each ticket actually builds. For every ticket, write one plain-language line:

> **#NN** — builds: <the user-visible behavior, in one sentence> · spec: <which section it implements>

Two hard flags:

- **Unrestatable** — the behavior cannot be said in one plain sentence; the ticket is probably fused or vague. Recommend a re-slice.
- **Untraceable** — no spec section backs it. Recommend re-slicing or dropping, never silent implementation.

This manifest doubles as the reconciliation baseline: when `afk-implement` later reports per-ticket acceptance, it checks against these restated promises — the before-list of plain-language commitments the after-report answers to.

Completion: every ticket carries its one-line restatement with a spec anchor, or is flagged as unrestatable / untraceable.

### 3. Propose bags

Partition the batch into bags. A bag is a set of tickets the AI can implement in one batch without losing the thread. Typical bag glue:

- same module or same seam — one context window covers them;
- shared fixture / shared scaffolding — one setup serves them all;
- one vertical slice — the tickets only make sense together;
- total size fits one AFK batch (aim for 3–8 tickets per bag).

Slicing granularity is itself on the table: a bag may propose merging tickets that share a seam or whose acceptance criteria overlap — the bag's acceptance is the **union** of its members', its plain-language line unions their restatements. Treat the incoming slice as raw material, not a fixed partition.

### 4. State the reason for every bag — and for every standalone

Both directions are mandatory. A suggestion without its reason is noise the user has to reconstruct:

- **Bagged → why together**: the glue from step 2, in one line.
- **Standalone → why alone**: the disqualifier, in one line. Typical ones:
  - acceptance criteria name another ticket or module — cross-module, the user reviews it personally;
  - touches the frozen layer (vocabulary / contracts / state machines / interface shape) — needs a decision first;
  - risks out of proportion to the rest of the batch — deserves its own spotlight;
  - genuinely independent — no shared context, bagging buys nothing.

Completion: every ticket belongs to exactly one bag or one standalone entry, and every entry — bag or standalone — carries its one-line reason.

### 5. Output to console, then stop

Print the suggestion to the console: the plain-language manifest (step 2, flags included), then each bag with its tickets and reason, each standalone with its reason. The user merges, splits, or confirms — **never apply the grouping yourself**. Ticket bodies stay untouched: this skill reads tickets, it does not edit them.

**Suggest the next move in bag terms.** For each confirmed bag: merge it into one work order on the tracker — one ticket whose acceptance unions its members', the rest closed as merged (or one bag label, where the tracker makes merging awkward) — then hand that bag to `afk-implement`. Recommending "create the tickets as sliced", at the original to-tickets count, discards the suggestion this skill just made. And the confirmation must land on the tracker, not just this console: a later `afk-implement` session finds its bag there.

Completion: the suggestion is printed; control returns to the user. The next move is suggested in bag terms, not started.
