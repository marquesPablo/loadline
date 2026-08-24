"""Junta as sondas de duas ou mais operações num `sondas.py` só.

natureza: correcao — quando ele não consegue juntar, ele diz o que colidiu e
não escreve nada. Um arquivo escrito pela metade é pior que arquivo nenhum.

    python operacoes/juntar.py instrucao-que-nao-mente readme-que-nao-mente \\
        --saida /caminho/do/seu/repo/sondas.py

Por que isto existe, e não é um `cat`: todo `sondas.py` de operação abre com
`from __future__ import annotations`, e o Python exige que essa linha seja a
PRIMEIRA instrução do arquivo. Concatenar dois arquivos com `cat` põe a segunda
no meio, e o resultado morre com `SyntaxError` na hora de importar — depois de
já ter sobrescrito o `sondas.py` de quem tentou.

O que ele faz, em três regras:

  1. `from __future__` sai de todos e volta uma vez só, no topo.
  2. Os demais `import` são reunidos, deduplicados e ordenados.
  3. Colisão de PADRÃO DE MÉTRICA entre duas operações é RECUSA. Duas sondas
     registrando o mesmo padrão não dão erro em Python: a segunda sombreia a
     primeira em silêncio, e a métrica sombreada some do relatório sem nunca
     ter reprovado.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent

_FUTURE = re.compile(r"^from __future__ import .*$", re.M)
_IMPORT = re.compile(r"^(?:import |from (?!__future__)\S+ import ).*$", re.M)
_PADRAO = re.compile(r'^@sonda\(\s*\n?\s*"([^"]+)"', re.M)


class Colisao(ValueError):
    """Duas operações registram o mesmo padrão de métrica. Recusa, nunca aviso."""


def _corpo(texto: str) -> str:
    """O arquivo sem as linhas de import — elas sobem para o topo do resultado."""
    sem_future = _FUTURE.sub("", texto)
    return _IMPORT.sub("", sem_future)


def _imports(texto: str) -> list[str]:
    return [linha.strip() for linha in _IMPORT.findall(texto)]


def padroes(texto: str) -> list[str]:
    """Os padrões de métrica que este arquivo registra."""
    return _PADRAO.findall(texto)


def juntar(nomes: list[str], raiz: Path = AQUI) -> str:
    fontes: dict[str, str] = {}
    for nome in nomes:
        arquivo = raiz / nome / "sondas.py"
        if not arquivo.is_file():
            # ⚠️ Operação que não existe é RECUSA, e nunca um arquivo a menos
            # escrito em silêncio: `foja` por `forja` produziria metade das
            # sondas pedidas, sem erro, e ninguém contaria as que faltaram.
            disponiveis = sorted(p.name for p in raiz.iterdir() if (p / "sondas.py").is_file())
            raise FileNotFoundError(
                f"`{nome}` não é uma operação com sondas. Existem: {', '.join(disponiveis)}"
            )
        fontes[nome] = arquivo.read_text(encoding="utf-8")

    dono: dict[str, str] = {}
    for nome, texto in fontes.items():
        for padrao in padroes(texto):
            if padrao in dono:
                raise Colisao(
                    f"`{padrao}` é registrado por `{dono[padrao]}` e por `{nome}`. "
                    "Em Python a segunda sombreia a primeira sem erro nenhum, e a métrica "
                    "sombreada some do relatório sem nunca ter reprovado. Renomeie uma "
                    "das duas antes de juntar."
                )
            dono[padrao] = nome

    cabeca = [
        '"""Sondas de: ' + ", ".join(nomes) + ".",
        "",
        "Gerado por `operacoes/juntar.py`. Editar aqui é legítimo — este arquivo é seu,",
        "e a partir daqui ele não volta para a ferramenta que o escreveu.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
    ]
    vistos: set[str] = set()
    for texto in fontes.values():
        for linha in _imports(texto):
            if linha not in vistos:
                vistos.add(linha)
                cabeca.append(linha)

    partes = ["\n".join(cabeca), ""]
    for nome, texto in fontes.items():
        partes.append(f"\n# {'=' * 68}\n# {nome}\n# {'=' * 68}\n")
        partes.append(_corpo(texto).strip("\n"))
    return "\n".join(partes) + "\n"


def _console_em_utf8() -> None:
    """O console do Windows abre em cp1252 e estoura no `✓` e no `⛔`.

    Falha aberto: se o stream não aceitar, seguimos com o que der. Uma recusa
    que morre por causa de um símbolo não é uma recusa — é um traceback.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(sys.argv[1:] if argv is None else argv)
    saida = None
    if "--saida" in argv:
        i = argv.index("--saida")
        saida = Path(argv[i + 1])
        del argv[i : i + 2]
    nomes = [a for a in argv if not a.startswith("-")]
    if len(nomes) < 2:
        print(__doc__)
        return 2
    try:
        texto = juntar(nomes)
    except (Colisao, FileNotFoundError) as recusa:
        print(f"⛔ RECUSADO  {recusa}")
        print()
        print("   Nada foi escrito. Um `sondas.py` pela metade é pior que nenhum:")
        print("   ele importa, roda, e devolve verde sobre o que ficou de fora.")
        return 1

    quantos = len(padroes(texto))
    if saida is None:
        print(texto)
        return 0
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(texto, encoding="utf-8")
    print(f"✓ {saida}  ·  {len(nomes)} operações, {quantos} sondas, 0 colisões")
    print()
    print("  Confira com:  python -m loadline /caminho/do/seu/repo --sondas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
