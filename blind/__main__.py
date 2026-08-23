"""`python -m blind <caminho>` — a sua varredura alcança o que ela alega cobrir?

    $ python -m blind .
    $ python -m blind /caminho/do/seu/projeto

Reprova com exit 1 quando alguma fronteira esconde `CLAUDE.md`, `AGENTS.md`,
`SKILL.md`, `agent.toml`, `settings.json` ou qualquer arquivo sob `.claude/`.
Fronteira sem nada sensível atrás sai como aviso (⚠️): é fato do disco, não
defeito — junction e symlink existem por motivo legítimo na maioria das vezes.

Sem dependência. Sem chave de API. Sem chamada de modelo. Roda offline.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from .limites import Fronteira, detectar

LARGURA = 74

_MOTIVO = {
    "junction": "junction do Windows — reparse point que uma varredura ingênua não desce",
    "symlink": "symlink de diretório — mesma fronteira estrutural, noutro sistema",
    "gitignore": "regra de `.gitignore` — esconde mesmo de quem atravessa a fronteira estrutural",
}


def relatorio(fronteiras: list[Fronteira], alvo: Path, hoje: str) -> list[str]:
    linhas = [f"blind · {alvo} · em {hoje}", "=" * LARGURA]

    if not fronteiras:
        linhas.append("Nenhuma fronteira encontrada — nenhuma junction, symlink de diretório")
        linhas.append("ou regra de `.gitignore` escondendo declaração sob este caminho.")
        linhas.append("")
        linhas.append("⚠️ Isto diz que ESTA varredura não achou fronteira — não que a sua")
        linhas.append("   ferramenta de verdade (rg, git grep, o seu CI) enxerga tudo. Se")
        linhas.append("   você sabe que há uma junction e ela não apareceu aqui, aponte este")
        linhas.append("   comando direto para dentro dela.")
        return linhas

    graves = [f for f in fronteiras if f.grave]
    avisos = [f for f in fronteiras if not f.grave]

    for grupo, marca in ((graves, "⛔"), (avisos, "⚠️")):
        for f in grupo:
            cabeca = f"{marca} {f.caminho}"
            linhas.append(cabeca)
            linhas.append(f"     tipo: {_MOTIVO[f.tipo]}")
            if f.alvo:
                linhas.append(f"     aponta para: {f.alvo}")
            if f.regra:
                linhas.append(f"     regra que casou: {f.regra!r}")
            if f.arquivos_atras:
                linhas.append(f"     esconde {len(f.arquivos_atras)} arquivo(s) de declaração:")
                for a in f.arquivos_atras[:6]:
                    linhas.append(f"       {a}")
                if len(f.arquivos_atras) > 6:
                    linhas.append(f"       … e mais {len(f.arquivos_atras) - 6}")
            else:
                linhas.append("     nada de declaração atrás — fato do disco, não defeito")
            linhas.append("")

    linhas.append("-" * LARGURA)
    linhas.append(
        f"{len(fronteiras)} fronteira(s) · {len(graves)} escondendo declaração · "
        f"{len(avisos)} sem nada sensível atrás"
    )
    linhas.append("")
    if graves:
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
        print(f"blind: caminho não existe — {alvo}", file=sys.stderr)
        return 2

    fronteiras = detectar(alvo)
    for linha in relatorio(fronteiras, alvo, date.today().isoformat()):
        print(linha)

    return 1 if any(f.grave for f in fronteiras) else 0


if __name__ == "__main__":
    raise SystemExit(main())
