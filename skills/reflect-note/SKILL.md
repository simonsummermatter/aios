---
name: reflect-note
targets: [claude]
has_assets: false
description: >
  Use this skill for ANY interaction with Reflect Notes — reading, searching,
  writing, or appending ("notiere in Reflect", "add to Reflect", "was steht in
  Reflect", "search Reflect"), or any use of the `reflect` CLI. Read it BEFORE
  calling the CLI or editing a graph file — it is the single source of truth for
  the daily-note layout and the placement, node, task, and deep-link rules.
---

# Reflect Note Skill

Reflect Open is **local-first and markdown-backed**. There is no MCP server and
no REST API. Read/search/resolve via the read-only `reflect` CLI; write by
editing the note's markdown file directly — the running app re-imports edits.

## Graph & CLI

Single graph, a folder of markdown notes:

    /Users/simonsummermatter/Library/Mobile Documents/iCloud~app~reflect/Documents/simonsummermatter

The CLI is bundled in the app (not on PATH):

    /Applications/Reflect Beta.app/Contents/MacOS/reflect

Export `REFLECT_GRAPH="<graph path>"` once for a sequence of calls, or pass
`--graph "<path>"` per call.

    reflect today [--path]     # today's daily note / its absolute path (works before the file exists)
    reflect search <query>     # ranked full-text search — use instead of grepping the graph
    reflect show <note>        # print a note by date, path, title, or alias
    reflect path <note>        # resolve a note to its absolute path
    reflect open <note>        # open in the app; --json returns the reflect:// url

- `--json` on any command gives the stable automation contract (field names, exit codes).
- `<note>` resolves in order: `YYYY-MM-DD` date → graph-relative path → title → alias.
- Exit codes: `0` ok · `1` runtime error · `2` usage · `3` not found or private ·
  `4` search index missing (open the graph in Reflect once to rebuild).

**Privacy**: notes with `private: true` frontmatter are invisible through the CLI
by design. Never work around this by reading graph files directly unless the
user explicitly asks.

**Git history**: each graph is a local Git repo (Reflect commits even without a
remote). Use `git -C "<graph>" log/show/diff -- <graph-relative-path>` only when
the user asks for history, diffs, or recovery — never to bypass privacy.

## Daily-note layout — source of truth

Daily notes live at `daily/YYYY-MM-DD.md`. The **LAST** line that is exactly
`---` (older notes may use `***`; ignore the YAML frontmatter delimiters at the
top) splits the note:

- **Above** the last divider: Simon's hand-maintained template (PROJECTS /
  AREAS / OTHER). **Never modify anything above the last divider.**
- **Below** it, at the **end** of the note, the **inbox zone**:

  ```
  ---
  ## [[Links]]         ← Reflect imports link captures here   (never write here)
  ###### Audio Memos   ← Reflect imports audio memos here     (never write here; absent in some notes)
  ## [[AI Assistant]]  ← ALL AI writes go here
  ## [[Scratch Pad]]   ← Simon's personal capture area        (never write here)
  ```

Heading rules:

- **Match headings by NAME, never by `#` level or wrapping.** Levels and
  `[[…]]` backlink-wrapping drift between notes (current notes:
  `## [[AI Assistant]]`; older notes: plain `Assistant` at `#####`/`######`).
  Locate each heading by its text at any `#` level, plain or backlink-wrapped,
  and **preserve the exact level and wrapping that note already uses**.
- **Legacy destination**: a note with an `Assistant` heading and no
  `AI Assistant` below the divider → that heading is the destination. Do not
  rename it, do not add a second heading.
- **No destination heading below the divider** → create `## [[AI Assistant]]`
  at the **very end of the note**, at the same `#` level as that note's `Links`
  heading (or `##` if there is none).
- **No divider at all** → append `---` at the very end, then the heading — but
  only when there is actually content to write.

## Pre-flight rules — apply before every write

1. **Placement**: daily-note content goes under the `AI Assistant` heading
   (legacy: `Assistant`), between it and the next heading. Never above the last
   divider; never under `Scratch Pad`, `Links`, or `Audio Memos`. No exceptions.
   (Mechanically reminded via an Edit/Write hook on Claude Code.)
2. **Nodes**: search first — `reflect search "#node ➡️" --json`. The list grows;
   never hardcode it. Only `#node`-tagged notes are nodes. Obvious match → nest
   the content under a top-level `- [[➡️ NodeName]]` bullet; when in doubt →
   plain top-level bullet, no node.
3. **No `#tags`** in any write. A literal `#word` goes in backticks
   (`` `#example` ``) so it renders as inline code.
4. **Tasks vs. checkboxes** — two different things in Reflect:
   - `+ [ ]` = **Task** (round, appears in the Tasks tab). Use when Simon says
     "Task", "Aufgabe", "Todo", "erledigen", "muss ich noch" — or for real
     action items when in doubt.
   - `- [ ]` = **checkbox** (square, invisible to the Tasks tab). Use when
     Simon says "Checkbox", "Liste", "abhaken" — or for temporary lists
     (Einkaufsliste) when in doubt.
   - Preserve the existing type when moving or editing items. Tasks backlinked
     to another daily note become Upcoming/Overdue.
5. **Point 2 — a new standalone note must be reachable.** At least one of:
   (a) its body contains a `[[Note Title]]` backlink to a non-daily note;
   (b) an existing non-daily note links to it; or (c) fallback — add a bullet
   with a `[[NewNoteTitle]]` backlink under today's `AI Assistant` heading
   (node-nested if obvious). Orphan notes are unreachable and effectively lost.
6. **Formatting**: 2-space indentation per level; structured content as
   sub-bullets, never flat mega-bullets or `·` separators; `**bold**`,
   backtick inline code.

## Deep links — ALWAYS include when referencing a note

Never mention a note without a clickable markdown link:

- **Daily notes**: construct directly — `reflect://daily/YYYY-MM-DD`, e.g.
  `[Daily Note — 21 March 2026](reflect://daily/2026-03-21)`.
- **Standalone notes**: `reflect open <note> --json` → `url` field
  (`reflect://note/<id>`). This launches the app; if that is undesirable,
  reference the note by title and offer to open it.

## Procedures

**Append to today's daily note**: `reflect today --path` → read the file (create
it if missing) → find the destination heading per the layout rules → add
top-level bullets between it and the next heading → save (the app re-imports) →
confirm with the daily deep link.

```
## [[AI Assistant]]

- [[➡️ NodeName]]
  - Your note text here
- Item with no obvious node
+ [ ] A real task
```

**Create a standalone note**: `reflect show "<Title>" --json` (exit `3` = free
to create; `0` = exists — edit that file instead) → write
`notes/<kebab-slug>.md` containing `# <Title>` and a bullet body. Do **not**
fabricate `id:` frontmatter — the app assigns the id on import. Apply Point 2 →
confirm with the `reflect open` url.

**Append to a standalone note**: `reflect path "<Title>"` → edit the file →
confirm with its deep link.

## Hook Enforcement (harness-specific)

The skill text above is the primary rule home. Where the harness supports hooks,
they add a mechanical backstop. Hooks are installed by `sync-skills` only —
never edit the harness config by hand.

### Claude Code (hooks supported)

`sync-skills` merges the following into `~/.claude/settings.json` under `hooks`
(additive merge: same `matcher` replaces its `hooks` array, new `matcher`
appends). The reminder fires whenever an Edit/Write/MultiEdit targets a file
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
            "command": "jq -r 'if ((.tool_input.file_path // \"\") | contains(\"iCloud~app~reflect/Documents/simonsummermatter\")) then {hookSpecificOutput:{hookEventName:\"PreToolUse\",additionalContext:\"Editing a Reflect graph file — reflect-note rules: daily-note writes go ONLY under the `AI Assistant` heading (legacy `Assistant`) in the inbox zone below the LAST `---` divider; match the heading by name at any `#` level and preserve its style; if missing, create `## [[AI Assistant]]` at the very end of the note; never change anything above the last divider; never write under `Scratch Pad`, `Links`, or `Audio Memos`; nest under `- [[➡️ node]]` when it obviously matches (search `#node ➡️` first); tasks `+ [ ]`, checkboxes `- [ ]`; never emit `#tags`; new standalone notes need a backlink (Point 2).\"}} else empty end'"
          }
        ]
      }
    ]
  }
}
```
