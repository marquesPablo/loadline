# The seals of this operation

Paste at the end of your instruction file. Swap `YYYY-MM-DD` for today's date — the date is what
makes `expires=` mean anything.

## The minimum (the two that stand on their own)

```markdown
## What this file promises

Every command cited here exists, and every path cited here exists.
<!-- measured: instrucao.comandos_quebrados=0 nature=relation on=YYYY-MM-DD expires=30d source=package.json -->
<!-- measured: instrucao.caminhos_quebrados=0 nature=relation on=YYYY-MM-DD expires=30d source=disk -->
```

**Why `relation` and not `count`.** A count quantity moves when someone writes — it went up,
re-seal and move on. These two only move if something broke: a script disappeared, a folder was
deleted, or the probe stopped seeing. Diverging here means **stop and investigate**, and the tool
prints those words. Marking this as `count` would train the team to re-seal the defect.

**Why `expires=30d`.** An instruction file changes with the repository. Thirty days is this
operation's default choice, not a measurement — and that is why the line below is an `arbitrated:`,
with an owner:

```markdown
The re-check deadline of the instruction file is 30 days.
<!-- arbitrated: instrucao.prazo=30 by="whoever adopted the operation" on=YYYY-MM-DD expires=180d
     breaks="a repository where the instruction stays stable for months, or one where it breaks every week" -->
```

## The full set (the seven)

```markdown
<!-- measured: instrucao.arquivos=N nature=count on=YYYY-MM-DD expires=90d source=root -->
<!-- measured: instrucao.linhas=N nature=count on=YYYY-MM-DD expires=90d source=instruction-files -->
<!-- measured: instrucao.comandos=N nature=count on=YYYY-MM-DD expires=90d source=code-fences -->
<!-- measured: instrucao.comandos_quebrados=0 nature=relation on=YYYY-MM-DD expires=30d source=package.json -->
<!-- measured: instrucao.caminhos=N nature=count on=YYYY-MM-DD expires=90d source=backticks -->
<!-- measured: instrucao.caminhos_quebrados=0 nature=relation on=YYYY-MM-DD expires=30d source=disk -->
<!-- measured: instrucao.divergencia=N nature=count on=YYYY-MM-DD expires=60d source=headings -->
```

Do not know which `N` to write? Do not write it. Run `python -m loadline . --selar` and the tool
writes all of them, as `arbitrated:`, with today's value. Then swap `arbitrated:` for `measured:` on
these seven — they have a ready probe, and the swap is what turns a chosen number into a recomputed
one.

## What NOT to seal here

**Nothing only the instruction file itself knows.** If the written number and the measured number
come from the same file, the pair passes green **locking** the defect in instead of finding it — it
is a mirror check, and it verifies nothing. All seven above check against a second source:
`package.json`, the `Makefile`, or the file system.

**And nothing that depends on the internet.** No probe of this operation leaves the machine. The
truth out there is exactly what `expires=` exists to demand of a human.
