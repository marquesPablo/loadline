"""`placar` negative controls — every gate is seen FAILING and PASSING.

    python -m placar.controles

A verifier that has never been seen accusing is worth nothing: it may be quiet
because the world is clean, or because it does not look. Each control builds a
REAL synthetic repository (real frontmatter, real `settings.json`, real
junction via `mklink /J`), runs the gate, and requires the expected verdict —
it fails when it should, and goes quiet when the defect is gone.

Fails with exit 1. No dependency, no network, no model.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .portas import avaliar


def _escrever(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def _agente(nome: str, tools: str = "Read", extra: str = "") -> str:
    return (
        "---\n"
        f"name: {nome}\n"
        f'description: "does {nome}"\n'
        f"tools: {tools}\n"
        "---\n"
        f"{extra}\n"
    )


def _por_id(alvo: Path, porta_id: str):
    p = avaliar(alvo)
    assert p is not None, f"avaliar({alvo}) returned None — no harness detected"
    for porta in p.portas:
        if porta.id == porta_id:
            return porta
    raise KeyError(porta_id)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover
        pass

    falhas: list[str] = []
    print("placar negative controls")
    print("=" * 74)

    def checar(rotulo: str, ok: bool, msg_falha: str = "") -> None:
        print(f"  {'ok   ' if ok else 'FAIL '} {rotulo}")
        if not ok:
            falhas.append(f"{rotulo}: {msg_falha or 'condition did not hold'}")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        # --- C1: OBJECTIVE fails with no mark, passes with `kill_criteria` ---
        r1 = base / "c1"
        _escrever(r1 / ".claude/agents/a.md", _agente("a"))
        c1a = _por_id(r1, "OBJECTIVE")
        _escrever(r1 / ".claude/agents/a.md", _agente("a", extra="kill_criteria: stop when done"))
        c1b = _por_id(r1, "OBJECTIVE")
        checar("C1   OBJECTIVE fails with no stop/budget mark", c1a.grave, "did not fail with no mark")
        checar("C1   OBJECTIVE passes with kill_criteria declared", not c1b.grave, "kept failing with the mark present")

        # --- C2: IDENTITY fails on a real secret, does not false-positive a placeholder ---
        r2 = base / "c2"
        _escrever(r2 / "CLAUDE.md", "# project\n")
        _escrever(r2 / "config.py", 'AWS_KEY = "AKIAABCDEFGHIJKLMNOP"\n')
        c2a = _por_id(r2, "IDENTITY")
        _escrever(r2 / "config.py", 'AWS_KEY = os.environ["AWS_KEY"]  # example: AKIAXXXXXXXXXXXXXXXX\n')
        c2b = _por_id(r2, "IDENTITY")
        checar("C2   IDENTITY fails on a real AWS key in the clear", c2a.grave, "did not find the literal AKIA...")
        checar("C2   IDENTITY does not false-positive an env var + placeholder", not c2b.grave, "flagged an env var reference")

        # --- C3: AUTHORITY (with roster) fails on V3/V7, passes with a boundary ---
        r3 = base / "c3"
        _escrever(r3 / ".claude/agents/w.md", _agente("w", tools="Write"))
        c3a = _por_id(r3, "AUTHORITY")
        _escrever(r3 / ".claude/agents/w.md", _agente("w", tools="Write", extra="writes only to build/"))
        c3b = _por_id(r3, "AUTHORITY")
        checar("C3   AUTHORITY fails on a Write agent with no declared fence", c3a.grave and c3a.forca_no_go, "did not fail, or is not NO-GO")
        checar("C3   AUTHORITY passes when the write fence is declared", not c3b.grave, "kept failing with the fence present")

        # --- C4: AUTHORITY with no roster falls back to PreToolUse coverage ---
        r4 = base / "c4"
        _escrever(r4 / "AGENTS.md", "# no agent roster\n")
        c4a = _por_id(r4, "AUTHORITY")
        settings4 = {
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "true"}]},
                    {"matcher": "Bash|WebFetch", "hooks": [{"type": "command", "command": "true"}]},
                ]
            }
        }
        _escrever(r4 / ".claude/settings.json", json.dumps(settings4))
        c4b = _por_id(r4, "AUTHORITY")
        checar("C4   AUTHORITY with no roster fails with no write/network PreToolUse", c4a.grave, "did not fail with no hooks")
        checar("C4   AUTHORITY with no roster passes with both matchers covered", not c4b.grave, "kept failing with the hooks present")

        # --- C5: FAILURE passes with a timeout OR a word, fails with neither ---
        r5 = base / "c5"
        _escrever(r5 / "CLAUDE.md", "# project with nothing\n")
        c5a = _por_id(r5, "FAILURE")
        settings5 = {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "true", "timeout": 10}]}]}}
        _escrever(r5 / ".claude/settings.json", json.dumps(settings5))
        c5b = _por_id(r5, "FAILURE")
        checar("C5   FAILURE fails with no timeout and no retry/fallback", c5a.grave, "did not fail on empty")
        checar("C5   FAILURE passes with a `timeout` declared on the hook", not c5b.grave, "kept failing with the timeout present")

        # --- C6/C7: APPROVAL fails with no PreToolUse, passes with deny, fails without the mark ---
        r6 = base / "c6"
        _escrever(r6 / "CLAUDE.md", "# project\n")
        c6a = _por_id(r6, "APPROVAL")
        _escrever(r6 / "hooks/nega.py", 'print(\'{"hookSpecificOutput": {"permissionDecision": "deny"}}\')\n')
        settings6 = {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "python hooks/nega.py"}]}]}}
        _escrever(r6 / ".claude/settings.json", json.dumps(settings6))
        c6b = _por_id(r6, "APPROVAL")
        _escrever(r6 / "hooks/nega.py", "print('ok')\n")
        c6c = _por_id(r6, "APPROVAL")
        checar("C6   APPROVAL fails with no PreToolUse at all", c6a.grave, "did not fail with no hook")
        checar("C6   APPROVAL passes with a script that emits permissionDecision=deny", not c6b.grave, "kept failing with the fail-closed script")
        checar("C7   APPROVAL fails again when the script loses the deny mark", c6c.grave, "did not start failing again")

        # --- C8/C9: TRACEABILITY passes with a dated record, or with PostToolUse alone ---
        r8 = base / "c8"
        _escrever(r8 / "CLAUDE.md", "# project\n")
        c8a = _por_id(r8, "TRACEABILITY")
        _escrever(r8 / "decisoes/ADR-001-primeira.md", "date: 2026-08-23\n\n# decision\n")
        c8b = _por_id(r8, "TRACEABILITY")
        checar("C8   TRACEABILITY fails with no decision record and no PostToolUse", c8a.grave, "did not fail on empty")
        checar("C8   TRACEABILITY passes with a dated ADR", not c8b.grave, "kept failing with the ADR present")

        r9 = base / "c9"
        _escrever(r9 / "CLAUDE.md", "# project\n")
        settings9 = {"hooks": {"PostToolUse": [{"hooks": [{"type": "command", "command": "true"}]}]}}
        _escrever(r9 / ".claude/settings.json", json.dumps(settings9))
        c9 = _por_id(r9, "TRACEABILITY")
        checar("C9   TRACEABILITY passes with an auditing PostToolUse alone, no decision folder", not c9.grave, "failed even with PostToolUse configured")

        # --- C10: CONTAINMENT passes with R0-R4 near a reversibility word ---
        r10 = base / "c10"
        _escrever(r10 / "CLAUDE.md", "# project\n")
        c10a = _por_id(r10, "CONTAINMENT")
        _escrever(r10 / "acoes.py", "# R3 requires human approval before any irreversible action\n")
        c10b = _por_id(r10, "CONTAINMENT")
        checar("C10  CONTAINMENT fails with no reversibility classification", c10a.grave, "did not fail on empty")
        checar("C10  CONTAINMENT passes with R3 near 'irreversible'", not c10b.grave, "kept failing with the classification present")

        # --- C11: a junction is pruned - a secret behind it does not appear ---
        r11 = base / "c11"
        alvo11 = base / "c11-atras"
        _escrever(r11 / "CLAUDE.md", "# project\n")
        _escrever(alvo11 / "segredo.py", 'K = "AKIAZZZZZZZZZZZZZZZZ"\n')
        link11 = r11 / "vinculo"
        link11.parent.mkdir(parents=True, exist_ok=True)
        criou11 = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link11), str(alvo11)],
            capture_output=True, text=True, stdin=subprocess.DEVNULL,
        ).returncode == 0
        if criou11:
            c11 = _por_id(r11, "IDENTITY")
            achou_atras = any("segredo.py" in item for item in c11.itens)
            avisou = "boundary" in c11.resumo.lower() or "junction" in c11.resumo.lower()
            try:
                os.rmdir(link11)
            except OSError:
                pass
            checar("C11  IDENTITY does NOT read what is behind a junction", not achou_atras, "found the secret behind the junction - crossed it silently")
            checar("C11  IDENTITY warns that a boundary was skipped", avisou, "did not name the skipped boundary in the summary")
        else:
            falhas.append("C11: could not create a real junction (mklink /J failed) - control could not run")
            print("  FAIL  C11  junction could not be created in this environment")

        # --- C12: with no harness at all, avaliar() returns None ---
        r12 = base / "c12-vazio"
        _escrever(r12 / "README.md", "no harness here\n")
        c12 = avaliar(r12)
        checar("C12  avaliar() returns None with no CLAUDE.md/AGENTS.md/.claude", c12 is None, f"returned {c12!r}")

        # --- C13: NO-GO only fires for IDENTITY/AUTHORITY/CONTAINMENT ---
        r13 = base / "c13"
        _escrever(r13 / ".claude/agents/a.md", _agente("a", extra="kill_criteria: x"))
        p13 = avaliar(r13)
        assert p13 is not None
        so_failure_falha = all(
            (not porta.grave) or porta.id == "FAILURE" for porta in p13.portas
        )
        checar(
            "C13  NO-GO does not fire when only FAILURE/TRACEABILITY fail",
            not p13.no_go or not so_failure_falha,
            "no_go=True even with no IDENTITY/AUTHORITY/CONTAINMENT failing",
        )

    print("-" * 74)
    if falhas:
        for f in falhas:
            print(f"  ⛔ {f}")
        print(f"\nFAIL — {len(falhas)} control(s)                                       (exit 1)")
        return 1
    print("PASS — every gate was seen accusing AND going quiet        (exit 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
