---
name: ob1-review
targets: [claude]
has_assets: false
description: Triage the ob1 (Open Brain) action-item queue. Invoke when the user types `/ob1-review`, says "review ob1", "triage ob1", "tidy ob1", "work through the ob1 action queue / to-dos", "clear ob1's task pile", or is working through the `[[OB1 tidied]]` habit. ob1 is a memory store, not a task tracker — this skill walks whatever landed in its action queue and, for each item, either promotes it to a real Reflect task or clears it as not-a-task, so the queue never accumulates. NOT for searching ob1 (use the `ob1` skill) and NOT for storing memories (that is automatic).
---

# ob1-review — triage the Open Brain action queue

> Why this exists: ob1 should hold almost no to-dos — real tasks live in **Reflect** (see the "Tasks" split in `~/.claude/CLAUDE.md`). Anything that still lands in ob1's action queue is either a task that belongs in Reflect, or something that was never a task. This skill drains that queue on a cadence Simon owns (his `[[OB1 tidied]]` habit), keeping a human in the loop for every disposition.

**Read the `reflect-note` skill before promoting anything** — every Reflect write follows its rules.

---

## The sweep

1. **Pull a batch.** `list_action_items(limit=20)` via the `open-brain` MCP. The tool paginates (`offset=`) and can filter with `since="YYYY-MM-DD"`. Each line shows the memory id and the item's integer index — you need both to resolve it.
2. **Also catch parked fallbacks.** `search_memory("To reconcile into Reflect")` — these are real tasks parked in ob1 because Reflect was unreachable at capture time. They belong in Reflect now, not in ob1.
3. **Classify each item** into exactly one bucket:

   | Bucket | What it looks like | Disposition |
   |---|---|---|
   | **Real & ready** | a concrete next step Simon would actually do | **Promote to Reflect** as `+ [ ]` under `AI Assistant`, then clear from ob1 |
   | **Not a task** | a rule, prohibition, fact, settled decision, or something already done | **Clear** from ob1; nothing goes to Reflect |
   | **Not yet ready** | a genuine intention but too vague to action | **Clear the action flag**, keep the memory text as a plain statement |

4. **Propose, don't act.** Present the batch as a numbered list — each with its `#memory_id[index]`, the item text, and your proposed disposition. Ask Simon to confirm or override (e.g. "all as proposed, or change any?"). Human-in-loop, exactly like `/ob1`.
5. **Apply confirmed items only:**
   - **Promote:** write the Reflect task per the `reflect-note` skill, then `resolve_action_item(memory_id, item_index, "promoted-to-reflect")`.
   - **Clear / not-a-task / not-yet-ready:** `resolve_action_item(memory_id, item_index, "not-a-task")` (or a fitting disposition string). The memory text is untouched; only the queued action item is removed.
   - **Parked fallback memory:** once the task is safely in Reflect, remove the holding copy with `delete_memory(id)`.
6. **Mind the index shift.** `resolve_action_item` removes one element, so the remaining indices on the **same** memory shift down. When clearing several items from one memory, resolve the **highest index first**, or re-run `list_action_items` between resolves.
7. **Repeat** with `offset=` until the queue is drained (the tool prints "… N more. Re-run with offset=…").

---

## Logging the sweep

After the batch, append a one-line summary to the `[[OB1 tidied]]` note (via the `reflect-note` skill) — date plus counts, e.g.:

> 2026-08-03 — swept 24: 5 → Reflect, 17 cleared, 2 parked-fallbacks reconciled. Queue now 0.

Also log it under today's daily `AI Assistant` heading per `reflect-note` Point 7.

---

## Not this skill's job
- **Searching** ob1 → the `ob1` skill.
- **Storing** memories → automatic (the CLAUDE.md Open Brain protocol).
- **Running on a timer** → deliberately on-demand. The cadence is Simon's habit, not a cron.

---

## Quick reference

| Trigger | Action |
|---|---|
| `/ob1-review`, "tidy/triage ob1", `[[OB1 tidied]]` | `list_action_items(limit=20)` → classify → propose → confirm → resolve |
| real & ready item | promote to Reflect (`+ [ ]`), then `resolve_action_item(id, idx, "promoted-to-reflect")` |
| not a task / not yet ready | `resolve_action_item(id, idx, "not-a-task")` |
| parked "To reconcile into Reflect" memory | move to Reflect, then `delete_memory(id)` |
| several items on one memory | resolve highest index first (indices shift) |
| more than one batch | re-run with `offset=` until drained |
