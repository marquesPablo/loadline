"""`python -m blind <path>` — does your scan reach what it claims to cover?

    $ python -m blind .
    $ python -m blind /path/to/your/project

Fails with exit 1 when a boundary hides `CLAUDE.md`, `AGENTS.md`, `SKILL.md`,
`agent.toml`, `settings.json` or any file under `.claude/`. A boundary with
nothing sensitive behind it comes out as a warning (⚠️): it is a fact of the
disk, not a defect — a junction or a symlink exists for a legitimate reason
most of the time.

No dependency. No API key. No model call. Runs offline.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from .limites import Fronteira, detectar

LARGURA = 74

_MOTIVO = {
    "junction": "a Windows junction — a reparse point a naive scan does not descend into",
    "symlink": "a directory symlink — the same structural boundary, on another system",
    "gitignore": "a `.gitignore` rule — hides even from whoever crosses the structural boundary",
}


def relatorio(fronteiras: list[Fronteira], alvo: Path, hoje: str) -> list[str]:
    linhas = [f"blind · {alvo} · on {hoje}", "=" * LARGURA]

    if not fronteiras:
        linhas.append("No boundary found — no junction, directory symlink or `.gitignore`")
        linhas.append("rule hiding a declaration under this path.")
        linhas.append("")
        linhas.append("⚠️ This says THIS scan found no boundary — not that your real tool")
        linhas.append("   (rg, git grep, your CI) sees everything. If you know there is a")
        linhas.append("   junction and it did not show up here, point this command straight")
        linhas.append("   into it.")
        return linhas

    graves = [f for f in fronteiras if f.grave]
    avisos = [f for f in fronteiras if not f.grave]

    for grupo, marca in ((graves, "⛔"), (avisos, "⚠️")):
        for f in grupo:
            cabeca = f"{marca} {f.caminho}"
            linhas.append(cabeca)
            linhas.append(f"     type: {_MOTIVO[f.tipo]}")
            if f.alvo:
                linhas.append(f"     points to: {f.alvo}")
            if f.regra:
                linhas.append(f"     rule that matched: {f.regra!r}")
            if f.arquivos_atras:
                linhas.append(f"     hides {len(f.arquivos_atras)} declaration file(s):")
                for a in f.arquivos_atras[:6]:
                    linhas.append(f"       {a}")
                if len(f.arquivos_atras) > 6:
                    linhas.append(f"       … and {len(f.arquivos_atras) - 6} more")
            else:
                linhas.append("     no declaration behind it — a fact of the disk, not a defect")
            linhas.append("")

    linhas.append("-" * LARGURA)
    linhas.append(
        f"{len(fronteiras)} boundary(ies) · {len(graves)} hiding a declaration · "
        f"{len(avisos)} with nothing sensitive behind them"
    )
    linhas.append("")
    if graves:
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
    if not args:
        print(__doc__)
        return 2

    alvo = Path(args[0]).expanduser()
    if not alvo.exists():
        print(f"blind: path does not exist — {alvo}", file=sys.stderr)
        return 2

    fronteiras = detectar(alvo)
    for linha in relatorio(fronteiras, alvo, date.today().isoformat()):
        print(linha)

    return 1 if any(f.grave for f in fronteiras) else 0


if __name__ == "__main__":
    raise SystemExit(main())
