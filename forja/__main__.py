"""CLI da forja: `python -m forja <spec.toml> [--saida DIR] [--conferir]`.

natureza: correcao — a saída é sempre impressa por inteiro, inclusive quando a
forja RECUSA. Uma recusa que não diz o conserto é um erro; uma recusa que diz o
conserto é a metade útil de um compilador.

    python -m forja                          # vistoria: lê os agentes que você JÁ tem
    python -m forja --adotar                 # ESCREVE: uma spec por agente lido
    python -m forja exemplos/revisor-de-licenca.toml
    python -m forja exemplos/*.toml --saida build/
    python -m forja spec.toml --conferir     # não escreve; sai 1 se estiver stale
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from . import alvos, conselho, vistoria
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


def _vistoria(raiz: Path, *, adotar: bool, saida: Path, saida_explicita: bool) -> int:
    """`python -m forja` sem argumento: lê os agentes que já existem."""
    hoje = date.today().isoformat()
    pasta = vistoria.achar_pasta(raiz)

    # ⚠️ Pasta que não existe é RECUSA, e nunca verde. Um erro de digitação no
    # caminho não pode deixar um gate aprovando para sempre — é *não medido*
    # virando *zero*, no ponto de entrada.
    if pasta is None:
        print(f"vistoria · {raiz} · em {hoje}")
        print("=" * vistoria.LARGURA)
        print("Não achei pasta de agentes aqui. Procurei, nesta ordem:")
        for relativo in vistoria.PASTAS:
            print(f"     {raiz / relativo}")
        print()
        print("RECUSADO — não li nada, e não vou devolver verde por isso.      (exit 2)")
        return 2

    roster = vistoria.ler_roster(pasta)
    if not roster:
        print(f"vistoria · {pasta} · em {hoje}")
        print("=" * vistoria.LARGURA)
        print("A pasta existe e não há nenhum agente dentro dela.")
        print()
        print("RECUSADO — zero agente lido não é zero defeito.                 (exit 2)")
        return 2

    achados = vistoria.vistoriar(roster)
    for linha in vistoria.relatorio(roster, achados, pasta, hoje):
        print(linha)

    if adotar:
        # ⚠️ A spec do leitor nasce ao lado dos AGENTES DELE, e não dentro do
        # clone desta ferramenta. Escrever relativo ao diretório corrente parece
        # inofensivo até alguém rodar `forja /caminho/do/projeto --adotar` de
        # dentro do clone: as specs caem aqui, numa pasta que o `.gitignore`
        # daqui ignora, e somem sem erro nenhum. `--saida` continua mandando
        # quando alguém a escreve por extenso.
        destino = (saida if saida_explicita else vistoria.raiz_do_projeto(pasta) / "build") / "specs"
        destino.mkdir(parents=True, exist_ok=True)
        print()
        print(f"escrevi {len(roster)} spec(s) em {destino}/ — uma por agente lido:")
        for lido in roster:
            arquivo = destino / f"{lido.slug}.toml"
            arquivo.write_text(vistoria.adotar(lido, hoje, arquivo), encoding="utf-8")
            print(f"  ✓ {arquivo}")
        print()
        print("  Cada `?` é um buraco que já existia no agente e que ninguém tinha onde")
        print("  ver. Preencha, e rode `python -m forja " + str(destino) + "/*.toml`.")

    print()
    if not achados:
        print("PASSA — todo agente lido declara as seis coisas.                (exit 0)")
        return 0
    print("REPROVA                                                        (exit 1)")
    if not adotar:
        print()
        print("  `python -m forja --adotar` escreve a spec de cada um a partir do que já")
        print("  está lá, com um `?` em cada buraco. Aí a forja compila os artefatos que")
        print("  faltam — inclusive o hook que NEGA, que é o único que o runtime lê.")
    return 1


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

    especes = [Path(a) for a in argv if not a.startswith("-")]

    # Sem argumento nenhum, a forja NÃO imprime a ajuda: ela olha o que você já
    # tem. Ninguém com doze agentes escritos à mão vai escrever doze specs na fé
    # para descobrir se valia a pena — a anotação é a saída da primeira rodada,
    # nunca o pedágio dela.
    # Diretório é sempre vistoria; `.toml` é sempre compilação. O argumento diz
    # qual das duas direções você quer, e nunca é preciso decorar uma bandeira.
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
    if adotar_agentes or not especes or aponta_pasta:
        return _vistoria(
            especes[0] if aponta_pasta else Path("."),
            adotar=adotar_agentes,
            saida=saida,
            saida_explicita=saida_explicita,
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
