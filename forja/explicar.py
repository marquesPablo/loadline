"""`--explain <finding>`: explains ONE finding, citing the paragraph it comes from.

nature: fix — this module NEVER copies the doctrine to a second place. A
duplicate rots the day the original changes and nobody remembers the twin;
instead it READS, on every call, the table row in `README.md` and the matching
paragraph in `LACUNAS.md` — the two files of this package, not the ones of the
project being surveyed.

Why this exists: a stranger who clones at 11pm and sees `⛔ V3` for the first
time does not know whether that is serious, or why. `python -m forja --explain
V3` answers with the SAME sentence the README already promises and the SAME
caveat the LACUNAS.md already declares — never a third version, written by
hand, that the two can contradict over time.

    python -m forja --explain V3
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ_DO_PACOTE = Path(__file__).resolve().parent.parent
README = RAIZ_DO_PACOTE / "README.md"
LACUNAS = RAIZ_DO_PACOTE / "LACUNAS.md"

CODIGOS = ("V1", "V2", "V3", "V4", "V5", "V6", "V7")

# Which numbered item(s) of the root LACUNAS.md talk about each finding — a
# fixed map because the link is editorial (someone decided item 11 talks about
# V6), not something to infer from the text alone.
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
    """`--explain` asked for a code outside the seven findings. Closed vocabulary."""


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
    """The lines ready to print — REFUSES if `regra` is not one of the seven."""
    regra = regra.strip().upper()
    if regra not in CODIGOS:
        raise RegraDesconhecida(
            f"`{regra}` is not a survey finding — the seven are {', '.join(CODIGOS)}"
        )

    linhas = [f"forja --explain {regra}", "=" * 74, ""]

    da_tabela = _linha_do_readme(regra)
    if da_tabela is None:
        linhas.append(f"⚠️ could not read the {regra} row in {README} — the file changed shape.")
    else:
        o_que, por_que = da_tabela
        linhas.append(f"What it finds: {o_que}")
        linhas.append(f"Why it hurts: {por_que}")
    linhas.append("")
    linhas.append(f"(cited live from {README.name}, table \"the seven findings\")")
    linhas.append("")

    paragrafos = _paragrafos_de_lacunas(LACUNAS_QUE_FALAM.get(regra, ()))
    if paragrafos:
        linhas.append(f"What {regra} does NOT prove, according to {LACUNAS.name}:")
        linhas.append("")
        for numero, titulo, corpo in paragrafos:
            linhas.append(f"  ## {numero} · {titulo}")
            for linha_corpo in corpo.splitlines():
                linhas.append(f"  {linha_corpo}" if linha_corpo else "")
            linhas.append("")
    else:
        linhas.append(f"⚠️ did not find the declared {LACUNAS.name} item for {regra} — the file changed shape.")

    return linhas
