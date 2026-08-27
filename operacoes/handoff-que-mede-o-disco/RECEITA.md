# Operation 10 · `handoff-que-mede-o-disco`

> You close the session and write — or ask the model to write — a handoff file:
> *"where we stopped, what is left, what runs"*.
> Two weeks later someone opens that file and follows what is in it.
> **How many of its claims are still true?**
> Nobody knows, because nothing re-checks them. And the document does not look old: it looks specific.

## The pain

A handoff file is a **written claim about the disk** — and it is the most fragile kind there is,
because the disk changes every day and the document does not.

It says the repository is clean, and there are twelve dirty files. It tells you to run a script that
was renamed. It cites a folder that became another. None of those lines is *visibly* wrong: they are
**specific and false**, which is worse. Whoever reads it goes there, does not find it, and concludes
*"I must be in the wrong place"* instead of *"the document is old"*.

And the usual way out makes the problem worse: asking the assistant to **remember** the last
session. Memory is exactly the side that decays. The disk is the side that does not.

## What this operation installs

Eight probes over your handoff file, all reading **git** and the **file system** — never the
document that makes the claim:
<!-- measured: operacao.handoff.sondas=8 nature=count on=2026-08-21 expires=never source=operacoes/handoff-que-mede-o-disco/sondas.py -->

| Metric | What it recomputes | Nature |
|---|---|---|
| **`handoff.commits_desde`** | **commits that landed after the document was last touched** | count |
| `handoff.caminhos_citados` · `handoff.comandos_citados` | the size of what it claims | count |
| **`handoff.caminhos_mortos`** | **cited paths that do not exist** | **relation** |
| **`handoff.comandos_sem_alvo`** | **commands whose script, `make` target or package script disappeared** | **relation** |
| **`handoff.deriva_de_git`** | **it says «it is clean» and `git status` disagrees** | **relation** |
| `handoff.linhas` | the bloat — the second way a handoff dies | count |
| `handoff.sessoes_desde` | sessions that ran without anyone updating the document | count |

**`handoff.commits_desde` is the number that opens the conversation.** A document with forty commits
on top of it is not wrong — it is **out of date**, which is different and worse, because it still
looks like the current state.

## ⚠️ This operation NEVER executes what the document tells you to

The handoff file is **text**. It could have been written by anyone, pasted from anywhere, or edited
by an agent. A probe that ran the commands cited in it would be **arbitrary execution from a
document** — injection with a written invitation.

What it does is check whether the **target exists**: the script file, the rule in the `Makefile`,
the key in `package.json`'s `scripts`. A command whose target disappeared is the defect that
matters, and finding it does not require running it.

**The honest consequence:** `handoff.comandos_sem_alvo=0` means *"the targets are there"*, **never**
*"the checks pass"*. They are different things, and the second this operation does not measure.

## The adjustment

**One field**, at the top of `sondas.py` — the name of your handoff file:

```python
NOMES_DE_HANDOFF = ("CONTINUAR.md", "HANDOFF.md", "RETOMAR.md", "CONTEXT.md", "STATE.md")
```

The first one that exists wins. If yours has another name, put it in front. If none exists, the
probe **blows up** with the error written out — because *"I did not find your handoff"* and *"your
handoff is flawless"* are opposite readings.

## How to run

```console
$ cp operacoes/handoff-que-mede-o-disco/sondas.py  /path/to/your/repo/sondas.py
$ cd /path/to/your/repo
$ PYTHONPATH=/path/to/loadline python -m loadline .
```

Run against a real 667-line handoff file, in a live repository:

```console
FAIL   CONTINUAR.md:228  handoff.caminhos_mortos: written=0 measured=11
       → nature=relation — STOP and investigate.
FAIL   CONTINUAR.md:228  handoff.deriva_de_git: written=0 measured=1
       → the document says it is committed; git disagrees.
```

<!-- frozen: exemplo.caminhos=44 exemplo.mortos=11 exemplo.comandos=3 exemplo.sem_alvo=0 exemplo.deriva=1 reason="a 2026-08-21 measurement over a handoff file from ANOTHER repository; it is the example printed above, not the state of this project, and recomputing it here would measure the wrong thing" -->

## The "dead" paths that were not deleted

**Everything is resolved from the repository root, and that is a decision.** A path cited as
`notas/x.md`, that only exists under `outra-pasta/notas/x.md`, counts as dead here — because it
counts as dead for whoever copies the line and pastes it into the terminal.

Of the 11 found in the measurement above, **none was a deleted file**: all of them were paths
written from an implicit root the document did not declare. The fix is to write the whole path, and
it is the same fix that serves the reader.

## From the alarm to the work

`handoff.commits_desde=40` says the document fell behind. **Rewriting it from the disk** is the
work, and it is what this operation's agent does:

```console
$ python -m forja operacoes/handoff-que-mede-o-disco/agente.toml
  ✓ build/escriba-de-retomada/.claude/agents/escriba-de-retomada.md
  ✓ build/escriba-de-retomada/hooks/cerca_escriba_de_retomada.py
  …
```

Its rule is a single one and it is hard: **either the claim comes out recomputed, or it comes out
marked as not verified.** It does not copy from the previous document — that is how an old number
survives ten rewrites, getting more trusted with each copy precisely because it was copied.

## What this operation does NOT do

1. **It does not execute anything.** See the section above. `comandos_sem_alvo=0` says the targets
   exist, never that the checks pass.

2. **It does not read the conversation.** It reads the disk. What was decided and did not become a
   file is invisible — and that is the biggest gap here, because it is the same gap the handoff file
   has.

3. **`commits_desde` and `sessoes_desde` only hold in your working tree.** `git` does not preserve
   `mtime`: in a clean clone every file is born with the same instant and the two blow up to the
   total. **A large number for them right after a clone is not a finding**, and the agent says so
   instead of writing it.

4. **It does not judge what is in flight.** A three-week-old to-do and a yesterday one come out side
   by side. Prioritizing stays with whoever reads.

5. **It does not know a commit's intent.** A formatting pass counts the same as an architecture
   change. The number is a **floor**: it says at least how much happened, never how much it mattered.
