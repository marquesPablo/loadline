"""`--explain <achado>`: explica UM achado, citando o parágrafo de onde ele vem.

natureza: correcao — este módulo NUNCA copia a doutrina para um segundo lugar.
Um duplicado apodrece no dia em que o original mudar e ninguém lembrar do
gêmeo; em vez disso ele LÊ, a cada chamada, a linha da tabela em `README.md` e
o parágrafo correspondente em `LACUNAS.md` — os dois arquivos deste pacote,
não os do projeto que está sendo vistoriado.

Por que isto existe: um estranho que clona às 23h e vê `⛔ V3` pela primeira
vez não sabe se isso é grave, nem por quê. `python -m forja --explain V3`
responde com a MESMA frase que o README já promete e a MESMA ressalva que o
LACUNAS.md já declara — nunca uma terceira versão, escrita à mão, que os dois
podem desmentir com o tempo.

    python -m forja --explain V3
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ_DO_PACOTE = Path(__file__).resolve().parent.parent
README = RAIZ_DO_PACOTE / "README.md"
LACUNAS = RAIZ_DO_PACOTE / "LACUNAS.md"

CODIGOS = ("V1", "V2", "V3", "V4", "V5", "V6", "V7")

# Que item(ns) numerado(s) do LACUNAS.md da raiz falam de cada achado — mapa
# fixo porque a ligação é editorial (alguém decidiu que o item 11 fala de V6),
# não algo que dê para inferir do texto sozinho.
LACUNAS_QUE_FALAM: dict[str, tuple[int, ...]] = {
    "V1": (9,),
    "V2": (9,),
    "V3": (9, 10),
    "V4": (9,),
    "V5": (9,),
    "V6": (9, 11, 13),
    "V7": (9,),
}

_LINHA_TABELA = re.compile(r"^\|\s*`(V\d)`\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$", re.M)
_ITEM_LACUNAS = re.compile(r"^## (\d+) · (.+?)\n(.*?)(?=\n## |\Z)", re.S | re.M)


class RegraDesconhecida(ValueError):
    """`--explain` pediu um código fora dos sete achados. Vocabulário fechado."""


def _linha_do_readme(regra: str) -> tuple[str, str] | None:
    if not README.is_file():
        return None
    texto = README.read_text(encoding="utf-8")
    for achado, o_que, por_que in _LINHA_TABELA.findall(texto):
        if achado == regra:
            return o_que, por_que
    return None


def _paragrafos_de_lacunas(numeros: tuple[int, ...]) -> list[tuple[int, str, str]]:
    if not LACUNAS.is_file():
        return []
    texto = LACUNAS.read_text(encoding="utf-8")
    achar = {n: None for n in numeros}
    for numero_str, titulo, corpo in _ITEM_LACUNAS.findall(texto):
        numero = int(numero_str)
        if numero in achar:
            achar[numero] = (titulo.strip(), corpo.strip())
    return [(n, *achar[n]) for n in numeros if achar[n] is not None]


def explicar(regra: str) -> list[str]:
    """As linhas prontas para imprimir — RECUSA se `regra` não é um dos sete."""
    regra = regra.strip().upper()
    if regra not in CODIGOS:
        raise RegraDesconhecida(
            f"`{regra}` não é um achado da vistoria — os sete são {', '.join(CODIGOS)}"
        )

    linhas = [f"forja --explain {regra}", "=" * 74, ""]

    da_tabela = _linha_do_readme(regra)
    if da_tabela is None:
        linhas.append(f"⚠️ não consegui ler a linha de {regra} em {README} — o arquivo mudou de forma.")
    else:
        o_que, por_que = da_tabela
        linhas.append(f"O que ele acha: {o_que}")
        linhas.append(f"Por que dói:    {por_que}")
    linhas.append("")
    linhas.append(f"(citado ao vivo de {README.name}, tabela \"os sete achados\")")
    linhas.append("")

    paragrafos = _paragrafos_de_lacunas(LACUNAS_QUE_FALAM.get(regra, ()))
    if paragrafos:
        linhas.append(f"O que {regra} NÃO prova, segundo {LACUNAS.name}:")
        linhas.append("")
        for numero, titulo, corpo in paragrafos:
            linhas.append(f"  ## {numero} · {titulo}")
            for linha_corpo in corpo.splitlines():
                linhas.append(f"  {linha_corpo}" if linha_corpo else "")
            linhas.append("")
    else:
        linhas.append(f"⚠️ não achei o item declarado de {LACUNAS.name} para {regra} — o arquivo mudou de forma.")

    return linhas
