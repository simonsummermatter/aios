---
name: ob1-map
targets: [claude]
has_assets: false
description: Regenerate the "Open Brain Map" note in Reflect — a snapshot of what the ob1 (Open Brain) memory layer holds, plus hygiene flags. Invoke when the user types `/ob1-map`, says "update the brain map", "refresh the open brain map", "regenerate the ob1 map", or asks to update the Open Brain overview note in Reflect. This is an on-demand refresh: it overwrites the whole note from live ob1 data and re-stamps the date. Not for searching ob1 (use the `ob1` skill for that).
---

# ob1-map — Regenerate the "Open Brain Map" Reflect note

Overwrites one fixed Reflect note (`notes/open-brain-map.md`, title **Open Brain Map**)
with a fresh, timestamped snapshot of the Open Brain (`ob1`) memory layer. The note is a
**human review artifact** — a map of the brain's *shape* plus hygiene flags. It is never
hand-maintained; every run replaces the body wholesale.

> **Read the `reflect-note` skill first** — it is the source of truth for graph paths,
> the daily-note deep-link format, and write rules. This skill only edits the standalone
> note (`notes/open-brain-map.md`) and never touches daily notes above their divider.

---

## Step 1 — Collect live data from ob1 (`open-brain` MCP)

1. **`memory_stats()`** — gives everything except action-item counts:
   total, last-7-days, metadata backfill health (pending/failed), by-type breakdown,
   top ~10 people, top ~10 tags. (These are top-N only; that is all the tool returns —
   that is fine, note it in the "By domain" section.)

2. **Action-item counts** — call **`list_action_items()`**. The output is large and will
   almost certainly exceed the token budget and be **saved to a file** instead of returned.
   **Do NOT read that file into context.** Count from it with a one-liner:
   ```bash
   python3 -c "import json,re; t=json.load(open('<saved-file-path>'))['result']; \
   print('todos', t.count('- [ ]'), '| mems', len([b for b in re.split(r'\n(?=\[#\\d)', t) if b.strip().startswith('[#')]))"
   ```
   Use `todos` (total to-do lines) and `mems` (memories carrying them).

## Step 2 — Derive hygiene flags

Each run, inspect the `memory_stats` people/tags and note:

- **Fragmented person labels** — the same person under multiple labels (e.g. `Simon` vs
  `Simon Summermatter`; `Noemi` / `Noemi Gämperli` / `Naomi`). List them as dedupe candidates.
- **Action-item inflation** — if the to-do count is high relative to memories, flag that it
  mixes completed work with genuinely-pending items and needs a review pass.
- Any other obvious anomaly (large `unknown`/`other` type buckets, a metadata backfill that
  is not 0/0, etc.).

## Step 3 — Overwrite the note

Write the full body to `notes/open-brain-map.md` in the Reflect graph
(`$REFLECT_GRAPH` / see reflect-note skill). **Preserve the header block exactly**, only
updating the daily-note backlink to today's date:

```markdown
# Open Brain Map

- [[Context & Remarks]]: [[➡️ PersonalKnowledgeMgmt]] · linked from [[Cribsheet]] · snapshot logged in [[YYYY-MM-DD]]

***

- **As of YYYY-MM-DD** · <total> memories · <last7> added in last 7 days · metadata backfill <pending>/<failed>
- **What this is**: a generated snapshot of what the Open Brain (`ob1`) AI-memory layer holds …
- Full end-user manual lives in the repo: `ansibleDefaultProject/DOCUMENTATION/OB1_USER_MANUAL.md`

- **By type**
  - <type> — <count>   (one line per type, descending)

- **By domain** (top tag clusters)
  - group the top tags into themes (Smart home / Infra & OS / Config mgmt / Named projects / Data safety …)
  - _Top 10 tags only — that is all `memory_stats` returns; the full taxonomy is larger._

- **People**
  - <name> (<count>) …   (from top people)

- **Open action items**
  - **<todos> to-do lines across <mems> memories**
  - Not a curated list — auto-extracted, mixes done with pending. Needs a human review pass.

- **Housekeeping flags**
  - <derived flags from Step 2>

- **How to refresh**
  - Run `/ob1-map` in Claude Code — regenerates this note from live `ob1` data and re-stamps the date. Do not hand-edit; edits are overwritten on the next run.
```

### Write rules (from reflect-note)
- The note's reachability is already guaranteed by the permanent `[[Open Brain Map]]`
  backlink in **Cribsheet** — do not remove or duplicate it.
- Keep the `[[Context & Remarks]]: [[➡️ PersonalKnowledgeMgmt]]` first line and the `***`
  divider — they follow Simon's cribsheet convention for dedicated notes.
- Update `[[YYYY-MM-DD]]` in the header to **today** each run (`reflect today` if unsure).
- No `#tags` in the body — render any literal `#tag` in backticks (e.g. `` `#nixos` ``).
- The Reflect app re-imports and may reformat bullet markers (`-` ↔ `+`) right after a
  write; if a follow-up Edit fails with "file content has changed", re-Read and retry.

## Step 4 — Confirm

Report the new totals and any hygiene flags to the user, with the note's Reflect deep link
(`reflect open "Open Brain Map" --json` → `url`, or reference by title if launching the app
is undesirable) and today's daily deep link `reflect://daily/YYYY-MM-DD`.

---

## Notes
- **On-demand only** by design. If the user later wants it kept current automatically, wire
  it to the `schedule` skill (e.g. monthly) — do not add scheduling silently.
- The map is intentionally **structural, not per-entry** — never enumerate all memories; that
  just duplicates the database in a place that goes stale. Counts, clusters, people, flags.
