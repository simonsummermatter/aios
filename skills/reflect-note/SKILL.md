---
name: reflect-note
targets: [claude, gemini]
has_assets: false
description: >
  Use this skill for ANY interaction with Reflect Notes — reading, searching, writing, or appending. This includes: saving/noting/adding content to daily or standalone notes ("notiere in Reflect", "füge in Reflect hinzu", "note in Reflect", "add to Reflect", "save to Reflect"); reading or searching notes ("was steht in Reflect", "search Reflect", "find in Reflect", "zeig mir meine Reflect Note"); or any use of reflect-notes MCP tools (search_notes, get_note, get_daily_note, append_to_daily_note, create_note). Always read this skill BEFORE calling any reflect-notes MCP tool or REST API — it contains critical rules about deep links that must be followed on every interaction.
---

# Reflect Note Skill

Read and write content in the user's Reflect notes.

## Pre-flight Checklist — Apply BEFORE Any Write/Edit/Delete

Before calling ANY Reflect write/edit/delete tool (MCP or REST), confirm:

1. **listName**: `append_to_daily_note` calls MUST use `listName: "[[AI Assistant]]"`. No exceptions. (Mechanically enforced via hook on Claude Code; skill-only rule on Gemini CLI and Claude Desktop / iPhone.)
2. **Node search done**: For daily-note writes that obviously belong under a `#node`, you must have searched (`search_notes(query: "#node ➡️", searchType: "text", limit: 100)`) and selected the matching node. When in doubt → no node, just `[[AI Assistant]]`.
3. **Point 2 (new standalone notes)**: When calling `create_note`, the new note MUST end up reachable. See "Creating a Standalone Note — Backlink Rule (Point 2)" below.
4. **No tags**: Never emit `#tag` syntax in any write. If a literal `#word` is needed, wrap it in backticks so it renders as inline code (e.g. `` `#example` ``). Tags clutter Simon's tag list.

These rules apply to MCP tools, REST API fallback, and every edit/delete operation on existing Reflect content. Edit/delete operations: confirm the placement still follows the rules after your change.

## Reading vs. Writing — Pick the Right Tool

| Action | Primary Tool | Fallback |
|--------|-------------|----------|
| **Read / Search** | MCP `reflect-notes:search_notes` | — (no REST fallback for reading) |
| **Get daily note** | MCP `reflect-notes:get_daily_note` | — |
| **Get note by ID** | MCP `reflect-notes:get_note` | — |
| **Write to daily note** | MCP `reflect-notes:append_to_daily_note` | REST API `PUT /daily-notes` |
| **Create standalone note** | MCP `reflect-notes:create_note` | REST API `POST /notes` |

**MCP-first rule:** Always try writing via the MCP server first. Only fall back to the REST API if the MCP tools are unavailable (e.g. MCP server not connected, tool call fails with a connection error). If the MCP tool returns a proper error about invalid input, fix the input — don't switch to REST.

## API Limitations

The Reflect REST API is **append-only by design** — notes are end-to-end encrypted, so the server cannot read existing note contents. This has two important consequences:

1. **No reading via REST API** — always use the MCP server for reading/searching.
2. **No appending to existing standalone notes** — there is no endpoint to append to a note that already exists. The only write options are:
   - Append to a daily note (works great via MCP or REST)
   - Create a *new* standalone note (does not modify existing ones)

If the user asks to add content to an existing standalone note, explain this limitation and offer alternatives:
- Append to today's daily note instead (with a backlink to the relevant note)
- Create a new note with a related title

**Official API documentation:** https://reflect.academy/api
**Full endpoint reference:** https://openpm.ai/packages/reflect

## Config

- **Graph ID**: `{graph-id}`
- **API Key** (REST fallback only): `${REFLECT_API_TOKEN}`
- **Base URL** (REST fallback only): `https://reflect.app/api`
- **Date format for MCP search**: English with ordinal, e.g. `"Thu 5th March 2026"`

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

**Scheduling von Tasks:** Tasks in Daily Notes erscheinen standardmässig als "Current". Durch Backlink auf eine andere Daily Note werden sie "Upcoming" (Zukunft) oder "Overdue" (Vergangenheit).

## Deep Links — ALWAYS Include When Referencing a Note

Whenever a Reflect note is mentioned, found via search, or written to, ALWAYS provide a clickable Markdown link in the response. No exceptions.

**URL schema:**
```
https://reflect.app/g/{graph-id}/{noteId}
```

The `noteId` comes directly from the MCP search result field `Note ID`.

**Daily notes** have a noteId in the format `DDMMYYYY`, e.g.:
- 7th March 2026 → `https://reflect.app/g/{graph-id}/07032026`
- 12th February 2026 → `https://reflect.app/g/{graph-id}/12022026`

**Regular and link notes** have a longer noteId (hash), e.g.:
- `https://reflect.app/g/{graph-id}/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- `https://reflect.app/g/{graph-id}/link-<hash>`

**Format always as a Markdown hyperlink**, e.g.:
`[Daily Note — 7th March 2026](https://reflect.app/g/{graph-id}/07032026)`
`[Erika Mustermann](https://reflect.app/g/{graph-id}/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)`

**RULE: Never mention a note by name without its link. Always construct the link from the Note ID returned by the MCP.**

## Reading (MCP Server)

Use `reflect-notes:search_notes`:
- `query`: search term — for daily notes use the English date format above
- `searchType`: `"text"` for exact match, `"vector"` for semantic search
- `limit`: number of results (default 3)

Use `reflect-notes:get_daily_note`:
- `date`: ISO format `YYYY-MM-DD`

Use `reflect-notes:get_note`:
- `noteId`: the unique note identifier

## Writing — Primary Method (MCP Server)

### Node System (2nd Brain / PARA)

The user's PKM uses **nodes** — tagged with `#node` and named with a `➡️` prefix (e.g. `➡️ AOMIForward`). Each node is like a folder in the PARA system (Projects, Areas, Resources, Archive). Every piece of information belongs under a node.

**When writing to a daily note:**

- **Always** append under `[[AI Assistant]]` using the `listName` parameter.
- **If the content obviously belongs to a specific node**, include the node backlink as an intermediate level. The `text` parameter becomes a nested structure: the node backlink on the first line, followed by the actual note as a sub-bullet.
- **If no node matches**, the `text` parameter is just the plain note text.

**How to match a node:**
- Before writing, always search for nodes dynamically: `reflect-notes:search_notes(query: "#node ➡️", searchType: "text", limit: 100)`.
- The node list grows over time — never rely on a hardcoded list. Always look up current nodes via the MCP search above.
- Scan the returned node names and their summaries. Pick a node only when it's a clear, obvious match for the note content.
- When in doubt, skip the node and only write under `[[AI Assistant]]`.
- Only notes tagged `#node` are valid nodes — ignore everything else.

### Append to Daily Note (MCP)

Use `reflect-notes:append_to_daily_note` with:
- `date` (string, required): ISO 8601 format, e.g. `"2026-03-13"`
- `text` (string, required): The note content — with or without a node prefix
- `listName` (string, optional): Always set to `"[[AI Assistant]]"`

**With node match** (creates three-level nesting):
```
append_to_daily_note(
  date: "2026-03-13",
  text: "[[➡️ NodeName]]\n  - Your note text here",
  listName: "[[AI Assistant]]"
)
```

This produces:
```
- [[AI Assistant]]
  - [[➡️ NodeName]]
    - Your note text here
```

**With multiple sub-bullets under a node** — use `\n    - ` (4 spaces + dash) for each sub-bullet:
```
text: "[[➡️ NodeName]]\n  - Parent title\n    - **Label**: first point\n    - **Label**: second point\n    - **Label**: third point"
```

This produces:
```
- [[AI Assistant]]
  - [[➡️ NodeName]]
    - Parent title
      - Label: first point
      - Label: second point
      - Label: third point
```

**Without node match** (creates two-level nesting):
```
append_to_daily_note(
  date: "2026-03-13",
  text: "Your note text here",
  listName: "[[AI Assistant]]"
)
```

**Formatting rules (confirmed working):**
- `**text**` → bold
- `` `text` `` → inline code
- `\n    - ` (4 spaces + dash) → sub-bullet under parent
- Never use `·` as a separator — always use `\n    - ` structure
- Never put multiple points in one long flat bullet — always use sub-bullets for structured content

### Create Standalone Note (MCP)

Use `reflect-notes:create_note` with:
- `subject` (string, required): Note title
- `contentMarkdown` (string, optional): Markdown body. Supports `[[Note Title]]` for backlinks and `#tag-name` for tags.

```
create_note(
  subject: "Project Ideas",
  contentMarkdown: "Some ideas for Q2...\n\n- Idea A\n- Idea B"
)
```

If a note with the same subject already exists, the MCP server returns the existing note without modifying it.

### Creating a Standalone Note — Backlink Rule (Point 2)

A newly created non-daily note MUST satisfy at least one of:

- **(a) Outgoing backlink**: the note's `contentMarkdown` already contains one or more `[[Note Title]]` references to other non-daily notes.
- **(b) Known incoming backlink**: another existing non-daily note already links to this one (e.g., the user explicitly said "linked from project X", or you are about to write that link).
- **(c) Daily-note backlink (default fallback)**: call `append_to_daily_note` with a backlink to the new note under `[[AI Assistant]]`, following the same node-matching rules as any other daily-note write.

**Why:** Reflect's graph value depends on connectivity. Orphan notes are unreachable from Reflect's backlink suggestions and effectively lost.

**Procedure after every `create_note`:**

1. Inspect the `contentMarkdown` you just wrote — does it already contain a `[[Note Title]]` reference to a non-daily note? → done (case a).
2. If not, is there a clear context implying an existing or about-to-be-written incoming link? → proceed with that follow-up write (case b).
3. Otherwise → call `append_to_daily_note` with `listName: "[[AI Assistant]]"`, a suitable node prefix if obvious, and the body containing a `[[NewNoteTitle]]` backlink (case c — default).

**Example — case (c), the default:**

```
create_note(subject: "Q3 2026 Goals", contentMarkdown: "## Personal\n- ...\n\n## Work\n- ...")
# After create_note succeeds:
append_to_daily_note(
  date: "2026-05-14",
  text: "[[➡️ Goals]]\n  - [[Q3 2026 Goals]]",
  listName: "[[AI Assistant]]"
)
```

**Same rule applies to REST fallback** (Claude Desktop on iPhone): after `POST /notes`, call `PUT /daily-notes` with a backlink. Skill text is the only enforcement on that harness — no hook reminder.

## Writing — Fallback Method (REST API)

Use the REST API only when the MCP tools are unavailable (server not connected, connection errors). Do not use REST if MCP returned a proper validation error — fix the input instead.

### Append to Daily Note (REST fallback)

```bash
curl -s -X PUT "https://reflect.app/api/graphs/{graph-id}/daily-notes" \
  -H "Authorization: Bearer ${REFLECT_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "YYYY-MM-DD",
    "text": "Your note text here",
    "transform_type": "list-append",
    "list_name": "[[AI Assistant]]"
  }'
```

Parameters:
- `date` (string, optional): ISO 8601 (e.g. "2026-03-05"). Defaults to today.
- `text` (string, required): The note content — with or without a node prefix.
- `transform_type`: Always `"list-append"`.
- `list_name`: Always `"[[AI Assistant]]"`.

The same node-prefix patterns apply as in the MCP section above.

### Create Standalone Note (REST fallback)

```bash
curl -s -X POST "https://reflect.app/api/graphs/{graph-id}/notes" \
  -H "Authorization: Bearer ${REFLECT_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Note Title",
    "content_markdown": "Your markdown content here"
  }'
```

Parameters:
- `subject` (string, required): Note title.
- `content_markdown` (string, required): Markdown body.
- `pinned` (boolean, optional): Pin the note.

Point 2 (backlink rule) applies here too: after creating the note via REST, also call `PUT /daily-notes` with a backlink under `[[AI Assistant]]` unless the new note's `content_markdown` already contains a non-daily `[[...]]` backlink.

## Examples

**Read today's note:**
"Was steht heute in Reflect?" → `search_notes(query: "Sat 7th March 2026", searchType: "text", limit: 3)`
→ Return result with link: [Daily Note — 7th March 2026](https://reflect.app/g/{graph-id}/07032026)

**Search for a person:**
"In welcher Note habe ich Notizen über Erika?" → `search_notes(query: "Erika Mustermann")`
→ Return result with link: [Erika Mustermann](https://reflect.app/g/{graph-id}/{noteId})

**Daily note — node match (MCP):**
"Notiere in Reflect dass ich mich um die MWST kümmern muss"
→ `append_to_daily_note(date: "2026-03-07", text: "[[➡️ MyFinances]]\n  - Muss mich um die MWST kümmern", listName: "[[AI Assistant]]")`
→ Confirm with link: "Notiert in Reflect unter `[[AI Assistant]]` → `[[➡️ MyFinances]]`. [Daily Note — 7th March 2026](https://reflect.app/g/{graph-id}/07032026)"

**Daily note — no obvious node (MCP):**
"Note in Reflect: Remember to call back Martin"
→ `append_to_daily_note(date: "2026-03-07", text: "Remember to call back Martin", listName: "[[AI Assistant]]")`
→ Confirm with link: "Notiert. [Daily Note — 7th March 2026](https://reflect.app/g/{graph-id}/07032026)"

**Specific date (MCP):**
"Add to Reflect on March 10th: Meeting with Anna at 2pm"
→ `append_to_daily_note(date: "2026-03-10", text: "Meeting with Anna at 2pm", listName: "[[AI Assistant]]")`
→ Confirm with link: "Notiert. [Daily Note — 10th March 2026](https://reflect.app/g/{graph-id}/10032026)"

**Task hinzufügen (rund, erscheint im Tasks-Tab):**
"Füge Task in Reflect hinzu: Rechnung an Kunde schicken"
→ `append_to_daily_note(date: "2026-03-07", text: "+ [ ] Rechnung an Kunde schicken", listName: "[[AI Assistant]]")`

**Checkbox-Liste (eckig, nur Scratchpad):**
"Notiere Einkaufsliste: Milch, Eier, Brot"
→ `append_to_daily_note(date: "2026-03-07", text: "Einkaufsliste\n  - [ ] Milch\n  - [ ] Eier\n  - [ ] Brot", listName: "[[AI Assistant]]")`

**Standalone note (MCP):**
"Create a new Reflect note titled 'Project Ideas'"
→ `create_note(subject: "Project Ideas", contentMarkdown: "...")`
→ Confirm with link using the noteId returned from the MCP response.
→ Then verify Point 2: ensure the note has a non-daily backlink to/from another note, or write one in today's daily note under `[[AI Assistant]]`.

**Fallback example (REST, only when MCP unavailable):**
If `append_to_daily_note` MCP tool fails with a connection error:
→ Fall back to `curl -s -X PUT "https://reflect.app/api/graphs/{graph-id}/daily-notes" ...` with the same content
→ Log that REST fallback was used so the user is aware

## Hook Enforcement (harness-specific)

The skill text above is the primary rule home — every harness reads and follows it. Where the host harness supports hooks, those hooks provide a mechanical backstop on top of the skill text. Hook installation is performed by `sync-skills` per harness; never edit the harness config by hand.

### Claude Code (hooks supported)

`sync-skills` merges the following into `~/.claude/settings.json` under the `hooks` key, preserving pre-existing unrelated entries (additive merge — same `matcher` means replace its `hooks` array; new `matcher` means append).

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__reflect-notes__append_to_daily_note",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r 'if (.tool_input.listName // \"\") == \"[[AI Assistant]]\" then empty else {decision:\"block\", reason:\"Reflect write blocked: listName must be \\\"[[AI Assistant]]\\\" per reflect-note skill Pre-flight Checklist. Re-read the skill and retry.\"} end'"
          }
        ]
      },
      {
        "matcher": "mcp__reflect-notes__(update_note_subject|replace_text_in_block|insert_at_top|insert_at_bottom|insert_at_position|replace_range|delete_range|toggle_checkbox|update_block_attributes|delete_tag)",
        "hooks": [
          {
            "type": "command",
            "command": "printf '%s' '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"additionalContext\":\"Editing/deleting Reflect content — confirm reflect-note skill Pre-flight Checklist applies (especially Point 1 placement under [[AI Assistant]]) before proceeding.\"}}'"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r 'if (.tool_input.command // \"\") | test(\"reflect\\\\.app/api\") then {hookSpecificOutput:{hookEventName:\"PreToolUse\",additionalContext:\"REST API hit on reflect.app/api detected. On Claude Code the MCP is always available — REST is the iPhone/Claude-Desktop fallback. Did the MCP fail? If yes, investigate. Otherwise switch to MCP.\"}} else empty end'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mcp__reflect-notes__create_note",
        "hooks": [
          {
            "type": "command",
            "command": "printf '%s' '{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"Just created a new standalone note. Verify Point 2 (backlink rule) NOW: does the body contain a non-daily [[...]] backlink? If yes → done. If you know another existing non-daily note already links to it → state that explicitly. Otherwise → you MUST call append_to_daily_note with [[AI Assistant]] + suitable node + a [[NewNoteTitle]] backlink before moving on.\"}}'"
          }
        ]
      }
    ]
  }
}
```

What each hook enforces:
- **PreToolUse `append_to_daily_note` block**: mechanical guarantee of Pre-flight Checklist rule 1 (`listName: "[[AI Assistant]]"`). Cannot be bypassed.
- **PreToolUse edit/delete reminder**: forced awareness on every Reflect edit so placement rules can't slip when mutating existing content.
- **PreToolUse Bash anomaly warning**: catches accidental REST API usage on Claude Code where MCP should always be the path.
- **PostToolUse `create_note` reminder**: forces explicit Point 2 verification after every standalone-note creation.

### Gemini CLI (no hook support)

Gemini CLI does not currently expose a PreToolUse/PostToolUse hook mechanism equivalent to Claude Code. This harness relies on skill text alone. If/when Gemini CLI gains hook support, the equivalent spec will be added here and `sync-skills` extended accordingly.

### Claude Desktop / iPhone (no hook support, REST path)

Claude Desktop has no hook mechanism, and on iPhone it cannot reach the locally-running Reflect MCP — it must use the REST API. Skill text alone is the enforcement here; the Pre-flight Checklist at the top and the REST fallback section above are the only safeguards. Read carefully and follow.
