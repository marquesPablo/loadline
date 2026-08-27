# What `placar` does NOT measure

> The same third list the root `LACUNAS.md`, `vitrine` and `blind` publish. Seven gates that answer
> "is there evidence?" are not seven gates that answer "is this well done?" — and it is this list
> that marks the border between the two.

## 1 · Every gate is the ABSENCE OF A DECLARATION, never a judgment of quality

The same contract as `vistoria` (`forja/vistoria.py`): a gate accuses when it finds no
machine-readable evidence — it never decides whether the evidence found is the right one. A
`PreToolUse` that denies for a wrong reason passes `APPROVAL`. A decision record full of dates and
empty of substance passes `TRACEABILITY`. **`placar` proves the piece exists, not that it works.**

## 2 · `OBJECTIVE` and `FAILURE` are word searches, and the list is CHOSEN

`MARCAS_OBJECTIVE` and `MARCAS_FAILURE` (`placar/portas.py`) are collected vocabulary, not normative.
An agent that declares a budget with a word outside the list comes out as FAIL. Finding a synonym
would need a model — and a verifier that depends on a model is not a verifier, it is a second opinion.

## 3 · `IDENTITY` is seven REAL patterns, not an entropy scanner

Seven known credential formats (AWS, GitHub, Slack, Anthropic, OpenAI, Google, a PEM private key).
It does **not** cover: a generic secret with no recognizable prefix, an internal-service credential,
a hash that looks like a key but is not, or the inverse — high-entropy text that IS a secret but
matches none of the seven formats. This is a floor, not a full `gitleaks`/`trufflehog`, and the
placeholder exclusion list (`_PLACEHOLDER`) may let through a real secret whose variable name
contains one of the list's words (`API_KEY_EXAMPLE_PROD = "sk-ant-..."`, for example).

## 4 · `IDENTITY` does not look at the git HISTORY

A secret removed from today's file and still alive in `git log -p` is not found. `placar` reads the
current disk, never the commit tree — the same boundary `blind` already declares for itself.

## 5 · `AUTHORITY` with no roster is weaker than `AUTHORITY` with a roster

With `.claude/agents/`, the gate reuses `V3`/`V7` from `vistoria` — per agent, with a name. With no
roster (a single-agent harness, or no agents folder), it falls back to a coarser question: *is there
any `PreToolUse` covering write and any covering network/execution, in the whole harness?* It cannot
say WHICH tool was left unfenced — only whether there is coverage or not.

## 6 · `APPROVAL` reads the SCRIPT, never RUNS the hook

The gate looks, in the text of the file referenced by `PreToolUse`, for the markers Claude Code
actually uses to deny (`permissionDecision: deny`, `decision: block`, `sys.exit(2)`). It does not
invoke the hook with a synthetic event and check the output — a script that contains the string
`"deny"` inside a comment, never executed, would pass. And a hook written in a language without those
three marks (Node with `process.exit(1)`, for example, which also blocks in Claude Code) may be
left without credit: `_MARCA_EXIT2` covers `process.exit(2)`, but not every non-zero exit code the
tool accepts.

## 7 · `TRACEABILITY` does not really verify APPEND-ONLY

The original proposal asks for "a record present, append-only, dated". `placar` checks presence and
date. It does **not** check append-only — that would need scanning `git log` per file for a removal
or a destructive edit of an old entry, and that was not built this round. A decision record that is
edited and rewritten over itself passes the same as one that only grows.

## 8 · `CONTAINMENT` is the weakest of the seven, and it is so on purpose

The search for `\bR[0-4]\b` near a reversibility word is the LEAST specific pattern in the module —
it will get it wrong both ways. **The R0–R4 rule itself is borrowed** from a source outside the
majority ecosystem; most repositories in the world use NO similar vocabulary, even while actually
having a reversibility mechanism (a documented `git revert`, a feature flag). This makes
`CONTAINMENT` fail the vast majority of real repositories today — **and that is the correct reading
of the proposal**: it is the rarest gate to pass, because it is the least practiced in the ecosystem.

Measured this round: the `loadline` repository itself **has no agent harness at the root**
(`python -m placar .` returns exit 2 — no `CLAUDE.md`/`AGENTS.md`/`.claude/`, because this repository
IS the tool, not a configured agent). Against `exemplos/roster-de-exemplo/` — the same fixture the
`forja` README uses — placar fails 6 of the 7 gates, and `CONTAINMENT` is one of them: none of the
four example agents classifies reversibility. `IDENTITY` is the only one that passes clean. This is
not published in the `README.md` — the `README.md` is deliberately short, and a full `placar` run
does not fit it without competing with the `forja` example, which is the front door.

## 9 · No gate is dynamic

`placar` reads a file at rest. It does not run the agent, does not watch the hook actually being
called by the harness, and does not know whether the `PreToolUse` is actually registered in the
place Claude Code reads (a malformed `settings.json` that the harness parser silently rejects would
pass here, because `json.loads` can read what Claude Code would refuse). The same boundary the root
`LACUNAS.md` already declares for `vistoria`, generalized to the seven gates.

## 10 · The 4,000-files-per-scan ceiling is CHOSEN, not measured

`_arquivos_de_texto` stops reading after 4,000 files (2,000 for `TRACEABILITY`) — a giant monorepo
may have a secret or a decision record outside the read window. **The cut itself is declared in the
report** (see the "Closed" item below); what is still open is only the NUMBER of the ceiling, which
was chosen not to hang, not measured against a real repository of that size.

## Closed

- **`_arquivos_de_texto` cut silently on hitting the ceiling** — closed in the same round it was
  born, before the first commit. `IDENTITY`, `TRACEABILITY` (the branch with no dedicated decision
  folder) and `CONTAINMENT` now receive `(files, truncated, skipped)` and print the warning in the
  `resumo` when the cut happened. It was exactly the trap the code's own comment cited (`rg` without
  `-L`) — leaving it standing would have been the tool that preaches honesty being dishonest about
  itself.
- **The file scan crossed a junction/symlink without warning** — closed in the same round. A
  careless `os.walk` descends into a Windows reparse point anyway (the same cause 1 `blind` measured).
  `_arquivos_de_texto` now PRUNES a junction and a directory symlink before descending, and the
  report names how many boundaries were skipped, pointing at `python -m blind` as the command that
  shows what is behind them. Without this, running `placar` at the root of a repository with a
  junction to external content (this `loadline` ecosystem itself lives next to a junction-mounted
  knowledge base) would read — and could report a secret from — a tree the declared target did not
  know it reached.
