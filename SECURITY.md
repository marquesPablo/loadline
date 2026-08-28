# Security

## Reporting a vulnerability

Use GitHub's **[private vulnerability reporting](https://github.com/marquesPablo/loadline/security/advisories/new)**
(the "Report a vulnerability" button on the Security tab). Do not open a public issue for anything
that could be exploited before a fix is out.

You should get a first response within a week. If a fix is warranted, the advisory is published
together with the release that carries it — coordinated, not surprise.

## What counts

This tool is meant to run offline, against a repository, with no network and no API key. The
failure modes that matter:

- **A guard that fails open.** `forja` compiles an agent spec into a `PreToolUse` hook that is
  supposed to *deny* under some condition. A spec that compiles to a hook which allows what it
  should block — or crashes in a way the harness reads as "allow" — is a vulnerability, not a bug.
- **Path traversal.** The `cerebro-local` operation ships a read-only MCP server. A request that
  escapes the served root (`../`, a symlink, an absolute path) reading a file it should not is in
  scope. So is any probe that can be pointed outside the target it was given.
- **Injection through a template.** `forja` writes hooks, `agente.toml` files and golden sets from
  spec fields. A spec field that reaches a shell, a Python `eval`, or the generated hook's control
  flow is in scope.
- **A probe that phones home.** Any code path that opens a network connection, since the whole
  contract is that there is none.

## What does not count

- The tool reporting a wrong answer that is not exploitable — that is a normal bug, open an issue.
- Findings that require you to already have write access to the repository being scanned, or to the
  machine running the scan.
- The deliberately-bad `exemplos/roster-de-exemplo/` — it exists to be flagged.

## Supported versions

Pre-1.0. Only the latest release (and `main`) gets fixes.
