# The seals of this operation

## The four that tell you to stop

Paste **into your vault's README** — the file that describes what the corpus is and what the server
serves.

```markdown
This server exposes four read-only tools over my notes, with no third-party dependency at all,
and the graph has no edge to the void.
<!-- measured: cerebro.ferramentas=4 nature=relation on=YYYY-MM-DD expires=never source=servidor.py -->
<!-- measured: cerebro.dependencias=0 nature=relation on=YYYY-MM-DD expires=never source=servidor.py -->
<!-- measured: cerebro.links_quebrados=0 nature=relation on=YYYY-MM-DD expires=30d source=corpus -->
<!-- measured: cerebro.orfas=0 nature=relation on=YYYY-MM-DD expires=90d source=corpus -->
```

**`cerebro.dependencias=0` is the most valuable seal of this operation**, and the least obvious.
*"Zero dependencies"* is the sentence that makes someone run this on a machine they do not
administer — and it dies the day someone adds an `import` for convenience. The diff shows one line;
no code review catches it. The probe reads the code and counts.

**`cerebro.ferramentas` with `expires=never`, on purpose.** It does not age with time: it moves when
someone touches the server, and that is exactly where it has to fail. Putting a deadline on it would
make the same metric fail for two different reasons, and the red would stop saying which.

## The two corpus counts

```markdown
<!-- measured: cerebro.notas=N nature=count on=YYYY-MM-DD expires=90d source=corpus -->
<!-- measured: cerebro.pastas=N nature=count on=YYYY-MM-DD expires=90d source=corpus -->
```

These move every time you write. They diverged, re-seal and move on — it is the case where the red
means *"you worked"*.

## ⚠️ The mistake this operation invites you to make

**Never write a `[[wiki-link]]` inside a seal's comment, nor in a note that exists to MEASURE the
graph.**

Naming an orphan note gives it an incoming edge. If the file where you record the orphans cites them
by wiki-link, it **closes the hole it is measuring** — and `cerebro.orfas` drops to zero because of
the record itself. The number goes green and the measurement died.

It holds for the seal too: the link parser does not tell an HTML comment from text. If you need to
name a note inside a seal or an orphan record, write the name **out in full, without the double
brackets**.

## The deadline is a choice, and it has an owner

```markdown
The notes graph is re-checked every 30 days.
<!-- arbitrated: cerebro.prazo=30 by="whoever adopted the operation" on=YYYY-MM-DD expires=180d
     breaks="a vault that only receives new notes, or one where several people rename files" -->
```

Thirty days for a broken link and ninety for an orphan is not forgotten symmetry: **a broken link
comes from a rename and is fixed in seconds**; **an orphan is a judgment** — many notes legitimately
are not cited by anyone yet, and charging that every month trains you to create a fake link.

## What NOT to seal here

**Nothing about the CONTENT being right.** The probes count files, links and imports. A whole wrong
note passes all of them. A green seal here says the corpus is well linked, never that it is correct.

**Nothing about performance or context size.** *"The server answers in 40 ms"* depends on the
machine of whoever ran it, and a number like that sealed in your README becomes a promise you make
with someone else's computer.

**Nothing about content security.** The server's fence is a **path** fence: it refuses to read
outside the root. It does not judge what is written inside the notes it serves, and a green seal is
not proof that your corpus contains no order aimed at an agent.
