---
name: mail-on-point
targets: [claude]
has_assets: false
description: >
  Use this skill whenever the user wants to write, draft, or compose any kind of message — emails, letters, Slack messages, SMS, or WhatsApp. Triggers include: "schreib eine Mail", "draft an email", "verfasse ein Schreiben", "write a message", or any request to compose communication to another person. Follows Swiss Standard German spelling conventions (no ß), UK English for English documents, and a structured format with greeting, positive connection, main request, details, next steps, and closing.
---

# Mail on Point

## Process

**Goal:** A perfect message in minimal time and steps.

If the user has already provided all necessary information, produce the text immediately (0 steps).

If information is missing, ask briefly and precisely — skip anything already known:

- **Action:** What is the purpose of the message? (Expected actions, questions, deadlines, ...)
- **Details:** Missing data, facts, or photo references?
- **Tone:** Recipient and level of familiarity? (see Levels of Familiarity)

Once all information is available, draft the message following the General Structure. Present the finished text to the user for review. If revisions are requested, apply them immediately and present the updated version.

## Levels of Familiarity

The level of familiarity determines the tone of the greeting, closing, and overall style. Choose the appropriate level based on the relationship with the recipient.

- **Formal** — First contact, official communication, or unknown recipient. Use last names and formal address.
- **Casual** — Existing business relationship with some rapport. Use last name or first name depending on established convention.
- **Personal** — Close contact, friendly relationship. Use first names and a warm tone.

## Tone and Style

- **Factual and polite** — No emotional language or colloquialisms in business contexts.
- **Conciseness** — No filler words, no redundant statements, no excessive details.
- **Clarity** — Short, understandable sentences. Technical jargon only when necessary.
- **No subservience** — Never apologise unnecessarily, relativise, or minimise the sender's position (e.g. "etwas verspätet", "leider erst jetzt", "falls es passt"). The sender communicates as an equal.
- **Direct calls to action** — State expected actions in the indicative, not the subjunctive II. "Lass uns diese Woche telefonieren" not "Es wäre ideal, wenn wir uns austauschen könnten".

## Spelling

- **Swiss Standard German** — Use Swiss Standard German spelling for German documents.
  - No sharp "S" (ß)
  - No comma after the salutation in letters
- **English UK** — Use United Kingdom spelling for English documents.

## General Structure

The following outline should be implemented both in terms of content and visual separation — each element should be presented as its own paragraph.

### 1. Greeting

See Levels of Familiarity.

- **Formal:** „Sehr geehrte/r Herr/Frau [Nachname]"
- **Casual:** „Hallo Herr/Frau [Nachname]" or „Hallo [Vorname]"
- **Personal:** „Liebe/r [Vorname]"
- Multiple recipients: „Sehr geehrte Damen und Herren" or „Hallo zusammen" depending on context.

### 2. Positive Connection

Open with reference to context (e.g. previous communication, reason for writing, positive event).

### 3. Main Request

The complete request in one sentence: What should happen, by whom, by when, where? All information without which the core message would be incomplete belongs here — not in Details or Next Steps.

### 4. Details

Only supplementary specifications that refine the main request but are not part of the core message. Present logically and clearly.

### 5. Next Steps

Clear instructions on expected or required actions (e.g. response, scheduling a meeting). Include deadlines if relevant.

### 6. Closing

Polite closing with thanks, sign-off and optional signature. Sign-off matching the level of familiarity:

- **Formal:** „Freundliche Grüsse, [Ihr Name]"
- **Casual:** „Beste Grüsse, [Vorname]"
- **Personal:** „Herzliche Grüsse, [Vorname]"

## Examples for the Positive Connection

| Context | Example |
|---------|---------|
| After previous communication | „Vielen Dank für Ihre Rückmeldung." / „Vielen Dank für das Gespräch vom [Datum]." / „Gut, dass Sie sich melden." |
| After recommendation / referral | „[Name] hat mich an Sie verwiesen." / „Auf Empfehlung von [Name] kontaktiere ich Sie." |
| After a longer gap | „Schön, dass wir wieder in Kontakt kommen." / „Vielen Dank, dass Sie sich wieder melden." |
| First contact / initial enquiry | „Schön, dass Sie sich für [Thema/Produkt] interessieren." / „Danke, dass Sie sich direkt an uns wenden." |
| After delivery / service | „Vielen Dank für die schnelle Lieferung." / „Die Abwicklung hat bestens geklappt – vielen Dank." |
| After appointment / meeting | „Vielen Dank für den Termin am [Datum]." / „Der Austausch am [Datum] war sehr hilfreich." |
| For complaints / problems | „Danke für den Hinweis – wir kümmern uns darum." / „Ihren Unmut können wir nachvollziehen." |

## Examples for Specific Cases

### Enquiry

- **Greeting:** „Sehr geehrter Herr Müller"
- **Positive Connection:** „Vielen Dank für Ihre schnelle Rückmeldung."
- **Main Request:** „Bitte senden Sie uns weitere Informationen zu [Thema]."
- **Details:** „Bitte senden Sie mir die Unterlagen bis [Datum]."
- **Next Steps:** „Bitte melden Sie sich bis [Datum], falls Rückfragen bestehen."
- **Closing:** „Freundliche Grüsse, [Ihr Name]"

### Offer

- **Greeting:** „Sehr geehrte Frau Meier"
- **Positive Connection:** „Vielen Dank für Ihr Interesse an unseren Dienstleistungen."
- **Main Request:** „Anbei unser Angebot für [Dienstleistung/Produkt]."
- **Details:** „Das Dokument enthält alle relevanten Details. Bei Fragen stehen wir zur Verfügung."
- **Next Steps:** „Bitte geben Sie uns bis [Datum] Bescheid, ob Sie das Angebot annehmen."
- **Closing:** „Freundliche Grüsse, [Ihr Name]"

### Reminder

- **Greeting:** „Sehr geehrter Herr Schmidt"
- **Positive Connection:** „Vielen Dank für den bisherigen Austausch."
- **Main Request:** „Ich erinnere an [Thema]."
- **Details:** „Die Frist endet am [Datum]. Falls bereits erledigt, können Sie diese Nachricht ignorieren."
- **Next Steps:** „Bei Rückfragen stehe ich zur Verfügung."
- **Closing:** „Freundliche Grüsse, [Ihr Name]"

### Collection Order

- **Greeting:** „Hallo zusammen"
- **Positive Connection:** „Besten Dank für die kurzfristige Lieferung der von [...] an [...]."
- **Main Request:** „Die Mulde ist voll und kann ab sofort abgeholt werden."
- **Details:** „Sie ist mit [...] gefüllt. Die Big Bags mit der [...] haben wir obenauf platziert. Details siehe Foto."
- **Next Steps:** „Vielen Dank für die unkomplizierte Erledigung."
- **Closing:** „Freundliche Grüsse [Ihr Name]"
