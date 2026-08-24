"""`python -m vitrine <caminho>` — a sua skill está na vitrine, ou no estoque?

    $ python -m vitrine ~/.claude/skills
    $ python -m vitrine .claude/skills --sem-git
    $ python -m vitrine caminho/para/uma/SKILL.md
    $ python -m vitrine --colher nome-da-skill --diz "o que ela faz, uma frase"

Reprova com exit 1 quando houver ⛔. Aviso (⚠️) não reprova: ele existe para o
caso em que a regra tem exceção legítima, e nesse caso quem decide é você.

`--colher` é o outro sentido: em vez de auditar o que já existe, ele recusa
ou escreve uma `SKILL.md` nova — ver `colheita.py`.

Sem dependência. Sem chave de API. Sem chamada de modelo. Roda offline.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .regras import Achado, Skill, ler_pasta, vistoriar

LARGURA = 74

#: Os três campos que o roteador vê antes de decidir carregar a skill. É este o
#: denominador do relatório — e ele está escrito na tela porque número sem
#: denominador é o defeito que esta ferramenta inteira existe para cobrar.
DECLARACOES_DE_VITRINE = ("S1", "S3", "S4")


def relatorio(skills: list[Skill], achados: list[Achado], alvo: Path, hoje: str) -> list[str]:
    linhas = [f"vitrine · {alvo} · em {hoje}", "=" * LARGURA]
    linhas.append(f"Li {len(skills)} skill(s).")
    linhas.append("")

    if not skills:
        linhas.append("Nenhum SKILL.md encontrado sob esse caminho.")
        linhas.append("")
        linhas.append("⚠️ Se a sua pasta de skills for uma junction do Windows ou um symlink")
        linhas.append("   de diretório, a varredura NÃO atravessa — e não dá erro. Aponte")
        linhas.append("   para o alvo real.")
        return linhas

    for achado in sorted(achados, key=lambda a: (not a.grave, -len(a.itens))):
        marca = "⛔" if achado.grave else "⚠️"
        contagem = (
            f"{len(achado.itens)} par(es)"
            if achado.regra == "S11"
            else f"{len(achado.skills)} de {len(skills)}"
        )
        cabeca = f"{marca} {achado.titulo}"
        recuo = max(1, LARGURA - len(cabeca) - len(contagem) - 1)
        linhas.append(f"{cabeca}{' ' * recuo}{contagem}")
        for item in achado.itens[:8]:
            linhas.append(f"     {item}")
        if len(achado.itens) > 8:
            linhas.append(f"     … e mais {len(achado.itens) - 8}")
        linhas.append(f"     → {achado.conserto}")
        linhas.append(f"       (regra {achado.regra}, da {achado.fonte})")
        linhas.append("")

    # O denominador: três declarações de vitrine por skill — o nome que é
    # endereço, o quando usar, e o quando NÃO usar. São as três que o roteador lê.
    possiveis = len(skills) * len(DECLARACOES_DE_VITRINE)
    ausentes = sum(len(a.skills) for a in achados if a.regra in DECLARACOES_DE_VITRINE)
    graves = {s for a in achados if a.grave for s in a.skills}

    linhas.append("-" * LARGURA)
    linhas.append(
        f"{len(skills)} skill(s) · {len(achados)} tipo(s) de defeito · "
        f"{ausentes} de {possiveis} declarações de vitrine ausentes"
    )
    linhas.append("")
    if graves:
        linhas.append(f"REPROVA — {len(graves)} de {len(skills)} skill(s) com ⛔" + " " * 20 + "(exit 1)")
    else:
        linhas.append("PASSA" + " " * 63 + "(exit 0)")
    return linhas


def _colher(argv: list[str]) -> int:
    """`--colher <slug> --diz "..." [--pasta <caminho>]` — ver `colheita.py`."""
    from .colheita import Recusa, colher

    args = [a for a in argv if a != "--colher"]
    if not args or args[0].startswith("--"):
        print(
            'vitrine --colher: falta o slug — python -m vitrine --colher '
            '<slug> --diz "o que a skill faz"',
            file=sys.stderr,
        )
        return 2
    slug, args = args[0], args[1:]

    descricao = ""
    pasta = Path(".claude/skills")
    i = 0
    while i < len(args):
        if args[i] == "--diz" and i + 1 < len(args):
            descricao, i = args[i + 1], i + 2
        elif args[i] == "--pasta" and i + 1 < len(args):
            pasta, i = Path(args[i + 1]).expanduser(), i + 2
        else:
            i += 1

    try:
        escrito = colher(slug, descricao, pasta)
    except Recusa as recusa:
        print(f"vitrine --colher: {recusa}", file=sys.stderr)
        return 1

    print(f"✓ {escrito}")
    print('  faltam 3 "?" — gatilho positivo (S3), gatilho negativo (S4) e o corpo.')
    print(f"  Depois de preencher: python -m vitrine {pasta}")
    return 0


def main(argv: list[str] | None = None) -> int:
    from datetime import date

    # O console do Windows abre em cp1252, e ⛔/⚠️ estouram nele. Sem isto a
    # ferramenta morre no `print` — depois de já ter feito todo o trabalho.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover — stdout redirecionado
        pass

    args = list(sys.argv[1:] if argv is None else argv)
    if "--colher" in args:
        return _colher(args)

    com_git = "--sem-git" not in args
    args = [a for a in args if not a.startswith("--")]

    if not args:
        print(__doc__)
        return 2

    alvo = Path(args[0]).expanduser()
    if not alvo.exists():
        print(f"vitrine: caminho não existe — {alvo}", file=sys.stderr)
        return 2

    skills = ler_pasta(alvo, com_git=com_git)
    achados = vistoriar(skills)
    for linha in relatorio(skills, achados, alvo, date.today().isoformat()):
        print(linha)

    return 1 if any(a.grave for a in achados) else 0


if __name__ == "__main__":
    raise SystemExit(main())
