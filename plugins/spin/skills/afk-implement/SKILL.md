---
name: afk-implement
description: Run one implementation batch while the user is away, inside explicit fences, and end with a structured handoff report. Use when the user announces they are going AFK for implementation — the fences and the closing report are what keep "away" from becoming "lost".
---

# AFK implement

Work one bag of tickets end to end while the user is away, then hand the wheel back with a report they can **drive by** — the user reads the report, not the diff.

AFK without a closing report is how a project drifts: tickets get implemented one after another, nothing forces anything to flow back, and the human returns owning a codebase they no longer understand. The fences below prevent the AI from improvising past its authority; the report guarantees the return has structure.

## Process

### 1. Declare the fences

AFK semantics take effect at invocation. State them, then hold them for the whole batch:

- **Batch-internal freedom.** The AI decides per-ticket technical choices and in-bag ordering on its own.
- **Batch-boundary stop.** The AI never cuts the next batch, opens new tickets, edits the spec or the MAP, touches the frozen layer (vocabulary / contracts / state machines / interface shape), or merges onto main.
- **Hit the wall → stop, don't route around.** A ticket needing anything beyond the fences (a contract change, an acceptance criterion with no grounding, a behavior-level change to an earlier ticket's output) is **not** worked around: stop at that ticket, draft a change ticket, put the draft in the report. A drafted change ticket links the old ticket and states what assumption it no longer holds — closed tickets are an append-only ledger, never edited.
- **Acceptance criteria are non-negotiable.** Discovering a criterion is unreasonable is hitting the wall: report it, never quietly lower it.

Completion: the fences are stated in the session before the first ticket starts.

### 2. Work the bag

Drive the stack's implementation skill (`implement`, which drives `tdd`) ticket by ticket through the confirmed bag. Commit each finished ticket with `snap`.

Completion: every ticket in the bag is either done (tests green, acceptance criteria met item by item) or stopped-at with a change-ticket draft.

### 3. The batch report — the batch is not done without it

The report is the up-gate of the batch; **a batch without its report is incomplete**, no exceptions. Five sections, in this order:

1. **Per-ticket summary** — what was done and the key tradeoff, 2–3 lines each. Not a diff. Module-internal tickets whose acceptance names no other ticket or module get one line each — the report's body is reserved for what the user must see.
2. **Frozen-layer reconciliation** — did this batch touch vocabulary / contracts / state machines / interface shape? Untouched → one line saying so. Touched → red-line event, flagged at the top, the user intervenes.
3. **Change-ticket drafts** — every hit wall, with the old ticket it links and the assumption that no longer holds. Awaiting user approval.
4. **New fog** — where implementation contradicted spec assumptions. These flow back into the MAP's *Not yet specified* section: the MAP stays open as the cockpit during implementation — Decisions are the settled direction, *Not yet specified* is the radar, reflowed tickets are the live traffic.
5. **Slicing suggestions for uncut tickets** — "having built this batch, ticket #NN's slice should be cut differently". This is the input `suggest-tickets-bag` feeds on next round; it comes from real code, which is why it is the orchestration layer's most valuable input.

Completion: all five sections are written and delivered to the console.

### 4. Suggest and stop

End the report with a suggested next step — usually "approve the change-ticket drafts" or "cut the next bag" — and **stop**. Never auto-advance to the next batch. The user steers every transition between batches; that is the difference between AFK and lost.

Completion: the suggestion is made and the session stops, waiting for the user.
