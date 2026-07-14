---
name: reflect-note
targets: [claude]
has_assets: false
description: >
  Use this skill for ANY interaction with Reflect Notes — reading, searching, writing, or appending. This includes: saving/noting/adding content to daily or standalone notes ("notiere in Reflect", "füge in Reflect hinzu", "note in Reflect", "add to Reflect", "save to Reflect"); reading or searching notes ("was steht in Reflect", "search Reflect", "find in Reflect", "zeig mir meine Reflect Note"); or any use of the `reflect` CLI (today, search, show, path, open). Always read this skill BEFORE calling the reflect CLI or editing a graph file — it contains the placement, node, and deep-link rules that must be followed on every interaction.
---

# Reflect Note Skill

Read and write content in the user's Reflect notes.

Reflect Open is **local-first and markdown-backed**. There is no MCP server and no
REST API anymore — the old `reflect-notes` MCP and `reflect.app/api` are gone.
Everything now goes through:

- **Reading / searching / resolving** → the read-only `reflect` CLI.
- **Writing / editing** → editing the note's markdown file directly. The running
  Reflect app watches the graph folder and re-imports your edits.

## The graph and the CLI

Single graph, a folder of markdown notes:

    /Users/simonsummermatter/Library/Mobile Documents/iCloud~app~reflect/Documents/simonsummermatter

The `reflect` CLI is bundled in the app (not on PATH by default):

    /Applications/Reflect Beta.app/Contents/MacOS/reflect

Always target the graph explicitly. Export it once for a sequence of calls:

    export REFLECT_GRAPH="/Users/simonsummermatter/Library/Mobile Documents/iCloud~app~reflect/Documents/simonsummermatter"

Then call e.g. `reflect today`, or pass `--graph "<path>"` on each call.

### CLI commands

    reflect today              # print today's daily note
    reflect today --path       # its absolute path (works before the file exists)
    reflect search <query>     # ranked full-text search over the graph
    reflect show <note>        # print a note by date, path, title, or alias
    reflect path <note>        # resolve a note to its absolute path
    reflect open <note>        # open the note in the Reflect app (returns a reflect:// url)

- Add `--json` to any command for stable machine-readable output (field names and
  exit codes are the automation contract).
- `<note>` resolves in order: `YYYY-MM-DD` date, graph-relative path, title, then
  alias (case-insensitive).
- Exit codes: `0` ok, `1` runtime error, `2` usage, `3` not found or private,
  `4` search index missing (open the graph in Reflect once to rebuild it).

### Privacy

Notes with `private: true` frontmatter are invisible through the CLI by design.
Never work around this by reading graph files directly unless the user explicitly
asks for that note.

## Pre-flight Checklist — Apply BEFORE Any Write/Edit/Delete

Before editing any graph file, confirm:

1. **Placement**: New daily-note content goes under the `Assistant` heading. Match
   that heading — and `Links` / `Scratch Pad` — by **name, not by `#` level**: the
   daily template's heading levels drift between notes (`Assistant` and `Scratch Pad`
   appear as either `#####` or `######`, and some notes omit `Audio Memos`), so the
   `#####`/`######` prefixes shown throughout this skill are illustrative only. Find
   the heading whose text is `Assistant` at any `#` level; do not fail the write
   because its level differs from the example. If that heading is missing, create it
   below the `Links` section (after the Links heading and its content) at the **same
   `#` level as that note's `Links` heading**; if there is no Links heading either,
   create `##### Assistant` as the first line of the note. Never write under
   `Scratch Pad` — that is Simon's personal capture area. No exceptions.
   (Mechanically reminded via an Edit/Write hook on Claude Code.)
2. **Node search done**: For daily-note writes that obviously belong under a
   `#node`, you must have searched (`reflect search "#node ➡️" --json`) and selected
   the matching node. When in doubt → no node, plain bullet under `##### Assistant`.
3. **Point 2 (new standalone notes)**: A new standalone note MUST end up reachable.
   See "Creating a Standalone Note — Backlink Rule (Point 2)" below.
4. **No tags**: Never emit `#tag` syntax in any write. If a literal `#word` is
   needed, wrap it in backticks so it renders as inline code (e.g. `` `#example` ``).
   Tags clutter Simon's tag list.

Edit/delete operations: confirm the placement still follows these rules after your change.

## Reading vs. Writing — Pick the Right Tool

| Action | How |
|--------|-----|
| **Read / Search** | `reflect search <query>` (ranked index) |
| **Get daily note** | `reflect today` or `reflect show <YYYY-MM-DD>` |
| **Get note by title/path** | `reflect show <note>` |
| **Resolve a note to a file** | `reflect path <note>` |
| **Write to daily note** | resolve `reflect today --path`, then edit the `.md` file |
| **Append to existing note** | resolve `reflect path <note>`, then edit the `.md` file |
| **Create standalone note** | write a new `notes/<slug>.md` file |
| **Open in the app** | `reflect open <note>` |

**The CLI never writes.** To change a note, edit the file the CLI resolves; the
running app picks the edit up. Unlike the old append-only REST API, you can now
**append to existing standalone notes** — just edit the file.

## Note file format

Notes are bullet-outline markdown. Indentation is **2 spaces per level**.

- **Daily notes**: `daily/YYYY-MM-DD.md`. The area above the `---` divider line is
  the day's gathering zone, organised under headings from the daily template; below
  the divider is Simon's hand-maintained template (PROJECTS / AREAS / OTHER). The
  gathering-zone headings and their owners:

  ```
  ##### Links          ← Reflect imports link captures here
  ###### Audio Memos   ← Reflect imports audio memos here (absent in some notes)
  ##### Assistant      ← ALL AI writes go here
  ###### Scratch Pad   ← Simon's personal capture area — never write here
  ---
  ```

  The `#` levels above are **illustrative** — they drift between notes. Match each
  heading by its **name** at any `#` level (see Pre-flight rule 1), and preserve
  the level a given note uses. AI writes go under the `Assistant` heading:

  ```
  ##### Assistant

  - [[➡️ NodeName]]
    - Your note text here
  ```

- **Standalone notes**: `notes/<kebab-slug>.md`, with optional `---\nid: "..."\n---`
  frontmatter, a `# Title` H1, then a bullet body:

  ```
  ---
  id: "..."
  ---

  # Project Alpha

  - first point
  - second point
  ```

  Do **not** fabricate an `id` — omit the frontmatter and let the Reflect app assign
  the id when it adopts the new file. The filename is a lowercase, hyphenated slug of
  the title (e.g. "Project Alpha" → `project-alpha.md`).

## Tasks vs. Checkboxes — Kritischer Unterschied

Reflect unterscheidet **zwei fundamentally verschiedene** Typen von Checkboxen:

| Typ | Aussehen | Markdown | Sichtbar in Tasks-Tab | Zweck |
|-----|----------|----------|----------------------|-------|
| **Task** | runde Checkbox | `+ [ ] Text` | Ja | Konkrete To-dos — suchbar, filterbar, schedulebar |
| **Checkbox** | eckige Checkbox | `- [ ] Text` | Nein | Scratchpad / temporäre Listen (z.B. Einkaufsliste) |

**Wann welchen Typ verwenden:**
- Der User sagt **"Task"**, **"Aufgabe"**, **"Todo"**, **"erledigen"**, **"muss ich noch"** → `+ [ ]` (rund)
- Der User sagt **"Checkbox"**, **"abhaken"**, **"Liste"**, **"Checkliste"** → `- [ ]` (eckig)
- Im Zweifel bei echten Aktionspunkten → Task (`+ [ ]`)
- Im Zweifel bei temporären Notizen/Listen → Checkbox (`- [ ]`)

**Markdown-Syntax:**
```
+ [ ] Offener Task (rund)
+ [x] Erledigter Task (rund)
- [ ] Offene Checkbox (eckig)
- [x] Erledigte Checkbox (eckig)
```

**Scheduling von Tasks:** Tasks in Daily Notes erscheinen standardmässig als
"Current". Durch Backlink auf eine andere Daily Note werden sie "Upcoming"
(Zukunft) oder "Overdue" (Vergangenheit).

## Deep Links — ALWAYS Include When Referencing a Note

Whenever a Reflect note is mentioned, found via search, or written to, ALWAYS
provide a clickable link in the response. No exceptions.

Reflect Open uses `reflect://` deep links (the old `https://reflect.app/g/...` web
URLs are no longer the canonical scheme):

```
reflect://daily/YYYY-MM-DD          # daily notes — construct directly from the date
reflect://note/<hash-id>            # standalone notes — get via `reflect open <note> --json`
```

- **Daily notes**: construct the link yourself, e.g. 21 March 2026 →
  `reflect://daily/2026-03-21`. No app launch needed.
- **Standalone notes**: run `reflect open <note> --json` and read the `url` field
  (this also launches the app). If launching is undesirable, reference the note by
  its title instead and offer to open it.

**Format always as a Markdown hyperlink**, e.g.:
`[Daily Note — 21 March 2026](reflect://daily/2026-03-21)`
`[Project Alpha](reflect://note/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)`

**RULE: Never mention a note by name without a link.**

## Reading (CLI)

**Search** — `reflect search <query> --json` returns ranked `results[]` with
`path`, `title`, `snippet`, `score`. Use it instead of grepping the graph.

**Daily note** — `reflect today` (today) or `reflect show <YYYY-MM-DD>` (any date).
`--json` returns `date`, `path`, `absolutePath`, `title`, `content`.

**Any note** — `reflect show <title|path|alias>`; `reflect path <note>` for just the
absolute path.

Date phrasing for the user's daily notes is `YYYY-MM-DD` for the CLI (the old
English-ordinal search format is no longer needed).

## Writing — Daily Note

### Node System (2nd Brain / PARA)

The user's PKM uses **nodes** — tagged with `#node` and named with a `➡️` prefix
(e.g. `➡️ AOMIForward`). Each node is like a folder in the PARA system (Projects,
Areas, Resources, Archive). Every piece of information belongs under a node.

**When writing to a daily note:**

- **Always** place the content under the `##### Assistant` heading (a heading from
  the daily template, not a bullet). New bullets go between that heading and the
  next heading (e.g. `###### Scratch Pad`).
- **If the content obviously belongs to a specific node**, start with a top-level
  `- [[➡️ NodeName]]` bullet under the heading, and the note text nested under that.
- **If no node matches**, put the note text as a plain top-level bullet directly
  under the heading.

**How to match a node:**
- Before writing, search for nodes dynamically: `reflect search "#node ➡️" --json`.
- The node list grows over time — never rely on a hardcoded list.
- Scan the returned node names/snippets. Pick a node only when it's a clear, obvious
  match for the note content.
- When in doubt, skip the node and write a plain bullet under `##### Assistant`.
- Only notes tagged `#node` are valid nodes — ignore everything else.

### Procedure — append to today's daily note

1. Resolve the file: `reflect today --path` (works even before today's file exists).
2. Read the current file (or create it if `reflect today --path` points at a
   missing file).
3. Find the `Assistant` heading **by name at any `#` level** (per Pre-flight rule
   1) — do not require a literal `##### Assistant`. If it is missing, create it below
   the `Links` section (after the Links heading and its content) at the same `#` level
   as that note's `Links` heading; if there is no Links heading either, create
   `##### Assistant` as the first line of the note.
4. Append your content as top-level bullets between the `Assistant` heading and the
   next heading, with **2-space-per-level** indentation, choosing `[[➡️ Node]]`
   nesting per the node rules above. Preserve the heading's existing `#` level.
5. Save the file with the Edit/Write tool. The app re-imports it automatically.
6. Confirm to the user with a `reflect://daily/YYYY-MM-DD` link.

**With node match**:
```
##### Assistant

- [[➡️ NodeName]]
  - Your note text here
```

**With multiple structured sub-bullets under a node:**
```
##### Assistant

- [[➡️ NodeName]]
  - Parent title
    - **Label**: first point
    - **Label**: second point
```

**Without node match** (plain top-level bullet):
```
##### Assistant

- Your note text here
```

**Formatting rules:**
- `**text**` → bold
- `` `text` `` → inline code
- 2 spaces per nesting level
- Never use `·` as a separator — always nest as sub-bullets
- Never put multiple points in one long flat bullet — use sub-bullets for structured content

## Writing — Standalone Note

### Create a standalone note

1. Choose a title. Check it doesn't already exist: `reflect show "<Title>" --json`
   (exit `3` = not found → safe to create; exit `0` = it exists, edit that file
   instead).
2. Write a new file `notes/<kebab-slug>.md`:
   ```
   # <Title>

   - first point
   - second point
   ```
   Omit `id:` frontmatter — the app assigns the id on import. Supports
   `[[Note Title]]` backlinks. Never emit `#tags` (Pre-flight rule 4).
3. Verify + get the link: `reflect open "<Title>" --json` → use the `url` field.
4. Apply Point 2 (backlink rule) below.

### Append to an existing standalone note

New in Reflect Open: editing existing notes is allowed (the old REST API couldn't).
Resolve `reflect path "<Title>"`, read the file, add your bullet(s) in the right
place, save. Confirm with the note's `reflect://note/<id>` link.

### Creating a Standalone Note — Backlink Rule (Point 2)

A newly created non-daily note MUST satisfy at least one of:

- **(a) Outgoing backlink**: the note body already contains one or more
  `[[Note Title]]` references to other non-daily notes.
- **(b) Known incoming backlink**: another existing non-daily note already links to
  this one (e.g., the user said "linked from project X", or you're about to write
  that link).
- **(c) Daily-note backlink (default fallback)**: append to today's daily note under
  the `##### Assistant` heading a bullet containing a `[[NewNoteTitle]]` backlink,
  following the same node-matching rules as any other daily-note write.

**Why:** Reflect's graph value depends on connectivity. Orphan notes are unreachable
from Reflect's backlink suggestions and effectively lost.

**Procedure after every note creation:**

1. Does the body already contain a `[[Note Title]]` reference to a non-daily note?
   → done (case a).
2. Is there a clear existing/about-to-be-written incoming link? → proceed with that
   write (case b).
3. Otherwise → append to today's daily note under `##### Assistant` (suitable node
   prefix if obvious) a bullet with a `[[NewNoteTitle]]` backlink (case c — default).

## Examples

**Read today's note:**
"Was steht heute in Reflect?" → `reflect today`
→ Return with link: [Daily Note — 9 July 2026](reflect://daily/2026-07-09)

**Search for a person:**
"In welcher Note habe ich Notizen über Erika?" → `reflect search "Erika Mustermann" --json`
→ Return top hit with link (get its url via `reflect open <title> --json`).

**Daily note — node match:**
"Notiere in Reflect dass ich mich um die MWST kümmern muss"
→ `reflect today --path`, read file, add under the `##### Assistant` heading:
```
- [[➡️ MyFinances]]
  - Muss mich um die MWST kümmern
```
→ Confirm: "Notiert unter `##### Assistant` → `[[➡️ MyFinances]]`. [Daily Note — 9 July 2026](reflect://daily/2026-07-09)"

**Daily note — no obvious node:**
"Note in Reflect: Remember to call back Martin"
→ add under `##### Assistant`: `- Remember to call back Martin`

**Task hinzufügen (rund, erscheint im Tasks-Tab):**
"Füge Task in Reflect hinzu: Rechnung an Kunde schicken"
→ under `##### Assistant`: `+ [ ] Rechnung an Kunde schicken`

**Checkbox-Liste (eckig, nur temporär):**
"Notiere Einkaufsliste: Milch, Eier, Brot"
→ under `##### Assistant`:
```
- Einkaufsliste
  - [ ] Milch
  - [ ] Eier
  - [ ] Brot
```

**Standalone note:**
"Create a new Reflect note titled 'Project Ideas'"
→ verify with `reflect show "Project Ideas" --json`, write `notes/project-ideas.md`
with `# Project Ideas` + body, then verify Point 2 and confirm with the
`reflect open "Project Ideas" --json` url.

## Git history

Each graph is a Git repo at its root (Reflect commits locally even with no remote).
Use Git only when the user asks for history, diffs, recovery, or past states:

    git -C "<graph>" log --oneline -- <graph-relative-path>
    git -C "<graph>" show <rev>:<graph-relative-path>

Do not use Git history to bypass privacy.

## Hook Enforcement (harness-specific)

The skill text above is the primary rule home — every harness reads and follows it.
Where the host harness supports hooks, those hooks provide a mechanical backstop on
top of the skill text. Hook installation is performed by `sync-skills` per harness;
never edit the harness config by hand.

### Claude Code (hooks supported)

`sync-skills` merges the following into `~/.claude/settings.json` under the `hooks`
key, preserving pre-existing unrelated entries (additive merge — same `matcher`
means replace its `hooks` array; new `matcher` means append). Writes are now plain
file edits, so the reminder fires whenever an Edit/Write/MultiEdit targets a file
inside the Reflect graph folder.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r 'if ((.tool_input.file_path // \"\") | contains(\"iCloud~app~reflect/Documents/simonsummermatter\")) then {hookSpecificOutput:{hookEventName:\"PreToolUse\",additionalContext:\"Editing a Reflect graph file — apply the reflect-note skill rules: place new daily content under the `##### Assistant` heading (create it below the Links section if missing, or as the first line if there is no Links heading); never write under `###### Scratch Pad`; nest under a top-level `- [[➡️ node]]` bullet when it obviously matches (search `#node ➡️` first); tasks use `+ [ ]`, checkboxes `- [ ]`; never emit `#tags`; a new standalone note needs a backlink (Point 2).\"}} else empty end'"
          }
        ]
      }
    ]
  }
}
```

What the hook enforces:
- **PreToolUse Edit/Write reminder**: on any edit to a file inside the Reflect graph
  folder, injects the placement (`##### Assistant` heading, Scratch Pad off-limits)
  /node/task/tag/Point-2 rules so they can't slip when writing or mutating note
  content.
