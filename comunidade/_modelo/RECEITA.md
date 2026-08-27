# Operation · `your-operation-name`

<!-- loadline-ignore-file: this file TEACHES the seal syntax to whoever is going to write a new
     operation — the `YYYY-MM-DD` below is a placeholder on purpose, not a broken date. -->

> TODO — one sentence summarizing the pain, in the same tone as "What is stuck right now waiting on
> a decision from you?" (`sala-de-decisao`) or "You have more than one agent and nobody looks at the
> set" (`forja`). If the sentence bothers nobody, the operation probably should not exist.

## The pain

TODO — two or three paragraphs. Describe the real problem, with a concrete example (file name,
format, situation). Do not describe the solution here — only the pain.

## What this operation installs

TODO — the probe table, in the same format as the others:

<!-- measured: operacao.NOME.sondas=N nature=count on=YYYY-MM-DD expires=never source=comunidade/your-operation-name/sondas.py -->

| Metric | What it recomputes | Nature |
|---|---|---|
| `NOME.exemplo` | TODO | count or relation |

## The adjustment

TODO — the field (or fields) whoever clones has to change. The house ruler: at most two fields.

```python
CAMPO_DE_AJUSTE = "TODO"
```

## How to run

```console
$ cp comunidade/your-operation-name/sondas.py /path/to/your/repo/sondas.py
$ cd /path/to/your/repo
$ PYTHONPATH=/path/to/loadline python -m loadline .
```

TODO — paste the real output of a run, not an invented one. If the output is invented, the reviewer
will ask for the real run before continuing.

## What this operation does NOT do

TODO — at least two items. Every operation on this shelf declares its limit in full; an operation
with no such section does not pass review. Re-read the repository's `LACUNAS.md` before writing this
section — three of the limits there (the probe proves internal coherence, never the truth of the
world; nothing here judges whether the metric was the right one; nothing here installs/downloads/
sends/phones) hold for your operation too, and do not need to be rewritten — only cited.
