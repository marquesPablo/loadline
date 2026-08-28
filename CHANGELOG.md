<!-- loadline-ignore-file: a changelog is a list of version numbers, not claims about the repository now. -->

# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project aims to follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing released yet. This section is what the first tagged release will carry.

### Added

- `loadline` — the claim × seal engine: reads `measured:` / `frozen:` / `arbitrated:` seals in your
  files and answers whether the number next to each one still matches what a probe recomputes today.
- `forja` — the agent roster survey (reads a whole `.claude/agents/` folder and finds what only
  shows up from the third agent on) and the spec compiler that turns one `agente.toml` into the
  hooks, golden set and gap file, with eight refusals that fail closed.
- `placar` — the seven gates of "would you ship this AI agent?", each checked against disk evidence.
- `blind` — the junction / gitignore boundary that a naive recursive scan crosses without an error.
- `vitrine` — the skill-window auditor (eleven rules over `SKILL.md`, no model call), and a
  `--harvest` mode that refuses to create a redundant skill instead of auditing the redundancy
  afterward.
- `censo` — a census of the AI-agent ecosystem, generated from a JSON source that fails the build
  when it drifts.
- `evidencia` — a self-contained HTML report per tool.
- `action.yml` — a composite GitHub Action that runs the three tools against the caller's repository.
- `vendorizado/forja.py` — the survey as a single file, downloadable with `curl -O`, zero
  dependencies.
- `operacoes/` — seven ready-made operations, each a whole job pre-assembled (probes, seals, gated
  agent, CI job).
- `comunidade/` — the contribution mechanism for domain probes.

[Unreleased]: https://github.com/marquesPablo/loadline/commits/main
