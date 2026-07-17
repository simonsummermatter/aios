---
name: reflect-inbox
targets: [claude]
has_assets: false
description: >
  Process Simon's Reflect daily-note inbox on demand. Triggered ONLY when the
  user types `/Reflect-inbox` (case-insensitive). Reorganizes the inbox zone of
  the requested date's daily note (default: today) under the `[[AI Assistant]]`
  heading with `#node ➡️` clustering, and gives referenced new standalone notes
  a `[[Context & Remarks:]]` first line. ALWAYS read the reflect-note skill
  first, then this skill, before processing.
---

# Reflect Inbox Skill

Reorganize the **inbox zone** of a Reflect daily note (everything below the
LAST `---` divider) under the `[[AI Assistant]]` heading, clustered by
`#node ➡️`. For non-daily backlinks Simon captured, give each genuinely-new
target note a `[[Context & Remarks:]]` first line so it stops being
context-less.

## Builds on `reflect-note`

Read `reflect-note` FIRST. It is the source of truth for: the graph and CLI,
the daily-note layout (last-`---` divider, inbox-zone headings, match-by-name
rules, legacy `Assistant`, missing-heading/divider handling), the node system,
tasks vs. checkboxes, the no-`#tags` rule, and deep links. None of that is
repeated here.

This skill adds: the inbox-processing workflow, `[[Context & Remarks:]]`
injection, and the `[[Reflect tidied]]` gate. Sources are the `Links`,
`Audio Memos`, and `Scratch Pad` sections; the destination is `AI Assistant`.

## Trigger

Fires **only** on `/Reflect-inbox`. No conversational triggers, no auto-fire.

- No date mentioned → **today** (`reflect today --path`).
- A specific date (any natural form) → convert to ISO `YYYY-MM-DD`, resolve via
  `reflect path daily/<date>.md`.

## Hard rules — every run

All `reflect-note` pre-flight rules apply, plus:

1. **Never** modify anything above the last `---` divider — the template stays
   byte-identical.
2. **Never** edit a standalone note except to insert the single
   `[[Context & Remarks:]]` bullet as its first content block.
3. **Never** tick or untick `[[Reflect tidied]]` — that checkbox is Simon's
   manual quality gate.
4. **Never** remove, demote, or restyle the inbox-zone headings. Only the
   bullets beneath them move; headings stay even when their section is emptied.
   Never add a missing `Audio Memos` heading.
5. **Never** create new notes. A URL Simon pasted already has an auto-created
   capture note under `Links` — treat it as a backlink.
6. **Always** end the confirmation with the daily deep link:
   `[Daily Note — Xth Month YYYY](reflect://daily/YYYY-MM-DD)`.

## Workflow

### Step 1 — Read & guard

1. Resolve and Read the daily-note file.
2. Locate the last `---` divider (per the `reflect-note` layout rules). No
   divider → no inbox zone; one is appended at the end only if Step 6 has
   content to write.
3. Find the `[[Reflect tidied]]` checkbox. If ticked (`[x]` / `+ [x]`), refuse:
   > *"This daily note is already marked tidied. Untick `[[Reflect tidied]]` in
   > the Habits section if you want to process new inbox items."*

### Step 2 — Collect the inbox

Items are every top-level bullet (with its full nested subtree) under the
source headings below the divider — `Links`, `Audio Memos`, `Scratch Pad` —
plus stray top-level bullets below the divider outside any heading.

- Keep everything above the divider (including the divider line) aside verbatim.
- Note whether `AI Assistant` already contains content (re-run case → Step 6
  Case B). Existing content is never re-clustered or rewritten.
- Preserve item formatting exactly: `+ [ ]` stays a task, `- [ ]` stays a
  checkbox, bold stays bold, sub-bullets stay nested, `[[title|alias]]` intact.

### Step 3 — Search nodes

`reflect search "#node ➡️" --json` — scan titles and snippets. Never hardcode
the node list.

### Step 4 — Classify each item

- **Pick a cluster node** by judgment (obvious match only; in doubt → no node,
  plain top-level bullet under `AI Assistant`).
- **Identify non-daily backlinks** in the item: any `[[Note Title]]` that is
  not a `[[YYYY-MM-DD]]` daily link. These feed Step 5. (`[[title|alias]]`
  points to the part before the `|`.)
- **Move or leave**: *move* to `AI Assistant` if restructuring adds value
  (node prefix, regrouping, nesting); *leave in place* if the item is already
  clean where it is — never duplicate it.
- Drop empty bullets (`-` with no text).

### Step 5 — Context & Remarks on referenced new notes

For each non-daily backlink from Step 4:

1. `reflect path "<exact title>"` — exit `3` (not found or private) → skip;
   exit `0` → read the file.
2. **Obviously-new test**: is the first content bullet (after frontmatter +
   `# Title`) already a `[[Context & Remarks:]]` bullet? Yes → skip.
3. Otherwise insert, as the very first content bullet:
   ```
   - [[Context & Remarks:]] [[➡️ ClusterNode]], [[RelatedBacklink1]], [[RelatedBacklink2]]
   ```
   - First backlink = the cluster node chosen in Step 4 — must equal the node
     the item sits under in `AI Assistant`. Non-negotiable.
   - Optionally up to 4 more genuinely context-adding backlinks. **Max 5 total,
     one line, no tags, no extra prose.** This is the only edit allowed on the
     standalone note.

### Step 6 — Place / extend the `AI Assistant` section

Build the reorganized content as top-level bullets, 2-space nesting:

```
- [[➡️ NodeA]]
  - Item 1
  - Item 2
- Item with no obvious node
```

Use the destination heading style that note already has (see `reflect-note`).

- **Case A — no destination heading exists below the divider**: create it per
  the `reflect-note` missing-heading rule (very end of the note; append `---`
  first if there is no divider at all) and put the bullets beneath it.
- **Case B — heading already exists** (re-run / earlier AI writes): keep its
  content untouched; nest new items under an existing `- [[➡️ NodeX]]` group
  rather than duplicating it; append genuinely new node groups at the end of
  the section.

### Step 7 — Remove moved originals

Do Steps 6 and 7 as a **single coherent rewrite of the below-divider region**:
headings in template order, left-in-place items under their source headings,
the reorganized bullets under `AI Assistant`, moved items gone from their
sources — then re-attach the above-divider text (and divider) verbatim in
front and save.

### Step 8 — Confirm

- One line per cluster: *"`[[➡️ NodeName]]` ← N item(s)"*.
- Standalone notes that got `[[Context & Remarks:]]`, each with its deep link
  (`reflect open "<title>" --json` → `url`).
- The daily deep link, and: *"Review and tick `[[Reflect tidied]]` when you're
  satisfied."*
- Empty inbox / nothing restructured → say so plainly, skip the write.

## Worked example

End of today's note (`2026-07-14`), below the last `---`:

```
---

## [[Links]]

- [[capture-2026-07-14-090000-000-abcd|How to Answer Any Question]]

###### Audio Memos

## [[AI Assistant]]

## [[Scratch Pad]]

- Idee: Newsletter über PKM schreiben
-
```

Run: node search returns (say) `[[➡️ Resources]]` and `[[➡️ ContentCreation]]`.
The capture clusters under Resources, the idea under ContentCreation, the empty
bullet is dropped. The capture note gets `- [[Context & Remarks:]] [[➡️ Resources]]`
as its first bullet. The below-divider region becomes:

```
---

## [[Links]]

###### Audio Memos

## [[AI Assistant]]

- [[➡️ Resources]]
  - [[capture-2026-07-14-090000-000-abcd|How to Answer Any Question]]
- [[➡️ ContentCreation]]
  - Idee: Newsletter über PKM schreiben

## [[Scratch Pad]]
```

Reply:

> Tidied today's inbox:
> - `[[➡️ Resources]]` ← 1 item
> - `[[➡️ ContentCreation]]` ← 1 item
>
> Added `[[Context & Remarks:]]` to: [How to Answer Any Question](reflect://note/<id>)
>
> [Daily Note — 14th July 2026](reflect://daily/2026-07-14)
>
> Review and tick `[[Reflect tidied]]` when you're satisfied.
