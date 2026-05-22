---
name: ob1
targets: [claude, gemini]
has_assets: false
description: Invoke for explicit Open Brain memory search — when the user types `/ob1 TOPIC`, says "search memory for X", "check ob1 for X", "what do I know about X", "pull up context on X", or asks what's stored about a past project, server, decision, fix, preference, or framework. Also invoke when user asks "what is new in ob1" or "what's new in open brain" (search the database for recent entries). Also invoke when user types bare `/ob1` with no topic (review current conversation for noteworthy content to store). Also invoke proactively at the very start of any session — ob1 is the memory layer for all AI interactions, not just technical ones. The CLAUDE.md always-active protocol handles background storing; this skill adds the explicit search-and-display layer on top.
---

# ob1 — Open Brain Memory Search

> The always-active storing protocol lives in `~/.claude/CLAUDE.md` (under "Open Brain") and is in effect every session automatically. This skill adds explicit search capability and richer session-start context loading on top of that baseline.

---

## On explicit invocation: `/ob1 <topic>`

1. **Search** — call `search_memory("<topic>")` via the `open-brain` MCP.
2. **Display** — present results in full (don't truncate or summarize). Group by type if multiple entries: `fact` / `decision` / `fix` / `idea`.
3. **Acknowledge** — briefly note what was found, or flag if nothing relevant is stored yet.

For broad topics, run two or three focused searches rather than one generic one.
Example: `/ob1 ansible` → search both `"ansible"` and `"MNEME deployment"`.

---

## Bare invocation: `/ob1` (no topic)

When the user types just `/ob1` with no topic, **do not search** — instead review the current conversation and identify what is worth storing:

1. **Scan** — read back through the current conversation for: decisions made, errors fixed, infrastructure facts confirmed, non-obvious configs that worked, preferences revealed, frameworks or protocols described.
2. **Propose** — present a numbered list of candidate memories to the user. For each, show the formatted entry (using the templates below) and the type (`fact` / `decision` / `fix` / `idea` / `preference` / `framework`).
3. **Confirm** — ask the user which ones to store (e.g. "Store all? Or pick numbers?").
4. **Store** — if there are 2 or more confirmed entries, call `batch_store_memories(memories=[...])` with all of them in a single call. Only use `store_memory()` for a single entry.

**Filter aggressively** — only surface things that would genuinely help a future AI with zero context. Skip anything already in code, docs, or git history.

---

## "What is new in ob1?" / "What's new in open brain?"

When the user asks what is new or recent in the Open Brain, **search the database** — do not describe changes to the skill file itself.

1. Call `memory_stats()` to get the overview (total, by type, recent activity).
2. Call `list_memories()` or `search_memory("recent")` to surface the most recently added entries.
3. Present the newest entries grouped by type, with dates if available.
4. Briefly summarize what areas have seen new activity.

---

## Proactive session-start search

At the start of **every session**:

1. Identify the topic from the user's opening message.
2. Call `search_memory("<topic>")` before or in parallel with your first response.
3. Weave relevant memories into your reply as active context — don't announce you searched, just arrive prepared.

---

## Mid-session reinforcement

Context dilutes over long sessions. As a reminder — the standing storage rules from CLAUDE.md:

| Moment | What to store |
|--------|--------------|
| Non-obvious decision made | The decision + the reasoning |
| Error fixed | The fix + the root cause |
| Infrastructure fact confirmed | Host, port, path, service name |
| Config confirmed working | The exact config detail |
| Personal preference revealed | How Simon likes things done |
| Framework or protocol described | Simon's approach to a repeatable task |
| Life fact surfaced | Personal/professional context not in any doc |

**Never store:** anything in code, git history, or official docs.
**One fact per entry** — never merge multiple facts into one memory string.
**Batching:** When storing 2+ entries, always use `batch_store_memories(memories=[...], source="...")` — it runs all API calls in parallel and is dramatically faster than N sequential `store_memory()` calls.
**Write for a future AI with zero context** — name the host, project, person, or context explicitly.

### Entry templates

**Decision:** "Decided to [X] on [host/component] because [reason]. Alternative [Y] rejected because [reason]."

**Fix:** "Fixed [error] on [host] by [solution]. Root cause was [cause]."

**Fact:** "[Host/component/person/context] [fact not in the code or docs]."

**Preference:** "Simon prefers [X] when [context]. Reason: [why]."

**Framework:** "Simon's [task] protocol: [steps/rules]."

---

## Quick reference

| Trigger | Action |
|---------|--------|
| `/ob1 <topic>` | `search_memory("<topic>")` → display full results |
| `/ob1` (bare) | Scan current conversation → propose candidates → confirm → store |
| "what's new in ob1/open brain?" | `memory_stats()` + recent entries from database |
| Session starts on known topic | `search_memory("<topic>")` silently, weave into context |
| 1 entry to store | `store_memory("…")` |
| 2+ entries to store | `batch_store_memories(memories=["…", "…", …])` |
| Already in code/docs | Skip |
