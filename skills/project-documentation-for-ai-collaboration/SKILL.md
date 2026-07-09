---
name: project-documentation-for-ai-collaboration
targets: [claude]
has_assets: false
description: >
  Use this skill when starting work on any project repository shared between humans and AI agents.
  Ensures README.md (static governance) and STATUS.md (living project state) exist and are maintained.
  Triggers include: new project setup, first session on an unfamiliar repo, or when asked about
  project documentation standards for AI collaboration.
---

# Project Documentation for AI Collaboration

Establish a meta-documentation layer that lets AI agents collaborate on a project effectively across sessions — without losing context, drifting from intent, or making unauthorised changes.

## Process

- **At session start:** Read `README.md` and `STATUS.md` before doing anything else. Treat them as the binding mandate for the session.
- **Before every commit:** Update `STATUS.md` to reflect what changed. No exceptions.
- **If either file is missing on a new project:** Create it following the structure below.

## README.md — Static Governance

**Purpose:** The single document an AI agent reads to understand the project, its rules, and where the agent must stop.

**Required sections:**

- **System Architecture** — Tech stack, build pipeline, hosting, key services, source of truth
- **Hard Rules for AI Agents** — What is never allowed (e.g. no force push, no auto-commit, no destructive workarounds), permission boundaries, what blocks the agent from acting
- **Governance & Mandates** — Numbered list of binding rules: content standards, navigation rules, formatting conventions, file naming, structural invariants
- **Editorial Workflow** — Step-by-step: who edits what, where the AI agent stops, where the human takes over (e.g. push, deploy, review)

**Tone:** Prescriptive and unambiguous. Use MUST / MUST NOT for non-negotiables.

## STATUS.md — Living Project State

**Purpose:** A continuously maintained snapshot of where the project stands. The agent updates this before every commit so the next session has full context.

**Required sections:**

- **Completed Tasks** — Log of decisions, reversals, and non-obvious context only. Routine changes (package additions, dependency updates) belong in git — do not duplicate them here. Each entry should answer: "Would a future agent misunderstand or undo this without knowing it?"
- **Architectural Mandates (DO NOT CHANGE / MUST NOT BE DELETED)** — Project-specific, non-obvious constraints only — things an agent might otherwise "fix" without realising the consequences (e.g. a flag required by a non-standard installer, a setting with irreversible migration implications). General agent rules (no push, read-first) belong in `README.md`, not here.
- **Issues & Blockers** — What is currently broken, pending, or waiting on a human decision.
- **Backlog** — Open items only. When a Completed Tasks section is present, finished items are moved there and removed from the Backlog. Do not use strikethrough for completed items — it creates redundancy.

**Tone:** Factual, in plain language, written for a future session that has zero memory of the current one.

## Key Rules

- `README.md` is read at session start. `STATUS.md` is read at session start AND updated before every commit.
- Git is the source of truth for what changed. `STATUS.md` is the source of truth for why decisions were made.
- AI agents stage and commit. AI agents do NOT push. The human reviews and pushes manually (e.g. via GitHub Desktop).
- When in doubt about whether a change is allowed, consult the Architectural Mandates in `STATUS.md` first, then the Governance section in `README.md`.
- Never bypass or "work around" the rules to make an obstacle go away. Stop and report instead.

## Adapting the Pattern

- The two-document structure is fixed. The internal sections can be extended for project-specific needs but never reduced below the required sections above.
- The pattern works for any project where humans and AI agents share the same repository — documentation projects, codebases, infrastructure repos, content libraries.
