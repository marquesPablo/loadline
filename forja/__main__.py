"""CLI da forja: `python -m forja <spec.toml> [--saida DIR] [--conferir]`.

nature: fix — a saída é sempre impressa por inteiro, inclusive quando a
forja RECUSA. Uma recusa que não diz o conserto é um erro; uma recusa que diz o
conserto é a metade útil de um compilador.

    python -m forja                          # vistoria: lê os agentes que você JÁ tem
    python -m forja --adotar                 # ESCREVE: uma spec por agente lido
    python -m forja exemplos/revisor-de-licenca.toml
    python -m forja exemplos/*.toml --saida build/
    python -m forja spec.toml --conferir     # não escreve; sai 1 se estiver stale
    python -m forja . --html relatorio.html  # ESCREVE, além do terminal: página autocontida
    python -m forja . --baseline             # diff contra .loadline-baseline.json
    python -m forja . --baseline --gravar    # ESCREVE o baseline com o estado de agora
    python -m forja --explain V3             # explica um achado, citando LACUNAS.md ao vivo
    python -m forja repoA repoB repoC        # comparação: uma tabela só, vários repositórios
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import evidencia

from . import alvos, comparar as _comparar, conselho, explicar as _explicar, vistoria
from .baseline import ARQUIVO_PADRAO, diff, gravar, ler as ler_baseline
from .spec import Recusa, Spec, ler

CENSO_PADRAO = Path(__file__).resolve().parent.parent / "censo" / "ecossistema.json"


def _console_em_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError, OSError):
            pass


def compilar(spec: Spec, hoje: date | None = None) -> dict[str, str]:
    """spec → {caminho relativo: conteúdo}. Determinístico: mesma spec, mesmos bytes."""
    saida: dict[str, str] = {}
    for emitir in alvos.TODOS:
        caminho, conteudo = emitir(spec)
        saida[caminho] = conteudo
    caminho, conteudo = alvos.receita(spec, sorted(saida), hoje=hoje)
    saida[caminho] = conteudo
    return saida


def _escrever(raiz: Path, artefatos: dict[str, str]) -> None:
    for relativo, conteudo in sorted(artefatos.items()):
        alvo = raiz / relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")


def _stale(raiz: Path, artefatos: dict[str, str]) -> list[str]:
    fora = []
    for relativo, conteudo in sorted(artefatos.items()):
        alvo = raiz / relativo
        if not alvo.exists():
            fora.append(f"{relativo}: não existe")
        elif alvo.read_text(encoding="utf-8") != conteudo:
            fora.append(f"{relativo}: diverge da spec")
    return fora


def _vistoria(
    raiz: Path,
    *,
    adotar: bool,
    saida: Path,
    saida_explicita: bool,
    html: Path | None = None,
    baseline: bool = False,
    baseline_gravar: bool = False,
) -> int:
    """`python -m forja` sem argumento: lê os agentes que já existem."""
    hoje = date.today().isoformat()
    pasta = vistoria.achar_pasta(raiz)
    linhas: list[str] = []

    def emitir(texto: str = "") -> None:
        linhas.append(texto)
        print(texto)

    def fechar(codigo: int) -> int:
        if html is not None:
            html.write_text(evidencia.pagina("forja", str(raiz), hoje, linhas, codigo), encoding="utf-8")
            emitir(f"\nrelatório HTML autocontido escrito em {html}")
        return codigo

    # ⚠️ Pasta que não existe é RECUSA, e nunca verde. Um erro de digitação no
    # caminho não pode deixar um gate aprovando para sempre — é *não medido*
    # virando *zero*, no ponto de entrada.
    if pasta is None:
        emitir(f"vistoria · {raiz} · em {hoje}")
        emitir("=" * vistoria.LARGURA)
        emitir("Não achei pasta de agentes aqui. Procurei, nesta ordem:")
        for relativo in vistoria.PASTAS:
            emitir(f"     {raiz / relativo}")
        emitir()
        emitir("RECUSADO — não li nada, e não vou devolver verde por isso.      (exit 2)")
        return fechar(2)

    roster = vistoria.ler_roster(pasta)
    if not roster:
        emitir(f"vistoria · {pasta} · em {hoje}")
        emitir("=" * vistoria.LARGURA)
        emitir("A pasta existe e não há nenhum agente dentro dela.")
        emitir()
        emitir("RECUSADO — zero agente lido não é zero defeito.                 (exit 2)")
        return fechar(2)

    achados = vistoria.vistoriar(roster)
    for linha in vistoria.relatorio(roster, achados, pasta, hoje):
        emitir(linha)

    if baseline:
        raiz_projeto = vistoria.raiz_do_projeto(pasta)
        arquivo_baseline = raiz_projeto / ARQUIVO_PADRAO
        if baseline_gravar:
            gravar(arquivo_baseline, achados, hoje)
            emitir()
            emitir(f"gravei o baseline em {arquivo_baseline} — {sum(len(a.itens) for a in achados)} item(ns).")
            emitir("A próxima rodada com `--baseline` (sem `--gravar`) mostra só o que MUDOU.")
            return fechar(0)

        anterior = ler_baseline(arquivo_baseline)
        if anterior is None:
            emitir()
            emitir(f"RECUSADO — não há baseline em {arquivo_baseline}.            (exit 2)")
            emitir(f"  Grave um com `python -m forja {raiz} --baseline --gravar`, e rode de novo.")
            return fechar(2)

        novos, resolvidos = diff(anterior, achados)
        emitir()
        emitir(f"baseline de {anterior.gravado_em} · {len(novos)} novo(s) · {len(resolvidos)} resolvido(s)")
        if novos:
            emitir("⛔ NOVO DESDE O BASELINE")
            for item in novos:
                emitir(f"     {item}")
        if resolvidos:
            emitir("✅ RESOLVIDO DESDE O BASELINE")
            for item in resolvidos:
                emitir(f"     {item}")
        emitir()
        if novos:
            emitir("REPROVA — há achado novo desde o baseline.                     (exit 1)")
            return fechar(1)
        emitir("PASSA — nada novo desde o baseline.                             (exit 0)")
        return fechar(0)

    if adotar:
        # ⚠️ A spec do leitor nasce ao lado dos AGENTES DELE, e não dentro do
        # clone desta ferramenta. Escrever relativo ao diretório corrente parece
        # inofensivo até alguém rodar `forja /caminho/do/projeto --adotar` de
        # dentro do clone: as specs caem aqui, numa pasta que o `.gitignore`
        # daqui ignora, e somem sem erro nenhum. `--saida` continua mandando
        # quando alguém a escreve por extenso.
        destino = (saida if saida_explicita else vistoria.raiz_do_projeto(pasta) / "build") / "specs"
        destino.mkdir(parents=True, exist_ok=True)
        emitir()
        emitir(f"escrevi {len(roster)} spec(s) em {destino}/ — uma por agente lido:")
        for lido in roster:
            arquivo = destino / f"{lido.slug}.toml"
            arquivo.write_text(vistoria.adotar(lido, hoje, arquivo), encoding="utf-8")
            emitir(f"  ✓ {arquivo}")
        emitir()
        emitir("  Cada `?` é um buraco que já existia no agente e que ninguém tinha onde")
        emitir("  ver. Preencha, e rode `python -m forja " + str(destino) + "/*.toml`.")

    emitir()
    if not achados:
        emitir("PASSA — todo agente lido declara as seis coisas.                (exit 0)")
        return fechar(0)
    emitir("REPROVA                                                        (exit 1)")
    if not adotar:
        emitir()
        emitir("  `python -m forja --adotar` escreve a spec de cada um a partir do que já")
        emitir("  está lá, com um `?` em cada buraco. Aí a forja compila os artefatos que")
        emitir("  faltam — inclusive o hook que NEGA, que é o único que o runtime lê.")
    return fechar(1)


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(sys.argv[1:] if argv is None else argv)

    saida = Path("build")
    saida_explicita = "--saida" in argv
    if saida_explicita:
        i = argv.index("--saida")
        saida = Path(argv[i + 1])
        del argv[i : i + 2]

    conferir = "--conferir" in argv
    if conferir:
        argv.remove("--conferir")

    adotar_agentes = "--adotar" in argv
    if adotar_agentes:
        argv.remove("--adotar")

    html_arg: Path | None = None
    if "--html" in argv:
        i = argv.index("--html")
        html_arg = Path(argv[i + 1])
        del argv[i : i + 2]

    baseline_arg = "--baseline" in argv
    if baseline_arg:
        argv.remove("--baseline")

    baseline_gravar = "--gravar" in argv
    if baseline_gravar:
        argv.remove("--gravar")

    if "--explain" in argv:
        i = argv.index("--explain")
        if i + 1 >= len(argv):
            print(_explicar.__doc__.strip().splitlines()[0])
            print(f"Achados válidos: {', '.join(_explicar.CODIGOS)}")
            return 2
        regra = argv[i + 1]
        del argv[i : i + 2]
        try:
            for linha in _explicar.explicar(regra):
                print(linha)
        except _explicar.RegraDesconhecida as exc:
            print(f"RECUSADO — {exc}                                          (exit 2)")
            return 2
        return 0

    especes = [Path(a) for a in argv if not a.startswith("-")]

    # Sem argumento nenhum, a forja NÃO imprime a ajuda: ela olha o que você já
    # tem. Ninguém com doze agentes escritos à mão vai escrever doze specs na fé
    # para descobrir se valia a pena — a anotação é a saída da primeira rodada,
    # nunca o pedágio dela.
    # Diretório é sempre vistoria; `.toml` é sempre compilação. O argumento diz
    # qual das duas direções você quer, e nunca é preciso decorar uma bandeira.
    #
    # Dois ou mais alvos, NENHUM `.toml`, é o modo COMPARAÇÃO: cada um é
    # vistoriado, e o resultado sai numa tabela só — nunca mais o comportamento
    # antigo (e nunca documentado) de vistoriar só o primeiro e ENGOLIR os
    # demais em silêncio.
    if len(especes) >= 2 and all(e.suffix != ".toml" for e in especes):
        faltando = [e for e in especes if not e.exists()]
        if faltando:
            print(f"forja · comparação de {len(especes)} repositório(s) · em {date.today().isoformat()}")
            print("=" * vistoria.LARGURA)
            for e in faltando:
                print(f"`{e}` não existe.")
            print()
            print("RECUSADO — não li nada, e não vou devolver verde por isso.      (exit 2)")
            return 2

        resultados = _comparar.comparar(especes)
        linhas = _comparar.relatorio(resultados, date.today().isoformat())
        for linha in linhas:
            print(linha)
        codigo = _comparar.codigo_de_saida(resultados)
        if html_arg is not None:
            alvo_html = ", ".join(str(e) for e in especes)
            html_arg.write_text(evidencia.pagina("forja", alvo_html, date.today().isoformat(), linhas, codigo), encoding="utf-8")
            print(f"\nrelatório HTML autocontido escrito em {html_arg}")
        return codigo

    # ⚠️ Alvo que não existe é RECUSA, nunca outra coisa — e este bug nasceu de
    # novo aqui depois de já ter sido consertado no varredor: sem esta linha,
    # `forja ./agentez` caía na compilação, morria lendo a spec e devolvia 1.
    # O `1` diz «a sua spec está errada»; o `2` diz «eu não li nada». Um erro de
    # digitação no CI encostado no código errado é não-medido virando zero.
    if especes and not especes[0].exists():
        print(f"forja · {especes[0]} · em {date.today().isoformat()}")
        print("=" * vistoria.LARGURA)
        print(f"`{especes[0]}` não existe — nem como pasta de agentes, nem como spec.")
        print()
        print("RECUSADO — não li nada, e não vou devolver verde por isso.      (exit 2)")
        return 2

    aponta_pasta = bool(especes) and especes[0].is_dir()
    if adotar_agentes or not especes or aponta_pasta or baseline_arg:
        return _vistoria(
            especes[0] if aponta_pasta else Path("."),
            adotar=adotar_agentes,
            saida=saida,
            saida_explicita=saida_explicita,
            html=html_arg,
            baseline=baseline_arg,
            baseline_gravar=baseline_gravar,
        )

    censo = conselho.carregar(CENSO_PADRAO)
    problemas = 0

    for caminho in especes:
        print(f"forja · {caminho}")
        print("=" * 72)
        try:
            spec = ler(caminho)
        except Recusa as recusa:
            print(f"⛔ RECUSADO  {recusa}")
            print()
            print("   A forja falha fechada. O que ela não consegue decidir, ela não emite —")
            print("   um compilador de agente que emite mesmo assim entrega o agente sem gate")
            print("   que ele existia para impedir.")
            print()
            problemas += 1
            continue
        except (OSError, ValueError) as exc:
            print(f"⛔ não deu para ler a spec: {type(exc).__name__}: {exc}")
            print()
            problemas += 1
            continue

        artefatos = compilar(spec)
        raiz = saida / spec.slug

        if conferir:
            fora = _stale(raiz, artefatos)
            if fora:
                print(f"DESATUALIZADO  {len(fora)} artefato(s) divergem de `{caminho}`:")
                for linha in fora:
                    print(f"  {linha}")
                problemas += 1
            else:
                print(f"em dia  {len(artefatos)} artefatos batem com a spec")
        else:
            _escrever(raiz, artefatos)
            for relativo in sorted(artefatos):
                print(f"  ✓ {raiz / relativo}")

        print()
        print(f"  fronteira: rede={spec.usa_rede} escrita={spec.usa_escrita} "
              f"execucao={spec.usa_execucao} toca_alvo={spec.toca_alvo}")
        print(f"  golden: {len(spec.golden)} caso(s) · lacunas declaradas: {len(spec.lacunas)}")
        if spec.desconhecidas:
            print(f"  ⚠️  ferramentas não classificadas pelo guarda: {', '.join(spec.desconhecidas)}")

        bloco = conselho.em_markdown(spec.precisa, censo, str(CENSO_PADRAO))
        if bloco:
            print()
            print(bloco)
        print()

    if problemas:
        print(f"REPROVA — {problemas} spec(s) recusadas ou desatualizadas")
        return 1
    print("PASSA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
