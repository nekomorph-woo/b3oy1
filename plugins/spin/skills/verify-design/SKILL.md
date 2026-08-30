---
name: verify-design
description: Design the verification chain before code moves — anchor table, judgment ladder, audit plan. Fires when a spec lands (after to-spec or grilling), when work is about to be delegated or run AFK, and when a bugfix feedback loop needs designing.
---

# Verify Design

Every acceptance item stands on three decisions: which **anchor** (fact source) it rests on, which rung of the **ladder** (judgment form) judges it, and how the **audit** (freeze, rerun, sampling) keeps it honest. Design those three before any code moves — a chain designed after the code is a defense, and defenses get argued down. The unit of design is the item; the product is a chain document an executor and an auditor can run without you.

## Principles

| Principle | What it rules |
|-----------|---------------|
| **Anchor-first** | An item that cannot name its fact source is a question, not an item. Questions go back to the interview. |
| **Climb the ladder** | Push each item's judgment to the highest rung it reaches. A downgrade below command states its reason beside the item. |
| **Separated judges** | Chain author, implementer, and auditor are three roles. One artifact never judges itself; an LLM judge reads the work blind of the authoring context. |
| **Adversarial quota** | Negative and punishing entries are a fixed allowance of every chain, waived only in writing. |
| **Audit radius** | Freeze + independent rerun + sampling rate together define how much the chain's green is worth. Final summaries are claims; verification handles are facts. |

## Process

### 1. Classify the archetype

Read the task and pick its row from the binding table below. Two archetypes in one task → the chain is the union, designed in both parts. The table binds anchor types, the ladder target, and the loop per archetype; worked specimens live in [reference/bindings.md](reference/bindings.md).

| Archetype | Anchor types | Ladder target | Loop | Quota emphasis |
|-----------|--------------|---------------|------|----------------|
| **bugfix** | the observed failure (strongest anchor — it happened) | command: the red-capable repro | red → green → regression (drive `diagnosing-bugs` Phase 1) | regression at a correct seam; a missing seam is itself a finding |
| **feature** | business rules + example scenarios (rules are the bulk; scenarios illustrate) | command per item; scenarios readable by the human | interview → spec → items → implementation | adversarial entries on boundaries and invalid input |
| **refactor / legacy** | invariants: behavior before == after | mechanical oracle: golden master / snapshot equivalence | freeze the master → transform → diff | consistency anchors on every neighbor the change could bend |
| **decision / core domain** | human value judgment | human for meaning; command for structural properties only (dependency direction, blast radius) | ADR + human-review queue | scope: what the decision rules out is verified by absence |
| **ux / prototype** | the human's walk | human walk-states; mechanical for regressions only (visual diff thresholds) | prototype → human walk → iterate | none — the human is the runner |
| **agent behavior** | eval set + error-analysis buckets | differential on frozen task set; LLM-judge only sandboxed | error analysis → chain revision → re-run | contamination checks; judge separated from author model |

**Completion:** the archetype is named in the chain document, with the binding row cited.

### 2. Build the anchor table

One row per acceptance item: **item | anchor | judge command (draft)**. Anchors, in descending strength: an observed failure, a business rule agreed in the interview, a contract clause (precondition / postcondition / invariant), a frozen behavior snapshot, a human judgment. When the expected outcome of an item cannot be stated, write it as an open question and route it back to the interview — an unstated expectation becomes a guessed command, and guessed commands are how chains lose their meaning.

**Completion:** every item carries an anchor and a draft command; open questions are logged and routed, never silently dropped.

### 3. Climb the ladder

Push each item's judgment to the highest rung it reaches:

| Rung | Form | Note |
|------|------|------|
| **command** | exit code / diff / grep / cmp — deterministic, independently rerunnable | the default target |
| **oracle** | property check, golden-master comparison, mutation score — deterministic with a harness | the harness freezes with the chain |
| **differential** | old-vs-new or A-vs-B on a frozen input set | pin the inputs first |
| **judge** | LLM-as-judge, sandboxed: frozen rubric, structured verdict **citing evidence spans**, judge separated from the author model, and its verdict **ranks work for human eyes** — it is a router for review, standing alone as the single gate for an item is a defect | the residual rung for dimensions with no mechanical alternative (clarity, feel) |
| **human** | walk, review, sign-off | core domain and meaning |

Judge commands are written for the audit environment, not the author's: literal pattern matches use fixed-string forms (`grep -F`) — a pattern whose meaning depends on tool dialect (`\s` in grep) is a defect the auditor's rerun exists to catch. And a command is written for the *time* it runs: a baseline pin (`HEAD == <sha>`) is a one-shot kickoff precondition, and its rerunnable form is ancestry (`merge-base --is-ancestor`) — after the work lands, equality is false by design.

**Completion:** every item names its rung; every item below command carries a one-line downgrade reason.

### 4. Quotas

Three families are mandatory in every chain, waivable only in writing:

- **Adversarial entries** — invalid input, boundary values, punishing cases ("done on a missing id exits non-zero"). Aim for roughly one per five items.
- **Side-effect locks** — assertions that untouched things stayed untouched (byte-compare a snapshot, grep for forbidden residue).
- **Consistency anchors** — one neighbor behavior frozen verbatim, so silent drift gets caught (lock a sibling command's output before and after).

**Completion:** all three families appear in the chain, or a written waiver names the reason per family.

### 5. Emit the audit plan

- **Freeze** — the chain author and the implementer are different roles; the chain freezes at kickoff, and post-freeze changes enter through the auditor as change entries. The auditor keeps a byte-copy of the frozen chain at kickoff: freeze is verified against that copy, never against memory.
- **Rerun set** — every judge command runnable standalone by someone who never saw the implementation. Commands are idempotent, or declare their one-shot semantics with their first-run evidence recorded; one-shot preconditions are rewritten in ancestry form before the chain freezes. The auditor's verdicts are written after the rerun, never before, and post-freeze chain edits land as scripted amendments followed immediately by a rerun of the amended command.
- **Sampling rate** — which items the human re-verifies personally (default: every item below command, plus a fixed sample of the rest). The rate is the chain's trust radius — set it by the cost of a silent miss.
- **Routing** — items on the core layer (per the project's core-first rule) route to the human-review queue regardless of rung.

**Completion:** the chain document exists with anchor table, rungs, quotas, and audit plan; a machine-readable JSON form accompanies it when the work is delegated or run AFK (frozen `criteria` array, `passes` fields the executor flips, `note` per item).

### 6. Hand off

The chain travels with the work: the JSON form goes into the kickoff prompt (delegate-task / afk-implement), the human-readable table goes onto the spec or ticket. The kickoff closes with the no-commit rule — the executor completes, reports, and waits; committing happens after acceptance. Size the executor's turn budget to roughly `8 + 2 × items` — the flip phase alone costs one turn per item, and a budget that clips mid-flip hands the remaining flips to the auditor.

**Completion:** the executor's kickoff reads the chain as its first act; the auditor knows their rerun set before the first change lands.

## Boundaries

- **Design, not run.** This skill emits chains; executing them belongs to implement / delegate-task / afk-implement, and the closing verdict to the project's verify flow.
- **The chain freezes at kickoff.** Everything after that is change entries through the auditor — the implementer edits code, the chain edits through review.
- **Waivers are written.** A quota skipped silently is a chain pretending to cover what it dropped.
