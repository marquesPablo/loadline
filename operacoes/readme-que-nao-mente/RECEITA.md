# Operation 2 · `readme-que-nao-mente`

> *"More than 200 tests."* Who counted? When? The sentence has been in the `README.md` since v0.3.
> Today it is 84, because the suite was split into two packages and half went to the other repository.
> **The number did not suddenly go wrong. It was never checked again.**

## The pain

Every README claims a quantity. Endpoints, tests, dependencies, languages, contributors, size. None
of those sentences has an expiry date, none fails when it ages, and the one that aged still has the
same look of being right — which is what makes it worse than a missing sentence.

## What this operation installs

Thirteen generic probes. They work in any repository, with not one line of configuration, and none
of them reads any `.md` — they all read code, a manifest or `git`.

| Metric | What it recomputes |
|---|---|
| `repo.arquivos` · `repo.fontes` · `repo.linhas` | the real size, outside `node_modules`, `venv`, `dist`, `build`… |
| `repo.linguagens` | distinct language extensions |
| `repo.testes` · `repo.arquivos_de_teste` | test functions by the convention of Python, Go, JS/TS, Rust, Java |
| `repo.dependencias` · `repo.dependencias_dev` | from `pyproject.toml`, `package.json`, `requirements.txt`, `go.mod` |
| `repo.workflows` | files in `.github/workflows/` |
| `repo.pendencias` | `TODO` / `FIXME` / `XXX` / `HACK` |
| `repo.maior_arquivo` | lines of the largest file — the number nobody wants to see |
| `repo.contribuidores` · `repo.commits` | from `git`, not from a file |

<!-- measured: operacao.readme.sondas=13 nature=count on=2026-08-21 expires=never source=operacoes/readme-que-nao-mente/sondas.py -->

## The adjustment

**None.** If your project has a build folder with an unusual name, add it to `_REPO_IGNORAR` at the
top of `sondas.py`. It is the only line anyone needs to touch, and only in that case.

## How to run — the 60 seconds

```console
$ cp operacoes/readme-que-nao-mente/sondas.py  /path/to/your/repo/sondas.py
$ cd /path/to/your/repo

$ PYTHONPATH=/path/to/loadline python -m loadline .            # what nobody can verify here
$ PYTHONPATH=/path/to/loadline python -m loadline . --selar    # writes each one's seal, for you to paste
```

`--selar` writes everything as `arbitrated:` — *this number was chosen, not measured* — because
nobody has measured anything yet. **Where there is a probe with the same name, swap `arbitrated:`
for `measured:`.** That swap is the whole operation: the number stops being a noted guess and
becomes recomputed on every run.

Do not know which have a probe? The tool says so:

```console
$ PYTHONPATH=/path/to/loadline python -m loadline . --sondas
probes loaded from: sondas.py
  repo.arquivos                ← files outside the dependency and build folders
  repo.commits                 ← `git rev-list --count HEAD`
  repo.contribuidores          ← distinct authors in `git shortlog -sne --all`
  ...
```

## What you see

```console
$ PYTHONPATH=/path/to/loadline python -m loadline .
DRIFTED   README.md:8   repo.testes: written=200 measured=84   → re-seal: a count moves when someone writes
EXPIRED   README.md:11  repo.dependencias: written=7 measured=7
          → re-check and re-seal — nobody has looked at this for 214 days (deadline: 90d)
```

> *An example written by hand to illustrate the two verdicts. It is not the output of a real
> repository — and the difference between illustrating and measuring is the reason this warning exists.*

Look at the second one: **the number is right and it still fails.** A number nobody has re-checked
in seven months is a number that has not been wrong yet — not a verified number. That is the point
of the whole project, and this is its cheapest example.

## The agent

`agente.toml` compiles the `auditor-de-afirmacao`, which answers the question that comes after the
third list: **for each claim nobody verifies, is there a ready probe, or does it need to become
`arbitrated:`, or should the number leave the text?** Those are three different destinations, and
choosing wrong is how a repository accumulates a decorative seal.

```console
$ python -m forja operacoes/readme-que-nao-mente/agente.toml
```

## The three things this operation does not do

1. **A count is not quality.** `repo.testes` counts what *looks like* a test by the language's
   convention. It does not know whether the test tests anything — and a repository can double that
   number without getting safer.
2. **`0` in `repo.dependencias` means "declares no dependency in a manifest I read"**, not "has no
   dependency". Four ecosystems are read; a fifth would pass as zero. If yours is the fifth, write
   the probe — it is six lines, and `sondas.py` shows the format.
3. **No probe here reaches the truth of the world.** They prove internal coherence. *"We are the
   fastest verifier on the market"* is verifiable by nothing here, and the tool says it is not,
   instead of letting it through.
