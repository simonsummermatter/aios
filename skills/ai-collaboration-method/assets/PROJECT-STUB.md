# The method on this project — stub template

Copy this file into a project as `docs/method/PROJECT.md`, fill it in once at the start, and do
not change it afterwards. It holds **only** this project's answers to the placeholders the method
leaves open. **No rule of the method is restated here** — the method lives in the
`ai-collaboration-method` skill, and a second copy beside the project is how the next project
ends up copying the folder instead of loading the skill.

Everything below is a project choice. The *roles* are fixed by the method; the names are not,
except for the three constraints named in `PLAYBOOK.md` §0.

---

## This project runs the `ai-collaboration-method` skill

The procedure, the state vocabulary, the evidence rule, the six-point close checklist and the
filing rules are in that skill. This file fills in its placeholders.

## Document names

| Placeholder | This project uses |
| --- | --- |
| `<GOVERNANCE>` | `README.md` |
| `<RECORD>` | `STATUS.md` |
| `<PLAN>` | `docs/delivery/vN/RUNBOOK.md` |
| `<CONCEPT>` | `docs/<subject>/CONCEPT.md` |
| `<HANDOVER>` | `⭐HANDOVER.md` at the repository root |

*(Change a name only if there is a reason, and record the reason. `<HANDOVER>`'s path can never
be changed again once a session has been handed over — see `PLAYBOOK.md` §8.)*

## `<DEV-BRINGUP>` — bringing the dev environment up

> The exact commands a session runs at step 1.4, in order, with anything that must be true first.
> Example shape: `ssh` to the dev host, start the containers, sync, install.

## `<ID-SCHEME>` — topic ids, from which the commit prefix derives

> Example: `S<n>` for steps an agent executes, `H<n>` for topics only the human can settle,
> `method:` for changes to the way of working. Ids are assigned once and kept for life.

## `<MEMORY-LAYER>`

> Where durable cross-project facts, decisions and preferences go, and how it is searched.

## `<DOC-LANGUAGE>`

> The documentation language, and where that mandate is written in `<GOVERNANCE>`.

## `<REVIEW-POINT>`

> When the method itself gets reviewed on this project — a number of sessions, a milestone, or a
> release. Name it now; a review point decided later never happens.

## Subjects

> The list of subject folders under `docs/`, one line each. This is the organising principle, and
> `PLAYBOOK.md` §5 says it is settled once, at the start, because re-filing later is the one cost
> the method has measured and cannot avoid twice.

## Deviations from the method, with their evidence

> Empty is the normal state. A deviation is written here with the evidence that forced it, in the
> same shape the method demands of its own rules — and if it holds up, it is carried back into
> the skill at the next method review rather than living on here.
