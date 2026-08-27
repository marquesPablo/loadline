# The seals of this operation

## The three that tell you to stop

Paste **into your decision record's index** — `decisoes/README.md` or the file that lists the
archive. The seal has to live in the file it judges.

```markdown
Every decision in this archive declares whether it is in force, says what was rejected, and no
revocation was declared on one side only.
<!-- measured: decisao.sem_status=0 nature=relation on=YYYY-MM-DD expires=90d source=decisoes/ -->
<!-- measured: decisao.revogacao_de_um_lado_so=0 nature=relation on=YYYY-MM-DD expires=90d source=decisoes/ -->
<!-- measured: decisao.sem_alternativa=0 nature=relation on=YYYY-MM-DD expires=90d source=decisoes/ -->
```

**The three of `relation`, and none of them should move when you write a new decision.** If one
left zero, something was left half done — and the right answer is to open the file, not re-seal.

## The queue, and the only number that gets worse on its own

```markdown
There are N items waiting on a decision, and the oldest has waited D days.
<!-- measured: decisao.gates_abertos=N nature=count on=YYYY-MM-DD expires=7d source=decisoes/ -->
<!-- measured: decisao.gate_mais_velho_dias=D nature=count on=YYYY-MM-DD expires=7d source=decisoes/ -->
```

⚠️ **`expires=7d` on both, and it is the shortest deadline on the whole shelf.** It is not rigor:
it is that their value goes stale in days, not months. A seal that says *"the oldest has waited 3
days"* written two months ago is not wrong — it is **obsolete**, which is worse, because it looks
like information.

**`decisao.gate_mais_velho_dias` is the only metric on this shelf that goes up when you do nothing.**
It is a count — it diverged, re-seal — but read the number before re-sealing. If it went from 12 to
47, the re-seal is not the task: the task is the item that has been there for 47 days.

## The three archive counts

```markdown
<!-- measured: decisao.total=N nature=count on=YYYY-MM-DD expires=90d source=decisoes/ -->
<!-- measured: decisao.aceitas=N nature=count on=YYYY-MM-DD expires=90d source=decisoes/ -->
<!-- measured: decisao.revogadas=N nature=count on=YYYY-MM-DD expires=90d source=decisoes/ -->
```

⚠️ **Do not write the three in a sentence that also claims the sum.** *"There are 44 decisions: 41
accepted and 3 revoked"* claims four things, and the seal covers three — the fourth (that 41+3
exhausts the 44) is a relation claim that no metric there names. That is what the `PROSE_DRIFT`
verdict exists for.

If you really do want to claim it exhausts, **sealing `decisao.sem_status=0` is what says that** —
and then the sentence and the seal are talking about the same thing.

## The deadline is a choice, and it has an owner

```markdown
An item waiting on a decision is reviewed every week.
<!-- arbitrated: decisao.prazo_de_fila=7 by="whoever runs the decision room" on=YYYY-MM-DD expires=180d
     breaks="a team that decides in monthly rounds, or an item whose cost of waiting is zero" -->
```

Seven days is this operation's default, not a measurement. A number chosen with no owner is a guess
with the face of a fact.

## What NOT to seal here

**Nothing claiming the decisions are being FOLLOWED.** *"We follow all our decisions"* is about
behavior, and the probes read files. A decision can be accepted, dated, intact — and nobody
following it. Sealing that would be giving a measurement's mark to a hope.

**Nothing about the decision's quality.** Recorded, dated and with an alternative is what is
measured. *Right* is recomputable by no function.

**Nothing about what did not become a file.** *"All our decisions are recorded"* is exactly what no
probe here can confirm: it counts what exists in the folder, and what was agreed in a meeting and
never written is invisible to it. A green seal there would be the tool attesting its own blind spot.
