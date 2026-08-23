"""Controles negativos do `placar` — cada porta é vista REPROVANDO e PASSANDO.

    python -m placar.controles

Um verificador que nunca foi visto acusar não vale nada: ele pode estar
quieto porque o mundo está limpo, ou porque ele não olha. Cada controle
monta um repositório sintético DE VERDADE (frontmatter real, `settings.json`
real, junction real via `mklink /J`), roda a porta, e exige o veredito
esperado — reprova quando devia, e cala quando o defeito some.

Reprova com exit 1. Sem dependência, sem rede, sem modelo.
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
        f'description: "faz {nome}"\n'
        f"tools: {tools}\n"
        "---\n"
        f"{extra}\n"
    )


def _por_id(alvo: Path, porta_id: str):
    p = avaliar(alvo)
    assert p is not None, f"avaliar({alvo}) devolveu None — sem harness detectado"
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
    print("controles negativos do placar")
    print("=" * 74)

    def checar(rotulo: str, ok: bool, msg_falha: str = "") -> None:
        print(f"  {'ok  ' if ok else 'FALHA'} {rotulo}")
        if not ok:
            falhas.append(f"{rotulo}: {msg_falha or 'condição não bateu'}")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        # --- C1: OBJECTIVE reprova sem marca, passa com `kill_criteria` ---
        r1 = base / "c1"
        _escrever(r1 / ".claude/agents/a.md", _agente("a"))
        c1a = _por_id(r1, "OBJECTIVE")
        _escrever(r1 / ".claude/agents/a.md", _agente("a", extra="kill_criteria: para quando acabar"))
        c1b = _por_id(r1, "OBJECTIVE")
        checar("C1   OBJECTIVE reprova sem marca de parada/orçamento", c1a.grave, "não reprovou sem marca")
        checar("C1   OBJECTIVE passa com kill_criteria declarado", not c1b.grave, "continuou reprovando com a marca presente")

        # --- C2: IDENTITY reprova segredo real, não falso-positiva placeholder ---
        r2 = base / "c2"
        _escrever(r2 / "CLAUDE.md", "# projeto\n")
        _escrever(r2 / "config.py", 'AWS_KEY = "AKIAABCDEFGHIJKLMNOP"\n')
        c2a = _por_id(r2, "IDENTITY")
        _escrever(r2 / "config.py", 'AWS_KEY = os.environ["AWS_KEY"]  # example: AKIAXXXXXXXXXXXXXXXX\n')
        c2b = _por_id(r2, "IDENTITY")
        checar("C2   IDENTITY reprova chave AWS real em claro", c2a.grave, "não achou AKIA... literal")
        checar("C2   IDENTITY não falso-positiva var de ambiente + placeholder", not c2b.grave, "acusou uma referência a env var")

        # --- C3: AUTHORITY (com roster) reprova V3/V7, passa com fronteira ---
        r3 = base / "c3"
        _escrever(r3 / ".claude/agents/w.md", _agente("w", tools="Write"))
        c3a = _por_id(r3, "AUTHORITY")
        _escrever(r3 / ".claude/agents/w.md", _agente("w", tools="Write", extra="saida_cercada apenas em build/"))
        c3b = _por_id(r3, "AUTHORITY")
        checar("C3   AUTHORITY reprova agente com Write sem cerca declarada", c3a.grave and c3a.forca_no_go, "não reprovou, ou não é NO-GO")
        checar("C3   AUTHORITY passa quando a cerca de escrita é declarada", not c3b.grave, "continuou reprovando com a cerca presente")

        # --- C4: AUTHORITY sem roster cai para cobertura de PreToolUse ---
        r4 = base / "c4"
        _escrever(r4 / "AGENTS.md", "# sem roster de agente\n")
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
        checar("C4   AUTHORITY sem roster reprova sem PreToolUse de escrita/rede", c4a.grave, "não reprovou sem hooks")
        checar("C4   AUTHORITY sem roster passa com os dois matchers cobertos", not c4b.grave, "continuou reprovando com os hooks presentes")

        # --- C5: FAILURE passa com timeout OU palavra, reprova sem nenhum ---
        r5 = base / "c5"
        _escrever(r5 / "CLAUDE.md", "# projeto sem nada\n")
        c5a = _por_id(r5, "FAILURE")
        settings5 = {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "true", "timeout": 10}]}]}}
        _escrever(r5 / ".claude/settings.json", json.dumps(settings5))
        c5b = _por_id(r5, "FAILURE")
        checar("C5   FAILURE reprova sem timeout e sem retry/fallback", c5a.grave, "não reprovou vazio")
        checar("C5   FAILURE passa com `timeout` declarado no hook", not c5b.grave, "continuou reprovando com timeout presente")

        # --- C6/C7: APPROVAL reprova sem PreToolUse, passa com deny, reprova sem marca ---
        r6 = base / "c6"
        _escrever(r6 / "CLAUDE.md", "# projeto\n")
        c6a = _por_id(r6, "APPROVAL")
        _escrever(r6 / "hooks/nega.py", 'print(\'{"hookSpecificOutput": {"permissionDecision": "deny"}}\')\n')
        settings6 = {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "python hooks/nega.py"}]}]}}
        _escrever(r6 / ".claude/settings.json", json.dumps(settings6))
        c6b = _por_id(r6, "APPROVAL")
        _escrever(r6 / "hooks/nega.py", "print('ok')\n")
        c6c = _por_id(r6, "APPROVAL")
        checar("C6   APPROVAL reprova sem PreToolUse nenhum", c6a.grave, "não reprovou sem hook")
        checar("C6   APPROVAL passa com script que emite permissionDecision=deny", not c6b.grave, "continuou reprovando com o script fail-closed")
        checar("C7   APPROVAL volta a reprovar quando o script perde a marca de negar", c6c.grave, "não voltou a reprovar")

        # --- C8/C9: TRACEABILITY passa com registro datado, ou só com PostToolUse ---
        r8 = base / "c8"
        _escrever(r8 / "CLAUDE.md", "# projeto\n")
        c8a = _por_id(r8, "TRACEABILITY")
        _escrever(r8 / "decisoes/ADR-001-primeira.md", "data: 2026-08-23\n\n# decisão\n")
        c8b = _por_id(r8, "TRACEABILITY")
        checar("C8   TRACEABILITY reprova sem registro de decisão e sem PostToolUse", c8a.grave, "não reprovou vazio")
        checar("C8   TRACEABILITY passa com um ADR datado", not c8b.grave, "continuou reprovando com o ADR presente")

        r9 = base / "c9"
        _escrever(r9 / "CLAUDE.md", "# projeto\n")
        settings9 = {"hooks": {"PostToolUse": [{"hooks": [{"type": "command", "command": "true"}]}]}}
        _escrever(r9 / ".claude/settings.json", json.dumps(settings9))
        c9 = _por_id(r9, "TRACEABILITY")
        checar("C9   TRACEABILITY passa só com PostToolUse de auditoria, sem pasta de decisão", not c9.grave, "reprovou mesmo com PostToolUse configurado")

        # --- C10: CONTAINMENT passa com R0-R4 perto de palavra de reversibilidade ---
        r10 = base / "c10"
        _escrever(r10 / "CLAUDE.md", "# projeto\n")
        c10a = _por_id(r10, "CONTAINMENT")
        _escrever(r10 / "acoes.py", "# R3 exige aprovacao humana antes de qualquer acao irreversivel\n")
        c10b = _por_id(r10, "CONTAINMENT")
        checar("C10  CONTAINMENT reprova sem classificação de reversibilidade", c10a.grave, "não reprovou vazio")
        checar("C10  CONTAINMENT passa com R3 perto de 'irreversível'", not c10b.grave, "continuou reprovando com a classificação presente")

        # --- C11: junction é podada — segredo atrás dela não aparece ---
        r11 = base / "c11"
        alvo11 = base / "c11-atras"
        _escrever(r11 / "CLAUDE.md", "# projeto\n")
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
            avisou = "fronteira" in c11.resumo.lower() or "junction" in c11.resumo.lower()
            try:
                os.rmdir(link11)
            except OSError:
                pass
            checar("C11  IDENTITY NÃO lê o que está atrás de uma junction", not achou_atras, "achou o segredo atrás da junction — atravessou em silêncio")
            checar("C11  IDENTITY avisa que uma fronteira foi pulada", avisou, "não nomeou a fronteira pulada no resumo")
        else:
            falhas.append("C11: não deu para criar junction real (mklink /J falhou) — controle não pôde rodar")
            print("  FALHA C11  junction não pôde ser criada neste ambiente")

        # --- C12: sem harness nenhum, avaliar() devolve None ---
        r12 = base / "c12-vazio"
        _escrever(r12 / "README.md", "nada de harness aqui\n")
        c12 = avaliar(r12)
        checar("C12  avaliar() devolve None sem CLAUDE.md/AGENTS.md/.claude", c12 is None, f"devolveu {c12!r}")

        # --- C13: NO-GO só dispara para IDENTITY/AUTHORITY/CONTAINMENT ---
        r13 = base / "c13"
        _escrever(r13 / ".claude/agents/a.md", _agente("a", extra="kill_criteria: x"))
        p13 = avaliar(r13)
        assert p13 is not None
        so_failure_falha = all(
            (not porta.grave) or porta.id == "FAILURE" for porta in p13.portas
        )
        checar(
            "C13  NO-GO não dispara quando só FAILURE/TRACEABILITY reprovam",
            not p13.no_go or not so_failure_falha,
            "no_go=True mesmo sem IDENTITY/AUTHORITY/CONTAINMENT reprovando",
        )

    print("-" * 74)
    if falhas:
        for f in falhas:
            print(f"  ⛔ {f}")
        print(f"\nREPROVA — {len(falhas)} controle(s)                                   (exit 1)")
        return 1
    print("PASSA — toda porta foi vista acusando E calando            (exit 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
