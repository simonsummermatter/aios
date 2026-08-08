---
name: ob1-review
targets: [claude]
has_assets: true
description: Triage the ob1 (Open Brain) action-item queue. Invoke when the user types `/ob1-review`, says "review ob1", "triage ob1", "tidy ob1", "work through the ob1 action queue / to-dos", "clear ob1's task pile", or is working through the `[[OB1 tidied]]` habit. ob1 is a memory store, not a task tracker — this skill walks whatever landed in its action queue and, for each item, either promotes it to a real Reflect task or clears it as not-a-task, so the queue never accumulates. NOT for searching ob1 (use the `ob1` skill) and NOT for storing memories (that is automatic).
---

# ob1-review — triage the Open Brain action queue

> Why this exists: ob1 should hold almost no to-dos — real tasks live in **Reflect** (see the "Tasks" split in `~/.claude/CLAUDE.md`). Anything that still lands in ob1's action queue is either a task that belongs in Reflect, or something that was never a task. This skill drains that queue on a cadence Simon owns (his `[[OB1 tidied]]` habit).

**Read the `reflect-note` skill before promoting anything** — every Reflect write follows its rules.

Two rules shape the whole workflow:

- **Never make Simon adjudicate what a rule can decide.** Roughly half the queue is mechanically resolvable (superseded, duplicated, past-dated). That half is auto-resolved and only reported.
- **Never make Simon type prose to confirm.** The remainder goes into a mouse-driven picker where he flips only the ones the agent got wrong. In practice that is 1–3 rows per batch.

---

## The sweep

### 1. Pull the queue

`list_action_items(limit=20)` via the `open-brain` MCP, paginating with `offset=` until drained (the tool prints "… N more"). Each line carries the memory id and the item's integer index — you need both to resolve it.

**`limit`, `offset` and the "N more" count are all in MEMORIES, not items.** One memory routinely carries two to five items, and every item is one picker row. The August 2026 sweep started at 122 memories but **223 items** — a queue described as "122" that is really 223 rows makes every batch-size estimate silently ~2× too small. Count the items yourself after paginating, and quote both numbers ("51 memories / ~90 items") whenever you report queue size.

Also run `search_memory("To reconcile into Reflect")` to catch **parked fallbacks** — real tasks stored in ob1 because Reflect was unreachable at capture time. They belong in Reflect now.

### 2. Pre-decide the safe classes — but always show them

These three classes need no thought from Simon, so decide them yourself. **Never resolve them silently.** They go into the picker like everything else, in their own section at the top (`"section": "auto-resolved · evidence in each row · flip any you disagree with"`), pre-set, so a wrong call costs one click instead of vanishing unseen.

The `note` on each of these rows **must name the memory that proves it** — "DONE — #880 records you deleting both fields on 2026-08-05", not "already done". The evidence is the entire point of showing the row; without it Simon is just being asked to rubber-stamp. If you cannot cite the proof, it is not a safe class — move it to the decision section.

| Class | Test | Disposition |
|---|---|---|
| **Superseded** | a later memory states the work is done (check `search_memory` on the item's subject; ob1's `supersedes` edges also flag it) | `"done-superseded-by-#N"` |
| **Duplicate** | the same item text appears on another memory in the queue | `"duplicate-of-#N[i]"` — keep one, resolve the rest |
| **Past-dated review** | the item *is* a date that has passed ("Simon reviews the draft on 2026-08-01") | `"stale-review-date"` |

Nothing else may be pre-decided. Real work and open design questions reach the picker with no proposal stronger than a guess.

Keep the pre-decided rows' `resolve_as` (e.g. `done-superseded-by-#880`) in your own items file — the picker only returns the six states, so the precise disposition string is joined back on `(memory_id, item_index)` at apply time. If Simon flipped the row, his choice wins and `resolve_as` is discarded.

### 3. Classify the remainder into six states

Four are dispositions; two are escalations that come back to you instead of being resolved.

| State | Key | What it looks like | What happens |
|---|---|---|---|
| **promote** | `p` | a concrete next step Simon would actually do | → Reflect `+ [ ]` task, then cleared from ob1 |
| **defer** | `d` | a genuine intention, too vague to action *yet* | → bullet in the Reflect note `[[OB1 Memories: Open Questions]]` under its node heading, then cleared from ob1 |
| **clear** | `c` | already done, contingent on work that has not started, or otherwise not a task | cleared from ob1, nothing written |
| **rule** | `r` | a policy/constraint the extractor wrongly rendered as a to-do | same action as clear, separate label |
| **explain** | `e` | Simon wants more context before deciding | **not** resolved — comes back to the agent |
| **wrong** | `w` | the *memory* is factually wrong — bad fact, stale address, misattributed decision | **not** resolved — the memory is corrected in chat, then the item is re-triaged |

**Why `wrong` is separate from `explain`.** `explain` says "your proposal may be right, I need the background". `wrong` says "the proposal is beside the point — what ob1 stored is false". Triaging an item that sits on a wrong memory is wasted motion: resolving it leaves the false fact in place to poison later searches. So a `wrong` row is a **correction ticket against the memory**, not a decision about the item. Never guess the correction — the row only tells you the memory is wrong, not what the truth is; that comes from Simon in the chat afterwards.

**Why `rule` is its own label.** Mechanically it is `clear`. Diagnostically it is evidence: the extractor fix of 2026-08-03 only suppressed rules-as-tasks for `fact`/`decision`/`person_note` memories, so a nonzero `rule` count at the end of a sweep means `event`/`decision` types are still generating them and the server-side rule needs extending. Folded into `clear`, that signal is invisible. Pre-set it — Simon should rarely have to press `r`.

**Why `defer` writes to Reflect.** Deferring must not mean forgetting. ob1 has no snooze field (`resolve_action_item` only removes), so a deferred item that is merely cleared silently disappears from view. Writing it to `[[OB1 Memories: Open Questions]]` first means the queue still drains while the open question waits where Simon will meet it — when he works that node, not during an unrelated sweep.

**How the note is structured.** Two levels, and the top one is **not** free-form:

1. **`## [[➡️ NodeName]]`** — a real Reflect node, found with `reflect search "#node ➡️" --json` per the `reflect-note` node rule. Never invent a heading and never hardcode the node list. No obvious node → put the question under the closest one rather than opening a headless section.
2. **A bold top-level bullet naming the topic** (`- **Am Wasser / [[ARTEMIS.Server]]**`, `- **Versicherungen**`) — the old free-form headings live on here, one level down. Several topics under one node is normal and wanted: four network-design questions across three locations all sit under `[[➡️ AutoOps]]`.

Call that second level a **topic**, never a "project" — in Simon's PKM, *project* is the PARA bucket `🔴 PROJECTS` and means something else.

Under the topic: the question as a bold one-liner ending in `— ob1 #N`, with the background in nested sub-bullets. If a topic outgrows the note, give it its own standalone note and leave a link.

The distinction that matters most in practice: a **constraint on work that has not started** ("ensure VLAN 22 is in the allow-list *when* hardening is applied") is `rule`, not `promote`. The network-design memories are full of these.

### 4. Hand the remainder to the picker

Write a proposal file and open it:

```sh
~/.claude/skills/ob1-review/assets/run_picker.sh <items.json> <out.json>
```

`items.json`:

```json
{"title": "ob1 review — batch 1",
 "items": [{"memory_id": 857, "item_index": 0, "proposal": "promote",
            "text": "the action item verbatim",
            "note": "why this proposal — or what makes it borderline",
            "context": "one or two sentences of the parent memory"}]}
```

The picker opens in its own Ghostty window (macOS cannot start the emulator from the CLI, so the runner goes through `open -na`; the command needs a real tty, which the agent's Bash tool does not provide).

Controls: left-click or `←`/`→` cycles the four **dispositions** (`promote → defer → clear → rule`); the two escalations are off the cycle and set directly — `w` for `wrong`, `e` or a two-finger (right) click for `explain`. Cycling an escalated row puts it back on your original proposal, so a mis-hit costs one click. `p` `d` `c` `r` set the row under the cursor; `↑`/`↓`, scroll, `g`/`Home` and `G`/`End` move; `a` applies, `q` quits. On a trackpad the first click moves the cursor and the second acts on the row — that is deliberate, it stops a mis-click from changing a row Simon was not looking at.

The picker opens **on row 1 with the list scrolled to the top**, and the footer carries a progress bar (`row 12/40 · 12 seen · 28 left`) so a batch has a visible end from the first frame. "Seen" counts rows the cursor has landed on, not rows changed — most rows are right and get no keystroke.

Wait for `out.json` with a backgrounded `until [ -f out.json ]; do sleep 2; done` — not a Monitor, since it is a single completion event.

`status` in `out.json` is `applied`, `cancelled`, or `interrupted`. **`interrupted` means Simon closed the window** — the dispositions are still there and are worth re-offering as the proposals of the next round. Do not treat it as an empty result and do not apply it unasked.

**Write a real `note` on every borderline row.** It is the only context Simon gets while clicking, and it is what makes a 30-row batch take 30 seconds. Flag explicitly where the proposal is weak ("ob1 #793 parked this — flip to defer if you disagree").

**Batch size is a hard cap in rows, and the cap depends on what the batch asks for:**

| Batch kind | Cap | Why |
|---|---|---|
| **Decision** rows (`promote`/`defer` judgements) | **30 rows** | each row is a real judgement with a note to read; past 30 the batch stops being reviewed and starts being skimmed |
| **Skim** rows (auto-resolved, or a run of standing rules) | 60 rows | one glance per row against the cited evidence |

Never mix the two kinds past the decision cap: a 54-row decision batch was sent on 2026-08-07, judged bad, and abandoned with nothing applied — the whole sweep's Reflect writes were lost with it. Split instead, and put the row count and batch number in the `title` (`"ob1 review — batch 2/4 · 28 decisions"`) so Simon can see how much is left overall.

Sub-items of one task (`#827[0-4]`) stay separate rows — the resolve API is per-item — but say so in the note so Simon knows they collapse into one Reflect task.

### 5. Apply

- **promote** → write the Reflect task per the `reflect-note` skill, then `resolve_action_item(memory_id, item_index, "promoted-to-reflect")`.
- **defer** → add the bullet to `[[OB1 Memories: Open Questions]]` first — under the right `## [[➡️ Node]]` heading and topic bullet — then `resolve_action_item(memory_id, item_index, "not-yet-ready")`. Never resolve before the note is written.
- **clear** → `resolve_action_item(memory_id, item_index, "not-a-task")`.
- **rule** → `resolve_action_item(memory_id, item_index, "not-a-task-policy")`.
- **explain** → resolve nothing. Write the fuller background for each and reopen the picker with just those rows, richer `context`, and a revised `proposal`.
- **wrong** → resolve nothing, correct the memory first (see below).
- **parked fallback** → once the task is safely in Reflect, `delete_memory(id)`.

**The `wrong` loop.** After the picker closes, take the `wrong` rows into the chat one at a time — never in the same message as the apply summary, and never in a batch of ten:

1. Show the memory as stored: id, date, type, full text, and the item under it.
2. Say what you believe is wrong and what you think it should say, or ask if you cannot tell.
3. On Simon's answer, `update_memory` with the corrected text, or `delete_memory(id)` when the whole memory is false rather than merely stale. Prefer correcting to deleting — a corrected memory keeps its edges and its date.
4. Then triage the item itself. Once the memory is right, the item is usually an obvious `clear` or `rule`; if it survives as real work, it goes into the next picker batch as a normal row.

A high `wrong` count is a signal about capture, not about triage: it means memories were stored from an unverified claim. Report the count in the sweep summary.

**Mind the index shift.** `resolve_action_item` removes one element, so remaining indices on the *same* memory shift down. Resolve the **highest index first**, or re-run `list_action_items` between resolves.

Consolidate on the Reflect side: several ob1 items that are steps of one job become **one** task with the steps in its body, not five tasks.

---

## Logging the sweep

Append a one-line summary to the `[[OB1 tidied]]` note (via `reflect-note`), and log it under today's daily `AI Assistant` heading per `reflect-note` Point 7:

> 2026-08-07 — swept 33 items: 5 auto-resolved, 11 → Reflect, 17 cleared/deferred, 2 memories corrected. Queue now N memories / M items.

**Only log a sweep that finished.** A batch that came back `interrupted` or `cancelled`, or one whose Reflect writes were not made, is not a sweep — leave `[[OB1 tidied]]` untouched and say so in the chat instead. A log line claiming work that did not happen is worse than no line.

---

## Not this skill's job

- **Searching** ob1 → the `ob1` skill.
- **Storing** memories → automatic (the CLAUDE.md Open Brain protocol).
- **Running on a timer** → deliberately on-demand. The cadence is Simon's habit, not a cron.

---

## Quick reference

| Trigger | Action |
|---|---|
| `/ob1-review`, "tidy/triage ob1", `[[OB1 tidied]]` | pull → auto-resolve → propose → picker → apply |
| superseded / duplicate / past-dated | auto-resolve, report, do not ask |
| everything else | picker row with a proposal and a `note` |
| several items on one memory | resolve highest index first (indices shift) |
| more than one batch | re-run with `offset=` until drained |
| queue size | count **items**, not memories — `list_action_items` pages by memory |
| batch cap | 30 decision rows · 60 skim rows · never mix past 30 |
| row marked `defer` | write `[[OB1 Memories: Open Questions]]` first → `## [[➡️ Node]]` → topic bullet (say "topic", never "project") |
| row marked `wrong` | resolve nothing — correct the memory in chat, then re-triage the item |
| picker came back `interrupted` | re-offer as next round's proposals; do **not** log a sweep |
