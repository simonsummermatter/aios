---
name: reflect-inbox
targets: [claude]
has_assets: false
description: >
  Process Simon's Reflect daily-note inbox on demand. Triggered ONLY when the user types `/Reflect-inbox` (case-insensitive). The skill reads the daily note for the requested date (default: today), takes everything above the `***` horizontal-rule divider (the "inbox" zone), and reorganizes it under a single `[[AI Assistant]]` top-level bullet placed immediately before `***`. Items are clustered by `#node ➡️` exactly like the `reflect-note` skill. For each non-daily backlink in the inbox whose target note has no `[[Context & Remarks:]]` first-line yet, the skill inserts that line at the top of the standalone note with the cluster node first and up to 4 related backlinks (max 5 total, no tags). Never touches anything below `***`, never edits standalone notes beyond the single Context & Remarks insert, and refuses to run if `[[Reflect tidied]]` is already checked. ALWAYS read this skill before processing the inbox.
---

# Reflect Inbox Skill

Process the **inbox zone** of a Reflect daily note (the area above the `***`
horizontal-rule divider) and reorganize it under `[[AI Assistant]]` with `#node ➡️`
clustering. For non-daily backlinks Simon added to the inbox, give each
genuinely-new target note a `[[Context & Remarks:]]` first line so it stops being
context-less.

Reflect Open is local-first markdown. There is no MCP and no REST API — you read
through the `reflect` CLI and write by **editing the note's markdown file
directly**. The running app re-imports edits automatically. Because you edit the
raw markdown text, the old block-position arithmetic is gone: splitting on `***`
and rebuilding the inbox is plain string manipulation.

## Relationship to `reflect-note`

This skill **builds on** `reflect-note`. Read that skill first for:

- The graph path, the `reflect` CLI commands, and the file format.
- Deep-link format (`reflect://daily/YYYY-MM-DD`, `reflect://note/<id>`) and the rule
  that every Reflect note mentioned in a reply gets a clickable link.
- The node search query: `reflect search "#node ➡️" --json`.
- The `- [[AI Assistant]]` placement rule for daily-note writes (2 spaces per level).
- Tasks (`+ [ ]`, round) vs. checkboxes (`- [ ]`, square) — preserve whichever
  Simon used.

This skill adds, on top of that base:

- **Inbox-zone awareness**: the `***` line splits the daily note into inbox (above)
  and template (below). Only the inbox is touched.
- **Positional insertion**: `[[AI Assistant]]` must end up as the **last top-level
  bullet before `***`**, not at the end of the note.
- **`[[Context & Remarks:]]` injection** on referenced standalone notes that don't
  have one yet.

## Trigger

This skill fires **only** when the user types `/Reflect-inbox`. No conversational
triggers, no auto-fire.

- If no date is mentioned → use **today** (`reflect today --path`).
- If Simon mentions a specific date (any natural form) → use that date. Convert to
  ISO `YYYY-MM-DD` and resolve via `reflect show <date> --path` /
  `reflect path daily/<date>.md`.

## Hard rules — apply on every run

1. **Never** modify content below the `***` line in the daily note. The template
   section (PROJECTS / AREAS / OTHER) is Simon's hand-maintained structure. It must
   stay byte-identical.
2. **Never** modify a standalone (non-daily) note **except** to insert a single
   `[[Context & Remarks:]]` bullet as its very first content block (after the
   frontmatter and `# Title`, before the existing body). No other edits, no
   reformatting, nothing.
3. **Never** emit `#tag` syntax in any write. If a literal `#word` is needed, wrap it
   in backticks so it renders as inline code (e.g. `` `#example` ``). Tags clutter
   Simon's tag list.
4. **Never** tick or untick `[[Reflect tidied]]`. That checkbox is Simon's manual
   quality gate after he reviews what the skill did.
5. **Always** include a deep link to the daily note in the confirmation reply:
   `[Daily Note — Xth Month YYYY](reflect://daily/YYYY-MM-DD)`.

## Workflow

### Step 1 — Read & guard

1. Resolve the daily-note file: `reflect today --path` (or `reflect path daily/<date>.md`).
2. Read the file's full markdown with the Read tool.
3. Locate the `***` line (a line that is exactly `***`). If none exists, abort with:
   *"Cannot find the `***` divider in the daily note — refusing to act."* Don't guess
   where it should go.
4. Find the `[[Reflect tidied]]` checkbox line. If it is ticked (`[x]` /`+ [x]`),
   refuse with:
   > *"This daily note is already marked tidied. Untick `[[Reflect tidied]]` in the
   > Habits section if you want to process new inbox items."*

### Step 2 — Collect the inbox

The inbox is every top-level bullet (and its full nested subtree) **above** the
`***` line.

- Work on the text above `***` only. Keep the below-`***` text aside verbatim to
  re-attach unchanged.
- Note whether a top-level `- [[AI Assistant]]` bullet **already exists** above `***`
  (re-run case — handled in Step 5 Case B).
- Preserve item formatting exactly: `+ [ ]` stays a task, `- [ ]` stays a checkbox,
  bold stays bold, sub-bullets stay nested.

### Step 3 — Search nodes

```
reflect search "#node ➡️" --json
```

Scan the returned titles and snippets. Never hardcode the node list — it grows over
time.

### Step 4 — Classify each inbox item

For each top-level inbox item (skipping `[[AI Assistant]]` itself if it already
exists):

- **Pick a cluster node** by judgment. Use the same "obvious match" standard as
  `reflect-note`. When in doubt → no node, attach directly under `[[AI Assistant]]`.
- **Identify non-daily backlinks** inside the item: any `[[Note Title]]` that is
  **not** a `[[YYYY-MM-DD]]` daily-note backlink. These are the candidates for the
  Context & Remarks step. (A `[[title|alias]]` link — like the `capture-…` link
  captures — points to the part before the `|`.)
- **Decide whether to move the original**:
  - **Move** (remove original, place under `[[AI Assistant]]`): the structured
    version differs meaningfully — added a node prefix, regrouped, changed nesting.
  - **Leave in place** (skip — do not duplicate under `[[AI Assistant]]`): the item is
    already clean and well-clustered.

### Step 5 — Context & Remarks on referenced new notes

For each non-daily backlink identified in Step 4:

1. Resolve it: `reflect path "<exact title>"` (exit `3` = not found or private → skip
   it; exit `0` → read the file).
2. Read the target note. **"Obviously new" test**: is the first content bullet (after
   frontmatter + `# Title`) a bullet whose text starts with `[[Context & Remarks:]]`?
   - **Yes** → skip. Don't touch the note.
   - **No** → proceed.
3. Build the line. Format:
   ```
   - [[Context & Remarks:]] [[➡️ ClusterNode]], [[RelatedBacklink1]], [[RelatedBacklink2]]
   ```
   - The **first** backlink after `[[Context & Remarks:]]` is the **cluster node**
     chosen in Step 4 — it must equal the node this item is clustered under in
     `[[AI Assistant]]`. Non-negotiable.
   - Optionally add up to 4 more related backlinks (other existing notes that
     genuinely add context). Comma-separated, single line.
   - **Total backlinks ≤ 5** including the cluster node. No tags. No extra prose.
4. Insert it with the Edit tool as the first content bullet of the target file
   (immediately after the `# Title` line / frontmatter, before the existing body).
   This is the **only** edit allowed on the standalone note.

### Step 6 — Place / extend the `[[AI Assistant]]` subtree

Build the reorganized subtree as markdown text, 2 spaces per nesting level:

```
- [[AI Assistant]]
  - [[➡️ NodeA]]
    - Item 1
    - Item 2
  - [[➡️ NodeB]]
    - Item 3
  - Item with no obvious node
```

#### Case A — `[[AI Assistant]]` does NOT yet exist above the line

Edit the file so the subtree becomes the **last top-level bullet immediately before
`***`** (one blank line before `***`, matching existing spacing). Everything below
`***` stays byte-identical.

#### Case B — `[[AI Assistant]]` already exists above the line (same-day re-run)

- **Do not duplicate cluster bullets.** If `[[➡️ NodeA]]` already exists under the
  existing `[[AI Assistant]]`, nest new items under that existing group rather than
  creating a sibling `[[➡️ NodeA]]`.
- For genuinely new cluster nodes, append a new `- [[➡️ NodeX]]` group under
  `[[AI Assistant]]` at the end of its subtree.

### Step 7 — Remove restructured originals

Remove each original inbox item that Step 4 marked as **moved** from the above-`***`
text (they now live under `[[AI Assistant]]`). Leave items marked "leave in place"
untouched. Never remove or alter the `***` line or anything below it.

Since you are editing raw markdown, do Steps 6 and 7 as a single coherent rewrite of
the **above-`***` region**: produce the new inbox text (surviving/left-in-place items
+ the `[[AI Assistant]]` subtree just before `***`), then write it back with the
below-`***` text re-attached verbatim.

### Step 8 — Confirm

Reply to Simon with a compact summary:

- One line per cluster: *"`[[➡️ NodeName]]` ← N item(s)"*.
- A separate list of standalone notes that got a new `[[Context & Remarks:]]` line,
  each with its deep link (`reflect open "<title>" --json` → `url`).
- The daily-note deep link: `[Daily Note — Xth Month YYYY](reflect://daily/YYYY-MM-DD)`.
- A reminder: *"Review and tick `[[Reflect tidied]]` when you're satisfied."*

If the inbox was empty or nothing was restructured, say so plainly and skip the
daily-note write.

## Worked example

**Input** — above the `***` in today's daily note (`2026-05-16`):

```
- [[Links]]
  - [[How to Answer Any Question (Even If You Don't Know the Answer)]]
-

***
```

**Skill run**:

1. `reflect search "#node ➡️" --json` returns a list including (say) `[[➡️ Resources]]`.
2. The item `[[How to Answer...]]` is judged to belong under `[[➡️ Resources]]`. The
   empty `-` bullet is dropped (nothing to cluster).
3. `reflect path "How to Answer Any Question (Even If You Don't Know the Answer)"`
   resolves the note; its first content bullet is not `[[Context & Remarks:]]` →
   insert one at the top of that note's body:
   ```
   - [[Context & Remarks:]] [[➡️ Resources]]
   ```
4. Rewrite the above-`***` region so the inbox becomes:
   ```
   - [[AI Assistant]]
     - [[➡️ Resources]]
       - [[How to Answer Any Question (Even If You Don't Know the Answer)]]

   ***
   ```
   The original `- [[Links]]` subtree and the empty `-` bullet are gone; everything
   below `***` is byte-identical.

**Reply to Simon**:

> Tidied today's inbox:
> - `[[➡️ Resources]]` ← 1 item
>
> Added `[[Context & Remarks:]]` to:
> - [How to Answer Any Question...](reflect://note/<id>)
>
> [Daily Note — 16th May 2026](reflect://daily/2026-05-16)
>
> Review and tick `[[Reflect tidied]]` when you're satisfied.

## CLI + tools used

Read / resolve (the `reflect` CLI):
- `reflect today --path` / `reflect path <note>` — resolve the daily note and
  referenced standalone notes to files.
- `reflect show <note>` — inspect a note's content.
- `reflect search "#node ➡️" --json` — the live node list.
- `reflect open <note> --json` — the `reflect://` deep link for confirmations.

Write (Edit/Write on the resolved files, guarded by the Hard Rules above):
- Rewrite the **above-`***`** region of the daily note to place/extend the
  `[[AI Assistant]]` subtree and remove restructured originals. Never touch below `***`.
- Insert the single `[[Context & Remarks:]]` first bullet on a referenced standalone
  note.

Deliberately **not** done:
- No edit below `***`, ever.
- No creating new notes. If Simon pasted a URL above the line, Reflect already
  auto-created a capture/link note; just treat it as a backlink.
- No reformatting a standalone note's body beyond the single Context & Remarks insert.
