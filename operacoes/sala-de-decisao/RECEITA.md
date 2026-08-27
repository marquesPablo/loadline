# Operation 7 · `sala-de-decisao`

> **What is stuck right now waiting on a decision from you?**
> If answering that means opening Slack, three threads and two people's memory, then nothing is
> waiting: things are **forgotten**, and the cost shows up the week one of them turns urgent.

## The pain

Every team has a decision record that died in the third week. And it almost always died for the same
reason: it recorded what had **already** been decided — which is the part nobody needs, because
whoever decided remembers.

The expensive part is the other one: **what has not been decided yet, and is stuck.**

A stuck item does not get worse suddenly. It gets worse one day at a time, and that is exactly why
nobody notices. There is no event, no notification, no diff. On day 40 someone says *"I thought you
were going to decide that"*, and both people are convinced the ball was in the other's court.

And there is a second defect, quieter: **a revocation declared on one side only.** The new decision
says `revoga: ADR-031`. `ADR-031` says nothing. Whoever opens the old one — which is the normal path,
because it is the one cited in the old places — reads a revoked rule as if it held. Both files are
right, each on its own. **The defect lives between them.**

## What this operation installs

Eight probes over a folder of markdown files:
<!-- measured: operacao.sala.sondas=8 nature=count on=2026-08-21 expires=never source=operacoes/sala-de-decisao/sondas.py -->

| Metric | What it recomputes | Nature |
|---|---|---|
| `decisao.total` · `decisao.aceitas` · `decisao.revogadas` | the size and state of the archive | count |
| **`decisao.sem_status`** | **decisions that do not say whether they are in force** | **relation** |
| **`decisao.revogacao_de_um_lado_so`** | **the new one revokes the old one, and the old one does not know** | **relation** |
| **`decisao.sem_alternativa`** | **decisions that do not say what was rejected** | **relation** |
| `decisao.gates_abertos` | how many items wait on a person | count |
| **`decisao.gate_mais_velho_dias`** | **how many days the oldest one has waited** | count |

**`decisao.gate_mais_velho_dias` is the only metric on this whole shelf that gets worse when you do
nothing.** It goes up on its own, every day, until someone decides. It is on purpose: a number that
only improves with action is the only honest way to measure what inertia costs.

## The two conventions, and why they live in the file NAME

**A gate is a file that waits on one person's decision.** It is recognized by two things:

```
decisoes/2026-03-04-gate-trocar-o-provedor-de-email.md
          └── the date        └── the word `gate`
```

1. **The word `gate` in the name.** Without it the file is an ordinary decision, and it disappears
   among the others.
2. **The date in the name.** It is where the age comes from.

This looks like a style detail and it is not. **The file name is the only part that shows up in
`ls`, in the explorer, in the PR diff and in a search — without anyone opening anything.** A
`criada_em:` field inside the frontmatter is invisible in all those places. An item that waits on a
decision and that nobody sees is not waiting: it is forgotten.

And the gate closes with a markdown **heading** containing `DECIDIDO`:

```markdown
## DECIDIDO — 2026-03-19

We stayed with the current provider for another year. Reason: the migration would cost two weeks of
one person and the measured gain was 4% on delivery.
```

**A heading, not bold.** `**DECIDIDO**` in the middle of a paragraph closes the gate and disappears
from the history — and a search by heading is how you read a record like this six months later.

## The adjustment

**One field**, at the top of `sondas.py`:

```python
PASTA_DE_DECISOES = "decisoes"
```

There is no required format for the body. The probes read `status:` in the frontmatter, the word
`revoga:`/`emenda:`, and look for an alternatives section. If your format uses other words, adjust
the four `re.compile` at the top — they are in a single named block.

## How to run

```console
$ cp operacoes/sala-de-decisao/sondas.py  /path/to/your/repo/sondas.py
$ cd /path/to/your/repo
$ PYTHONPATH=/path/to/loadline python -m loadline .
```

```console
FAIL   decisoes/README.md:8  decisao.revogacao_de_um_lado_so: written=0 measured=3
       → nature=relation — STOP and investigate.
FAIL   decisoes/README.md:9  decisao.gate_mais_velho_dias: written=12 measured=47
       → nature=count — re-seal; and read the number first.
```

**The second one is the one that hurts.** It is not an annotation error: it is 47 days of an item
waiting on you, and the seal written a month ago is the proof that nobody has looked since.

## What this operation does NOT do

1. **It does not decide, and never will.** The agent surfaces the decisions that contradict each
   other and stops. Choosing would need knowing which was more thought through, which the team still
   holds and what changed in the world — none of the three is in the text. **Deciding is the one job
   this record exists not to automate.**

2. **It does not see what did not become a file.** What was agreed in a meeting and was not written
   is invisible to all eight probes. That is the biggest gap here, and no tool closes it — it closes
   with the habit of writing.

3. **It does not measure whether the decision is being FOLLOWED.** A decision can be accepted, dated,
   intact, with alternatives — and nobody following it. The probes read the record, not the behavior.

4. **It does not judge whether the decision was good.** It measures whether it is recorded, dated,
   with an alternative and with a back-pointer. Judgment quality is recomputable by no function, and
   a green seal about it would be a guess with a measurement's mark.
