"""CLI da forja: `python -m forja <spec.toml> [--saida DIR] [--conferir]`.

natureza: correcao — a saída é sempre impressa por inteiro, inclusive quando a
forja RECUSA. Uma recusa que não diz o conserto é um erro; uma recusa que diz o
conserto é a metade útil de um compilador.

    python -m forja exemplos/revisor-de-licenca.toml
    python -m forja exemplos/*.toml --saida build/
    python -m forja spec.toml --conferir     # não escreve; sai 1 se estiver stale
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from . import alvos, conselho
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


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(sys.argv[1:] if argv is None else argv)

    saida = Path("build")
    if "--saida" in argv:
        i = argv.index("--saida")
        saida = Path(argv[i + 1])
        del argv[i : i + 2]

    conferir = "--conferir" in argv
    if conferir:
        argv.remove("--conferir")

    especes = [Path(a) for a in argv if not a.startswith("-")]
    if not especes:
        print(__doc__)
        return 2

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
