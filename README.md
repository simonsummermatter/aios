# aios — AI Operating System skills

Portable skill definitions for AI assistants (Claude Code today, future Codex and similar). Each subdirectory under `skills/` contains a single `SKILL.md` plus any optional asset files.

A companion command, `/sync-skills`, lives in `skills/sync-skills/` and copies the right files into each AI tool's local harness based on per-skill `targets` metadata.

## Layout

```
skills/
├── <skill-name>/
│   ├── SKILL.md         # frontmatter + body, the skill definition
│   └── assets/          # optional, only when frontmatter sets has_assets: true
```

## Frontmatter contract

Every `SKILL.md` starts with:

```yaml
---
name: <skill-name>         # must equal the directory name
targets: [claude]          # which harnesses pick up this skill (supported: claude, codex)
has_assets: false          # whether the skill ships extra files
description: >
  Short, action-oriented summary used by the harness to decide when to load this skill.
---
```

## How `/sync-skills` works

1. `git pull --ff-only` inside the local clone of this repo
2. For each `skills/*/SKILL.md`, parse the YAML frontmatter
3. If `targets` includes the current harness → write to that harness's skill path
4. If `has_assets: true` → rsync the whole skill directory
5. If the body contains a `## Hook Enforcement (harness-specific)` section → install hooks (Claude Code only, today)

No string-blob parsing. One file in, one file out, byte-for-byte.

## Configuration placeholders

Some skills (notably `reflect-note` and `reflect-inbox`) reference external configuration that lives outside this repo. [Reflect](https://reflect.app) Open is local-first and markdown-backed: there is no MCP server or REST API. Reading goes through a bundled CLI, and writing is done by editing the note files directly.

- **Reflect graph path** — the local folder of markdown notes that is the user's graph. Each user supplies their own path (e.g., exported as `REFLECT_GRAPH` or passed via `--graph`, set in their CLAUDE.md or equivalent harness-level instructions).
- **`reflect` CLI** — the read-only CLI bundled inside the Reflect app (not on `PATH` by default). The skills call it to read, search, and resolve notes; writes edit the resolved `.md` file, which the running app re-imports automatically.

## License

MIT — see [LICENSE](LICENSE).
