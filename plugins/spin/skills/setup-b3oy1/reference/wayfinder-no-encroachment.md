# Wayfinder planning does not implement

Wayfinder is **plan, don't do**. Planning sessions (map open, tickets at the frontier) decide *what* to build and *where* the seams go. They do not write the destination's code.

## The seam

A ticket's state tells you whether you plan or do:

- **Frontier / grilling / hand-off** → you are still planning. Hand the work off — leave the wayfinder session; implementation happens elsewhere (to-spec → implement, or implement directly). Do not write destination code. This rule does not prescribe *how* the implementation workstream isolates its work (branch, worktree, container — that is the runtime's concern); it only marks the seam.
- **Closed / handed off** → the implementation workstream owns it. That is where code gets written.

## Hand off regionally — the map does not have to clear first

The trigger for implementation is a **settled region**, not the empty frontier. A region is settled when its tickets are closed and their decisions compose into something buildable that waits on no open question. When a session's resolution completes a region, **recommending the hand-off is planning work**: name the region, point the user at `to-spec` → `to-tickets` → `implement` for it, and keep the map open — wayfinding continues on the rest.

- Waiting for the whole map produces one giant spec and a front-loaded waterfall — the highest-cost failure of from-zero projects. Decisions decay while unimplemented, and implementation returns facts that redraw the remaining fog: explore a region, build it, let what it teaches reopen the map.
- **Region test.** The closed decisions compose; no open ticket blocks the build; nothing in *Not yet specified* hangs on the region's premises. Buildability waiting on an open question → not settled, keep wayfinding.
- **Cadence.** Every settled region, every time — not once at the end. During implementation the map stays the cockpit: batch reports (`afk-implement`) flow back as new fog and change tickets, and the next region sharpens from real code instead of speculation.
- The core's settling is the first such region — the core-volume spec (see the core-first rule); business regions repeat the same pattern.

## Strong signal: do not cross

Inside a wayfinder session, do **not** enter the "plan mode + ask the user for consent to write destination code" pattern. That is the encroachment slip — planning dressed as implementation. The output of planning is decisions, tickets, and pointers, not source files.

## Naturally exempt

`task` / `prototype` / `research` tickets produce facts, throwaway artifacts, or small state-mutating actions (registering an account, moving data) by design. They are not destination code. This rule does not block them.

## Fallback principle

If you feel the pull to write destination code directly during planning, you are at the **map's edge** — that is exactly the hand-off point. Write a ticket, point at it, and stop.
