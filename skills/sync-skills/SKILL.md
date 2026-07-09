---
name: sync-skills
targets: [claude]
has_assets: false
description: >
  Sync AI skills from the local clone of the aios repo into this harness. Triggered by
  /sync-skills, "sync skills", "pull skills", "update skills". Reads each
  skills/<name>/SKILL.md, checks per-skill `targets` metadata, and writes only the
  skills targeted at the current harness. Also installs harness-specific hooks when
  declared. Each harness runs this independently and only writes to its own paths.
---

# Sync Skills — local clone → harness

Read skill definitions from the local checkout of `github.com/simonsummermatter/aios` and write the matching `SKILL.md` files (plus assets, plus hooks) into **this harness's own paths only**.

Each tool (Claude Code, future Codex) runs `/sync-skills` independently. A tool MUST NEVER write to another tool's harness — it only syncs skills whose `targets:` list includes itself.

## When to use

- `/sync-skills` — pull the latest skills and apply them to this harness
- After editing a `SKILL.md` in the local clone and pushing to GitHub
- After someone else updates the repo and you want the changes locally
- After adding/changing a skill's hook spec (hooks are installed by this command, never by hand)

## Source of truth

- **Repo:** `github.com/simonsummermatter/aios`
- **Local clone:** `/Users/simonsummermatter/LAB/AREAS/nd_PersonalKnowledgeMgmt/aios`
- **Skills directory in the clone:** `skills/<skill-name>/SKILL.md` (+ optional `assets/` subtree)

If the local clone does not exist, abort and instruct the user to clone first:

```
git clone https://github.com/simonsummermatter/aios.git \
  /Users/simonsummermatter/LAB/AREAS/nd_PersonalKnowledgeMgmt/aios
```

Do **not** auto-clone. The user picks the clone location and auth method.

## Frontmatter contract

Every `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: <skill-name>             # must equal the parent directory name
targets: [claude]              # array; supported values: claude, codex
has_assets: false              # boolean; controls whether assets/ is rsynced
description: >
  ...
---
```

If a skill's frontmatter is missing `targets`, treat as `[claude, codex]` (sync everywhere). If `has_assets` is missing, treat as `false`.

## Harness path map

| Harness | SKILL.md target path | Hook config | Hooks supported |
|---------|----------------------|-------------|-----------------|
| claude  | `~/.claude/skills/<name>/SKILL.md` | `~/.claude/settings.json` | yes |
| codex   | TBD — skip until configured | TBD | TBD |

**Detect the current harness** from where THIS `SKILL.md` is being executed:
- If the running skill file's path matches `*/.claude/skills/sync-skills/SKILL.md` → harness is `claude`
- Otherwise → abort and ask the user which harness this is

## Steps

### 1. Update the local clone

```
cd /Users/simonsummermatter/LAB/AREAS/nd_PersonalKnowledgeMgmt/aios
git pull --ff-only
```

If the clone has uncommitted local changes, report them but proceed (the pull will fast-forward as long as no conflicts). If `git pull` fails (e.g., divergent history), abort and surface the error — do not auto-merge, do not stash.

### 2. Enumerate skills

List every directory under `skills/` that contains a `SKILL.md` file. The directory name MUST equal the `name:` field in the SKILL.md frontmatter; if they differ, skip that skill and report a naming mismatch.

### 3. Per-skill: read, filter, write

For each `skills/<name>/SKILL.md`:

1. Read the file in full.
2. Parse the YAML frontmatter (the block between the first two `---` lines). Extract `name`, `targets`, `has_assets`.
3. Validate `name` == directory name. Mismatch → skip + report.
4. If the current harness is not in `targets` → skip + report as "skipped (not targeted)".
5. Compute the target SKILL.md path from the harness path map.
6. `mkdir -p` the target directory.
7. Compare existing SKILL.md (if any) with the new content:
   - identical → record as "up to date", skip write
   - different → write new content, record as "updated"
   - new file → write, record as "created"
8. If `has_assets: true` and an `assets/` subtree exists in the source: rsync the entire `skills/<name>/` directory into the target skill directory (so SKILL.md AND all assets are mirrored). Use `rsync -a --delete` so removed assets are cleaned up.

### 4. Install harness-specific hooks (Claude Code only, today)

For each just-written SKILL.md, scan for a `## Hook Enforcement (harness-specific)` heading at column 0 (a true markdown H2 — not inside backticks or code fences).

If present:
1. Find a line at column 0 starting with `### Claude Code (hooks supported)`.
2. Inside that subsection, find the first fenced ```json block.
3. Parse the JSON. Expected shape: `{"hooks": {"<EventName>": [{"matcher": "...", "hooks": [...]}, ...], ...}}`.
4. Merge into `~/.claude/settings.json`:
   - If the file doesn't exist → start from `{}`. If it has no top-level `hooks` key → treat as `{"hooks": {}}`.
   - For each `EventName`, ensure `settings.hooks[EventName]` is an array.
   - For each `{matcher, hooks}` entry in the skill spec:
     - If an existing entry has the same `matcher` string → replace its `hooks` array (record as "updated").
     - Otherwise → append (record as "installed").
   - Preserve all other top-level keys (`permissions`, `model`, `theme`, etc.) verbatim.
   - Write back with 2-space indent.

If the JSON block fails to parse → skip hook install for that skill, record `hook install error: invalid JSON`, never write a partial merge.

**Other harnesses**: no hook mechanism today — skip silently and report "n/a (harness does not support hooks)".

### 5. Report

```
Skill Sync Complete (<harness>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Skill | Status | Hooks | Notes |
|-------|--------|-------|-------|
| reflect-note | updated | installed (4) | |
| ob1 | up to date | n/a | |
| pdf | created | n/a | has assets |
| <skill> | skipped | — | not targeted at this harness |

Total: X processed, Y updated, Z created, W up to date, V skipped
Hooks: A installed, B updated, C unchanged, D harness does not support hooks
```

- Flag skills with `has_assets: true` in the Notes column.
- Each skill row links to its source: `[skill-name](https://github.com/simonsummermatter/aios/blob/main/skills/<name>/SKILL.md)`.
- If any skill was skipped due to a parse/validation error, list the reason in Notes — do not silently omit.

## Guardrails

- **Never edit hook configs by hand.** The source of truth is the per-skill `## Hook Enforcement` section in the repo. To change hooks, edit the SKILL.md and re-sync.
- **Do NOT auto-remove hooks** when a skill loses its Hook Enforcement section. Report orphaned hooks (matchers in `settings.json` that no live skill claims) so the user can decide manually.
- **Never write to another harness's path.** A harness only writes to its own target path (Claude → `~/.claude/...`). The harness-detection step gates this.

## Error handling

- Local clone missing → abort, print the `git clone` command shown above.
- `git pull` fails (network, divergent history, conflict) → abort, surface git's exit code and stderr. Do not stash, do not force-update.
- A `skills/<name>/SKILL.md` has malformed YAML frontmatter → skip that skill, report "skipped — frontmatter malformed".
- A skill's `name:` field doesn't match its directory name → skip, report the mismatch.
- A skill's `targets:` field is missing or empty → treat as `[claude, codex]` (sync everywhere).
- `~/.claude/settings.json` exists but is not valid JSON → stop hook installation entirely, do not attempt merge, report the file path so the user can repair it manually.
- A skill's Hook Enforcement section exists but the JSON code block is malformed → skip hook install for that skill, report "hook install error: invalid JSON".
