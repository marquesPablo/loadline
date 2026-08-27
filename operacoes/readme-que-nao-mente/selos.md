# The seals of this operation

Do not copy this list by hand. **Run `python -m loadline . --selar`** — it writes the seal for each
claim in your text, in the right place, with today's value, and never overwrites an existing seal.

This file exists for the decision that comes AFTER: which mark each seal should have.

## The flow, in three steps

```console
$ python -m loadline .          # 1. what nobody verifies here
$ python -m loadline . --selar  # 2. writes everything as `arbitrated:`
$ python -m loadline . --sondas # 3. which metrics have a ready probe
```

After step 3, for each seal whose metric name appears in the probe list: swap `arbitrated:` for
`measured:`, add `nature=` and `source=`, and delete the `by=`.

```diff
- <!-- arbitrated: testes=84 by=? on=2026-08-21 expires=90d -->
+ <!-- measured: repo.testes=84 nature=count on=2026-08-21 expires=90d source=code -->
```

⚠️ **The metric name that `--selar` writes is a guess.** It comes from the word right after the
number in the sentence — *"84 tests"* becomes `tests=84`. Rename it to `repo.testes`, which is the
name the probe covers. The tool says so in the output of every run that writes; it is not a trick,
it is a suggestion declared as a suggestion.

## The thirteen with a ready probe

```markdown
<!-- measured: repo.arquivos=N nature=count on=YYYY-MM-DD expires=90d source=disk -->
<!-- measured: repo.fontes=N nature=count on=YYYY-MM-DD expires=90d source=disk -->
<!-- measured: repo.linhas=N nature=count on=YYYY-MM-DD expires=90d source=code -->
<!-- measured: repo.linguagens=N nature=count on=YYYY-MM-DD expires=90d source=extensions -->
<!-- measured: repo.testes=N nature=count on=YYYY-MM-DD expires=90d source=code -->
<!-- measured: repo.arquivos_de_teste=N nature=count on=YYYY-MM-DD expires=90d source=disk -->
<!-- measured: repo.dependencias=N nature=count on=YYYY-MM-DD expires=60d source=manifest -->
<!-- measured: repo.dependencias_dev=N nature=count on=YYYY-MM-DD expires=60d source=manifest -->
<!-- measured: repo.workflows=N nature=count on=YYYY-MM-DD expires=90d source=.github/workflows -->
<!-- measured: repo.pendencias=N nature=count on=YYYY-MM-DD expires=90d source=code -->
<!-- measured: repo.maior_arquivo=N nature=count on=YYYY-MM-DD expires=90d source=code -->
<!-- measured: repo.contribuidores=N nature=count on=YYYY-MM-DD expires=90d source=git -->
<!-- measured: repo.commits=N nature=count on=YYYY-MM-DD expires=90d source=git -->
```

All of them are `count`: they move when someone writes code. It diverged, re-seal and move on — it
is normal behavior, not a defect. If you want one of them *not* to move — a ceiling on
`repo.maior_arquivo`, for example — that is not a measurement, it is a **choice**, and the mark is
another:

```markdown
No file in this repository is over 400 lines.
<!-- arbitrated: repo.teto_de_arquivo=400 by="platform team" on=YYYY-MM-DD expires=180d
     breaks="the first file that is only readable above that" -->
```

## What NOT to seal

**Nothing generated.** If the number is in a file produced by a script from another source, sealing
the value is a mirror check: both sides come from the same place and the pair passes green
**locking** the defect in. For a derived artifact, use **one** `nature=relation` seal that answers
*"does this still match the source?"* — it does not move when someone adds an item, it only moves if
someone edited the published one by hand or touched the source without regenerating.

**Nothing about the world out there.** *"The fastest on the market"*, *"used by 200 companies"*,
*"the industry standard"*. No offline probe reaches that. Either the sentence gets a denominator and
a date and becomes an honest `frozen:`, or it goes.

```markdown
On 2026-08-20, among the three neighbors we found, it was the only one with a deadline in the claim.
<!-- frozen: neighbors.with_deadline=1 reason="comparison made on 2026-08-20 reading the three public pages; a claim about that date, not a live assertion about today's" -->
```
