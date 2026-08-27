# What `blind` does NOT measure

> The same third list the root `LACUNAS.md` and `vitrine` publish. Almost every
> tool says what passed and what failed; few say what they never looked at —
> and it is that list that decides whether `blind`'s silence means anything.

## 1 · Two named causes, and only those two

<!-- measured: blind.causas=2 nature=count on=2026-08-26 expires=never source=blind/limites.py -->

`blind` knows how to look for a reparse point (junction/symlink) and a
`.gitignore` rule inside a real git repository. It does **not** look for:

- **A git submodule** (`.gitmodules`) — named in the original proposal, not
  implemented this round. A submodule with a `CLAUDE.md` inside it escapes.
- **`.ignore`/`.rgignore`** — ripgrep respects both on top of `.gitignore`,
  even outside a git repository. Not read here.
- **`.git/info/exclude`** and the **global** gitignore (`core.excludesFile`) —
  an exclusion rule that does not live in a versioned `.gitignore` is not seen.
- **A monorepo boundary** (a pnpm/Bazel/Nx workspace pointing outside the tree)
  — named in the proposal, not measured: there is no single format to detect by
  parser.
- **A FILE symlink**, only a directory one. A `CLAUDE.md` that is itself a
  symlink to somewhere else is not found.

## 2 · The `.gitignore` parser is a floor, not the spec

It covers a plain name, a leading `/` (anchored to the folder of the
`.gitignore` itself), a trailing `/` (directory only) and a wildcard via
`fnmatch`. It does **not** cover: negation (`!pattern`), `**`, a character class
`[abc]`, or the precedence between nested `.gitignore`s (a deeper `.gitignore`
that reverts the parent's rule). A pattern using any of these may match wrong —
a false positive or a false negative, with no warning.

## 3 · The "declaration file" list is CHOSEN, not normative

`CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `agent.toml`, `settings.json`, plus
anything under a `.claude/` folder. It is the list of names today's harnesses
use — **not** a format standard. A harness that invents another
instruction-file name is not recognized here.

<!-- measured: blind.declaracao=5 nature=count on=2026-08-23 expires=never source=blind/limites.py -->

## 4 · `blind` does not prove what YOUR tool does

It inventories the boundary and simulates the two causes measured here (rg,
Python `os.walk`/`rglob`). It does **not run** your `grep`, your IDE indexer or
your CI crawler against the target — it does not know whether THEY specifically
see the boundary. It answers *"there is a boundary here that IS KNOWN to fool a
non-aware tool"*, not *"your tool X specifically failed just now"*.

## 5 · A symlink cycle was not stress-tested

A symlink pointing at an ancestor of itself (a cycle) is not explicitly
prevented — the `_reparse_points` scan stack does not descend INTO the boundary
it finds (it scans to inventory, not to walk again via the main stack), which
avoids the common case, but no directed test was built for the cycle.

## 6 · Built and tested only on Windows, this session

Junction detection uses `os.path.isjunction` (Python ≥ 3.12) with a fallback to
the reparse tag `0xA0000003`, and the five negative controls
(`blind/controles.py`) run `mklink /J`. `os.path.islink` (the symlink branch,
for POSIX) is written code and has no directed negative control this round —
**named, not verified**.

## 7 · It does not judge whether the boundary should exist

A junction is often a legitimate decision — it is how a knowledge base links
vaults. `blind` never says "remove this"; it says "this exists, and here is
what a naive scan would not see behind it". The decision about whether the
boundary is appropriate stays with whoever reads the report.
