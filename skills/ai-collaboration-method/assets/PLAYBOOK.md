# Working method for human + AI sessions — playbook

The full procedure. `SKILL.md` above it holds what an agent needs every session; this file is
read when setting a project up, when writing a runbook or hand-over for the first time, or when
`SKILL.md` is too terse for the case at hand. The reasoning behind every rule is in
`CONCEPT.md` beside this file — read that only when amending the method.

This playbook is binding for sessions on a project that runs the method. It is written to be
portable: everything a project must decide for itself is a **named placeholder**, listed in §0
and filled in that project's method stub — `method/PROJECT.md` inside the project's own
documentation folder, whatever it is called (template: `PROJECT-STUB.md`). No other
line needs changing.

## 0. The placeholders, and what is method rather than project

A project fills these once, at the start, and does not change them:

| Placeholder | What it is |
| --- | --- |
| `<GOVERNANCE>` | the governance document — default `README.md` |
| `<RECORD>` | the running record, one entry per session — default `STATUS.md` |
| `<PLAN>` | the release plan — default `docs/delivery/vN/RUNBOOK.md` |
| `<CONCEPT>` | a subject concept — default `docs/<subject>/CONCEPT.md` |
| `<HANDOVER>` | the hand-over prompt at the repository root — default `⭐HANDOVER.md` |
| `<DEV-BRINGUP>` | the commands that bring the dev environment up |
| `<ID-SCHEME>` | the topic ids the commit prefix derives from — e.g. `S<n>` steps, `H<n>` human topics |
| `<MEMORY-LAYER>` | where durable cross-project facts go |
| `<DOC-LANGUAGE>` | the documentation language |
| `<REVIEW-POINT>` | when the method itself gets reviewed |

**The method fixes the roles, not the names.** Any of the five documents may be called something
else, provided each role has exactly one home and no document holds two roles.

**Check what already holds a default name before taking it.** A file may carry the default name and
do a different job — measured 2026-09-26 on a project whose `STATUS.md` is 253 KB of component state
rather than session entries. Where the name is taken, the role takes a new one and the stub says why. Three things
about the names are fixed, and each is measured:

- **`<HANDOVER>`'s path never changes once chosen** (§8's measurement).
- **`<GOVERNANCE>`, `<RECORD>` and `<HANDOVER>` sit together at the repository root**, being the
  three files a session opens first. The root is also what makes them findable rather than any
  ornament in the name — §8's collation measurement.
- **The version, if the project has one, appears in `<PLAN>`'s path and nowhere else** (§5). A
  project that releases nothing has no version and invents none — measured 2026-09-26 on an estate
  repository whose plans are migrations rather than releases.

## 1. Starting a session

**A new topic starts in a new, cleared session. Always.** The session that wrote the hand-over
must never execute it, even when the human says «go» and even when the next step looks small.
Writing the hand-over *is* the end of the session; the reply that follows it is «the hand-over is
written, clear the session and paste it», and nothing else.

The reason is the whole point of the hand-over. A session that keeps going carries every file it
has already read, every dead end and every superseded draft into work that needs none of it. That
costs tokens, and worse, it hides whether the hand-over is any good: the agent appears to know
things the prompt never said. **A hand-over is only proven by being pasted into an agent with
nothing in its head.** An agent continuing in the same session cannot test its own hand-over, and
must not pretend to.

1. **Read the hand-over first.** `<HANDOVER>` is the prompt for this session. It names the topic,
   the reading order, the state, the single next step and the constraints.
2. **Read in this order and no further:** `<GOVERNANCE>`, `<RECORD>` (the last four entries), the
   `<PLAN>` entries named by the hand-over. Do not read the whole plan.
3. **Search `<MEMORY-LAYER>` once** for the session's topic, and say so in the first reply.
4. **Bring the dev environment up** — `<DEV-BRINGUP>`.

## 2. Doing the work

- **Stay on the primary topic.** One session has one. Work that turns out to be needed and is
  outside it gets **raised as a new topic** and executed only if the human says so in that
  session.
- **If something outside the topic is broken and blocking**, fix the minimum, and write down that
  you did.
- **Red tests block the commit.** No exceptions, no "known failure" carried forward silently.

### The evidence rule

- A status code, a byte count, a row count or a green run is a **measurement**. Before it is
  written down as a **finding**, look at the thing itself: open the body, read the table, print
  the rows.
- **Every hard number that goes into a checklist as an assertion is computed against the real
  data first.** Never reasoned, never carried over from a plan.
- When a measurement contradicts something the project already believes, the belief is wrong
  until proven otherwise, and **the correction is written down as its own finding** — not
  silently absorbed.
- Do not measure a system that is mid-change. A check taken during a deploy reports the deploy,
  not the system.

## 3. Closing a session

**First, check whether the topic is actually finished.** If it is not, say so in one sentence and
stop — do not close a session that is not closed. If it is, run the whole checklist without
asking; closing is not a decision the human should have to authorise each time.

A session is closed when **all six** of these are done. Five of six is an open session.

1. **The topic is marked** in `<PLAN>` with the state vocabulary below.
2. **The project documents are pulled onto the built state** — `<CONCEPT>`, `<PLAN>`,
   `<GOVERNANCE>` — wherever the session changed what is true. A concept that describes the plan
   instead of the thing is worse than no concept.
3. **One `<RECORD>` entry** is written for the session — what happened, what was surprising, what
   the next session must know, with its plain-language layer.
4. **Durable facts go to `<MEMORY-LAYER>`**, one idea per entry, as plain statements.
5. **`<HANDOVER>` is overwritten** with the prompt for the next session, and the same text is
   printed in the reply as one fenced `text` block under a plain heading that names it, with
   nothing else inside the fence. Same text in both places, so there is nothing to keep in sync:
   the file is the record, the fenced block is for copying straight out of the terminal. *Amended
   2026-09-26: this used `>>> PROMPT START >>>` and `<<< PROMPT END <<<` marker lines, which
   rendered as a quoted, italicised block running into the surrounding prose and made the
   boundary harder to see rather than easier. A fence is what the hand-over file itself uses.*
6. **Committed locally** with the derived prefix. **Never pushed** — the human pushes.

**Then stop.** Do not begin the next topic, do not «just start» it because the human agreed to
it, do not read the files it names. The session ends at the commit.

### The closing reply

The reply that closes a session is written for the human, not for the record. `<RECORD>` is the
record, `<PLAN>` is the plan, `<HANDOVER>` is the next session. The reply's only job is to tell
one person what they now have to do. Three parts, in this order, and nothing else:

1. **What the human needs to decide.** Only items that genuinely block delivery. Each one is
   three short lines — the problem, the options, the recommendation — and each one is **written
   into `<PLAN>` or `<RECORD>` before the reply is sent**. The human may not act today, and a
   decision that exists only in a terminal reply is lost when the terminal is closed. Nothing to
   decide is itself worth one line.
2. **What was done.** Labelled as information. A few lines only; the detail is in `<RECORD>`.
3. **The prompt**, as one fenced block (point 5 above).

**Parts 1 and 2 are kept short by being handled earlier.** A decision the human must make is
raised in the middle of the session, when it appears, where answering it is cheap and the answer
can still change the work. Holding it back to the close produces a long reply and a decision made
too late to be useful. Compressing at the end is not the fix; not accumulating is.

**Simple language, precise, no abbreviations, short sentences.** Only what the reader does not
already know.

*Evidence: on 2026-09-26 a session closed with a two-page reply. It was accurate, and all of it
was already written in `<RECORD>`. The human replied «not sure what I need to do». The two things
he had to act on — choose the next project, push three commits — were unlabelled and sat at the
bottom, under findings that were filed elsewhere already.*

**What the hand-over prompt must be.** It addresses an agent with **zero context**. It names the
files to read, the current state in one line, and the single next step. No history, no recap
beyond what the next step needs. Same language as the session; `<DOC-LANGUAGE>` if unclear. Keep
text outside the markers to a minimum, and add a remark after `PROMPT END` **only** if it would
block the next session — otherwise end there. No extras, no «one more thing».

## 4. The status vocabulary

One notation, never varied. No strikethrough, no deleting, and **no row ever moves to another
table**. One emoji and one only: the ✅ described below.

- Executable lines use GitHub task lists: `- [ ]` open, `- [x]` done.
- A topic or a step carries **one bold state word**, and a date once it leaves *Open*:

| State | Written as | Means |
| --- | --- | --- |
| Open | `**Open**` | not started or in progress |
| Blocked | `**Blocked**` | cannot start; the blocker is named in the row |
| Done | `**Done 2026-09-23**` | finished; the reasoning stays in place |
| Dropped | `**Dropped 2026-09-23**` | deliberately not doing it; the reason stays in place |

**A heading whose state is *Done* is prefixed with ✅.** *(Decided 2026-09-24, amending the «no
emoji» half of this rule one day after it was written.)* The tick is a **mirror of the state
word, never a substitute for it**: it carries no date, settles nothing, and where the two
disagree the state word is right and the tick is stale. Its one job is the outline — a document
of thirty headings has to be scannable for what is still open, and a bold word mid-line is not.
The rule survives the addition because it is still **one** notation: the tick is derived from the
state word, not an alternative to it, and no other emoji is in use.

- A `###` topic or step that is **Done** carries `### ✅ <id> — …`.
- A `##` section carries a tick only when every topic under it is done.
- **Open**, **Blocked** and **Dropped** get no marker. The absence of a tick is the signal.

Three consequences, all of them the point:

- **An id is an identity, assigned once, kept for life.** An id is the same id when it closes. No
  second numbering, no "this one is also that one".
- **A closed topic stays exactly where it is**, gains its state and date, and keeps its
  reasoning. Nothing is deleted and no separate "done" list exists — a done list is the same rows
  with a filter applied, and maintaining it by hand is how they fell out of sync.
- **A partial close is not a close.** If half a topic is finished, the row stays `**Open**` and
  says which half is done.

## 5. How `docs/` is filed, and how the plan is organised

### Where a document lives

**Subjects are folders and are never versioned. The release plan is versioned and is never a
subject.** Those are the two halves of one rule, settled 2026-09-26 and executed the same day.

- A subject gets a folder — `docs/reporting/`, `docs/devops/`, `docs/finance/` — and its
  `CONCEPT.md` describes the thing as it stands. **A subject concept is rewritten onto whatever
  is built and never forks per release**, so it carries no version, in its title or anywhere
  else.
- The release plan gets `docs/delivery/vN/RUNBOOK.md`. It is the only document that carries a
  version, because a release is the only thing here that has one.

**In plain words.** A folder name is an address and a version is a state, so filing by version
means moving files every time something is deferred. Put the version where something genuinely
changes version: the plan for a release. Leave the address alone.

- **A shipped release keeps its own `vN/` folder, frozen in place.** When v1 ships, nothing moves:
  `docs/delivery/v1/` stops changing and becomes the record of that release, with room for the
  acceptance results and the cutover notes. `v2/` then opens beside it, **seeded from v1's
  deferred back chapters** — which is what the work order below already produces, so the deferral
  and the next release's opening scope are the same list.
- **A shipped release does not move to `docs/archive/`.** Archive reads as dead and `v1` reads as
  shipped. `docs/archive/` is for `<RECORD>` quarterly cuts (§10) and nothing else.
- **A subject can have a concept and no runbook** — a designed subject not in a release yet. That
  is the rule's own proof rather than a gap.
- **A next version is planned by rewriting the subject concept in place and opening
  `docs/delivery/vN+1/` beside the frozen `vN/`**, seeded from `vN`'s deferred back chapters. The
  rewrite *is* the new version's design; there is never a second concept for the same subject,
  and a subject that enters a release for the first time gains chapters in that release's runbook
  and nothing else.
- **Rewriting a concept is not a deletion.** The no-deletion rule (§4) governs records of
  events — `<RECORD>` entries, plan rows — where a superseded sentence is evidence. A concept is
  a description of a current thing, and keeping every superseded description inside it is how it
  stops being readable. The previous text is in `git log -p` on that path, and what a shipped
  release actually built is in its frozen `vN/`.
- **While a release is in flight the concept describes unbuilt behaviour, so it carries one
  header line: «As built: … · In flight: …».** A reader cannot otherwise tell which paragraphs
  are live. The line is updated when a release ships; nothing is marked per section unless the
  ambiguity actually bites, and then it is §4's vocabulary that marks it.

*Evidence, and its limit.* Measured 2026-09-26 executing this on the reference project: the
runbook held no relative links and never named its own path, so moving it broke not one outbound
reference — the whole cost was eight files naming it from outside, and `git log --follow` reached
the creating commit because the move was committed alone, with no content change. Retitling the
subject concept read right immediately. **But that concept's body was still written about v1**,
so an unversioned title sat over a v1-shaped body. **The rule is therefore proven in the filing
and untested in the rewriting**: its promise that a concept is rewritten rather than forked only
comes due when a second release changes that subject. State it that way until a project has run
it.

### How the plan is chaptered

**Chapters are subjects, not job types and not states.** One chapter per part of the system, and
everything belonging to that part lives in it — the steps an agent executes and the topics only
the human can settle, side by side. **Subject decides *which* chapter an entry is in. A second
rule decides *where that chapter sits*: does it ship the release?** *(Added 2026-09-24, the day
after the chapters were first written.)*

*Evidence:* splitting the file by who executes a thing put a tunnel step in one table and the
token that tunnel needed in another; a timer step in a third and the three accounts that made
those timers mean anything three hundred lines away. A step could be, and was, ticked while its
human half sat unread somewhere else. Filed by subject, the two halves are a few lines apart and
neither can be closed without seeing the other.

- **Chapters are ordered the way they get worked off, and ticked off from the top.** Either you
  execute a chapter or you decide to defer it, and deferring means it moves to a chapter at the
  back. The back chapters are themselves ordered by when they can be started at all.

  *Evidence:* an entry reporting a security finding to a supplier sat in the second of eight
  chapters because it is about that supplier's system. Filed correctly by subject, and blocked
  until that system is decommissioned — which is after the data migration, which is after
  go-live. A reader working down the chapters met, in second position, the one entry that cannot
  be touched until everything else is finished. Subject was right about *which* chapter and
  silent about *where*.

- **Build order is not the rule, even when it looks like it.** A system built bottom-up will have
  its build order and its work order agree for everything still outstanding, and the steps will
  still read in ascending order down the file. That is a coincidence worth naming rather than a
  rule; where the two disagree, the work order wins.

- **Re-filing an entry is a one-off act, licensed only by a change to the organising principle
  itself** — never by a change to an entry's state, which is the failure mode §4 forbids
  outright. **The principle is settled once, at the start of a project.** Measured on the
  reference project: adding the shipping rule one day after the subject rule cost a re-file of
  five entries across a 37-entry document, and that is the cheap version. It should have to be
  bought once and never again.
- **An entry never moves.** It is filed by what it is about, which does not change when it
  closes. Grouping by state would mean shuffling entries on every close, which is §4's failure
  mode.
- **An agent does not find its next step by walking the file.** It is told the topic by the
  hand-over (§1). A merged list cannot be walked: the first human-only entry an agent
  structurally cannot perform would deadlock it. Dependencies run sideways through each entry's
  **Needed by** line.
- **A chapter with nothing in it but human topics is normal**, and so is one with nothing but
  steps. Neither is a sign that the chapter is wrong.

## 6. The formatting law

- **No table cell longer than one line** — about 120 characters. Anything longer becomes a
  heading with bullets underneath it.
- **Tables are for short, comparable attributes**: at most four columns, one line per cell. If a
  cell wants a command, a list, a measurement or a paragraph, it is not a table.
- **Prose is hard-wrapped at a consistent width** — about 100 characters — so a correction touches
  only the lines it changes, and one paragraph is one idea. `<HANDOVER>`'s prompt is the one
  exception and is never wrapped (§8). *Amended 2026-09-26: this read «one sentence per line»,
  which no document in the method had ever followed — 61 such lines in `SKILL.md`, 100 in this
  file, 664 in the reference project's `<RECORD>`. See `CONCEPT.md` principle 5.*
- Headings and bullets are the default for everything else. A document that needs a big table
  almost always needs a section.

## 7. The commit rule

- **The prefix is derived, not chosen: it is the id of the topic the commit advances**, under
  `<ID-SCHEME>` — e.g. `S11: …`, `H20: …`, `method: …`.
- **Work on a different topic is a different commit.** Do not file one topic's work under
  another's prefix.
- The subject says what changed and, where it fits, what was surprising. It is read later by a
  human scanning for when something broke.
- Any number of commits per session is fine. **One `<RECORD>` entry per session is not
  negotiable** — the commits are the trace, the entry is the record.
- **The agent commits and never pushes.** The human pushes.

*Evidence: at the review of 2026-09-23 the reference project had three prefix vocabularies live at
once — `DevOps:`/`Docs:`, then `S<n>:`, then `H<n>:` — and step S10 had reached 14 commits over
three days, absorbing three unrelated topics under a single prefix. A chosen prefix drifts because
nothing outside the author's memory holds it; a derived one cannot, the id existing before the
commit does.*

## 8. The hand-over file

- **One file, always at the same path:** `<HANDOVER>` at the repository root, beside
  `<GOVERNANCE>` and `<RECORD>` — the three files a session opens first.
- **Overwritten at the close of every session**, never deleted and re-created, never accumulated
  into a folder. Because the path never changes, `git log -p <HANDOVER>` is the archive of every
  hand-over written since the file took that path, at no cost and with no clutter. Checked on
  2026-09-23: a move plus a full rewrite in one commit defeats git's rename detection, so
  `--follow` does **not** reach back past the move. Moving this file costs its history; do not.
- **It is a prompt, not a record.** Hard constraint: nothing may exist only in it, because the
  next session overwrites it. Everything it says is also in `<RECORD>` or `<PLAN>`.
- **Meta and prompt are visibly separated, and the prompt is one copy.** The file opens with a
  short *Meta — do not paste any of this* section (what the file is, how to use it, when it was
  written, what the next topic is), and the prompt itself sits in a single fenced ```text block.
  One fence means one click to copy and no judgement about where the prompt begins. Nothing
  outside the fence is ever pasted.
- **The prompt text is not hard-wrapped.** One paragraph is one line; the editor wraps it for
  display. A pasted prompt with fixed line breaks in it reads as broken text.
- **Its shape inside the fence**, in this order:
  - what this session is — and, where it matters, explicitly what it is *not*
  - what to read, in which order, and how much of it
  - the state in about three lines
  - the single next step
  - the constraints (language, documentation duties, commit and push rules)
- **A star or other ornament in the filename is for the eye, not for the sort order.** It makes
  the file impossible to miss in a listing, which is its whole job. It does **not** sort the file
  first, and no rule may depend on that: measured on 2026-09-23, macOS collation ignores the
  symbol and sorts on the letters behind it, git sorts by raw bytes and puts it last, and every
  git output prints the name as escaped octal (`\342\255\220HANDOVER.md`). Sorting first is
  achieved by an ASCII prefix or by living at the repository root.

## 9. Where things are written

| Document | Holds | Does not hold |
| --- | --- | --- |
| `<GOVERNANCE>` | governance, mandates, architecture, how to run it | events, history |
| `<RECORD>` | one entry per session: what happened, why it matters | instructions for what to do next |
| `<CONCEPT>` | one subject as it stands, and why it is that way | a version, a release scope, a plan |
| `<PLAN>` | one release's plan: steps and human topics by subject, the traps ahead | narrative history of finished work |
| `<HANDOVER>` | the next session's prompt | anything that exists nowhere else |
| `docs/archive/` | `<RECORD>` quarterly cuts | shipped releases — those stay in their own `vN/` |
| `<MEMORY-LAYER>` | durable cross-project facts, decisions, preferences | live task tracking |
| `docs/method/PROJECT.md` | this project's placeholder values | any rule of the method itself |

Nothing is written in two of them. If a finding seems to belong in two, it belongs in `<RECORD>`,
and the other place links to it.

**The version is in exactly one place: the release folder.** A subject concept that names a
version in its title is the sign the axes have been crossed — it was true of the reference
project's reporting concept until 2026-09-26, and fixing it was the first real test of §5's rule.

## 10. Keeping the record readable

- **`<RECORD>` is archived per quarter** to `docs/archive/STATUS-YYYY-Qn.md` once it passes
  roughly 60 KB, newest entries staying in place.
- **The header line of `<RECORD>` is at most three bullets** — the current state, the last topic,
  where the next session starts. It is not a summary of the entry below it.
- **Language:** documentation in `<DOC-LANGUAGE>`. Entries written before a language rule changed
  are **not** retranslated — a note records what was decided when, and rewriting it falsifies it.
  The same applies to any record of an event: correcting a closed entry in place falsifies it, so
  the correction goes in the current entry and points back.

## 11. Reviewing the method itself

The method is reviewed when the work it governs is far enough along to judge it — `<REVIEW-POINT>`
names when, and on the reference project that was after eleven sessions. The review reads the
artefacts the sessions produced, not memories of them, and every proposed rule names the evidence
that forced it. Amendments are recorded in `CONCEPT.md`, with their evidence, before they are
written into this playbook.

**Two tests, not one.** Asking «does every rule name its evidence» finds a rule that was never
measured. It does not find a rule that everything silently ignores, and that is the worse of the two
because it is invisible until compliance is measured. So the review also asks, of each rule,
**«does any document actually obey this?»** — and answers it by counting, not by remembering.

*Evidence:* «prose gets one sentence per line» stood in the playbook for three days and had never
been obeyed by anything, including the file that stated it — 61 multi-sentence lines in `SKILL.md`,
100 in the playbook, 664 in the reference project's record. Every reading that checked for evidence
had passed over it. Only counting found it.

**The review opens the standing agenda below**, in `CONCEPT.md`, and closes each item or writes down
why it stays open.

A review that produces no changed rules has almost certainly not looked hard enough.
