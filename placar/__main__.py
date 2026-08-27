"""`python -m placar <path>` — the seven gates, with evidence.

    $ python -m placar .
    $ python -m placar /path/to/your/project
    $ python -m placar . --html report.html   # WRITES, on top of the terminal

Exit code: 0 seven of seven · 1 a gate fails · 2 there was no agent
harness to read (no `CLAUDE.md`, `AGENTS.md` or `.claude/`).

No dependency. No API key. No model call. Runs offline.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import evidencia

from .portas import Placar, Porta, avaliar

LARGURA = 74


def _linha_porta(p: Porta) -> list[str]:
    marca = "⛔" if p.grave else "✅"
    no_go = "  (NO-GO)" if p.grave and p.forca_no_go else ""
    cabeca = f"{marca} {p.numero} · {p.id} — {p.pergunta}{no_go}"
    linhas = [cabeca, f"     {p.resumo}"]
    for item in p.itens[:6]:
        linhas.append(f"       {item}")
    if len(p.itens) > 6:
        linhas.append(f"       … and {len(p.itens) - 6} more")
    if p.grave and p.conserto:
        linhas.append(f"     → {p.conserto}")
    linhas.append("")
    return linhas


def relatorio(placar: Placar, hoje: str) -> list[str]:
    linhas = [f"placar · {placar.alvo} · on {hoje}", "=" * LARGURA, ""]
    for p in placar.portas:
        linhas.extend(_linha_porta(p))

    linhas.append("-" * LARGURA)
    linhas.append(f"{placar.passam} of {len(placar.portas)} gates")
    linhas.append("")
    if placar.no_go:
        linhas.append("NO-GO" + " " * 45 + "(exit 1)")
        linhas.append("IDENTITY, AUTHORITY or CONTAINMENT failing is automatic — the rest of the")
        linhas.append("scoreboard does not make up for a gate that decides what the agent REACHES.")
    elif placar.reprova:
        linhas.append("FAIL" + " " * 65 + "(exit 1)")
    else:
        linhas.append("PASS" + " " * 65 + "(exit 0)")
    return linhas


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover — stdout redirected
        pass

    args = list(sys.argv[1:] if argv is None else argv)

    html_arg: Path | None = None
    if "--html" in args:
        i = args.index("--html")
        html_arg = Path(args[i + 1])
        del args[i : i + 2]

    if not args:
        print(__doc__)
        return 2

    alvo = Path(args[0]).expanduser()
    hoje = date.today().isoformat()
    if not alvo.exists():
        print(f"placar: path does not exist — {alvo}", file=sys.stderr)
        return 2

    placar = avaliar(alvo)
    if placar is None:
        print(f"placar: no agent harness under {alvo}", file=sys.stderr)
        print("        (looked for CLAUDE.md, AGENTS.md and .claude/ at the root and one level down)", file=sys.stderr)
        return 2

    linhas = relatorio(placar, hoje)
    for linha in linhas:
        print(linha)

    codigo = 1 if placar.reprova else 0
    if html_arg is not None:
        html_arg.write_text(evidencia.pagina("placar", str(alvo), hoje, linhas, codigo), encoding="utf-8")
        print(f"\nself-contained HTML report written to {html_arg}")
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
