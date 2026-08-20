"""CLI: `python -m aferido <caminho>` — o relatório de evidência de uma corrida.

natureza: correcao — a saída é sempre impressa por inteiro, mesmo quando
reprova. Um relatório que só aparece quando passa não é evidência.

    python -m aferido .              # varre o projeto
    python -m aferido README.md      # varre um arquivo
    python -m aferido . --sondas     # mostra de onde cada sonda tira o valor
    python -m aferido . --hoje 2027-01-01   # simula o futuro; é assim que se
                                            # prova que o vencimento reprova

Código de saída: 0 se tudo verde, 1 se qualquer coisa não-verde. Vencido
reprova de propósito.
"""

from __future__ import annotations

import sys
from datetime import date

from .registro import explicar
from .varredura import carregar_sondas, varrer
from .veredito import CONGELADO, DERIVOU, PROSA_MUDA, SEM_PROVA, VALE, VENCIDO

ORDEM = (DERIVOU, PROSA_MUDA, VENCIDO, SEM_PROVA, CONGELADO, VALE)


def _console_em_utf8() -> None:
    """O console do Windows abre em cp1252 e estoura em `→`, `←`, `⚠️`.

    Um relatório de evidência que morre por causa de uma seta não é evidência.
    Reconfigurar falha aberto: se o stream não aceitar, seguimos com o que der.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(sys.argv[1:] if argv is None else argv)

    hoje = date.today()
    if "--hoje" in argv:
        i = argv.index("--hoje")
        hoje = date.fromisoformat(argv[i + 1])
        del argv[i : i + 2]

    mostrar_sondas = "--sondas" in argv
    if mostrar_sondas:
        argv.remove("--sondas")

    alvo = argv[0] if argv else "."

    usado = carregar_sondas(__import__("pathlib").Path(alvo))
    if mostrar_sondas:
        print(f"sondas carregadas de: {usado or '(nenhum sondas.py encontrado)'}")
        for padrao, origem in explicar():
            print(f"  {padrao:<28} ← {origem}")
        print()

    relatorio = varrer(alvo, hoje=hoje)

    print(f"aferido · {alvo} · em {hoje.isoformat()}")
    print("=" * 72)
    for veredito in ORDEM:
        for achado in relatorio.por(veredito):
            print(achado)
    for problema in relatorio.malformados:
        print(f"MALFORMADO {problema}")

    print("-" * 72)
    print(relatorio.resumo())

    if relatorio.defeitos:
        print()
        print("⚠️  Divergência de RELAÇÃO não se resela. Ela só anda se o medidor ou o")
        print("    corpus quebrou — resselar aqui é esconder o defeito, não corrigi-lo:")
        for achado in relatorio.defeitos:
            print(f"      {achado.selo.arquivo}:{achado.selo.linha}  {achado.metrica}")

    print()
    print("REPROVA" if relatorio.reprova else "PASSA")
    return 1 if relatorio.reprova else 0


if __name__ == "__main__":
    raise SystemExit(main())
