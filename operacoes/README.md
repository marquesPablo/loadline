# Ready-made operations

> An **operation** is not an example. It is a whole job, pre-assembled: the probes that recompute,
> the seals that expire, the gated agent that keeps it all up, and the CI job that fails when it ages.
>
> You adjust what the `RECEITA.md` tells you to adjust — in most of them, at most two fields — and run it.

The `loadline` core answers *"is what is written still true today?"*. On its own, it is an engine
with no load: it arrives at a new repository, knows none of its metrics, and the first thing it asks
for is work — **write your probe**.

This folder is the load.

---

## The seven, by family

<!-- measured: operacoes.total=7 nature=count on=2026-08-26 expires=never source=operacoes/ -->

The operations are not numbered: the shelf changes by decision, and a number someone memorized ages.
They are referred to by name.

### 🔧 Capability — what you **become able to do**

These install a job you were not doing. Start here.

| Operation | What you get by cloning | Adjust |
|---|---|---:|
| [`cerebro-local`](cerebro-local/) | a **read-only MCP server over your notes**, in one file, no API key, no cloud | **1 field** |
| [`vitrine`](vitrine/) | an agent decides to load your skill by reading only `name` and `description` — **26 of 31 official Anthropic skills** do not declare when not to use them, and one has a `name` that diverges from its own folder | **1 field** |

### 🩺 Hygiene — what **stops lying** in your repository

These measure things that already exist and aged silently.

| Operation | The pain | Adjust |
|---|---|---:|
| [`instrucao-que-nao-mente`](instrucao-que-nao-mente/) | your `AGENTS.md` tells you to run a command that no longer exists, and to edit a deleted folder | **0 fields** |
| [`readme-que-nao-mente`](readme-que-nao-mente/) | the README claims numbers nobody has recomputed since they were written | **0 fields** |
| [`handoff-que-mede-o-disco`](handoff-que-mede-o-disco/) | the handoff file starts being **written from the disk** — commits since, a dead path, a command with no target, git drift | **1 field** |
| [`sala-de-decisao`](sala-de-decisao/) | a decision record that answers **what is stuck waiting on you, and for how many days** | **1 field** |
| [`suite-que-acusa`](suite-que-acusa/) | the rule that answers **which of your tests would pass if the mechanism were removed** | **2 fields** |

> **The shelf grows by decision, not by accumulation.** It was born with ten candidates; four left.
> `dependencia-com-veredito` and `revisao-de-seguranca`, for being pure alarm — the first reads no
> license, the second assumes one `.md` per finding where a real scanner spits SARIF.
> `fronteira-de-agente` and `fabrica-de-agentes`, because the roster survey (`python -m forja`, at
> the repository root) already produces what the two promised.

---

## The anatomy is fixed: if you learned one, you learned them all

<!-- measured: operacoes.arquivos_por_operacao=5 nature=relation on=2026-08-21 expires=never source=operacoes/ -->

| File | What it is |
|---|---|
| `RECEITA.md` | the pain, what to adjust (numbered), how to run it, and what you see on screen |
| `sondas.py` | the ready-made probes — **copy to the root of your repository** |
| `agente.toml` | the forge spec; compiles to the 7 artifacts, including the hook that denies |
| `selos.md` | the seals this operation installs, with the nature and deadline of each |
| `ci.yml` | the job that makes it fail in CI, to copy into `.github/workflows/` |

An operation can carry **more** than the five — `cerebro-local` carries `servidor.py`. What it
cannot do is carry **less**: the anatomy probe blows up when one is missing.

---

## The 60 seconds

```console
$ git clone <this repo> && cd loadline

$ cp operacoes/instrucao-que-nao-mente/sondas.py /path/to/your/repo/sondas.py
$ cd /path/to/your/repo

$ PYTHONPATH=/path/to/loadline python -m loadline .
```

### How `loadline` becomes reachable from inside YOUR repository

Two ways, and both work. **Neither downloads anything from the internet.**

| | How | When |
|---|---|---|
| **without installing** | `PYTHONPATH=/path/to/loadline python -m loadline .` | trying it out, ephemeral CI, a machine you do not administer |
| **installing** | `pip install -e /path/to/loadline`, and then just `loadline .` | daily use; the `pyproject.toml` declares the command and **zero dependencies** |

The recipe examples use the first way, because it is the one that works anywhere without asking
anyone's permission. If you installed, swap `PYTHONPATH=... python -m loadline` for `loadline` in
all of them.

The first run **asks nothing of you**. It returns three lists, and the third is the one that
matters: every numeric claim in your files that no seal covers, with the file, the line and the seal
ready to paste.

```console
$ python -m loadline . --selar
```

This writes the seals, all as `arbitrated:` — because nobody has measured anything yet. Where the
operation already ships a ready probe, you swap `arbitrated:` for `measured:` and the number starts
being **recomputed** instead of chosen. Each operation's `RECEITA.md` says exactly which.

### Using two operations in the same repository

The probes are written to coexist. Each operation uses its own prefix on the helper functions, and
**no metric pattern collides** between them — this is gated by a check with a negative control,
because a collision would shadow the older probe with no error at all.

**But do not join them with `cat`.** Every `sondas.py` opens with `from __future__ import
annotations`, and Python requires that line to be the first statement in the file. Concatenated, the
second file puts its own in the middle, and the result dies with `SyntaxError` on import — after it
has already overwritten the `sondas.py` of whoever tried. Measured: **every possible pair breaks.**

```console
$ python operacoes/juntar.py instrucao-que-nao-mente readme-que-nao-mente \
      --saida /path/to/your/repo/sondas.py
✓ /path/to/your/repo/sondas.py  ·  2 operations, 20 probes, 0 collisions
```

It lifts the imports to the top, deduplicates, and **refuses** if two operations register the same
metric pattern — in Python the second would shadow the first with no error at all, and the shadowed
metric would disappear from the report without ever having failed. When it refuses, it writes
nothing: a half-written `sondas.py` imports, runs, and returns green over what was left out.

---

## What these operations do NOT do

Each operation declares its gaps in the `LACUNAS.md` the forge emits when it compiles the agent.
Three hold for all of them, and are written here so nobody discovers them by using:

1. **The probe proves internal coherence, never the truth of the world.** It recomputes from a
   source on disk. If the source is wrong, the pair passes green with both sides wrong together.
   That is what `expires=` is for: it is the only mechanism here that forces someone to leave the
   machine.

2. **None of them judges whether the metric was the right one.** *"Does this number still match?"*
   and *"does this sentence repeat it right?"* are the two questions. If the claim mattered, that
   stays a judgment for whoever writes.

3. **None of them installs, downloads, sends or phones anywhere.** Zero dependencies, zero network,
   zero API key, zero telemetry. If a probe needs the internet, it becomes `UNPROVEN` with the error
   written out — never a guess dressed as a measurement.

**And a fourth, which holds for the operation that carries a heuristic** (`suite-que-acusa`): **it
gets it wrong both ways, and it says so.** The number the `suite.sem_controle_negativo` probe
produces is a **reading list**, not a verdict — it should not fail CI on its own. A heuristic rule
that fails trains the team to write code to please the rule, and then it has stopped measuring the
code.

---

## Writing your own

An operation is a folder with the five files above. What makes a good one:

- **The probe must not read the source that produced the written number.** If both sides come from
  the same place, the pair passes green **locking** the defect in instead of finding it. Every probe
  here declares `origem=` precisely so that rule is auditable from outside.
- **`nature` is required, and it changes what to do with the red.** `count` moves when someone
  writes — it diverged, re-seal and move on. `relation` only moves if the meter or the repository
  broke — it diverged, **stop and investigate**. Without the distinction, every red is noise and
  the answer to every red becomes "re-seal".
- **Blowing up is better than returning zero.** *"I did not look"* and *"I looked and there is
  nothing"* say opposite things. A probe that returns `0` when the folder does not exist turned the
  first into the second — the defect this whole project exists to forbid.
- **The `agente.toml` compiles or is refused.** The forge has eight refusals and all of them fail
  closed. If your spec asks for network without declaring a domain, or write without declaring a
  path, it does not come out — and the refusal carries the fix written out.

A new domain probe comes in by PR to [`comunidade/`](../comunidade/), reviewed by human decision —
never by green CI alone.

> *The operations on this shelf were born on 2026-08-21, and up to that date none had been run by
> anyone else. That is a declared denominator, not modesty.*
