"""`python -m placar <caminho>` — as sete portas, com evidência.

    $ python -m placar .
    $ python -m placar /caminho/do/seu/projeto

Código de saída: 0 sete de sete · 1 alguma porta reprova · 2 não havia
harness de agente para ler (nenhum `CLAUDE.md`, `AGENTS.md` ou `.claude/`).

Sem dependência. Sem chave de API. Sem chamada de modelo. Roda offline.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

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
        linhas.append(f"       … e mais {len(p.itens) - 6}")
    if p.grave and p.conserto:
        linhas.append(f"     → {p.conserto}")
    linhas.append("")
    return linhas


def relatorio(placar: Placar, hoje: str) -> list[str]:
    linhas = [f"placar · {placar.alvo} · em {hoje}", "=" * LARGURA, ""]
    for p in placar.portas:
        linhas.extend(_linha_porta(p))

    linhas.append("-" * LARGURA)
    linhas.append(f"{placar.passam} de {len(placar.portas)} portas")
    linhas.append("")
    if placar.no_go:
        linhas.append("NO-GO" + " " * 45 + "(exit 1)")
        linhas.append("IDENTITY, AUTHORITY ou CONTAINMENT reprovando é automático — o resto do")
        linhas.append("placar não compensa uma porta que decide o que o agente ALCANÇA.")
    elif placar.reprova:
        linhas.append("REPROVA" + " " * 63 + "(exit 1)")
    else:
        linhas.append("PASSA" + " " * 65 + "(exit 0)")
    return linhas


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover — stdout redirecionado
        pass

    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 2

    alvo = Path(args[0]).expanduser()
    if not alvo.exists():
        print(f"placar: caminho não existe — {alvo}", file=sys.stderr)
        return 2

    placar = avaliar(alvo)
    if placar is None:
        print(f"placar: nenhum harness de agente sob {alvo}", file=sys.stderr)
        print("        (procurei CLAUDE.md, AGENTS.md e .claude/ na raiz e um nível abaixo)", file=sys.stderr)
        return 2

    for linha in relatorio(placar, date.today().isoformat()):
        print(linha)

    return 1 if placar.reprova else 0


if __name__ == "__main__":
    raise SystemExit(main())
