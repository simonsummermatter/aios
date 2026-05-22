# aios — AI Operating System skills

Portable skill definitions for AI assistants (Claude Code, Gemini CLI, and similar). Each subdirectory under `skills/` contains a single `SKILL.md` plus any optional asset files.

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
targets: [claude, gemini]  # which harnesses pick up this skill
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

Some skills (notably `reflect-note` and `reflect-inbox`) reference external configuration that lives outside this repo:

- `{graph-id}` — the user's [Reflect](https://reflect.app) graph identifier. Each user supplies their own (e.g., via their CLAUDE.md or equivalent harness-level instructions).
- `${REFLECT_API_TOKEN}` — the user's Reflect personal API token. Never committed; user provides at runtime via env var, keychain, or prompt.

## License

MIT — see [LICENSE](LICENSE).
