# An example roster, and it is bad on purpose

Four hand-written agents, the way almost everyone writes the first one: a good description, a
reasonable prompt, and no declaration a runtime can read.

```console
$ python -m forja exemplos/roster-de-exemplo
```

**All four show up in the report, and they do not show up the same** — which is the point. `tradutor.md`
is the best written of the four and comes out with two findings; `revisor-de-pr.md` comes out with
seven. If the survey flagged all four the same way, it would not be measuring anything.

| File | What is wrong with it | Findings |
|---|---|---:|
| `revisor-de-pr.md` | no `tools:` (inherits all), no anti-description, no trigger, and gets confused with the auditor | 7 |
| `auditor-de-seguranca.md` | asks for network without saying who it talks to, no trigger, and gets confused with the reviewer | 6 |
| `redator-de-changelog.md` | asks for write and `Bash` without saying where it writes; does not say what it never does | 4 |
| `tradutor.md` | says `Write only in docs/en/` **in the prose** — and no runtime reads prose; and nothing checks its answer | 2 |

The `tradutor` case is the most instructive of the four: it **does** declare where it writes, in
clear English, in the body of the prompt. And it is flagged anyway, on purpose. The sentence governs
whoever reads the file; it does not govern the process that runs the tool.

The first two are the case that only exists from the second agent on: the descriptions fight over the
same dispatch, and **neither one names the other**. The orchestrator will guess, and it will guess a
different way every day.

After looking at the report, try the second step — it writes, and it does not overwrite anything
that is here:

```console
$ python -m forja exemplos/roster-de-exemplo --adotar
```
