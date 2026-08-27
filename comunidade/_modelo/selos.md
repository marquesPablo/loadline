# The seals of this operation

TODO — paste into the file your metric judges (the seal must live in the file it measures, never in
a separate report).

```markdown
TODO — the prose sentence the metric holds up.
<!-- measured: NOME.exemplo=N nature=count-or-relation on=YYYY-MM-DD expires=90d source=relative/path/ -->
```

## About `nature`

- **`count`** — moves when someone writes. It diverged, re-seal and move on.
- **`relation`** — only moves if the meter or the repository broke. It diverged, **stop and
  investigate**.

If your metric is ambiguous between the two, re-read the repository's `LACUNAS.md` — the distinction
exists precisely so nobody has to guess what a red means.

## About `expires`

TODO — pick the deadline and say why, in the same spirit as
`operacoes/sala-de-decisao/selos.md` (`expires=7d` because the value there ages in days, not
months). A seal with no named `expires` is a number with no expiry date.

## What NOT to seal here

TODO — at least one sentence that would seem natural to seal and that your probe CANNOT hold up
(e.g. quality, intent, behavior in production — things the probe does not read). Every operation on
this shelf names this; it is what keeps a green seal from becoming the tool attesting its own blind
spot.
