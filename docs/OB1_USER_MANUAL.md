# Open Brain (ob1) — End-User Manual

> A plain-language guide to what ob1 is, everything it can do, and how it behaves
> when you ask it to "remember" a document. Written for a user, not a developer.
> Last updated 2026-08-08.

---

## 1. What ob1 is

A **shared long-term memory notebook for the AI** — a database of short **text notes**
("memories") on the MNEME server that *any* AI session can read and write. Its purpose:
a future AI conversation, days or months later with zero memory of today, can be reminded
of your decisions, infrastructure, people, and preferences.

You never talk to ob1 directly — you talk to the AI, and it reads/writes ob1 for you.
"Remember this" → a save. Needs background → a search.

## 2. The two basics — store & retrieve

| You say… | What happens |
|---|---|
| "Remember that…" / "store this" | The AI saves a short text note. |
| "What do I know about X?" / `/ob1 X` | The AI searches and shows matching notes. |

Everything else is a variation of those two.

## 3. The actions

You speak naturally and the AI picks the right one.

- **Writing** — store one · store many (batch = "memorise this document") · update
  (correct without duplicating) · delete by ID.
- **Reading** — search (by meaning) · browse recent/filtered (by type/tag/person) ·
  stats overview · daily digest (last N days) · list action items (paginated).
- **To-do queue** — list open action items · clear one once handled (`resolve`). The
  queue is worked down with the `/ob1-review` skill during the `[[OB1 tidied]]` habit:
  each item is promoted to a real Reflect task, deferred to `Open Questions`, or cleared
  as not-a-task. See §7.
- **Housekeeping** (usually automatic) — de-duplicate *exact* duplicates (it does not
  merge two notes that say the same thing in different words — nothing does) · retry
  failed metadata if the cloud labeller was down.
- **Keeping current** (the review queue) — review pending links · confirm/reject a link ·
  link two notes by hand · mark a note reviewed · sweep older notes. See §6.

## 4. Tags, types & the task policy (auto-labelling)

You do **not** tag by hand. On every save an AI step attaches a **type**
(`fact`/`decision`/`idea`/`event`/`person_note`/`reference`/`other`), 1–4 **tags**,
**people**, and any **action items**. The note is stored **instantly**; these fill in a
few seconds later in the background (this is what keeps saving fast).

> **⚠️ ob1 is a memory store, not a task tracker.** Real, ready tasks go to **Reflect**
> as a `+ [ ]` Task, never ob1. ob1 only holds task-shaped items in three cases, all
> written as **plain statements, never as to-dos**:
> - **Parked fallback** — a real task captured when Reflect was unreachable (as a
>   "to reconcile into Reflect" statement); the review loop moves it to Reflect.
> - **Not-yet-ready** — a genuine intention too vague to action yet.
> - **Aspirational wish** — "eventually we should do more sport."
>
> Whatever still lands in the to-do queue is triaged via `/ob1-review`. Since
> 2026-08-03 the extractor returns an empty list for rules/negations (e.g. "never…",
> "do not…") and for `fact`/`decision`/`person_note` memories, so a ban no longer
> becomes a checkbox that reads as an instruction to do the forbidden thing. This split
> is enforced in the AI's always-active protocol in `~/.claude/CLAUDE.md`.

## 5. How search finds things (why it's "smart")

Not keywords. Each note's text becomes an "embedding" (numbers representing its meaning);
your query is embedded the same way, and ob1 returns the closest-meaning notes with a
**similarity score** (higher = closer). So you can search in your own words — synonyms
and paraphrases work. It searches across **everything**, one pool.

**Recency-aware** (since 2026-08-02): results blend meaning with recency, so a fact from
last week edges out an equally-relevant one from two years ago. The weighting is mild and
can be turned off per search ("ignoring recency"); the score shown is still the raw
meaning score.

## 6. The review queue — keeping knowledge current (2026-08-02)

Old notes never expire, so this keeps stale knowledge from quietly outranking current
knowledge:

- On every save ob1 compares the new note against its closest existing notes and asks
  whether it **replaces / contradicts / refines / supports / depends on** them, parking
  each as a **proposal**.
- **Proposals change nothing until you decide** — a wrong "replaces" would bury a note
  that is still correct. Ask *"what's in my ob1 review queue?"* and confirm/reject. A
  confirmed replacement flags the old note `⚠ superseded by 825` in searches but never
  deletes it.
- Notes the AI saved on its own start **unreviewed** with a small ranking penalty (never
  hidden); confirm with *"mark 812 confirmed."* Everything before 2026-08-02 counts as
  confirmed.
- Work the pre-feature backlog with *"sweep 20 memories for relations"* — check each
  batch's proposals before running more.
- **Deliberate gap**: no near-duplicate detection — two notes saying the same thing in
  different words stay separate (upstream OpenBrain has no answer for this either).

## 7. The `/ob1-review` sweep — draining the to-do queue (rebuilt 2026-08-07)

Not the same thing as §6. That one curates *links between notes*; this one triages the
*action items* that got extracted onto notes and should mostly never have been to-dos.

You start it by typing **`/ob1-review`**, on the cadence of the `[[OB1 tidied]]` habit —
it never runs on a timer.

Two rules shape it. **Never make the user adjudicate what a rule can decide**:
superseded, duplicated and past-dated items are pre-decided by the agent, but still shown
with the evidence cited on each row, so a wrong call costs one click instead of vanishing
unseen. **Never make the user type prose to confirm**: everything lands in a mouse-driven
picker (`skills/ob1-review/assets/picker.py` in the `aios` repo) where only the wrong rows
get flipped.

**Six states — four dispositions, two escalations:**

| Key | State | What happens |
|---|---|---|
| `p` | **promote** | Real next step → a `+ [ ]` task in the Reflect daily note, then cleared from ob1. |
| `d` | **defer** | Real but not yet actionable → a bullet in the Reflect note `OB1 Memories: Open Questions` **first**, then cleared. |
| `c` | **clear** | Never was a task. Nothing written; the memory itself stays and still surfaces in searches. |
| `r` | **rule** | A standing policy the extractor rendered as a to-do. Same effect as clear, counted separately. |
| `e` | **explain** | A hold, not a decision. Returns to the agent for background, then back to the picker. |
| `w` | **wrong** | The *memory* is factually wrong. Nothing resolved; the memory is corrected in chat (`update_memory`, or `delete_memory` if false rather than stale), then the item is re-triaged. |

Left-click and `←`/`→` cycle only the four dispositions; the two escalations are set with
`w`/`e` or a right-click and sit outside the cycle, so cycling an escalated row restores
the agent's original proposal.

**Why `defer` writes to Reflect before clearing.** `resolve_action_item` only removes —
there is no snooze field — so a deferred item that is merely resolved disappears silently.
The `OB1 Memories: Open Questions` bullet is what stops deferring from meaning forgetting.

**Why `rule` is counted separately.** Mechanically it is `clear`, but diagnostically it is
evidence: the 2026-08-03 extractor fix only suppressed rules-as-tasks for
`fact`/`decision`/`person_note`, so a nonzero `rule` tally at the end of a sweep means
`event`/`decision` types still generate them and the server-side rule needs extending.

**The dedup gate.** Reflect is searched for an existing task before any promote is
written. On 2026-08-07 this caught three of six promotes already in the graph.

**One memory can carry several items.** `list_action_items` paginates by *memory*, so
"51 in the queue" means 51 notes — those 51 held **90** items, and each item is one picker
row. Batch caps are therefore counted in rows: **30** for real decisions, 60 for
evidence-only skim rows.

**A sweep that did not finish is not logged.** A picker closed early returns
`interrupted`; its marks are re-offered next round and nothing is written to
`[[OB1 tidied]]` or the daily note.

**What a sweep is allowed to write into Reflect (2026-08-09).** Exactly four things,
and nothing else — a sweep is housekeeping, not a story worth retelling:

1. **Promoted tasks** — `+ [ ]` under *their own* node.
2. **Deferred bullets** — into `OB1 Memories: Open Questions`.
3. **The habit line** — one line on `[[OB1 tidied]]`.
4. **One daily-note line**, always nested under `- [[➡️ PersonalKnowledgeMgmt]]`
   whatever nodes the individual items touched, because the sweep itself is PKM
   housekeeping. One bullet, no sub-bullets:

   ```
   - **Swept the ob1 queue** — 71 items · 3 → Reflect · 2 → [[OB1 Memories: Open Questions]] · 66 resolved. Queue now empty.
   ```

   It carries only what cannot be reconstructed later: item count, how many became
   tasks, how many were parked, what is left, plus `· N memories corrected` when the
   `wrong` loop ran. The per-item reasoning, proofs, memory ids and tooling changes
   stay in ob1 and the picker log.

This is one instance of a general rule that now governs every AI write to the graph:
**the Reflect daily note is not an automatic mirror of AI work.** The 2026-08-08 daily
note ran to 33 lines because the `reflect-note` skill logged every note the agent
created *or edited* and then expanded each entry into nested detail — all of it already
in ob1, in the edited notes, and in git. Since 2026-08-09 the only unprompted daily-note
write left is a **one-line backlink when a brand-new standalone note is created**, so
nothing becomes an orphan. Edits to existing notes and session narration are written
only when Simon asks for them — and then in full detail, since the restriction is about
unrequested writes, not about brevity for its own sake.

## 8. "Memorise this PDF." What really happens

**ob1 cannot store a PDF** — only short text sentences. So: the AI **reads** it →
**distils** it into small standalone notes (one idea each; a 5-pager might become 8–20) →
**saves** them (usually a batch) → **the original is not kept**.

So ob1 holds *summarised takeaways*, not a photocopy. "What was the notice period?" works
only if that fact became a note. **Steer it**: *"memorise this — I care about dates,
names, and any obligations on me."* For a faithful full-text copy, ob1 is the wrong tool.

**Same for a `skill.md` or anything already in a file/code/docs** — ob1's rule is
**"never store what already has a home."** Store the non-obvious meta-fact ("there's a
skill X that does Y, use it when Z", or "we chose A over B because…") instead of copying
the file. Say so explicitly if you want the whole thing mirrored anyway.

## 9. Cheat sheet

| I want to… | Just say… |
|---|---|
| Save a fact | "Remember that…" |
| Memorise a doc's key points | "Memorise this PDF — focus on X and Y." |
| Find what's stored | "What do I know about backups?" / `/ob1 backups` |
| See the newest | "What's new in ob1 this week?" |
| Get an overview | "What's in my open brain?" |
| See open to-dos | "Any open action items in ob1?" |
| Tidy the to-do queue | `/ob1-review` |
| Fix a wrong note | "Update that note…" |
| Remove a note | "Delete memory 123." |
| What needs my decision | "What's in my ob1 review queue?" |
| Mark one note replaced another | "Note 825 supersedes 376." |
| Confirm the AI got it right | "Mark 812 confirmed." |
| Work the backlog | "Sweep 20 memories for relations." |

## 10. Things to keep in mind

- Shared across **every** AI session, not just this one.
- A **summariser**, not a filing cabinet — distilled facts, not source documents.
- You don't manage tags or folders — labelling is automatic. Saving is instant; full
  labelling lands a few seconds later.
- **Nothing is ever deleted or expires on its own.** Old notes stay searchable forever —
  the review queue (§6) marks what was *replaced* rather than throwing anything away.
  Only *exact* duplicates are auto-cleaned.

## 11. Offline read cache — removed 2026-09-26

There is **no offline copy of ob1 any more.** From 2026-07-25 to 2026-09-26 each Mac kept a
read-only local copy of every memory (`ob1-local <keyword>`, refreshed every 3 hours by the
background job `cc.summermatter.ob1-cache`). It was removed on Simon's decision: with no
network there is no AI agent to read it, and no agent was ever told to fall back to it, so in
practice it only kept a plaintext copy of every memory on each Mac.

**If ob1 is unreachable**, bring the path back rather than looking for a copy: at Wildhorn or
Niesehorn switch on the WireGuard profile «private-admin» or «private-admin-full» (MNEME is in `vlan_lab` since
2026-09-26 and is reached only that way from outside Am Wasser), then run `/mcp` in the Claude
Code session to reconnect `open-brain`.

Running `client/ob1-client-setup.sh` on a Mac that still has the old cache removes it.
