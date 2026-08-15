---
name: suggest-tickets-bag
description: After to-tickets slices a spec into tickets, review the fresh batch and suggest how they group into implementation bags — with the reason stated for every bag AND for every ticket kept standalone. Invoked by the model right after a to-tickets run; output goes to the console for the user to judge.
---

# Suggest tickets bag

Review the tickets that `to-tickets` just created, and suggest how they group into **bags** — units the AI can implement in one AFK batch (see `afk-implement`).

The skill exists because over-sliced tickets are the fuel for reviewer fatigue: thirty thin tickets reviewed one by one drain the human far faster than five well-shaped bags. Grouping happens **before** the fatigue, at slice time, when merging is still free.

## Process

### 1. Read the fresh batch

Collect the tickets `to-tickets` just created — titles, acceptance criteria, and blocking edges.

Completion: every ticket from the run is in hand, with its acceptance criteria read.

### 2. Propose bags

Partition the batch into bags. A bag is a set of tickets the AI can implement in one batch without losing the thread. Typical bag glue:

- same module or same seam — one context window covers them;
- shared fixture / shared scaffolding — one setup serves them all;
- one vertical slice — the tickets only make sense together;
- total size fits one AFK batch (aim for 3–8 tickets per bag).

### 3. State the reason for every bag — and for every standalone

Both directions are mandatory. A suggestion without its reason is noise the user has to reconstruct:

- **Bagged → why together**: the glue from step 2, in one line.
- **Standalone → why alone**: the disqualifier, in one line. Typical ones:
  - acceptance criteria name another ticket or module — cross-module, the user reviews it personally;
  - touches the frozen layer (vocabulary / contracts / state machines / interface shape) — needs a decision first;
  - risks out of proportion to the rest of the batch — deserves its own spotlight;
  - genuinely independent — no shared context, bagging buys nothing.

Completion: every ticket belongs to exactly one bag or one standalone entry, and every entry — bag or standalone — carries its one-line reason.

### 4. Output to console, then stop

Print the suggestion to the console: each bag with its tickets and reason, each standalone with its reason. The user merges, splits, or confirms — **never apply the grouping yourself**. Ticket bodies stay untouched: this skill reads tickets, it does not edit them.

Completion: the suggestion is printed; control returns to the user. The next move (usually `afk-implement` on a confirmed bag) is suggested, not started.
