"""CLI: `python -m loadline <caminho>` — o relatório de evidência de uma corrida.

natureza: correcao — a saída é sempre impressa por inteiro, mesmo quando
reprova. Um relatório que só aparece quando passa não é evidência.

    python -m loadline .              # varre o projeto
    python -m loadline README.md      # varre um arquivo
    python -m loadline . --sondas     # mostra de onde cada sonda tira o valor
    python -m loadline . --selar      # ESCREVE: anota o que ninguém confere
    python -m loadline . --html relatorio.html  # ESCREVE, além do terminal
    python -m loadline . --hoje 2027-01-01   # simula o futuro; é assim que se
                                             # prova que o vencimento reprova

Toda rodada devolve TRÊS listas, e a terceira é a que faz a primeira execução
valer alguma coisa num repositório que nunca anotou nada:

    ✅ conferido e bate          o que uma sonda recomputou
    ❌ conferido e NÃO bate      derivou, venceu, não tem sonda, prosa muda
    ⚠️  ninguém confere isto     afirmação que nenhum selo cobre — SUSPEITA

Código de saída: 0 tudo verde · 1 reprova · 2 sem denominador (nada reprova, e
há afirmação que ninguém consegue conferir). O 2 separa *"suas anotações estão
erradas"* de *"você ainda não anotou nada"* — e antes dele as duas
devolviam 0, que era não-medido virando zero dentro da ferramenta que existe
para proibir isso.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import evidencia

from .registro import explicar
from .selar import selar
from .varredura import carregar_sondas, varrer
from .veredito import ARBITRATED, FROZEN, DRIFTED, PROSE_DRIFT, UNPROVEN, MATCHES, EXPIRED

ORDEM = (DRIFTED, PROSE_DRIFT, EXPIRED, UNPROVEN, FROZEN, ARBITRATED, MATCHES)


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

    escrever_selos = "--selar" in argv
    if escrever_selos:
        argv.remove("--selar")

    html_arg: Path | None = None
    if "--html" in argv:
        i = argv.index("--html")
        html_arg = Path(argv[i + 1])
        del argv[i : i + 2]

    alvo = argv[0] if argv else "."
    linhas: list[str] = []

    def emitir(texto: str = "") -> None:
        linhas.append(texto)
        print(texto)

    def fechar(codigo: int) -> int:
        if html_arg is not None:
            html_arg.write_text(evidencia.pagina("loadline", alvo, hoje.isoformat(), linhas, codigo), encoding="utf-8")
            emitir(f"\nrelatório HTML autocontido escrito em {html_arg}")
        return codigo

    # ⚠️ Alvo que não existe é RECUSA, nunca `PASSA`.
    #
    # Sem isto, `loadline ./sr` (por `./src`) varria zero arquivo, não achava
    # nenhuma afirmação, e saía **verde com código 0** — um erro de digitação no
    # CI deixava o gate aprovando para sempre. É exatamente *não medido* virando
    # *zero*, no ponto de entrada da ferramenta cuja tese inteira é que isso não
    # pode acontecer. Bandeira desconhecida cai aqui pelo mesmo caminho: ela é
    # lida como caminho, e nenhum caminho chamado `--sondaz` existe.
    caminho_do_alvo = Path(alvo)
    if not caminho_do_alvo.exists():
        emitir(f"loadline · {alvo} · em {hoje.isoformat()}")
        emitir("=" * 72)
        if alvo.startswith("-"):
            emitir(f"`{alvo}` não é uma bandeira conhecida, e não existe como caminho.")
            emitir("Bandeiras: --selar · --sondas · --html ARQUIVO · --hoje AAAA-MM-DD")
        else:
            emitir(f"`{alvo}` não existe.")
        emitir()
        emitir("RECUSADO — não varri nada, e não vou devolver verde por isso.   (exit 2)")
        return fechar(2)

    usado = carregar_sondas(caminho_do_alvo)
    if mostrar_sondas:
        emitir(f"sondas carregadas de: {usado or '(nenhum sondas.py encontrado)'}")
        for padrao, origem in explicar():
            emitir(f"  {padrao:<28} ← {origem}")
        emitir()

    relatorio = varrer(alvo, hoje=hoje)

    emitir(f"loadline · {alvo} · em {hoje.isoformat()}")
    emitir("=" * 72)
    for veredito in ORDEM:
        for achado in relatorio.por(veredito):
            emitir(str(achado))
    for problema in relatorio.malformados:
        emitir(f"MALFORMADO {problema}")

    if relatorio.sem_prova_nenhuma:
        emitir()
        emitir("⚠️  NINGUÉM CONSEGUE CONFERIR ISTO — são suspeitas, não defeitos.")
        emitir("    Um número que ninguém confere não é um número errado; é um número")
        emitir("    sobre o qual nada aqui tem o que dizer. `--selar` anota todos eles.")
        for afirmacao in relatorio.sem_prova_nenhuma:
            emitir(f"      {afirmacao}")

    emitir("-" * 72)
    emitir(str(relatorio.resumo()))

    if relatorio.defeitos:
        emitir()
        emitir("⚠️  Divergência de RELAÇÃO não se resela. Ela só anda se o medidor ou o")
        emitir("    corpus quebrou — resselar aqui é esconder o defeito, não corrigi-lo:")
        for achado in relatorio.defeitos:
            emitir(f"      {achado.selo.arquivo}:{achado.selo.linha}  {achado.metrica}")

    if escrever_selos:
        escritos, problemas = selar(relatorio.sem_prova_nenhuma, hoje=hoje)
        emitir()
        if escritos:
            arquivos = len({e.arquivo for e in escritos})
            emitir(
                f"escrevi {len(escritos)} selo(s) em {arquivos} arquivo(s), todos como "
                "`arbitrated:` — ninguém mediu nada ainda."
            )
            for e in escritos:
                emitir(f"  {e.arquivo}:{e.linha}  {e.texto}")
            emitir()
            emitir("  Agora troque cada `por=?` por quem escolheu o número, e renomeie a")
            emitir("  métrica se o nome que eu chutei não for o certo — ele saiu da palavra")
            emitir("  ao lado do número, não de entender o que ele significa.")
        else:
            emitir("nada a selar: ou não há afirmação sem prova, ou o lugar já tem selo.")
        for problema in problemas:
            emitir(f"  ⛔ {problema}")

    emitir()
    emitir(str(relatorio.veredito_da_corrida))
    return fechar(relatorio.codigo_de_saida)


if __name__ == "__main__":
    raise SystemExit(main())
