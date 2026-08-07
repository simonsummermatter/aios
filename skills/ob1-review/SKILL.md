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

Also run `search_memory("To reconcile into Reflect")` to catch **parked fallbacks** — real tasks stored in ob1 because Reflect was unreachable at capture time. They belong in Reflect now.

### 2. Auto-resolve the safe classes — no questions asked

Resolve these without consulting Simon, then **report what was auto-resolved** so he can veto:

| Class | Test | Disposition |
|---|---|---|
| **Superseded** | a later memory states the work is done (check `search_memory` on the item's subject; ob1's `supersedes` edges also flag it) | `"done-superseded-by-#N"` |
| **Duplicate** | the same item text appears on another memory in the queue | `"duplicate-of-#N[i]"` — keep one, resolve the rest |
| **Past-dated review** | the item *is* a date that has passed ("Simon reviews the draft on 2026-08-01") | `"stale-review-date"` |

Never auto-resolve anything else. Real work and open design questions always reach the picker.

### 3. Classify the remainder into three buckets

| Bucket | What it looks like | What happens |
|---|---|---|
| **promote** | a concrete next step Simon would actually do | → Reflect `+ [ ]` task, then cleared from ob1 |
| **clear** | a rule, constraint, prohibition, settled decision, or something already done | cleared from ob1, nothing goes to Reflect |
| **defer** | a genuine intention, too vague to action *yet* | action flag cleared, memory text stays as a plain statement |

The distinction that matters most in practice: a **constraint on work that has not started** ("ensure VLAN 22 is in the allow-list *when* hardening is applied") is `clear`, not `promote`. The network-design memories are full of these.

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

The picker opens in its own Ghostty window (macOS cannot start the emulator from the CLI, so the runner goes through `open -na`; the command needs a real tty, which the agent's Bash tool does not provide). Simon clicks a row to cycle `promote → clear → defer`, or uses `p`/`c`/`d`, then `a` to apply. `out.json` appears with the confirmed dispositions.

Wait for it with a backgrounded `until [ -f out.json ]; do sleep 2; done` — not a Monitor, since it is a single completion event.

**Write a real `note` on every borderline row.** It is the only context Simon gets while clicking, and it is what makes a 30-row batch take 30 seconds. Flag explicitly where the proposal is weak ("ob1 #793 parked this — flip to defer if you disagree").

Keep batches to ~30 rows. Sub-items of one task (`#827[0-4]`) stay separate rows — the resolve API is per-item — but say so in the note so Simon knows they collapse into one Reflect task.

### 5. Apply

- **promote** → write the Reflect task per the `reflect-note` skill, then `resolve_action_item(memory_id, item_index, "promoted-to-reflect")`.
- **clear** → `resolve_action_item(memory_id, item_index, "not-a-task")`.
- **defer** → `resolve_action_item(memory_id, item_index, "not-yet-ready")`.
- **parked fallback** → once the task is safely in Reflect, `delete_memory(id)`.

**Mind the index shift.** `resolve_action_item` removes one element, so remaining indices on the *same* memory shift down. Resolve the **highest index first**, or re-run `list_action_items` between resolves.

Consolidate on the Reflect side: several ob1 items that are steps of one job become **one** task with the steps in its body, not five tasks.

---

## Logging the sweep

Append a one-line summary to the `[[OB1 tidied]]` note (via `reflect-note`), and log it under today's daily `AI Assistant` heading per `reflect-note` Point 7:

> 2026-08-07 — swept 33: 5 auto-resolved, 11 → Reflect, 17 cleared/deferred. Queue now N.

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
