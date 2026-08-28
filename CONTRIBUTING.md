# Contributing

Thanks for looking. This project is small on purpose, and it stays small by decision, not by
accident.

## The one rule

**Every new behavior comes in with a negative control** — a check in `autoteste.py` that
reintroduces the exact defect the behavior exists to catch, and fails if you remove the mechanism.
A check that only confirms the happy path passes the same after the mechanism is deleted; it proves
nothing, and its cost is giving someone the feeling of being covered.

Run `python autoteste.py` before and after your change. Then run `python -m loadline .` — it must
not start *failing*. It is allowed to keep reporting that the repo has prose numbers nobody sealed;
it is not allowed to report that a seal drifted.

## What kind of change

| You want to… | Start here |
|---|---|
| report a wrong answer or a crash | open an issue with the command, the output, and a minimal repository |
| fix a bug | a PR with the fix **and** the negative control that would have caught it |
| propose a domain probe (an "operation") | [`comunidade/README.md`](comunidade/README.md) — the checklist and the `_modelo/` template |
| improve the docs or a message | a PR; keep it in the same voice as what is there |

## Operations are reviewed by a person, never by green CI alone

The shelf started with more candidate operations than it kept — the ones that left were either pure
alarm or already done by another piece. Accepting contributions by volume would repeat that mistake
with nobody to cut afterward. CI is the floor — it fails what is mechanically wrong. A person
decides whether the operation deserves to exist. You will get an accept, a request for
changes, or a refusal with the reason written out — never silence.

## No dependencies

The whole point is that a verifier which depends on a model is a second opinion, and one that
depends on a service does not run in the CI of whoever needs it most. `pyproject.toml` says
`dependencies = []`, the README asserts it, and a probe measures it. A PR that adds a dependency
fails the README until someone rewrites that sentence — which is a conversation, not a merge.

## Style

- Python 3.10+, standard library only.
- Comments explain *why*, never *what*. Default to none.
- English, in the same register as the surrounding text.
- Absolute paths, real dates, no "last week".
