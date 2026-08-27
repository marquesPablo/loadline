# The seals of this operation

## The seal that stands on its own

Paste **into your repository's README**, in the section about the tests — that is where the promise
is made.

```markdown
The suite has N checks, and none of them is a function that cannot fail.
<!-- measured: suite.checks=N nature=count on=YYYY-MM-DD expires=never source=tests/ -->
<!-- measured: suite.sem_assercao=0 nature=relation on=YYYY-MM-DD expires=never source=tests/ -->
```

**`suite.sem_assercao=0` is the only seal of this operation that is a verdict**, and so it is the
only one that deserves to fail CI on its own. A test function with no assertion cannot fail — it is
a property of the code, not opinion.

`expires=never` on both, on purpose: they do not age with time, they only move when someone touches
the suite. Putting a deadline would make the same metric fail for two different reasons, and the red
would stop saying which.

## The third list

```markdown
This suite declares N things it does NOT measure.
<!-- measured: suite.lacunas_declaradas=N nature=count on=YYYY-MM-DD expires=90d source=LACUNAS.md -->
```

**`expires=90d` here, and the deadline is the mechanism.** A gap list ages in a particular way: the
gaps **close** without anyone deleting the line. The check that was missing was written two months
ago and the list still declares the hole. A declared limit that no longer exists is as misleading
as one that was not declared — and the deadline is what forces someone to re-read.

## ⚠️ The heuristic seal, and how to write it without lying

```markdown
The rule points at N tests with no apparent negative control. It is a reading list, not a verdict:
the detection gets it wrong both ways and is declared a heuristic.
<!-- arbitrated: suite.sem_controle_negativo=N by="whoever looks after the suite" on=YYYY-MM-DD expires=60d
     breaks="any test on this list that, when opened, reveals a negative control the rule did not recognize" -->
```

**`arbitrated:`, and not `measured:`.** The mark matters: `measured:` says *this was measured*, and
this metric is a declared approximation. `arbitrated:` says *someone chose to treat it this way, and
here is who*.

And `breaks=` is the most valuable part — it writes, before it happens, what would make the number
stop holding. **Do not put this metric in CI as a failure.** A heuristic rule that fails trains the
team to write a test to please the rule, and then it stops measuring the code.

## The two hygiene ones

```markdown
<!-- measured: suite.arquivos=N nature=count on=YYYY-MM-DD expires=never source=tests/ -->
<!-- measured: suite.pulados=0 nature=relation on=YYYY-MM-DD expires=30d source=tests/ -->
```

**`suite.pulados` with a short deadline.** A skipped test is a test that does not exist, with the
look of existing: it counts in the list, shows up in the report, and the only thing it measures is
how long ago someone gave up on it. Thirty days is what stops a temporary `skip` from becoming
permanent with nobody deciding it.

## The deadline is a choice, and it has an owner

```markdown
The suite's rule is re-checked every 60 days.
<!-- arbitrated: suite.prazo=60 by="whoever looks after the suite" on=YYYY-MM-DD expires=180d
     breaks="a project that rewrites the suite every release, or one whose suite has not changed in a year" -->
```

## What NOT to seal here

**Nothing claiming the suite is COMPLETE.** *"We cover every case"* is the claim the third list
exists to make impossible. What did not become a test is invisible to all six probes.

**Nothing about line coverage.** Another question, another tool — and **high coverage with zero
negative control is the exact state this operation exists to find**. Sealing coverage next to these
metrics invites reading one as confirmation of the other, when they frequently contradict each other.

**Nothing claiming the tests WOULD CATCH a real bug.** `sem_controle_negativo=0` says the rule
recognized a failure-expectation construct in every test. It does not say the reintroduced defect
was the right one, nor that it is what will happen in production.
