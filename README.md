# loadline

**You have more than one AI agent in your repository. Nobody looks at the set.**

There is a tool to review **one** `AGENTS.md`. There is none that reads your whole
`.claude/agents/` folder and answers the question that only shows up from the third agent on:

> *Do two of these fight over the same dispatch? Does any reach the whole disk? What does none of them cover?*

One command, no configuration, nothing to write. Clone, and run it against the example roster that
ships with it — or swap the path for your own project:

```console
$ git clone https://github.com/marquesPablo/loadline && cd loadline
$ python -m forja exemplos/roster-de-exemplo
survey · exemplos\roster-de-exemplo\.claude\agents · on 2026-08-22
==========================================================================
Read 4 agent(s).

⛔ THE BOUNDARY IS ONLY IN THE PROSE                                4 of 4
     auditor-de-seguranca.md            asks for network and does not declare who it may talk to
     redator-de-changelog.md            asks for write and does not declare where it may write
     revisor-de-pr.md                   asks for write and does not declare where it may write
     revisor-de-pr.md                   asks for network and does not declare who it may talk to
     tradutor.md                        asks for write and does not declare where it may write
     → "I only write in one path" and "I only read the docs" are intent.
       No runtime reads prose: with no declaration, the agent reaches
       everything the harness reaches.

⛔ GET CONFUSED WITH EACH OTHER                                  1 pair(s)
     auditor-de-seguranca.md × revisor-de-pr.md    64% of the words in common
     → descriptions fighting over the same dispatch, and neither one names the other.
       The fix is nominal: each cites the sibling in what it NEVER does.

--------------------------------------------------------------------------
4 agent(s) · 7 defect type(s) · 17 of 24 declarations missing

FAIL                                                          (exit 1)
```

In your project, it is the same line with another path — or no path, from inside it:

```console
$ python -m forja /path/to/your/project
```

**Zero dependencies.** Just the Python 3.10+ standard library. No LLM, no API key, no
service. A verifier that depends on a model is not a verifier — it is a second opinion.

<!-- measured: nucleo.dependencias=0 nature=relation on=2026-08-22 expires=never source=pyproject.toml -->

---

## Who this is for

**It is for you if** you have three or more hand-written subagents, you no longer remember which does
what, and none of them has a fence a runtime actually reads.

**It is not for you if** you have a single agent. With one, you do not have a system — you have a
file, and a file you read.

---

## The seven findings

The first five are about **one** agent. The last two only exist because there is **more than one**, and
they are the reason this exists.

<!-- measured: vistoria.achados=7 nature=relation on=2026-08-22 expires=never source=forja/vistoria.py -->

| | What it finds | Why it hurts |
|---|---|---|
| `V1` | does not say what it **never** does | the orchestrator dispatches by topic, and the topic of two agents looks far more alike than their work does |
| `V2` | does not say **when** to use it | an agent with no trigger exists on disk and never in the dispatch |
| `V3` | the boundary is **only in the prose** | no runtime reads prose; with no declaration, it reaches everything the harness reaches |
| `V4` | does not say **what it does not cover** | silence is read as coverage, and what was missing becomes "not there" |
| `V5` | nothing checks the **answer** | you test whether it ran, never whether it was right |
| `V6` | **two get confused** | two descriptions fighting over the same dispatch, and neither names the other |
| `V7` | **inherits every tool** | a missing `tools:` does not mean none: in today's harnesses it means ALL |

Every finding is the **absence of a machine-readable declaration** — never a judgment about the
quality of the agent. An excellent agent whose boundary is written in prose shows up here, and it
should. Prose is not a fence; it is intent.

**And the survey looks at the sibling files.** If the fence is in a hook next to it and not in the
prompt text, it counts — otherwise the tool would flag exactly what it emits itself.

---

## It does not stop at the alarm

A report saying you are in bad shape is not work done. The second command writes.

```console
$ python -m forja --adotar
wrote 4 spec(s) in build/specs/ — one per agent read:
  ✓ build/specs/revisor-de-pr.toml
  …
```

Each spec comes out **filled in with what was already in your file**, and with a `?` in every hole
that already existed and nobody had anywhere to see. You fill in the `?` — and then:

```console
$ python -m forja build/specs/revisor-de-pr.toml
  ✓ .claude/agents/revisor-de-pr.md      your subagent, now with a source
  ✓ AGENTS.md                            the format no harness owns
  ✓ revisor-de-pr.system.md              raw system prompt, for an SDK
  ✓ hooks/cerca_revisor-de-pr.py         ⬅ CODE THAT DENIES
  ✓ golden/revisor-de-pr.md              ⬅ the question that checks the ANSWER
  ✓ LACUNAS.md                           ⬅ what it does not measure
  ✓ RECEITA.md                           from which spec came what, and when
```

**The three marked are not text for the model to read.** The hook is a `PreToolUse` process that
reads the event and answers `deny` before the tool runs. A nice prompt without those three is an
ungated agent with a better description.

And the loop closes: run the survey on what the forge produced, and it passes — `0 of 6 declarations missing`.

### The forge refuses to compile eight things

Absent and empty mean the same thing, and both block — because treating a missing field as
permissive is how every fence becomes a back door. **Every refusal carries the fix written out**: a
refusal that does not name the way out trains whoever reads it to route around it.

| | Refuses when | | Refuses when |
|---|---|---|---|
| `R1` | asks for network without saying who it talks to | `R5` | golden set empty |
| `R2` | asks for write without saying where it writes | `R6` | golden taken from inside the agent output |
| `R3` | does not say what it never does | `R7` | touches an external target without authorization |
| `R4` | does not say what it does not cover | `R8` | slug that makes an invalid filename |

<!-- measured: forja.recusas=8 nature=count on=2026-08-22 expires=never source=forja/spec.py -->

---

## Install

```console
$ git clone https://github.com/marquesPablo/loadline && cd loadline
$ python -m forja /path/to/your/project
```

There is no second step.

---

## CI — no infra of its own, no Docker, just the adopter's runner

A composite Action runs `forja`, `placar` and `loadline` in full on your own runner —
no call leaves it.

```yaml
# .github/workflows/loadline.yml
name: loadline
on: [pull_request]
jobs:
  loadline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: marquesPablo/loadline@main
        with:
          html: 'true'          # writes loadline-{forja,placar,loadline}.html
          falhar-em: 'nenhuma'  # default: diagnostic, does not break the build
```

`falhar-em` turns the gate on when you decide it is ready — `'forja'`, `'placar,loadline'`, or
any combination of the three. With `html: 'true'`, the three reports upload as a job artifact
(`loadline-report`); a link to them, in your README, is the real evidence a badge is missing so it
is not just a number that promises without proving:

```markdown
[📄 loadline report](LINK-TO-THE-ARTIFACT-OR-PAGE-YOU-HOST)
```

**Why not a ready-made `shields.io` badge.** A badge that only says "passed", with no clickable link
to the evidence that produced it, was already proposed for this project and **withdrawn**: it is
gameable the same way any green seal with nothing behind it is. The link above points at the real
`--html` — the same run the badge would be summarizing — because a green with no click is no
different from an assertion off the top of your head.

⚠️ **The Action is not on the GitHub Marketplace yet** (that requires a public repository), and this
repository is private today — the `uses: marquesPablo/loadline@main` above starts working from
outside when both change. Writing and testing the Action locally does not depend on either.

---

## What it does NOT do

- **It does not judge the quality** of your agent. It answers *"does this declaration exist?"*, never
  *"was this the right declaration?"*. That is judgment, and it stays yours.
- **It does not read multi-line frontmatter.** It reads one-line `key: value`, which is what today's
  harnesses write.
- **`V6` compares words, not meaning.** It finds `revisor` × `auditor`, which repeat the same
  words. It **does not find** `pesquisador` × `investigador` — same role, written with synonyms,
  17% of words in common. Finding a synonym would need a model, and then this would stop running offline.
  **It is a floor, never a ceiling:** its silence does not prove your roster does not get confused.
- **The `V6` threshold was chosen** — 30% of words in common — and not measured. The number is in
  the code with the reason next to it, instead of buried in an `if`.
- **It does not run your agent.** Nothing here knows whether it answers well; only whether there is
  something capable of saying it answered badly.

The fifteen declared gaps are in [`LACUNAS.md`](LACUNAS.md).

<!-- measured: nucleo.lacunas=15 nature=count on=2026-08-24 expires=never source=LACUNAS.md -->

Every tool publishes what passed and what failed; almost none publishes **what it never looked at**, and
it is that third list that decides whether a green means anything.

---

## Who already does something similar

Checked on 2026-08-20 and re-checked on 2026-08-26, reading each one's public page. None was
cloned or run.

| Project | What it does | Where it stops |
|---|---|---|
| [`agents-lint`](https://github.com/giacomo/agents-lint) | a path that does not exist, a dead script, a deprecated package, a missing section | one file at a time; does not see the roster |
| `AgentLint` | 33 checks on five axes, over one `AGENTS.md` | structural and stylistic audit of one file |
| `AgentLinter` | clarity, structure, security, memory | prompt quality, not an executable boundary |
| [`drift`](https://www.driftdev.sh/) | anchors a markdown spec in the code and fails CI | document × code, and never agent × agent |
| [`agent-pd`](https://github.com/varmabudharaju/agent-pd) | audits the main agent + every subagent **at runtime**, tamper-evident, detects redundancy and self-permissioning | runs the agent to audit it — does not read a file at rest, and does not compare the DESCRIPTION of two agents |
| [`agent-audit`](https://github.com/scadastrangelove/agent-audit) | 296 imported security rules over agent homes and repositories with skills/MCP | per-agent security forensics; does not see overlap between agents |

**They all lint one file, or audit one agent at a time, static or at runtime. None compares the
description of one agent against another and emits a gate over the SET.** That is the difference, and it
is the only one that matters here — and it is narrower than it looks: `agent-pd` already covers part
of the same ground (redundancy, self-permissioning) at runtime, and that list has less than a week
of life before it needs re-checking.

---

## Also lives in this repository

- [`loadline/`](loadline/) — the same rule applied to **text**: a written claim gets an expiry date
  and a probe that recomputes it, and the probe **must not read the source that produced the number**.
  `python -m loadline .`

  > The first run in a repository that never annotated anything — **this one included** — returns a
  > long list of `UNVERIFIED`: a number in the prose that the seals do not cover. That is **expected,
  > and it is not a failure** — it is the third list (*what nobody can verify*), and the exit code is
  > the one the tool reserves for *you have not annotated anything yet*, distinct from the failure code.
  > Seal by hand what matters; `python -m loadline . --selar` annotates the rest in one go, for you
  > to sign later.

- [`operacoes/`](operacoes/) — seven ready-made jobs that run in your repository with no configuration.
  <!-- measured: operacoes.total=7 nature=count on=2026-08-26 expires=never source=operacoes/ -->
- [`censo/`](censo/) — a register of the AI-agent ecosystem where every entry **expires**.
- [`blind/`](blind/) — the boundary a naive scan crosses silently: a junction, a directory symlink,
  and the `.gitignore` rule that hides even from whoever crosses the structural boundary.
  `python -m blind .`
- [`placar/`](placar/) — the seven gates of "Would you ship this AI agent?" (OBJECTIVE · IDENTITY ·
  AUTHORITY · FAILURE · APPROVAL · TRACEABILITY · CONTAINMENT), each checked with disk evidence,
  never opinion. Failing IDENTITY, AUTHORITY or CONTAINMENT is NO-GO. `python -m placar .`
  <!-- measured: placar.portas=7 nature=count on=2026-08-23 expires=never source=placar/portas.py -->

---

## The negative controls

```console
$ python autoteste.py
82 checks declared · 82 run · 0 outside the denominator
PASSED
```

<!-- measured: nucleo.checks=82 nucleo.fora=0 nature=count on=2026-08-26 expires=never source=autoteste.py -->

**Every check reintroduces the defect it exists to catch.** A check that only confirms the happy path
passes the same if the mechanism is removed — it proves nothing, and its cost is giving someone the
feeling of being covered. It was one of them that found, while this text was being written, that
pointing the forge at a nonexistent path returned *"your spec is wrong"* instead of *"I read nothing"*.

---

## License

MIT. If the criterion is that anyone can read, understand and apply it, a license that excludes
someone has already failed the criterion.
