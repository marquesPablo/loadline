# What this project does NOT measure

> **The third list.** Every tool publishes what passed and what failed. Almost none publishes
> **what it never looked at** — and it is that third list that decides whether a green means anything.
>
> This file is the denominator of the whole project, in the same spirit as the `LACUNAS.md` that
> `forja` emits for every agent it compiles. It exists so that nobody has to discover a limit
> **by using** the tool and being surprised by it.

## 1 · The probe proves internal coherence, never the truth of the world

The probe recomputes the number from a source on disk. If that source is wrong, the pair passes
green with both sides wrong together. **A coherent JSON is not a true fact.**

That is what `expires=` is for: it is the only mechanism here that forces someone to leave the
machine. No green in this project means *"this is true out there"*.

## 2 · The prose-vs-seal cross-check bites in one direction only

`PROSE_DRIFT` flags **a number in the sentence that no seal in the block covers**. The other
direction — *the sentence claims a QUANTITY the seal does not name*, without writing a number —
needs a closed register of quantities and a judgment about what counts as a claim. **It is not
implemented.**

Practical consequence: *"the suite is green"* and *"the repository is in sync"* are claims, and they
pass with no charge at all here.

## 3 · `um` and `uma` are not read as a numeral

In Portuguese they are an indefinite article before they are a number, and *"Um registro do
ecossistema"* claims no quantity. Telling the two uses apart needs syntactic analysis this project
does not do.

**The cost:** a sentence that really does claim *"one project has no canonical"* passes with no
charge. The way out for whoever needs it is to write the digit.

## 4 · A percentage is not cross-checked

A percentage is derived, and checking it would need the denominator — which is exactly what the text
usually omits. It is removed before the cross-check, along with dates, versions and identifiers.

## 5 · The cross-check only looks at prose, not code

In a `.py`, what surrounds a seal is code, and demanding a prose echo of a number there would flag
every neighboring literal. A seal in a code comment is judged by its value, never by the sentence.

## 6 · Nothing here measures the QUALITY of what was written

The project answers *"does this number still match?"* and *"does this sentence repeat it right?"*. It
does not answer whether the metric was the right one, whether the probe measures what it claims to
measure, or whether the claim mattered. That is judgment, and it stays with whoever writes.

## 7 · The neighbors' denominator is from one date, not from always

The comparison with `agents-lint`, `agent-pd` and `agent-audit` in `README.md` was done on
**2026-08-20**, reading the public page. None of the three was cloned, installed or run. They may
have changed since then, and nothing here re-checks that by itself — it is gap nº 1 applied to this
very argument.

## 8 · The metric name that `--selar` writes is a GUESS

It comes from the word right after the number in the sentence — *"12 endpoints"* becomes
`endpoints=12`. It is the same reading a human does, and it gets it wrong for the same reasons:
reversed order (*"endpoints: 12"*), the next word being a preposition, or the number having no noun
next to it at all. In those cases it writes `YOUR_METRIC`, and repeated names in the same file get a
suffix.

**This is a suggestion to rename, never a claim that the tool understood what the number means** —
and the difference between the two is written in the output of every run that writes.

## 9 · The survey flags the ABSENCE of the declaration, never its quality

It answers *"is there anything machine-readable here saying what this agent never does?"*. It does
not answer whether the anti-description was right, whether the declared boundary was the good
boundary, or whether the golden-set case asks what matters. **An excellent agent with its boundary
written in prose shows up on the list, and it should** — but the converse does not hold: declaring
is not getting it right.

## 10 · Multi-line frontmatter is not read

The reader takes one-line `key: value`, which is what today's harnesses write. A `description`
broken across several lines, or a nested YAML block, is read half-way — and the half that was
missing becomes an absence, which is exactly the error this file exists to name.

**The cost:** an agent well declared in multi-line YAML can be flagged for nothing.

## 11 · The `V6` threshold is CHOSEN, not measured

Thirty percent of words in common. Nobody measured that 30% is where two agents start fighting over
the same dispatch — the number was chosen looking at real rosters, and it is in the code with the
reason next to it instead of buried in a condition. It gets it wrong both ways, and its output is a
**reading list, never a verdict**: `V6` alone should not fail anyone's CI.

## 12 · Nothing here runs the agent

The survey reads a file at rest. It does not dispatch, does not watch the orchestrator choosing, and
does not know whether your agent answers well. It knows whether there is, in the repository,
**something capable of saying it answered badly** — which is a smaller question, and the only one
that can be answered offline and without a model.

## 13 · `V6` compares WORDS, not meaning

It finds `revisor` × `auditor` when both descriptions say *"looking for quality, security and
architecture problems"* — same words, ~64% in common. It **does not find**
`pesquisador` × `investigador` when one says *"searches the web and summarizes what it found about a
topic"* and the other *"investigates on the web and summarizes what it turned up about a subject"*.
They are the same role, written with synonyms: 17% of words in common, below the threshold, and they
pass green.

Finding a synonym would need a model, and a verifier that depends on a model is not a verifier —
it is a second opinion, and it does not run offline or in the CI of whoever needs it most.

**The cost, spelled out:** `V6` finds a VOCABULARY collision. It is a floor, never a ceiling —
its silence is not proof that your roster does not get confused. The question it does not ask, and
that stays yours: *if I hid the names, would I know which of the two to dispatch?*

## 14 · `--baseline` identifies a finding by TEXT, not by a stable identity

Each item's key is `"RULE: item text"` (`forja/baseline.py`) — the same text that shows on screen.
Renaming an agent (`tradutor.md` → `traducao.md`) makes the old item vanish and a new one with an
identical look appear: `--baseline` reports that as **1 resolved + 1 new**, not as **0 changes**.
Tracking a real identity would need a key that survives the rename — the filename is the only thing
available, and it is exactly what changes on the rename.

**The cost:** a repository that only renames files, without touching any declaration, sees
`--baseline` flag noise. It is a false positive of NOISE, never a false negative of a real defect —
the "new" item does exist, it is just not new in the sense the person reading the diff expected.

## 15 · `action.yml` has never actually run on a GitHub runner

`acao/gate.py` — the only part with real branching — has a negative control in `autoteste.py`
(`CA`–`CD`). `action.yml` itself (the step composition, `${{ github.action_path }}`,
`actions/upload-artifact@v4`) was only checked by reading it and by running the same commands
manually with `PYTHONPATH` simulating what `github.action_path` would resolve to. **There is no
automated test that stands up a real workflow and confirms the YAML composes as this file
promises** — that would need a public repository with Actions enabled, which is exactly the gate the
launch decision reserves for the owner.

## Closed

A gap leaves this list when the mechanism that closed it starts to exist and to have a negative
control. The record stays, because the list shrinking silently would be the same family of defect
this file exists to prevent.

- **`There is no mark for a number that was CHOSEN, not measured`** — closed on 2026-08-20 by the
  `arbitrated:` mark, which requires the owner (`by=`) and expires like any other seal. It was
  described here as *"the deepest gap on the list, and the next thing to be born"*. Negative
  controls: three autoteste checks, each reintroducing the defect.
