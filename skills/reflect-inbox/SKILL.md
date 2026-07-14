---
name: reflect-inbox
targets: [claude]
has_assets: false
description: >
  Process Simon's Reflect daily-note inbox on demand. Triggered ONLY when the user types `/Reflect-inbox` (case-insensitive). The skill reads the daily note for the requested date (default: today), takes everything above the `---` horizontal-rule divider (the "inbox" zone — the sections under the headings `##### Links`, `###### Audio Memos`, and `###### Scratch Pad`), and reorganizes it under the `##### Assistant` heading. Items are clustered by `#node ➡️` exactly like the `reflect-note` skill. For each non-daily backlink in the inbox whose target note has no `[[Context & Remarks:]]` first-line yet, the skill inserts that line at the top of the standalone note with the cluster node first and up to 4 related backlinks (max 5 total, no tags). Never touches anything below `---`, never edits standalone notes beyond the single Context & Remarks insert, and refuses to run if `[[Reflect tidied]]` is already checked. ALWAYS read this skill before processing the inbox.
---

# Reflect Inbox Skill

Process the **inbox zone** of a Reflect daily note (the area above the `---`
horizontal-rule divider) and reorganize it under the `##### Assistant` heading with
`#node ➡️` clustering. For non-daily backlinks Simon added to the inbox, give each
genuinely-new target note a `[[Context & Remarks:]]` first line so it stops being
context-less.

Reflect Open is local-first markdown. There is no MCP and no REST API — you read
through the `reflect` CLI and write by **editing the note's markdown file
directly**. The running app re-imports edits automatically. Because you edit the
raw markdown text, splitting on the `---` divider and rebuilding the inbox is plain
string manipulation.

## Relationship to `reflect-note`

This skill **builds on** `reflect-note`. Read that skill first for:

- The graph path, the `reflect` CLI commands, and the file format.
- Deep-link format (`reflect://daily/YYYY-MM-DD`, `reflect://note/<id>`) and the rule
  that every Reflect note mentioned in a reply gets a clickable link.
- The node search query: `reflect search "#node ➡️" --json`.
- The `##### Assistant` heading placement rule for daily-note writes (top-level
  bullets under the heading, 2 spaces per nesting level).
- Tasks (`+ [ ]`, round) vs. checkboxes (`- [ ]`, square) — preserve whichever
  Simon used.

This skill adds, on top of that base:

- **Inbox-zone awareness**: the `---` line splits the daily note into inbox (above)
  and template (below). Only the inbox is touched.
- **Source-section awareness**: Reflect imports captures under **headings** in the
  inbox zone — `##### Links` (link captures), `###### Audio Memos` (audio memos) —
  and Simon gathers his personal notes under `###### Scratch Pad`. Those three
  sections are the item sources; `##### Assistant` is the destination.
- **`[[Context & Remarks:]]` injection** on referenced standalone notes that don't
  have one yet.

## The inbox-zone layout

Above the `---` divider, the daily template provides these headings:

```
##### Links          ← Reflect imports link captures here      (source)
###### Audio Memos   ← Reflect imports audio memos here        (source)
##### Assistant      ← reorganized items end up here           (destination)
###### Scratch Pad   ← Simon's personal capture area           (source)
---
```

- Items live as top-level bullets under their heading; a heading's section runs to
  the next heading (or the divider).
- The **headings themselves always stay in place**, even when their section is
  emptied by this skill.
- **Match headings by NAME, never by `#` level.** The daily template's heading levels
  drift between notes: `Assistant` and `Scratch Pad` show up as either `#####` or
  `######`, and older notes omit `Audio Memos` entirely. The literal prefixes shown
  above (`##### Links`, `###### Audio Memos`, …) are only illustrative. Locate each
  section by its heading **text** (`Links`, `Audio Memos`, `Assistant`, `Scratch Pad`)
  with any run of leading `#` (any level), and when you write, **preserve the exact level that
  note already uses**. A run that fails to find `##### Assistant` because the note
  wrote `###### Assistant` is the bug this rule exists to prevent — do not skip the
  write, and do not create a second heading at a different level.
- If there is **no** `Assistant` heading at all, create one at the **same `#` level as
  that note's `Links` heading**, directly below the Links section (after the Links
  heading and its content); if there is no Links heading either, create `Assistant`
  as the first line of the note using level `#####`.

## Trigger

This skill fires **only** when the user types `/Reflect-inbox`. No conversational
triggers, no auto-fire.

- If no date is mentioned → use **today** (`reflect today --path`).
- If Simon mentions a specific date (any natural form) → use that date. Convert to
  ISO `YYYY-MM-DD` and resolve via `reflect show <date> --path` /
  `reflect path daily/<date>.md`.

## Hard rules — apply on every run

1. **Never** modify content below the `---` divider line in the daily note. The
   template section (PROJECTS / AREAS / OTHER) is Simon's hand-maintained structure.
   It must stay byte-identical.
2. **Never** modify a standalone (non-daily) note **except** to insert a single
   `[[Context & Remarks:]]` bullet as its very first content block (after the
   frontmatter and `# Title`, before the existing body). No other edits, no
   reformatting, nothing.
3. **Never** emit `#tag` syntax in any write. If a literal `#word` is needed, wrap it
   in backticks so it renders as inline code (e.g. `` `#example` ``). Tags clutter
   Simon's tag list.
4. **Never** tick or untick `[[Reflect tidied]]`. That checkbox is Simon's manual
   quality gate after he reviews what the skill did.
5. **Never** remove, demote, or change the `#` level of the inbox-zone headings
   (`Links`, `Audio Memos`, `Assistant`, `Scratch Pad` — matched by name at whatever
   `#` level a given note uses). Only the bullets beneath them move. Some notes
   have no `Audio Memos` heading; that is fine — never add one.
6. **Always** include a deep link to the daily note in the confirmation reply:
   `[Daily Note — Xth Month YYYY](reflect://daily/YYYY-MM-DD)`.

## Workflow

### Step 1 — Read & guard

1. Resolve the daily-note file: `reflect today --path` (or `reflect path daily/<date>.md`).
2. Read the file's full markdown with the Read tool.
3. Locate the divider: the first line that is exactly `---` (older notes may use
   `***` — accept that as the divider too). If none exists, abort with:
   *"Cannot find the `---` divider in the daily note — refusing to act."* Don't guess
   where it should go.
4. Find the `[[Reflect tidied]]` checkbox line. If it is ticked (`[x]` /`+ [x]`),
   refuse with:
   > *"This daily note is already marked tidied. Untick `[[Reflect tidied]]` in the
   > Habits section if you want to process new inbox items."*

### Step 2 — Collect the inbox

The inbox items are every top-level bullet (with its full nested subtree) in the
**source sections** above the divider: under the `Links`, `Audio Memos`, and
`Scratch Pad` headings (matched by name at any `#` level — see "Match headings
by NAME" in the layout section; `Audio Memos` may be absent) — plus any stray
top-level bullets sitting outside any heading.

- Work on the text above the divider only. Keep the below-divider text aside
  verbatim to re-attach unchanged.
- Note whether the `##### Assistant` section **already contains content** (re-run
  case, or earlier same-day AI writes — handled in Step 6 Case B). Existing
  Assistant content is never re-clustered or rewritten; new items only merge in.
- Preserve item formatting exactly: `+ [ ]` stays a task, `- [ ]` stays a checkbox,
  bold stays bold, sub-bullets stay nested, `[[title|alias]]` links stay intact.

### Step 3 — Search nodes

```
reflect search "#node ➡️" --json
```

Scan the returned titles and snippets. Never hardcode the node list — it grows over
time.

### Step 4 — Classify each inbox item

For each top-level inbox item from the source sections:

- **Pick a cluster node** by judgment. Use the same "obvious match" standard as
  `reflect-note`. When in doubt → no node, attach as a plain top-level bullet under
  `##### Assistant`.
- **Identify non-daily backlinks** inside the item: any `[[Note Title]]` that is
  **not** a `[[YYYY-MM-DD]]` daily-note backlink. These are the candidates for the
  Context & Remarks step. (A `[[title|alias]]` link — like the `capture-…` link
  captures Reflect files under `##### Links` — points to the part before the `|`.)
- **Decide whether to move the original**:
  - **Move** (remove from its source section, place under `##### Assistant`): the
    structured version differs meaningfully — added a node prefix, regrouped,
    changed nesting.
  - **Leave in place** (skip — do not duplicate under `##### Assistant`): the item
    is already clean and well-clustered where it is.
- Drop empty bullets (`-` with no text) — nothing to cluster.

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
     chosen in Step 4 — it must equal the node this item is clustered under in the
     `##### Assistant` section. Non-negotiable.
   - Optionally add up to 4 more related backlinks (other existing notes that
     genuinely add context). Comma-separated, single line.
   - **Total backlinks ≤ 5** including the cluster node. No tags. No extra prose.
4. Insert it with the Edit tool as the first content bullet of the target file
   (immediately after the `# Title` line / frontmatter, before the existing body).
   This is the **only** edit allowed on the standalone note.

### Step 6 — Place / extend the `##### Assistant` section

Build the reorganized content as top-level bullets, 2 spaces per nesting level:

```
##### Assistant

- [[➡️ NodeA]]
  - Item 1
  - Item 2
- [[➡️ NodeB]]
  - Item 3
- Item with no obvious node
```

Use the same `#` level for the `Assistant` heading that the note already uses; the
`#####` shown here is only illustrative (see "Match headings by NAME").

#### Case A — the `Assistant` heading does NOT yet exist

Create it below the `Links` section (after the Links heading and its content), at the
**same `#` level as that note's `Links` heading**; if there is no Links heading
either, create it as the first line of the note at level `#####`. Put the reorganized
bullets directly beneath it. Everything below the divider stays byte-identical.

#### Case B — the `Assistant` heading already exists (same-day re-run or earlier AI writes)

- Keep its existing content untouched and in place.
- **Do not duplicate cluster bullets.** If `- [[➡️ NodeA]]` already exists in the
  section, nest new items under that existing group rather than creating a sibling
  `- [[➡️ NodeA]]`.
- For genuinely new cluster nodes, append a new `- [[➡️ NodeX]]` group at the end of
  the section (before the next heading).

### Step 7 — Remove restructured originals

Remove each original inbox item that Step 4 marked as **moved** from its source
section (`##### Links` / `###### Audio Memos` / `###### Scratch Pad`) — they now
live under `##### Assistant`. Leave items marked "leave in place" untouched. The
source headings always stay, even if their section is now empty. Never remove or
alter the divider or anything below it.

Since you are editing raw markdown, do Steps 6 and 7 as a single coherent rewrite of
the **above-divider region**: produce the new inbox text (headings in template
order, surviving/left-in-place items under their source headings, the reorganized
bullets under `##### Assistant`), then write it back with the below-divider text
re-attached verbatim.

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

**Input** — above the `---` in today's daily note (`2026-07-14`):

```
##### Links

- [[capture-2026-07-14-090000-000-abcd|How to Answer Any Question (Even If You Don't Know the Answer)]]

###### Audio Memos

##### Assistant

###### Scratch Pad

- Idee: Newsletter über PKM schreiben
-

---
```

**Skill run**:

1. `reflect search "#node ➡️" --json` returns a list including (say)
   `[[➡️ Resources]]` and `[[➡️ ContentCreation]]`.
2. The Links capture is judged to belong under `[[➡️ Resources]]`; the Scratch Pad
   idea under `[[➡️ ContentCreation]]`. The empty `-` bullet is dropped.
3. `reflect path "capture-2026-07-14-090000-000-abcd"` resolves the capture note;
   its first content bullet is not `[[Context & Remarks:]]` → insert one at the top
   of that note's body:
   ```
   - [[Context & Remarks:]] [[➡️ Resources]]
   ```
4. Rewrite the above-divider region so the inbox becomes:
   ```
   ##### Links

   ###### Audio Memos

   ##### Assistant

   - [[➡️ Resources]]
     - [[capture-2026-07-14-090000-000-abcd|How to Answer Any Question (Even If You Don't Know the Answer)]]
   - [[➡️ ContentCreation]]
     - Idee: Newsletter über PKM schreiben

   ###### Scratch Pad

   ---
   ```
   The moved bullets are gone from `##### Links` and `###### Scratch Pad`, the
   headings stay, and everything below `---` is byte-identical.

**Reply to Simon**:

> Tidied today's inbox:
> - `[[➡️ Resources]]` ← 1 item
> - `[[➡️ ContentCreation]]` ← 1 item
>
> Added `[[Context & Remarks:]]` to:
> - [How to Answer Any Question...](reflect://note/<id>)
>
> [Daily Note — 14th July 2026](reflect://daily/2026-07-14)
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
- Rewrite the **above-`---`** region of the daily note to fill/extend the
  `##### Assistant` section and remove moved items from the source sections. Never
  touch below the divider.
- Insert the single `[[Context & Remarks:]]` first bullet on a referenced standalone
  note.

Deliberately **not** done:
- No edit below the `---` divider, ever.
- No creating new notes. If Simon pasted a URL in the inbox, Reflect already
  auto-created a capture/link note under `##### Links`; just treat it as a backlink.
- No reformatting a standalone note's body beyond the single Context & Remarks insert.
- No removing or reordering the inbox-zone headings.
