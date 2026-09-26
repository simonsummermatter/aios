---
name: ai-collaboration-method
targets: [claude]
has_assets: true
description: >
  The working method for human+AI sessions on a project repository: one session is one topic
  with one hand-over, findings carry evidence, state has one notation, and a session is closed
  only by a six-point checklist. Use this skill at the START of any session on a project that
  is run this way — a repository holding a hand-over file, a per-session STATUS.md, or a
  docs/method/ stub pointing here — and at the END of every such session before committing.
  Also use it when setting a new project up for AI collaboration, when asked how a project's
  documentation, runbook, status file or hand-over should be structured, or when amending the
  method itself. Triggers: "start the session", "close the session", "write the hand-over",
  "set this project up for AI collaboration", "where does this get written down".
---

# The AI collaboration method

One human, one agent, one repository. The human decides and owns the outside world — logins,
payments, DNS, deploys, pushes, every judgement about scope or risk. The agent builds, verifies
and records, including what it got wrong. Neither owns the method: it is reviewed on purpose.

The method was written on 2026-09-23 by reviewing what eleven sessions on a real project
actually produced, and amended on 2026-09-24 and 2026-09-26 by the same test. **Every rule
below names the evidence that forced it. A rule with no evidence does not belong here.**

**What to read.** This file is what an agent needs every session. Two assets are read only when
that is not enough:

- `assets/PLAYBOOK.md` — the full procedure. Read it when setting a project up, when writing a
  runbook or a hand-over for the first time, or when this file is too terse for the case at hand.
- `assets/CONCEPT.md` — the reasoning and the evidence behind every rule. Read it **only when
  the method itself is being amended**, never for routine work.
- `assets/PROJECT-STUB.md` — a template for the per-project file that fills in the placeholders
  this method deliberately leaves open.

## What is method and what is one project's choice

The method fixes **roles**, not filenames. A project chooses its names once, records them in its
`docs/method/PROJECT.md` stub (`assets/PROJECT-STUB.md`), and never changes them.

| Role | Default name | Fixed by the method? |
| --- | --- | --- |
| governance | `README.md` | the role, not the name |
| running record | `STATUS.md` | the role, and **one entry per session** |
| release plan | `docs/delivery/vN/RUNBOOK.md` | the role, and that the version sits here and nowhere else |
| subject concept | `docs/<subject>/CONCEPT.md` | the role, and that it carries no version |
| hand-over prompt | `⭐HANDOVER.md` at the repository root | the role, and that **the path never changes once chosen** |

Three constraints on those names are not negotiable, and each is measured:

- **The hand-over file never moves.** Measured 2026-09-23: moving it and rewriting it in one
  commit defeats git's rename detection, so `git log -p` on the path — which is the entire
  archive of every hand-over — stops reaching back past the move.
- **Governance, record and hand-over sit together at the repository root.** They are the three
  files a session opens first, and the root is what makes them findable. Measured 2026-09-23: an
  ornament in a filename does not sort it first — macOS collation ignores the symbol, git sorts by
  raw bytes and puts it last, and git output prints the name as escaped octal. Being found first
  comes from the location, never from the decoration.
- **The version appears in the release plan's path and nowhere else** — the filing rule below
  carries the measurement.

Placeholders this method leaves to the project stub: the dev-environment bring-up, the
documentation language, the id scheme the commit prefix derives from, the memory layer, and the
point at which the method is reviewed. Everything else here applies unchanged.

## A session

One session is one sitting: **one primary topic**, any number of commits, exactly one entry in
the running record, one written hand-over — **and it ends there**.

**Start:**

1. Read the hand-over file. It is this session's prompt: topic, reading order, state, the single
   next step, constraints.
2. Read the project's `docs/method/PROJECT.md`. It fills every placeholder this method leaves
   open — the id scheme the commit prefix derives from, which memory layer step 4 searches, the
   documentation language, and the project's own names for the five documents.
3. Read the governance file, the last four entries of the running record, and only the runbook
   entries the hand-over names. Not the whole runbook.
4. Search the memory layer once for the topic, and say so in the first reply.
5. Bring the dev environment up as the project stub describes.

**If there is no hand-over file and no stub, this is a set-up session and not a working one.**
The sequence above has nothing to read until those exist: read `assets/PLAYBOOK.md` §0 and create
the stub from `assets/PROJECT-STUB.md` first.

**During:** stay on the topic. Work that turns out to be needed but is outside it is **raised as
a new topic** and executed only if the human says so in this session. If something outside the
topic is broken and blocking, fix the minimum and write down that you did. Red tests block the
commit — no "known failure" carried forward silently.

**The session that wrote the hand-over must never execute it**, even on an explicit «go» and
even when the next step looks small. A hand-over is only proven by being pasted into an agent
with nothing in its head; a session that carries on cannot test its own hand-over and must not
pretend to. *Evidence: on 2026-09-24 the session that invented this rule broke it within the
hour, on an explicit «go». The rule is written for that moment, not for the easy one.*

## The evidence rule

- A status code, a byte count, a row count, a green run are **measurements**. Before one is
  written down as a **finding**, look at the thing itself: open the body, read the table, print
  the rows.
- **Every hard number that enters a checklist as an assertion is computed against the real data
  first** — never reasoned, never carried over from a plan.
- When a measurement contradicts something the project believes, the belief is wrong until
  proven otherwise, and the correction is written down **as its own finding**.
- Do not measure a system that is mid-change. A check taken during a deploy reports the deploy.

*Evidence, twice over: a wrong address was recorded for weeks as «handled — returns our own
error page, 1065 bytes»; both facts were true and the page was the host's stock page, which one
look at the body would have shown. And two build steps wrote hard numbers into their own
checklists as assertions — «must match 98 rows», «must come back green» — both impossible
against the actual data, because the numbers had been reasoned rather than computed.*

## Two layers on every finding

Every finding carries the precise version **and** a short plain-language one beside it. The
plain layer never replaces the precise layer and is never the only version. The reader is a
human six months later or a fresh agent: both need what was done *and why anyone cared*.

*Evidence: added late, on 2026-09-23, and it is the only late addition with total adoption.
Rules that change what you write stick; rules that ask you to remember something do not.*

## The state vocabulary

One notation, never varied. No strikethrough, no deleting, and **no row ever moves to another
table**. One emoji only: the ✅ below.

- Executable lines are GitHub task lists: `- [ ]` open, `- [x]` done.
- A topic or step carries **one bold state word**, and a date once it leaves *Open*:

| State | Written as | Means |
| --- | --- | --- |
| Open | `**Open**` | not started, or in progress |
| Blocked | `**Blocked**` | cannot start; the blocker is named in the row |
| Done | `**Done 2026-09-23**` | finished; the reasoning stays in place |
| Dropped | `**Dropped 2026-09-23**` | deliberately not doing it; the reason stays in place |

- A `###` topic or step that is **Done** is prefixed `### ✅ <id> — …`. A `##` section is ticked
  only when everything under it is done. **Open**, **Blocked** and **Dropped** get no marker —
  the absence of a tick is the signal.
- The tick is a **mirror of the state word, never a substitute**: no date, settles nothing, and
  where the two disagree the state word is right and the tick is stale.
- **An id is an identity, assigned once, kept for life.** No second numbering.
- **A closed topic stays exactly where it is**, gains its state and date, keeps its reasoning.
  No separate "done" list — that is the same rows with a filter, and maintaining it by hand is
  how they fall out of sync.
- **A partial close is not a close.** Half finished stays `**Open**` and says which half is done.

*Evidence: five ways of saying «this is done» appeared in one file — struck through and left,
not struck and left, moved to another table, silently downgraded, and a tick in a heading. Each
was reasonable on the day; together the file could not be read or searched. The cure is not the
best notation but **one** notation. The tick was then re-admitted on 2026-09-24 only because it
is redundant by construction — derived from the state word, doing the one job the state word
cannot do, which is show up in a thirty-heading outline.*

## Where things are written

| Document | Holds | Does not hold |
| --- | --- | --- |
| `README.md` | governance, mandates, architecture, how to run it | events, history |
| `STATUS.md` | one entry per session: what happened, why it matters | instructions for what to do next |
| `docs/<subject>/CONCEPT.md` | one subject as it stands, and why | a version, a release scope, a plan |
| `docs/delivery/vN/RUNBOOK.md` | one release's plan: steps and human topics by subject, the traps | narrative history of finished work |
| `⭐HANDOVER.md` | the next session's prompt | anything that exists nowhere else |
| `docs/archive/` | `STATUS.md` quarterly cuts | shipped releases — they stay in their `vN/` |
| the memory layer | durable cross-project facts, decisions, preferences | live task tracking |
| `docs/method/PROJECT.md` | this project's placeholder values | any rule of the method itself |

This table names the roles by their default filenames for readability; on a project that chose
other names, its own stub holds the mapping.

**Nothing is written in two of them.** If a finding seems to belong in two, it belongs in
`STATUS.md` and the other place links to it. *Evidence: one step's runbook block reached 23 KB
covering the same days as 5.8 KB of status entries with no stated boundary; one topic got two
status entries on one day; two consecutive commits recorded the same decision.*

**Subjects are folders and are never versioned. The release plan is versioned and is never a
subject.** A folder name is an address, a version is a state. *Evidence: settled and executed
2026-09-26 — the retitle read right immediately, and moving the runbook broke not one outbound
reference because it holds no relative links; the whole cost was eight files naming it from
outside.* **The rule is proven in the filing and still untested in the rewriting**: the promise
that a subject concept is rewritten rather than forked only comes due when a second release
changes that subject. Treat that half as unproven.

Full filing and chaptering rules — freeze-at-ship, chapters by subject then by work order, the
in-flight header line — are in `assets/PLAYBOOK.md` §5. The running record is cut to
`docs/archive/` per quarter once it passes roughly 60 KB, newest entries staying in place;
`assets/PLAYBOOK.md` §10 has that and the record's header-line rule.

## The formatting law

- **No table cell longer than one line** (~120 characters). Longer becomes a heading with
  bullets under it.
- **Tables are for short, comparable attributes**: at most four columns, one line per cell. A
  cell that wants a command, a list, a measurement or a paragraph means it is not a table.
- **Prose is hard-wrapped at a consistent width** — about 100 characters — so that a correction
  touches only the lines it changes. One paragraph is one idea. The exception is the hand-over
  prompt, which is never wrapped at all: see the close checklist.

*Evidence: one table row reached 12,765 characters on a single line and five more passed 1,700.
Such a row cannot be read, cannot be reviewed in a diff — a one-word fix rewrites the whole
line — and cannot hold a command or a measurement.*

*The wrapping rule was amended on 2026-09-26. It previously read «prose gets one sentence per
line», which no document in the method had ever followed — 61 such lines in this file, 100 in the
playbook, 664 in the reference project's record. An unobserved rule is the failure the method
already named once: a written rule the work has silently outgrown is worse than none, because it
is still being quoted. What the measurement above actually supports is a reviewable diff, and
consistent wrapping delivers that.*

## The commit rule

- **The prefix is derived, not chosen: it is the id of the topic the commit advances** —
  `S11: …`, `H20: …`, `method: …`, `skill: …`.
- **Work on a different topic is a different commit.** Never file one topic's work under
  another's prefix.
- Any number of commits per session. **One `STATUS.md` entry per session is not negotiable** —
  the commits are the trace, the entry is the record.
- **The agent commits. The agent never pushes.** The human pushes.

*Evidence: at the review of 2026-09-23 the reference project had three prefix vocabularies in use
at once — `DevOps:`/`Docs:`, then `S<n>:`, then `H<n>:` — and its step S10 had run to 14 commits
across three days, absorbing three unrelated topics under one prefix. A chosen prefix drifts,
because nothing outside the author's memory holds it; a prefix derived from the topic id cannot,
because the id already exists before the commit does.*

## Closing a session — the six-point checklist

**First check whether the topic is actually finished.** If it is not, say so in one sentence and
stop; do not close a session that is not closed. If it is, run the whole checklist without
asking — closing is not a decision the human should have to authorise each time.

A session is closed when **all six** are done. Five of six is an open session.

1. **The topic is marked** in the runbook with the state vocabulary above.
2. **The project documents are pulled onto the built state** — concept, runbook, `README.md` —
   wherever the session changed what is true. A concept describing the plan instead of the thing
   is worse than no concept.
3. **One `STATUS.md` entry** for the session: what happened, what was surprising, what the next
   session must know, with its plain-language layer.
4. **Durable facts go to the memory layer**, one idea per entry, as plain statements.
5. **The hand-over file is overwritten** with the next session's prompt, and the same text is
   printed in the reply as one fenced `text` block, under a plain heading that names it, with
   nothing else inside the fence. Same text in both places, so there is nothing to keep in sync.
6. **Committed locally** with the derived prefix. **Never pushed.**

**Then stop.** Do not begin the next topic, do not «just start» it because the human agreed to
it, do not read the files it names. The session ends at the commit.

**The hand-over prompt** addresses an agent with **zero context**: what this session is and,
where it matters, what it is *not*; what to read, in what order, how much; the state in about
three lines; the single next step; the constraints. No history, no recap beyond what the next
step needs. Not hard-wrapped — one paragraph is one line, because a pasted prompt with fixed
line breaks reads as broken text. Meta and prompt are visibly separated and the prompt is one
fenced ```text block, so copying it takes one click and no judgement. Shape and rules in full:
`assets/PLAYBOOK.md` §8.


## The closing reply

The reply that closes a session is for the human, not for the record. The record is the running
record, the plan is the runbook, the next session is the hand-over file. The reply exists to tell
one person what they now have to do. It has three parts, in this order, and nothing else.

1. **What you need to decide.** Only what genuinely blocks delivery. Each item is three short
   lines: the problem, the options, the recommendation. Every item is **also written into the
   runbook or the running record before the reply is sent**, because the human may not act today
   and a decision that exists only in a reply dies when the terminal is closed. If there is
   nothing to decide, say so in one line.
2. **What was done.** Information only, and labelled as information. A few lines. The detail is
   already in the running record, and repeating it here is how a reply turns into a report that
   nobody reads.
3. **The prompt for the next session**, as one fenced block.

**Parts 1 and 2 are kept short by being handled earlier, not by being compressed at the end.**
A decision the human has to make is raised the moment it appears, in the middle of the session,
where it is cheap to answer and where the answer can still change the work. Saving it for the
close is what produces both a long reply and a decision made too late to matter.

**Simple language, precise, no abbreviations.** Short sentences. Only what the reader does not
already know. Less is more.

*Evidence: on 2026-09-26 a session closed with a reply two pages long. It was accurate and every
word of it was already in the running record. The human's answer was «not sure what I need to
do». The two things he actually had to act on — choose the next project, push three commits —
were unlabelled and sat at the bottom under findings that were filed elsewhere already.*

## Reviewing the method itself

The method is reviewed when the work it governs is far enough along to judge it — the project
stub names that point. The review reads the artefacts the sessions produced, not memories of
them, and every proposed rule names the evidence that forced it. **A review that produces no
changed rules has almost certainly not looked hard enough.** Read `assets/CONCEPT.md` before
amending anything, and record the amendment's evidence there.

## What this method deliberately does not do

- **It does not try to prevent mistakes.** Several of the findings above were only reachable by
  doing the work and looking. The method makes wrong beliefs *cheap to discover*, not rare.
- **It does not add review gates.** There is one human; ceremony that assumes a team is theatre.
- **It does not archive by deleting.** A closed topic keeps its identity and its reasoning where
  it already sits.
