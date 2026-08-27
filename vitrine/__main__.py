"""`python -m vitrine <path>` — is your skill in the window, or in the stockroom?

    $ python -m vitrine ~/.claude/skills
    $ python -m vitrine .claude/skills --no-git
    $ python -m vitrine path/to/a/SKILL.md
    $ python -m vitrine --harvest skill-name --says "what it does, one sentence"

Fails with exit 1 when there is a ⛔. A warning (⚠️) does not fail: it exists
for the case where the rule has a legitimate exception, and there the one who
decides is you.

`--harvest` is the other direction: instead of auditing what already exists, it
refuses or writes a new `SKILL.md` — see `colheita.py`.

No dependency. No API key. No model call. Runs offline.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .regras import Achado, Skill, ler_pasta, vistoriar

LARGURA = 74

#: The three fields the router sees before deciding to load the skill. This is
#: the report's denominator — and it is written on screen because a number with
#: no denominator is the defect this whole tool exists to demand.
DECLARACOES_DE_VITRINE = ("S1", "S3", "S4")


def relatorio(skills: list[Skill], achados: list[Achado], alvo: Path, hoje: str) -> list[str]:
    linhas = [f"vitrine · {alvo} · on {hoje}", "=" * LARGURA]
    linhas.append(f"Read {len(skills)} skill(s).")
    linhas.append("")

    if not skills:
        linhas.append("No SKILL.md found under that path.")
        linhas.append("")
        linhas.append("⚠️ If your skills folder is a Windows junction or a directory symlink,")
        linhas.append("   the scan does NOT cross it — and gives no error. Point at the real")
        linhas.append("   target.")
        return linhas

    for achado in sorted(achados, key=lambda a: (not a.grave, -len(a.itens))):
        marca = "⛔" if achado.grave else "⚠️"
        contagem = (
            f"{len(achado.itens)} pair(s)"
            if achado.regra == "S11"
            else f"{len(achado.skills)} of {len(skills)}"
        )
        cabeca = f"{marca} {achado.titulo}"
        recuo = max(1, LARGURA - len(cabeca) - len(contagem) - 1)
        linhas.append(f"{cabeca}{' ' * recuo}{contagem}")
        for item in achado.itens[:8]:
            linhas.append(f"     {item}")
        if len(achado.itens) > 8:
            linhas.append(f"     … and {len(achado.itens) - 8} more")
        linhas.append(f"     → {achado.conserto}")
        linhas.append(f"       (rule {achado.regra}, from {achado.fonte})")
        linhas.append("")

    # The denominator: three vitrine declarations per skill — the name that is
    # an address, the when to use it, and the when NOT to. The three the router reads.
    possiveis = len(skills) * len(DECLARACOES_DE_VITRINE)
    ausentes = sum(len(a.skills) for a in achados if a.regra in DECLARACOES_DE_VITRINE)
    graves = {s for a in achados if a.grave for s in a.skills}

    linhas.append("-" * LARGURA)
    linhas.append(
        f"{len(skills)} skill(s) · {len(achados)} defect type(s) · "
        f"{ausentes} of {possiveis} vitrine declarations missing"
    )
    linhas.append("")
    if graves:
        linhas.append(f"FAIL — {len(graves)} of {len(skills)} skill(s) with ⛔" + " " * 22 + "(exit 1)")
    else:
        linhas.append("PASS" + " " * 65 + "(exit 0)")
    return linhas


def _colher(argv: list[str]) -> int:
    """`--harvest <slug> --says "..." [--folder <path>]` — see `colheita.py`."""
    from .colheita import Recusa, colher

    args = [a for a in argv if a != "--harvest"]
    if not args or args[0].startswith("--"):
        print(
            'vitrine --harvest: the slug is missing — python -m vitrine --harvest '
            '<slug> --says "what the skill does"',
            file=sys.stderr,
        )
        return 2
    slug, args = args[0], args[1:]

    descricao = ""
    pasta = Path(".claude/skills")
    i = 0
    while i < len(args):
        if args[i] == "--says" and i + 1 < len(args):
            descricao, i = args[i + 1], i + 2
        elif args[i] == "--folder" and i + 1 < len(args):
            pasta, i = Path(args[i + 1]).expanduser(), i + 2
        else:
            i += 1

    try:
        escrito = colher(slug, descricao, pasta)
    except Recusa as recusa:
        print(f"vitrine --harvest: {recusa}", file=sys.stderr)
        return 1

    print(f"✓ {escrito}")
    print('  3 "?" remain — the positive trigger (S3), the negative trigger (S4) and the body.')
    print(f"  Once filled in: python -m vitrine {pasta}")
    return 0


def main(argv: list[str] | None = None) -> int:
    from datetime import date

    # The Windows console opens in cp1252, and ⛔/⚠️ blow up on it. Without this
    # the tool dies on the `print` — after it has already done all the work.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover — stdout redirected
        pass

    args = list(sys.argv[1:] if argv is None else argv)
    if "--harvest" in args:
        return _colher(args)

    com_git = "--no-git" not in args
    args = [a for a in args if not a.startswith("--")]

    if not args:
        print(__doc__)
        return 2

    alvo = Path(args[0]).expanduser()
    if not alvo.exists():
        print(f"vitrine: path does not exist — {alvo}", file=sys.stderr)
        return 2

    skills = ler_pasta(alvo, com_git=com_git)
    achados = vistoriar(skills)
    for linha in relatorio(skills, achados, alvo, date.today().isoformat()):
        print(linha)

    return 1 if any(a.grave for a in achados) else 0


if __name__ == "__main__":
    raise SystemExit(main())
