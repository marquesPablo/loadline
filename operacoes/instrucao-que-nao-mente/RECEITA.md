# Operation 1 · `instrucao-que-nao-mente`

> Your `AGENTS.md` tells you to run `npm run test:unit`. That script was renamed in March.
> The agent reads the instruction, runs the command, fails, and tries to guess what you meant.
> **Nobody was warned, because nothing looks at this.**

## The pain

More than 60,000 repositories adopted `AGENTS.md`, read today by Claude Code, Codex CLI, Cursor,
Aider, Copilot, Gemini CLI, Zed, Continue and others. Whoever has two files — `CLAUDE.md` **and**
`AGENTS.md` — has the problem twice over: one is kept up, the other is left, and the two diverge
silently.

An instruction file is a document full of **claims about the repository**: run this command, edit
this folder, the tests are over there. Every claim ages. None fails when it ages.

## What this operation installs

Seven probes that check the instruction file's promises against the disk — not against itself:
<!-- measured: operacao.instrucao.sondas=7 nature=count on=2026-08-21 expires=never source=operacoes/instrucao-que-nao-mente/sondas.py -->

| Metric | What it recomputes | Nature |
|---|---|---|
| `instrucao.arquivos` | how many instruction files exist | count |
| `instrucao.linhas` | their combined size | count |
| `instrucao.comandos` | distinct commands cited inside a code fence | count |
| **`instrucao.comandos_quebrados`** | **commands whose script/target does not exist** in `package.json`, `Makefile` or on disk | **relation** |
| `instrucao.caminhos` | relative paths cited between backticks | count |
| **`instrucao.caminhos_quebrados`** | **cited paths that do not exist** | **relation** |
| `instrucao.divergencia` | headings present in one file and absent from the other | count |

The two in **relation** are the heart. They should always be `0`, and when they leave zero that is
not "the number changed" — it is a **defect**. The tool says so on screen, in those words.

## The adjustment

**None.** The probes discover the instruction files on their own, from the closed list of names
today's harnesses read. If yours has another name, add it to `NOMES_DE_INSTRUCAO`, at the top of
`sondas.py` — it is the only line of this operation anyone needs to touch, and only in that case.

## How to run

```console
$ cp operacoes/instrucao-que-nao-mente/sondas.py  /path/to/your/repo/sondas.py
$ cd /path/to/your/repo
$ PYTHONPATH=/path/to/loadline python -m loadline .
```

> Installed with `pip install -e /path/to/loadline`? Then it is just `loadline .`. Both ways are in
> [`operacoes/README.md`](../README.md), and neither downloads anything.

The first run asks nothing. It returns what nobody can verify in your repository. Then, paste at the
end of your `AGENTS.md`:

```markdown
## What this file promises

Every command cited here exists, and every path cited here exists.
<!-- measured: instrucao.comandos_quebrados=0 nature=relation on=YYYY-MM-DD expires=30d source=package.json -->
<!-- measured: instrucao.caminhos_quebrados=0 nature=relation on=YYYY-MM-DD expires=30d source=disk -->
```

Swap `YYYY-MM-DD` for today. Done — the operation is live.

## What you see when something breaks

```console
$ PYTHONPATH=/path/to/loadline python -m loadline .
loadline · . · on 2026-08-21
========================================================================
DRIFTED   AGENTS.md:19  instrucao.comandos_quebrados: written=0 measured=2  → STOP. A relation diverging is a defect — investigate before re-sealing
DRIFTED   AGENTS.md:20  instrucao.caminhos_quebrados: written=0 measured=2  → STOP. A relation diverging is a defect — investigate before re-sealing

⚠️  NOBODY CAN VERIFY THIS — these are suspects, not defects.
      UNVERIFIED  AGENTS.md:3  "This repo has 3 services and 12 endpoints." → nobody verifies 3
      UNVERIFIED  AGENTS.md:3  "This repo has 3 services and 12 endpoints." → nobody verifies 12
------------------------------------------------------------------------
2 metrics in 3 files · 2 files with no seal at all · 2 claims nobody verifies
  DRIFTED    2
  ⚠️  2 of RELATION — that is a defect, not a re-seal

FAIL
```

> *Literal output of this operation over a synthetic repository, run on 2026-08-21. It is an example
> of that run, not the state of your repository.*

## The agent

`agente.toml` compiles the `guardiao-de-instrucao`, which does what the probe does not: **it opens
each break and says which one it is**. The probe counts 2; the agent says *"`npm run test:unit` no
longer exists in `package.json`, and `src/legacy/velho.ts` was deleted"*.

```console
$ python -m forja operacoes/instrucao-que-nao-mente/agente.toml
```

Seven artifacts come out, among them a `LACUNAS.md` that declares what this agent does **not**
measure — read it before trusting a green.

## The CI

`ci.yml` makes the operation fail the build. Copy it to `.github/workflows/`. It tells the three
exit codes apart: `0` green, `1` something checked does not match, `2` you have not annotated
anything yet.

## The three things this operation does not do

1. **If nobody CITES a command, nothing here finds that it existed and disappeared.** The coverage
   is of what is written, and the denominator is the instruction file — never the whole repository.
2. **A command outside a code fence does not count.** `npm test` in the middle of a sentence can be
   an example, a counter-example or what *not* to do. Inside the fence it is an instruction;
   outside, it is prose.
3. **The break check is conservative, and errs on the side of going quiet.** With no `package.json`
   there is no way to decide about `npm run X`, and it does not decide. A probe that cries wolf is a
   probe someone deletes in the second week.
