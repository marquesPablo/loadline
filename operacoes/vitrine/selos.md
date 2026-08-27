# The seals of this operation

Paste at the end of your `README.md` (or `CLAUDE.md`/`AGENTS.md`). Replace `YYYY-MM-DD` with
today's date.

## The minimum (what stands on its own)

```markdown
## What the skills in this repository promise

Every skill under `.claude/skills/` passes the vitrine — name matching the folder,
usage trigger and negative trigger declared.
<!-- measured: vitrine.reprovas=0 nature=relation on=YYYY-MM-DD expires=30d source=vitrine -->
```

**Why `relation` and not `count`.** A count metric moves when someone writes — it went up, re-seal
and move on. This one only moves if a skill went invisible: diverging name, broken grammar, or no
trigger clause. Diverging here means **stop and fix the skill**, never re-seal the number upward —
marking this as `count` would train the team to re-seal the defect instead of correcting it.

**Why `expires=30d`.** A skill is born and dies with the repository — thirty days is this
operation's default choice, not a measurement, and that is why it is an `arbitrated:`, with an owner:

```markdown
The skill re-check deadline is 30 days.
<!-- arbitrated: vitrine.prazo=30 by="whoever adopted the operation" on=YYYY-MM-DD expires=180d
     breaks="a repository where new skills show up every week, or none in months" -->
```

## The complete one (both)

```markdown
<!-- measured: vitrine.skills=N nature=count on=YYYY-MM-DD expires=90d source=.claude/skills -->
<!-- measured: vitrine.reprovas=0 nature=relation on=YYYY-MM-DD expires=30d source=vitrine -->
```

Don't know which `N` to write? Don't write it. Run `python -m loadline . --selar` and the tool
writes both, as `arbitrated:`, with today's value. Swap `arbitrated:` for `measured:` — that swap is
what turns a chosen number into a recomputed one.

## What NOT to seal here

**Nothing about whether the skill WORKS.** The `vitrine` judges whether the skill is **findable** —
correct window, declared trigger. Whether it solves the problem once found is another job, one that
requires running the skill against a real task, and there is no probe for it here. See
`vitrine/LACUNAS.md`.

**And nothing about the BODY of the `SKILL.md`** beyond the line count. A contradictory instruction,
a command that no longer exists, an order planted by another agent — none of that is examined by
this operation.
