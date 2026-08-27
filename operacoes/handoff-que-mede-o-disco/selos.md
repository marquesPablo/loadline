# The seals of this operation

## Where they live, and here that is the whole decision

Paste **inside the handoff file itself**, at the top. In no other operation on the shelf does the
place matter this much: the seal has to be in the document it judges, because it is that document
someone will open in three weeks believing it.

A seal about the handoff kept in the README is a warning hung on the wrong door.

## The three that tell you to stop

```markdown
This file was written reading the disk: no cited path is dead, no command lost its target, and what
it says about the state of the repository is what git says.
<!-- measured: handoff.caminhos_mortos=0 nature=relation on=YYYY-MM-DD expires=7d source=disk -->
<!-- measured: handoff.comandos_sem_alvo=0 nature=relation on=YYYY-MM-DD expires=7d source=disk -->
<!-- measured: handoff.deriva_de_git=0 nature=relation on=YYYY-MM-DD expires=7d source=git -->
```

**`expires=7d` on all three, and it is the shortest deadline on the whole shelf** — together with
the decision queue's. It is not rigor: it is that their value goes stale in days. A handoff that was
right a month ago is not *almost* right today; it is false with the look of specific, which is the
most expensive state of all.

⚠️ **`handoff.deriva_de_git` is 0 or 1, not a count.** It answers *"does the document claim one
thing about the state and git claim another?"*. If the document **claims nothing** about the state,
it is 0 — silence is not an assertion, and accusing it would turn the probe into a style demand.

## The age, which is the number that opens the conversation

```markdown
Written after commit N. Nothing landed since then.
<!-- measured: handoff.commits_desde=0 nature=count on=YYYY-MM-DD expires=7d source=git -->
<!-- measured: handoff.sessoes_desde=0 nature=count on=YYYY-MM-DD expires=7d source=harness -->
```

`count`: they move on their own, every day, and that is the point. **They diverged, re-seal — but
read the number first.** If `commits_desde` went from 0 to 40, the re-seal is not the task: the task
is to rewrite the document, and the re-seal is the consequence.

⚠️ **The two only hold in your working tree.** git does not preserve `mtime`; in a clean clone they
blow up to the total. **Do not read their green in CI as proof** — and if your CI runs this
operation, read the warning in `ci.yml`.

## The size, and why it is `arbitrated:` and not `measured:`

```markdown
This file fits in 400 lines. Past that, something here became history and should have left.
<!-- arbitrated: handoff.teto_de_linhas=400 by="whoever looks after the project" on=YYYY-MM-DD expires=180d
     breaks="a project with many parallel fronts, or a handoff that came to be read by people from outside" -->
<!-- measured: handoff.linhas=N nature=count on=YYYY-MM-DD expires=30d source=disk -->
```

**The ceiling is a choice, not a measurement** — hence the third mark. A handoff dies in two ways:
by aging and by **bloating**. The second is quieter, because nobody rejects it: it just starts
taking up the beginning of every session without giving anything back, and each round adds a little.

## What NOT to seal here

**Nothing claiming that the checks PASS.** This operation executes nothing — it checks that the
command's target exists. `comandos_sem_alvo=0` and *"the suite is green"* are different claims, and
sealing the second with the first's probe is giving a measurement's mark to a hope.

**Nothing about what was decided in the session.** The probes read the disk. What was agreed and did
not become a file is invisible to all eight, and a green seal is not proof that the context is
complete.

**Nothing about the handoff being RIGHT.** It can have zero dead paths, zero drift, zero commits on
top — and describe badly what matters. The probes measure whether it matches the disk. Whether it
tells the right story stays a judgment for whoever writes.
