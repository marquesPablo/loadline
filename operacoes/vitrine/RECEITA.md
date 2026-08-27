# Operation 11 · `vitrine`

> An agent decides to load a skill by reading **two fields**: `name` and `description`.
> The body of the `SKILL.md` is only read **after** the decision has already been made.
> **Nobody checks those two fields, because nothing looks at them.**

## The pain

Measured on this machine, on 2026-08-23, without touching a line of code: of the **31 skills in
Anthropic's official marketplace**, **26 do not declare when NOT to use them** and **1 declares a
`name` that does not match its own folder name** — `writing-rules/SKILL.md` says
`name: writing-hookify-rules`.

This is not a syntax error. It is an error that **produces no error at all**: the skill keeps
existing, keeps being read by whoever opens the file, and keeps being **invisible** to the router
that decides, at runtime, which skill to load. The report from outside is always "the skill did not
catch", never "the `name` diverges from the folder" — because nothing ever said so.

## What this operation installs

Two probes that recompute the window again on every run — never from what was already written:
<!-- measured: operacao.vitrine.sondas=2 nature=count on=2026-08-23 expires=never source=operacoes/vitrine/sondas.py -->

| Metric | What it recomputes | Nature |
|---|---|---|
| `vitrine.skills` | how many `SKILL.md` exist under the declared path | count |
| **`vitrine.reprovas`** | **how many of those skills have a ⛔ on any of the eleven `vitrine` rules** (name diverging from the folder, name grammar, no usage trigger, no negative trigger, two skills getting confused) | **relation** |

The second is the heart. It should always be `0`; when it leaves zero, that is not "the number
changed", it is **a defect** — a skill went invisible or is about to, and the tool says exactly that,
in those words.

The eleven full rules, each citing the public source it comes from, are in `vitrine/regras.py`. To
run the linter on its own, outside this seal: `python -m vitrine <path>`.

**The vitrine also knows how to CREATE a new skill**, not just audit the ones that already exist —
`python -m vitrine --harvest <slug> --says "what it does"` refuses to be born if it collides with a
skill that already exists (the same `S11` rule) and writes a `SKILL.md` that is born clean on the
structural rules, with a `?` only in the two fields nobody but whoever lived the work can fill in:
the positive trigger and the negative one. No model, no API key — see `vitrine/colheita.py`.

## The adjustment

**One field.** Open this operation's `sondas.py` and change `CAMINHO_DE_SKILLS` to the real path of
your skills folder — the default points at `.claude/skills`, which is where Claude Code, and most
harnesses with Agent Skills support, look.

⚠️ **Copy the whole `vitrine/` folder**, not just this operation's `sondas.py` — it is the only
drawer on the shelf, along with `cerebro-local`, that ships more than the five standard files.
