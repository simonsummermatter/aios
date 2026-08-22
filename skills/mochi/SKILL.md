---
name: mochi
targets: [claude]
has_assets: false
description: >
  ANY Mochi flashcard work: generating cards from a source ("mach daraus
  Karten", "make flashcards", "Karteikarte"), or listing, editing, deleting
  and reviewing cards. Read BEFORE touching Mochi.
---

# Mochi Skill

Mochi is a markdown-based spaced-repetition app. It exposes a small REST API.
There is no MCP server in this setup and none is needed: Claude Code has a
shell, and the whole API is a handful of `curl` calls.

The value of this skill is **not** the plumbing. It is the card-quality rules
below. A bad card is worse than no card, because it costs review time forever.

**Everything goes through the API.** Simon does not want manual import files.
Never write a deck to a markdown file for him to import by hand, and never ask
him to click through Mochi's import dialog: create the cards directly.

## Auth

The API key lives in 1Password (item `Mochi`, vault `Personal`, field `apiKey`).
Never hardcode it, never echo it, never write it into a file.

```bash
export MOCHI_API_KEY="$(op read 'op://Personal/Mochi/apiKey')"
```

**Shell state does not persist between Bash tool calls.** Put that `export` line
at the top of *every* command block that talks to Mochi. Do not try to set it
once and reuse it later.

Auth is HTTP Basic with the key as username and an empty password:
`curl -u "$MOCHI_API_KEY:"`. The trailing colon is required.

If `op read` returns empty, the 1Password app is locked. Ask Simon to unlock it
rather than looking for the key elsewhere.

## Hard constraints

- **One concurrent request per account.** Never run Mochi curls in parallel or
  background them. Batch creations sequentially in a `for` loop.
- **API access needs Mochi Pro.** A `401` usually means a lapsed subscription or
  a stale key, not a malformed request.
- Pagination: `?limit=N` (1..100, default 10) plus `bookmark` from the previous
  response. The payload is `{"docs": [...], "bookmark": "..."}`.
- Base URL is `https://app.mochi.cards/api/`.

## Decks

Resolve deck names to ids before creating anything. Ids are short strings, they
are stable, and Simon has duplicate deck *names*, so never match on name alone
without showing him which id you picked.

```bash
export MOCHI_API_KEY="$(op read 'op://Personal/Mochi/apiKey')"
curl -s -u "$MOCHI_API_KEY:" 'https://app.mochi.cards/api/decks?limit=100' \
  | python3 -c "import json,sys;[print(d['id'],'|',d.get('name')) for d in json.load(sys.stdin)['docs']]"
```

Known ids as of 2026-08-22 (re-check, decks change):
`4O2lPbjj` Flashcards (empty, the real target deck) · `4vlB4e7p` Notes ·
`lbJwyBeg` Notes (two distinct decks share the name "Notes", each holding only
Mochi's two built-in starter cards)

**Deck routing rule**: if no deck is named, ask once which deck, then reuse that
answer for the rest of the session. Never invent a new deck without asking.

## Card format

Card bodies are plain markdown. Two shapes, and they are not interchangeable:

**Q/A card** — `---` on its own line splits front from back.

```markdown
What problem does HTTP Basic auth's trailing colon solve in curl?
---
`-u "key:"` sends an empty password. Without the colon curl prompts
interactively and the call hangs.
```

**Cloze card** — `{{...}}` hides text in place. Numbered groups
`{{1::x}} … {{2::y}}` create separate review variants, each with its own
schedule. Use groups only when both blanks are genuinely worth separate recall.

```markdown
Mochi's API allows {{1::one}} concurrent request per account, so batch
writes must run {{2::sequentially}}.
```

Tags: either inline `#tag` in the content, or the `manual-tags` array on the
card object. Prefer `manual-tags`, it keeps the card body clean.

(Note the contrast with the `reflect-note` skill, where `#tags` are forbidden.
In Mochi tags are the organising mechanism and are wanted.)

## Recipes

**Create a card**

```bash
export MOCHI_API_KEY="$(op read 'op://Personal/Mochi/apiKey')"
python3 - <<'PY' | curl -s -u "$MOCHI_API_KEY:" -H 'Content-Type: application/json' \
  -d @- 'https://app.mochi.cards/api/cards' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])"
import json
print(json.dumps({
  "content": "Front of the card\n---\nBack of the card",
  "deck-id": "4O2lPbjj",
  "manual-tags": ["python", "async"],
}))
PY
```

Build the JSON in Python, never by string-interpolating markdown into a shell
heredoc. Card content contains backticks, quotes, newlines, and `$` signs that
the shell will happily mangle.

**Create several cards** (sequential, because of the concurrency limit)

```bash
export MOCHI_API_KEY="$(op read 'op://Personal/Mochi/apiKey')"
python3 - <<'PY'
import json, os, subprocess
DECK = "4O2lPbjj"
cards = [
    {"content": "Front A\n---\nBack A", "manual-tags": ["topic"]},
    {"content": "Front B\n---\nBack B", "manual-tags": ["topic"]},
]
for c in cards:
    c["deck-id"] = DECK
    out = subprocess.run(
        ["curl", "-s", "-u", os.environ["MOCHI_API_KEY"] + ":",
         "-H", "Content-Type: application/json", "-d", json.dumps(c),
         "https://app.mochi.cards/api/cards"],
        capture_output=True, text=True).stdout
    print(json.loads(out)["id"], c["content"].split("\n")[0][:60])
PY
```

**List / read**

```bash
export MOCHI_API_KEY="$(op read 'op://Personal/Mochi/apiKey')"
curl -s -u "$MOCHI_API_KEY:" 'https://app.mochi.cards/api/cards?deck-id=4O2lPbjj&limit=100' \
  | python3 -c "import json,sys;[print(c['id'],'|',c['content'].split(chr(10))[0][:70]) for c in json.load(sys.stdin)['docs']]"
curl -s -u "$MOCHI_API_KEY:" 'https://app.mochi.cards/api/cards/<id>'
```

There is no server-side full-text search. To find a card, pull the deck and
filter locally in Python.

**Update** (`POST`, not `PUT`; send only the fields that change)

```bash
curl -s -u "$MOCHI_API_KEY:" -H 'Content-Type: application/json' \
  -d '{"content":"New front\n---\nNew back"}' \
  'https://app.mochi.cards/api/cards/<id>'
```

**Delete** — destructive. Show Simon the card content and get a yes first.

```bash
curl -s -X DELETE -u "$MOCHI_API_KEY:" 'https://app.mochi.cards/api/cards/<id>'
```

**Due today**

```bash
curl -s -u "$MOCHI_API_KEY:" 'https://app.mochi.cards/api/due' \
  | python3 -c "import json,sys;d=json.load(sys.stdin)['docs'];print(len(d),'due')"
```

Other endpoints, rarely needed: `/decks` CRUD, `/templates`,
`/cards/:id/attachments/:filename`.

## Card-quality rules

This is the part that matters. Apply it before writing a single card.

1. **One card, one fact.** If the back has a bulleted list of five things, it is
   five cards or it is a card that will never be recalled cleanly. The only
   exception is a list Simon explicitly wants memorised as a list.
2. **The front must be answerable.** Read the front alone and ask: is there
   exactly one right answer? "Tell me about decorators" fails. "What does a
   decorator return?" passes.
3. **The front is a trigger, not an intention.** For any card drilling a
   response (a conversation, a negotiation, a decision) the front carries the
   actual prompt: the other side's move in their own words, or a recognisable
   situation. It never states the intention behind the answer. "Wie drehe ich
   X?" gives the game away and drills nothing. The back is the response.
4. **A comparison on the back needs its baseline on the card.** If the back
   claims something is "the cheaper way" or "the lower risk", the thing it is
   cheaper *than* must be written in the card itself. Otherwise the card
   collapses the moment the counterpart's premise differs, and an argument for
   a cheapest option loses to doing nothing at all.
5. **No context orphans.** The card must still make sense in six months with the
   source long forgotten. Never write "the function above", "this approach", "as
   discussed". Name the thing.
6. **Prefer cloze for facts inside a sentence**, Q/A for concepts, mechanisms,
   and "why" questions. Reach for Q/A when the answer is a sentence rather than
   a word.
7. **Test understanding, not trivia.** A card about *why* an API has a
   one-concurrent-request limit beats a card about the exact number, unless the
   number is the thing that bites in practice.
8. **Code cards**: front carries the signature or the question, back carries the
   code block plus one line on why it works. Keep the block short enough to read
   in a review, five lines or so, not a whole function.
9. **Attribution belongs on the back**, one line at the end, source name and
   link. Never on the front, it leaks the answer.
10. **Fewer, better.** From an article, five sharp cards beat twenty mediocre
   ones. When a source seems to justify more than about ten cards, stop and ask
   Simon which threads he actually wants to retain.
11. **Draft, then confirm.** Show the proposed cards as markdown in chat before
   creating them, unless Simon said "just make them". Editing a card in Mochi
   later is more friction than reviewing a draft now.
12. **Check for duplicates** in the target deck before creating. Pull the deck,
    scan the fronts, and flag near-matches rather than creating a second copy.

## After creating

Report the count, the deck, and the first line of each card. Do not paste the
full card bodies back, Simon just approved them.

Do **not** write a bullet into the Reflect daily note about cards created. Per
`reflect-note` Point 7 the daily note is not an automatic mirror. Only write
there if Simon asks.
