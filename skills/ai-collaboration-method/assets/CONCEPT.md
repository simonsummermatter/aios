# Working method for human + AI sessions — concept

**Read this only when the method itself is being amended.** It is the *why*, and it
justifies rules rather than instructing. Routine sessions need `SKILL.md`; the full
procedure is in `PLAYBOOK.md` beside this file. If this file and the playbook disagree,
this one explains the intent and the playbook wins on the mechanics.

The method was written on 2026-09-23 on the **reference project** — a SaaS reporting module
built across roughly eleven human+AI sessions — by reviewing what those sessions actually
produced rather than what they were supposed to produce. It was amended on 2026-09-24 and
2026-09-26 by the same test. Every rule below names the evidence that forced it. A rule with
no evidence behind it is not in here, and an amendment that cannot name its evidence is not
made.

**Amending the method.** Propose the rule, name the artefact that forced it, write the
principle here with that evidence, then change `PLAYBOOK.md` and, if it is a rule an agent
needs every session, `SKILL.md`. Never the other way round: a playbook rule whose reasoning
was never written down is the rule this project exists to stop being quoted.

**In plain words.** We built something real with an AI over about two weeks, and then
stopped to ask how the *working* went, not how the product turned out. The answer was that
the habits we started with quietly stopped being true, nobody noticed, and the notes we
kept got harder to read the more valuable they became. This paper is the fix, written down
so the next project starts where this one ended instead of relearning it.

## Who does what

- **The human decides and owns the outside world.** Logins, payments, signups, DNS,
  deploys, pushes, and every judgement call about scope or risk. The human is also the only
  reader the documentation is written for; an agent can re-read code, a human cannot
  re-attend a session.
- **The agent builds and records.** It writes code, runs it on the dev host, verifies it,
  and writes down what happened — including what it got wrong.
- **Neither owns the method.** It is reviewed on purpose, at a point where there is enough
  history to review. That is what this document is.

## What a session is

One session is one sitting: one primary topic, any number of commits, exactly one entry in
the living status file, and one written hand-over to the next session.

**And it ends there.** The next topic begins in a cleared session, started by pasting that
hand-over. A session that writes a hand-over and then carries on has not handed anything
over — it has kept the context it was supposed to drop, which is both the expense the
hand-over exists to avoid and the only thing that would have tested whether the hand-over
works. *(Evidence: on 2026-09-24 the session that invented this rule broke it within the
hour, on an explicit «go» from the human. The rule is written for that moment, not for the
easy one.)*

That definition is a correction. The old rule said *one step = one session = one commit*,
and it stopped being true on 2026-09-21 without anyone noticing: step S10 ran across three
days and fourteen commits and absorbed three unrelated topics along the way. Nothing was
wrong with the work — the rule was wrong about the work. **A written rule that the project
has silently outgrown is worse than no rule, because it is still being quoted.**

## The nine principles

Seven were written on 2026-09-23; the eighth and ninth were added on 2026-09-26 and are the
newest and the least proven.

### 1. Documentation is written for the person who was not there

The reader is a human six months later, or a fresh agent with no memory of the session.
Both need the same thing: what was done, and *why anyone cared*. The precise version
answers the first. It does not answer the second, and an exact command survives the gap
between sessions far worse than an everyday analogy does.

So every finding carries **two layers**: the precise one, and a short plain-language one
beside it. The plain layer never replaces the precise layer and is never the only version.

*Evidence:* this rule was added late (2026-09-23) and is the only late addition with total
adoption — every status entry written since has it. Rules that change what you write stick;
rules that ask you to remember something do not.

### 2. A number is not a finding until the body has been read

A status code, a byte count, a row count and a green test are all *measurements*. What they
mean is a separate question, and the gap between the two is where this project lost the most
time.

*Evidence, twice over:*
- A wrong web address was recorded for weeks as "already handled — it returns our own
  designed error page, 1065 bytes". Both facts were true. The page was the hosting
  company's stock page, dated months before the site existed. One look at the body would
  have shown it.
- Two build steps wrote hard numbers into their own checklists as test assertions — "the
  correction rule must match 98 rows", "a windowed sync must come back green" — and both
  were impossible against the actual data. The numbers had been reasoned, not computed.

### 3. One event has one home

Anything that happened is written **once**. The living status file holds what happened and
why a future reader cares. The build runbook holds what to do next and the trap waiting for
whoever does it. A thing written in both places drifts, and the reader cannot tell which
copy is current.

*Evidence:* one step's runbook block reached 23 KB while its status entries covered the same
days in 5.8 KB, with no stated boundary between them; one topic got two status entries on the
same day; two consecutive commits recorded the same decision.

### 4. Marking is a vocabulary, not a preference

Five ways of saying "this is done" appeared in one file: struck-through and left in place,
not struck and left in place, removed to a different table, silently downgraded, and a tick
emoji in a heading. Each was reasonable on the day. Together they mean the file cannot be
read or searched, and a closed item can be mistaken for an open one.

The cure is not the *best* notation. It is **one** notation, written down, never varied.

**Amended 2026-09-24, one day later, by the human — and the amendment is the interesting part.**
The first version of the rule banned emoji outright, and the tick emoji in a heading was listed
above as one of the five offending notations. Simon reversed that half after reading the rewritten
runbook: with thirty headings in one file, the outline is how the file is actually navigated, and
a bold state word sitting mid-line does not show up there. So a *Done* heading now carries a ✅ in
front of its id.

This is not a return to five notations, and the distinction is worth stating because it is the
whole defence. **The tick is derived, not chosen.** It is a mirror of the state word, written
wherever the state word says *Done* and nowhere else; it carries no date, it settles nothing, and
where the two disagree the state word wins and the tick is simply stale. The failure mode of 2026-09
was five *independent* ways of asserting the same thing, each authoritative, none agreeing. One
authority with one derived marker is a different shape — the same shape as a checkbox next to a
sentence, which nobody has ever mistaken for a second opinion.

*The general rule behind it:* a notation may be added when it is **redundant by construction** and
serves a job the canonical form cannot do. It may not be added when it is a second way of saying
the thing.

### 5. The layout has to survive a diff

Long-form writing inside table cells is the single worst habit the reference project
developed. One
row reached **12,765 characters on one line**; five more passed 1,700. Such a row cannot be
read by a person, cannot be reviewed in a diff — a one-word correction rewrites the whole
line — and cannot hold a command, a list, or a measurement.

Tables are for short, comparable attributes. Everything longer is headings and bullets.

*Amended 2026-09-26.* The playbook had carried a second clause under this principle — «prose gets
one sentence per line» — which this principle's measurement never supported and which no document
in the method had ever obeyed: 61 multi-sentence lines in `SKILL.md`, 100 in `PLAYBOOK.md`, 664 in
the reference project's status file. That is the failure named in *What a session is*: a written
rule the work has silently outgrown is worse than no rule, because it is still being quoted. The
measurement supports a diff a person can review, and consistent hard wrapping at about 100
characters delivers that while being what every document already does. The rule now states the
practice. The hand-over prompt stays the deliberate exception, unwrapped, because a pasted prompt
carrying fixed line breaks reads as broken text.

### 6. Every session hands over in writing

A session ends by writing the prompt that starts the next one: what it is, what to read,
where the state stands, the single next step, the constraints. It lives in one file that is
overwritten each time, so it never accumulates and never has to be searched.

The hand-over is a *prompt*, not a record — it is disposable by design, so nothing may
exist only there.

*Evidence:* introduced on 2026-09-23 at the human's request, and the session reading this
paper was started by one. It worked: no context was needed beyond that file.

### 7. Documents are organised by subject, not by who does the work

*Added 2026-09-24, after the runbook was rewritten and the human read the result.*

The build plan and the list of things only the human can do were two separate lists for the life of
the reference project. That felt obvious — one is the agent's, one is Simon's — and it was wrong. They are the
same work seen from two sides, and splitting them by executor filed related things apart.

*Evidence:* the tunnel step and the token it needed sat in different tables. The step that armed
three nightly jobs sat three hundred lines from the three accounts that made those jobs mean
anything, and was ticked while they were still open. Nobody was confused at the time; the cost shows
up on re-reading, when a closed step gives no hint that its human half is still outstanding.

So a document is chaptered by **subject** — the part of the system a thing belongs to — and each
chapter holds every kind of entry about that part. Two consequences follow, and both are features:
the executor becomes an attribute of an entry rather than its address, and an entry never has to
move, because what a thing is about does not change when it closes.

*Amended 2026-09-24, one day later, by the human reading the result.* Subject turned out to answer
only half the question. It says **which** chapter an entry belongs in; it says nothing about **where
that chapter sits**, and a chapter list that cannot be worked down from the top is a filing system
rather than a plan. The second rule is **does it ship the release** — either you execute a chapter
or you decide to defer it, and deferring means it moves to a chapter at the back.

*Evidence:* an entry reporting a security finding to a supplier sat in the second of eight chapters,
because it is about that supplier's system. Filed correctly, and blocked until that system is
decommissioned — which is after the data migration, which is after go-live. So a reader working down
the chapters met the one entry that cannot be started until everything else is finished in second
position. Nothing was wrong with the filing. What was missing was an axis.

*And the cost of learning this late, which is the transferable part.* Adding the second rule the day
after the first one meant re-filing five entries in a 37-document file — a move that principle 4
forbids when a *state* changes, and permits here only because the organising principle itself
changed. **The principle is settled once, at the start of a project.** A re-file is the price of
getting it wrong, it is payable once, and a project that pays it twice has not learnt anything from
paying it the first time.

*The limit worth naming:* a merged list cannot be walked from the top, because an agent will hit the
first entry it structurally cannot perform and stop. That is only a problem for a project that finds
its next task by scanning. A project run this way is told its task by the hand-over, which is
principle 6, so the two rules pay for each other.

### 8. A folder name is an address; a version is a state

*Added 2026-09-26, after the reference project had run for one release and started asking what a
second one would look like.*

**Subjects are folders and are never versioned. The release plan is versioned and is never a
subject.** Filing by version means moving files every time something is deferred, and a subject
concept forked per release means two descriptions of one thing, which is principle 3's failure
mode with a version number on it. Put the version where something genuinely changes version — the
plan for a release — and leave the address alone.

*Evidence, and it is deliberately only half:*

- **Proven in the filing.** Executed the day it was decided. The build plan for the first release
  sat in the folder named after the subject, as though it were a subject document; moved to
  `docs/delivery/v1/RUNBOOK.md`, the retitled concept read right immediately — «Reporting —
  Concept» is the natural title and «Reporting v1 — Concept» was the odd one, which had only ever
  looked normal because the release plan shared its folder. The move itself cost almost nothing: a
  209 KB document holding no relative links and never naming its own path broke not one outbound
  reference, and the entire cost was eight files naming it from outside. History survived because
  the move was committed **alone**, with no content change — `git log --follow` on the new path
  reached the creating commit, which the hand-over file's own history (principle 6's measurement)
  did not, having been moved and rewritten in one commit.
- **Untested in the rewriting.** The concept's body was still written about v1 — its opening
  sentence and its scope section both — so an unversioned title now sits over a versioned body,
  and a header line explains the gap rather than closing it. The rule's real promise, that a
  subject concept is *rewritten* onto the built state rather than forked, only comes due the first
  time a second release changes that subject. **Anyone carrying this rule into a new project
  states it as proven in the filing and untested in the rewriting**, and reports back.

*The consequence that made the rule usable:* while a release is in flight, a subject concept
describes behaviour that is partly built and partly not, and a reader cannot tell which. One
header line — «As built: … · In flight: …» — fixes that, and nothing is marked per section unless
the ambiguity actually bites. Without it the rule is unusable from the second release onwards,
which is why v1 got away without noticing.

### 9. The closing reply is an instruction to one person, not a report

Everything a session produces is already written down: the record holds what happened, the plan
holds what is open, the hand-over holds what comes next. The reply that ends the session
therefore has nothing to preserve. Its only job is to tell the human what he now has to do, and
it competes with nothing — so anything in it that is not an instruction is noise that hides the
instruction.

Two failures follow from ignoring that. A reply that recounts the session buries the one thing
the human must act on. And a decision raised for the first time at the close arrives after the
work it should have shaped is finished, which makes it both expensive to answer and pointless to
have asked. The rule that follows is therefore about *when*, not only about *length*: decisions
go to the human as they appear, mid-session, and the close is short because nothing was saved up
for it.

Anything the human must decide is also written into the plan or the record before the reply is
sent. A reply is not storage. The terminal is closed, the decision is gone, and the next session
starts without it.

*Evidence: on 2026-09-26 the session that installed this method's own skill closed with a
two-page reply. Every statement in it was true and every statement was already in the record.
The human's response was «not sure what I need to do» — and the two items he had to act on,
choosing the next project and pushing three commits, were unlabelled and last. The same session
also had to fix the marker around the pasted prompt, which rendered as an italic quoted block
merging into the prose it was supposed to be separated from.*

## What this method deliberately does not do

- **It does not try to prevent mistakes.** Four of the findings above were only reachable by
  doing the work and looking. The method is built to make wrong beliefs *cheap to discover*,
  not to avoid having them.
- **It does not add review gates.** There is one human. Ceremony that assumes a team would
  be theatre.
- **It does not archive by deleting.** A closed topic keeps its identity and its reasoning
  where it already sits. Deleting the reasoning is how a project loses the answer to
  "why did we decide that?".
