"""The emission targets — a spec goes in, seven artifacts come out.

nature: fix — this module only formats text from an ALREADY validated spec.
The one that blocks is `spec.validar`; here, an exception is a formatting
defect and shows up in full instead of turning into a half-written artifact.

    .claude/agents/<slug>.md   Claude Code subagent (frontmatter + prompt)
    AGENTS.md                  the harness-agnostic format
    <slug>.system.md           raw system prompt, for an SDK or a custom harness
    hooks/cerca_<slug>.py      the PreToolUse guard, which FAILS CLOSED
    golden/<slug>.md           the golden set, with the derivation rule
    LACUNAS.md                 what this agent does not measure
    RECEITA.md                 what was emitted, from which spec, when

What sets this apart from a prompt generator: **three of the seven are not text
for the model to read.** The hook is code that runs before the tool and denies;
the golden set is the question that checks the ANSWER; the gaps are the absence
with an owner. A nice prompt without those three is an ungated agent with a
better description.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from . import vacina
from .spec import ESCRITA, EXECUCAO, REDE, Spec


def _lista_md(itens: list[str], marca: str = "-") -> str:
    return "\n".join(f"{marca} {x}" for x in itens) if itens else "_(none)_"


def _data_da_spec(spec: Spec) -> date:
    """The spec's last-write date. Stable while the spec does not change."""
    try:
        return date.fromtimestamp(Path(spec.origem).stat().st_mtime)
    except (OSError, ValueError):
        return date.today()


def _fronteira_em_prosa(spec: Spec) -> list[str]:
    L = []
    if spec.usa_rede:
        alvos = ", ".join(f"`{d}`" for d in (spec.dominios_permitidos or []))
        if spec.dominios_permitidos == ["nenhum"]:
            L.append(
                "- **Network: BLOCKED always.** This spec declares `nenhum`, and the guard denies "
                "every outbound call, no exception."
            )
        else:
            L.append(
                f"- **Network: {alvos} only.** Any other domain is denied by the guard before "
                "the call goes out — including a subdomain that looks obvious."
            )
    if spec.usa_escrita:
        alvos = ", ".join(f"`{c}`" for c in (spec.saida_cercada or []))
        L.append(
            f"- **Write: only under {alvos}.** The guard compares the REAL path (resolving "
            "link and junction) — writing outside that is denied, not warned."
        )
    if spec.usa_execucao:
        L.append(
            "- **Execution:** this spec asks for a shell. Every command goes into the run log, "
            "with the exact argv."
        )
    if spec.toca_alvo:
        L.append(
            f"- **Touches an external target.** Requires valid authorization in `{spec.autorizacao}`, with "
            "target, scope, authorization and validity. **A command outside the authorized target is "
            "an incident, not a finding.**"
        )
    if spec.desconhecidas:
        L.append(
            "- ⚠️ **Tools outside the known vocabulary:** "
            + ", ".join(f"`{f}`" for f in spec.desconhecidas)
            + ". The guard **cannot classify them** and so does not fence them. This is "
            "written here instead of staying silent."
        )
    if not L:
        L.append("- Read-only. This spec asks for no network, write or shell.")
    return L


# ---------------------------------------------------------------- prompt ----
def corpo_do_prompt(spec: Spec) -> str:
    """The core every target shares — what the model reads."""
    return f"""# {spec.nome}

{spec.uma_frase}

## Use this agent when

{_lista_md(spec.usar_quando)}

## NEVER use this agent for

{_lista_md(spec.nunca_usar)}

> The anti-description is not politeness, it is mechanism. An orchestrator that
> only reads what the agent DOES dispatches by topic similarity, and the wrong
> agent answers with confidence about what is not its job.

## Your boundary

{chr(10).join(_fronteira_em_prosa(spec))}

**The boundary above does not depend on you obeying it.** It is implemented in
`hooks/cerca_{spec.slug.replace("-", "_")}.py`, which runs BEFORE the tool and denies.
If you try to step outside it, the call does not happen — and the refusal carries the fix written out.

## What you do NOT measure

{_lista_md(spec.lacunas)}

When a question falls into one of these, **say you do not measure it** and say who does.
Filling a gap with plausibility is the defect this section exists to prevent.

## How you answer

- **Verify before you assert.** Run it, read the file, check the output. If you
  did not verify, say you did not verify. If you did not find it, write **"not found"**.
- **Declare the denominator.** Every time you count something, say out of how many.
  A filter that skips silently returns a plausible, empty answer.
- **Absolute dates** (`YYYY-MM-DD`), never "last week" — the reader of your answer
  does not know when you wrote it.
- Cite `path:line` for everything you assert about the disk.

{vacina.paragrafo(spec.idioma)}"""


# --------------------------------------------------------------- targets ------
def claude_code(spec: Spec) -> tuple[str, str]:
    """Claude Code subagent: frontmatter + prompt in the body."""
    descricao = (
        f"{spec.uma_frase} "
        + (f"Use when: {'; '.join(spec.usar_quando)}. " if spec.usar_quando else "")
        + f"NEVER use for: {'; '.join(spec.nunca_usar)}."
    ).replace("\n", " ")
    frontmatter = "\n".join(
        [
            "---",
            f"name: {spec.slug}",
            f"description: {json.dumps(descricao, ensure_ascii=False)}",
            f"tools: {', '.join(spec.ferramentas)}" if spec.ferramentas else "tools:",
            "---",
            "",
        ]
    )
    return f".claude/agents/{spec.slug}.md", frontmatter + corpo_do_prompt(spec)


def agents_md(spec: Spec) -> tuple[str, str]:
    """`AGENTS.md` — the format no harness owns."""
    return "AGENTS.md", (
        f"# AGENTS.md — {spec.nome}\n\n"
        "> This file is read by harnesses that are not Claude Code. It says the same\n"
        "> thing as `.claude/agents/`, on purpose: an agent whose boundary changes from\n"
        "> harness to harness has no boundary, it has luck.\n\n"
        + corpo_do_prompt(spec)
    )


def system_prompt(spec: Spec) -> tuple[str, str]:
    """Raw system prompt, for an SDK or a custom harness."""
    return f"{spec.slug}.system.md", corpo_do_prompt(spec)


def hook(spec: Spec) -> tuple[str, str]:
    """The `PreToolUse` guard, generated from the declared boundary. Fails CLOSED."""
    sub = spec.slug.replace("-", "_")
    config = json.dumps(
        {
            "slug": spec.slug,
            "rede": sorted(REDE),
            "escrita": sorted(ESCRITA),
            "dominios_permitidos": spec.dominios_permitidos or [],
            "saida_cercada": spec.saida_cercada or [],
        },
        ensure_ascii=False,
        indent=4,
    )
    corpo = '''"""PreToolUse guard for `%(slug)s` — GENERATED by the forge, do not edit by hand.

nature: security — every exception BLOCKS. What this guard cannot decide, it
denies: a guard that opens up when it breaks is not a guard, and the moment it
breaks is exactly the moment someone is trying to get through.

Install it as `PreToolUse` in the harness settings. It reads the event as JSON
on stdin and answers in the permission-decision format.

⚠️ **Narrow jurisdiction, and it is declared.** This guard only acts when it
can identify the agent — by the event's `agent_type` or by the `FORJA_AGENTE`
environment variable. A main session with no subagent stays under whatever the
harness already did. This is NOT fail-open: it is the guard saying whose it is.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

CONFIG = %(config)s


def _negar(motivo: str, conserto: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"{motivo}\\n\\nFix: {conserto}",
                }
            }
        )
    )
    raise SystemExit(0)


def _sou_eu(evento: dict) -> bool:
    identidade = evento.get("agent_type") or os.environ.get("FORJA_AGENTE") or ""
    return identidade == CONFIG["slug"]


def _cobre(host: str, permitido: str) -> bool:
    """`api.github.com` falls under `github.com`; `github.com.mau.site` does NOT.

    The comparison is by domain label, never by string `endswith` —
    `endswith` lets through exactly the forged suffix the attacker chooses.
    """
    host, permitido = host.lower().strip("."), permitido.lower().strip(".")
    return host == permitido or host.endswith("." + permitido)


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except Exception:
        _negar(
            "the hook event could not be read",
            "this is fail-closed on purpose — a guard that does not understand the request denies",
        )
        return 0

    if not _sou_eu(evento):
        return 0

    ferramenta = evento.get("tool_name", "")
    entrada = evento.get("tool_input", {}) or {}

    if ferramenta in CONFIG["rede"]:
        permitidos = CONFIG["dominios_permitidos"]
        if not permitidos or permitidos == ["nenhum"]:
            _negar(
                f"`{CONFIG['slug']}` has no allowed domain at all; network output is blocked.",
                'declare `dominios_permitidos` in the spec and recompile with `python -m forja`',
            )
        alvo = entrada.get("url") or ""
        hosts = [urlparse(alvo).hostname or ""] if alvo else list(entrada.get("allowed_domains") or [])
        if not hosts or not any(h for h in hosts):
            _negar(
                f"could not extract a domain from `{ferramenta}`.",
                "a network call with no readable target is denied — the guard does not guess a destination",
            )
        for h in hosts:
            if not any(_cobre(h, d) for d in permitidos):
                _negar(
                    f"`{h}` is outside `dominios_permitidos` for `{CONFIG['slug']}`: {permitidos}",
                    "add the domain to the spec and recompile, or use another source",
                )

    if ferramenta in CONFIG["escrita"]:
        cercas = CONFIG["saida_cercada"]
        if not cercas:
            _negar(
                f"`{CONFIG['slug']}` does not declare `saida_cercada`; every write is blocked.",
                "declare `saida_cercada` in the spec and recompile",
            )
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or ""
        if not alvo:
            _negar(
                f"`{ferramenta}` with no readable path.",
                "a write with no readable destination is denied — the guard does not guess a path",
            )
        try:
            real = Path(alvo).resolve()
            permitido = any(
                real == Path(c).resolve() or Path(c).resolve() in real.parents for c in cercas
            )
        except OSError:
            permitido = False
        if not permitido:
            _negar(
                f"`{alvo}` is outside `saida_cercada` for `{CONFIG['slug']}`: {cercas}",
                "write under one of the declared paths, or change the spec and recompile",
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''' % {"slug": spec.slug, "config": config}
    return f"hooks/cerca_{sub}.py", corpo


def golden(spec: Spec) -> tuple[str, str]:
    """The golden set — the only surface that asks whether the ANSWER is right."""
    L = [
        f"# Golden set — `{spec.slug}`",
        "",
        "> Every expected answer here was written **by hand, reading the disk**. If it comes",
        "> from a call to the agent itself, the case is a mirror check: both sides come from",
        "> the same source, the pair passes green and **locks** the defect in instead of finding it.",
        "",
        f"**{len(spec.golden)} case(s).** Coverage is not gated on purpose: a coverage gate",
        "pushes toward a weak case, and a weak case is worse than a missing one.",
        "",
    ]
    for i, caso in enumerate(spec.golden, start=1):
        L += [
            f"## G{i:02d}",
            "",
            f"**Question:** {caso.pergunta}",
            "",
            f"**Expected answer:** {caso.esperado}",
            "",
            f"**Derived from:** `{caso.derivado_de}` — outside the agent's output.",
            "",
        ]
    return f"golden/{spec.slug}.md", "\n".join(L)


def lacunas(spec: Spec) -> tuple[str, str]:
    """What the agent does not measure — absence with an owner, not silence."""
    return "LACUNAS.md", (
        f"# What `{spec.slug}` does NOT measure\n\n"
        "> An absence leaves no trace. A question the agent does not answer produces\n"
        "> no object for anyone to inspect — it only produces a plausible answer.\n"
        "> That is why it is written here, and why the forge refuses to compile without this list.\n\n"
        f"{_lista_md(spec.lacunas)}\n\n"
        "## How to close one of these\n\n"
        "Do not delete the line. Write next to it **who** started measuring it and **where** —\n"
        "a check, another agent, a human with a name. A gap that disappears with no owner comes back silent.\n"
    )


def receita(spec: Spec, emitidos: list[str], hoje: date | None = None) -> tuple[str, str]:
    """The run's recipe — from which spec came what, and when.

    ⚠️ The date is the SPEC's, not today's. Stamping today would make the
    artifact change by itself at midnight and `--conferir` would flag it as
    "stale" with nobody having touched anything — an alarm that only knows how
    to fire by the passage of time is noise, and noise trains whoever reads it
    to ignore it.
    """
    hoje = hoje or _data_da_spec(spec)
    L = [
        f"# Recipe — `{spec.slug}`",
        "",
        f"<!-- measured: forja.artefatos={len(emitidos)} nature=count "
        f"on={hoje.isoformat()} expires=never source={spec.origem} -->",
        "",
        f"- **Source spec:** `{spec.origem}`",
        f"- **Emitted on:** {hoje.isoformat()}",
        f"- **Tools granted:** {', '.join(spec.ferramentas) or '_(none)_'}",
        f"- **Idea-virus vaccine:** present in every prompt artifact — `{vacina.FONTE}`",
        "",
        "## Artifacts emitted",
        "",
        *(f"- `{caminho}`" for caminho in emitidos),
        "",
        "## What this recipe does NOT prove",
        "",
        "- **That the agent is good.** The forge verifies that the boundary exists, is",
        "  executable and fails closed. Whether the agent answers well is what the golden set",
        "  says, and it was written by whoever wrote the spec.",
        "- **That the gap list is complete.** It is declared, not measured.",
        "- **That the hook is installed.** Emitting the guard and registering it in the harness",
        "  are two things, and the second is yours — it is written in `RECEITA.md` so it does not disappear.",
        "",
    ]
    if spec.desconhecidas:
        L += [
            "## ⚠️ Tools the guard does not classify",
            "",
            *(f"- `{f}`" for f in spec.desconhecidas),
            "",
            "They were granted and are **not fenced** — the guard does not know whether they are",
            "network, write or read. This is printed instead of staying silent.",
            "",
        ]
    return "RECEITA.md", "\n".join(L)


TODOS = (claude_code, agents_md, system_prompt, hook, golden, lacunas)
