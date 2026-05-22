---
name: reflect-inbox
targets: [claude, gemini]
has_assets: false
description: >
  Process Simon's Reflect daily-note inbox on demand. Triggered ONLY when the user types `/Reflect-inbox` (case-insensitive). The skill reads the daily note for the requested date (default: today), takes everything above the `***` horizontal-rule divider (the "inbox" zone), and reorganizes it under a single `[[AI Assistant]]` top-level bullet placed immediately before `***`. Items are clustered by `#node ➡️` exactly like the `reflect-note` skill. For each non-daily backlink in the inbox whose target note has no `[[Context & Remarks:]]` first-line yet, the skill inserts that line at the top of the standalone note with the cluster node first and up to 4 related backlinks (max 5 total, no tags). Never touches anything below `***`, never edits standalone notes beyond the single Context & Remarks insert, and refuses to run if `[[Reflect tidied]]` is already checked. ALWAYS read this skill before processing the inbox.
---

# Reflect Inbox Skill

Process the **inbox zone** of a Reflect daily note (the area above the `***` horizontal-rule divider) and reorganize it under `[[AI Assistant]]` with `#node ➡️` clustering. For non-daily backlinks Simon added to the inbox, give each genuinely-new target note a `[[Context & Remarks:]]` first line so it stops being context-less.

## Relationship to `reflect-note`

This skill **builds on** `reflect-note`. Read that skill first for:

- Deep-link format (`https://reflect.app/g/{graph-id}/{noteId}`) and the rule that every Reflect note mentioned in a reply gets a clickable link.
- The node search query: `search_notes(query: "#node ➡️", searchType: "text", limit: 100)`.
- The `listName: "[[AI Assistant]]"` rule for `append_to_daily_note` (mechanically enforced by hook on Claude Code).
- Tasks (`+ [ ]`, round) vs. checkboxes (`- [ ]`, square) — preserve whichever Simon used.

This skill adds, on top of that base:

- **Inbox-zone awareness**: the `***` line splits the daily note into inbox (above) and template (below). Only the inbox is touched.
- **Positional insertion**: `[[AI Assistant]]` must end up as the **last top-level bullet before `***`**, not at the end of the note. Use `insert_at_position`, not `append_to_daily_note`.
- **`[[Context & Remarks:]]` injection** on referenced standalone notes that don't have one yet.

## Trigger

This skill fires **only** when the user types `/Reflect-inbox`. No conversational triggers, no auto-fire.

- If no date is mentioned → use **today** (read the current date from system context).
- If Simon mentions a specific date (any natural form) → use that date. Always convert to ISO `YYYY-MM-DD` for MCP calls.

## Hard rules — apply on every run

1. **Never** modify content below the `***` line in the daily note. The template section (PROJECTS / AREAS / OTHER) is Simon's hand-maintained structure.
2. **Never** modify a standalone (non-daily) note **except** to insert a single `[[Context & Remarks:]]` bullet as its very first content block. No other edits, no reformatting, nothing.
3. **Never** emit `#tag` syntax in any write. If a literal `#word` is needed, wrap it in backticks so it renders as inline code (e.g. `` `#example` ``). Tags clutter Simon's tag list.
4. **Never** tick or untick `[[Reflect tidied]]`. That checkbox is Simon's manual quality gate after he reviews what the skill did.
5. **Always** include a deep link to the daily note in the confirmation reply: `[Daily Note — Xth Month YYYY](https://reflect.app/g/{graph-id}/DDMMYYYY)`.

## Workflow

### Step 1 — Read & guard

1. `mcp__reflect-notes__get_daily_note(date: "YYYY-MM-DD")` → full markdown.
2. Locate the `***` block. If no `***` exists, abort with: *"Cannot find the `***` divider in the daily note — refusing to act."* Don't guess where it should go.
3. `mcp__reflect-notes__list_checkboxes(noteId: "DDMMYYYY")` → find a checkbox whose text is or contains `[[Reflect tidied]]`. If its checked state is `true`, refuse with:
   > *"This daily note is already marked tidied. Untick `[[Reflect tidied]]` in the Habits section if you want to process new inbox items."*

### Step 2 — Collect the inbox

The inbox is every top-level bullet (and its full nested subtree) **above** the `***` block.

- Call `mcp__reflect-notes__get_note_outline(noteId)` to get block positions. Record the `from`/`to` outer positions of each top-level inbox bullet — you'll need these in Step 7 to delete restructured originals.
- Note whether a top-level `[[AI Assistant]]` bullet **already exists** above `***` (re-run case — handled in Step 6 Case B).
- Preserve item formatting exactly: `+ [ ]` stays a task, `- [ ]` stays a checkbox, bold stays bold, sub-bullets stay nested.

### Step 3 — Search nodes

```
mcp__reflect-notes__search_notes(query: "#node ➡️", searchType: "text", limit: 100)
```

Scan the returned names and summaries. Never hardcode the node list — it grows over time.

### Step 4 — Classify each inbox item

For each top-level inbox item (skipping `[[AI Assistant]]` itself if it already exists):

- **Pick a cluster node** by judgment. Use the same "obvious match" standard as `reflect-note`. When in doubt → no node, attach directly under `[[AI Assistant]]`.
- **Identify non-daily backlinks** inside the item: any `[[Note Title]]` that is **not** a `[[YYYY-MM-DD]]` daily-note backlink. These are the candidates for the Context & Remarks step.
- **Decide whether to move the original**:
  - **Move** (delete original, place under `[[AI Assistant]]`): the skill's structured version differs meaningfully — added a node prefix, regrouped, changed nesting.
  - **Leave in place** (skip — do not duplicate under `[[AI Assistant]]`): the item is already clean and well-clustered.

### Step 5 — Context & Remarks on referenced new notes

For each non-daily backlink identified in Step 4:

1. Resolve to a noteId: `mcp__reflect-notes__search_notes(query: "<exact title>", searchType: "text", exactSearch: true, limit: 1)`.
2. `mcp__reflect-notes__get_note(noteId)` → inspect.
3. **"Obviously new" test**: is the first non-title content block a bullet whose text starts with `[[Context & Remarks:]]`?
   - **Yes** → skip. Don't touch the note.
   - **No** → proceed.
4. Build the line. Format:
   ```
   - [[Context & Remarks:]] [[➡️ ClusterNode]], [[RelatedBacklink1]], [[RelatedBacklink2]]
   ```
   - The **first** backlink after `[[Context & Remarks:]]` is the **cluster node** chosen in Step 4 — it must equal the node this item is being clustered under in `[[AI Assistant]]`. This is non-negotiable.
   - Optionally add up to 4 more related backlinks (other existing notes that genuinely add context). Comma-separated, single line.
   - **Total backlinks ≤ 5** including the cluster node. No tags. No extra prose.
5. Insert:
   ```
   mcp__reflect-notes__insert_at_top(
     noteId: "<the target note's noteId>",
     contentMarkdown: "- [[Context & Remarks:]] [[➡️ ClusterNode]], [[RelatedBacklink1]]"
   )
   ```
   This is the **only** edit allowed on the standalone note.

### Step 6 — Place / extend the `[[AI Assistant]]` subtree

#### Case A — `[[AI Assistant]]` does NOT yet exist above the line

1. From the outline (Step 2), get the **position of the `***` block**.
2. Build the full subtree as one markdown blob, with `[[➡️ NodeName]]` as the intermediate level (same indentation pattern as `reflect-note`):

   ```
   - [[AI Assistant]]
     - [[➡️ NodeA]]
       - Item 1
       - Item 2
     - [[➡️ NodeB]]
       - Item 3
     - Item with no obvious node
   ```

3. Insert immediately before `***`:
   ```
   mcp__reflect-notes__insert_at_position(
     noteId: "DDMMYYYY",
     position: <position of ***>,
     contentMarkdown: "<the subtree above>"
   )
   ```
   This makes `[[AI Assistant]]` the **last top-level bullet before `***`**.

#### Case B — `[[AI Assistant]]` already exists above the line (same-day re-run)

1. Find the existing `[[AI Assistant]]` subtree in the outline.
2. Find the position **just after the last child** of that subtree (the next sibling block — usually `***` itself if AI Assistant is currently last).
3. Look at what nodes are already nested under the existing `[[AI Assistant]]`. **Do not duplicate cluster bullets** — if `[[➡️ NodeA]]` already exists there, nest new items under the existing one rather than creating a sibling `[[➡️ NodeA]]`. To do that, find the position right after the last child of `[[➡️ NodeA]]` and insert the new items there with matching indentation.
4. For genuinely new cluster nodes, append a new `- [[➡️ NodeX]]` group under `[[AI Assistant]]` at the end.
5. Use `mcp__reflect-notes__insert_at_position` for each insertion.

### Step 7 — Remove restructured originals

For each original inbox item Step 4 marked as **moved**:

- Use its `from` / `to` outer positions from the outline captured in Step 2.
- `mcp__reflect-notes__delete_range(noteId, from, to)`.
- **Delete in reverse position order** (highest position first). Earlier positions stay valid as later blocks are removed; deleting from the top first would shift everything below and invalidate the saved positions.
- Never include the `***` block or anything below it in a delete range. The MCP refuses ranges touching the title — but it does **not** refuse ranges crossing `***`. Range boundaries are your responsibility.

### Step 8 — Confirm

Reply to Simon with a compact summary:

- One line per cluster: *"`[[➡️ NodeName]]` ← N item(s)"*.
- A separate list of standalone notes that got a new `[[Context & Remarks:]]` line, each with its deep link.
- The daily-note deep link: `[Daily Note — Xth Month YYYY](https://reflect.app/g/{graph-id}/DDMMYYYY)`.
- A reminder: *"Review and tick `[[Reflect tidied]]` when you're satisfied."*

If the inbox was empty or nothing was restructured, say so plainly and skip the daily-note write.

## Worked example

**Input** — above the `***` in today's daily note (`2026-05-16`):

```
- [[Links]]
  - [[How to Answer Any Question (Even If You Don't Know the Answer)]]
-

***
```

**Skill run**:

1. Node search returns a list including (say) `[[➡️ Resources]]`.
2. The item `[[How to Answer...]]` is judged to belong under `[[➡️ Resources]]`. The empty `-` bullet is dropped (nothing to cluster).
3. Note `[[How to Answer...]]` is resolved; its first content block is not `[[Context & Remarks:]]` → insert one:
   ```
   - [[Context & Remarks:]] [[➡️ Resources]]
   ```
   at the top of the article note.
4. Build the AI Assistant subtree and insert immediately before `***`:
   ```
   - [[AI Assistant]]
     - [[➡️ Resources]]
       - [[How to Answer Any Question (Even If You Don't Know the Answer)]]
   ```
5. Delete the original `- [[Links]]` subtree and the empty `-` bullet.

**Result** — above `***`:

```
- [[AI Assistant]]
  - [[➡️ Resources]]
    - [[How to Answer Any Question (Even If You Don't Know the Answer)]]

***
```

Everything below `***` is byte-identical to before.

**Reply to Simon**:

> Tidied today's inbox:
> - `[[➡️ Resources]]` ← 1 item
>
> Added `[[Context & Remarks:]]` to:
> - [How to Answer Any Question...](https://reflect.app/g/{graph-id}/<noteId>)
>
> [Daily Note — 16th May 2026](https://reflect.app/g/{graph-id}/16052026)
>
> Review and tick `[[Reflect tidied]]` when you're satisfied.

## MCP tools used

Read-only:
- `mcp__reflect-notes__get_daily_note`
- `mcp__reflect-notes__get_note`
- `mcp__reflect-notes__get_note_outline`
- `mcp__reflect-notes__search_notes`
- `mcp__reflect-notes__list_checkboxes`

Mutating (guarded by the Hard Rules above):
- `mcp__reflect-notes__insert_at_position` — placing the `[[AI Assistant]]` subtree just before `***`, or extending it on re-run.
- `mcp__reflect-notes__insert_at_top` — the single `[[Context & Remarks:]]` line on a referenced standalone note.
- `mcp__reflect-notes__delete_range` — removing restructured originals from the inbox (above-`***` only).

Deliberately **not** used:
- `append_to_daily_note` — appends at the bottom of the note, but `[[AI Assistant]]` must sit immediately before `***`. Positional insert is required.
- `create_note` — this skill does not create new notes. If Simon pasted a URL above the line, Reflect already auto-created a link note; just treat it as a backlink.
- Any tool that would edit content below `***` or rewrite a standalone note's body.
