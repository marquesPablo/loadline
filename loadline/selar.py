"""`--selar` — the annotation becomes the OUTPUT of the first run, not its toll.

loadline-ignore-file: this file TEACHES the syntax it emits, and the seals
written here are specimens, not claims. Without this line the module reads its
own generator as if it declared facts.

nature: fix — this module writes, and that is why it is the only one in
the project that has to fail conservatively: a file it could not read or write
becomes a line in the report and the run carries on, never an exception in the
middle of a batch that leaves half the files changed and half not.

## Why this exists

Without `--selar`, the whole cost of the product is paid up front: the user has
to write the seal BY HAND **and** a probe for every metric, and the return only
arrives in 90 days, when the first `expires=` fires. It is the adoption path
that loses.

With it, the user runs once, sees the list of what nobody can verify, and walks
out of the first session with the file annotated. What was a toll became a
product.

## Four rules, and each has a reason

1. **Only writes with the flag.** Without `--selar` the whole project is
   read-only, and that is how it is presented.
2. **Emits `arbitrated:` and never `measured:`.** Nobody measured anything.
   Emitting `measured:` would be the tool inventing that a measurement happened
   — the exact lie it exists to chase.
3. **`by=?` is written out.** The tool does not know who chose the number, and
   pretending it does is the same family of defect. The `?` parses (the file
   stays valid) and the report demands it be filled in on every later run —
   a visible failure instead of a silent one.
4. **Never overwrites and never writes into a specimen.** If the next line
   already has a seal, the spot already has an owner and this module does not
   touch it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .eco import Afirmacao
from .selo import _PADRAO  # the same recognizer that reads — never a second rule

#: Default deadline of the emitted seal. It is, itself, an ARBITRATED number —
#: and the project would be incoherent if it pretended otherwise. See `LACUNAS.md`.
VENCE_PADRAO = "90d"


@dataclass(frozen=True)
class Escrito:
    arquivo: str
    linha: int
    texto: str


def _ja_tem_selo(linhas: list[str], indice: int) -> bool:
    """Does the line just below already carry a seal? Then the spot has an owner."""
    seguinte = indice + 1
    return seguinte < len(linhas) and bool(_PADRAO.search(linhas[seguinte]))


def _nomes_unicos(afirmacoes: list[Afirmacao]) -> dict[int, list[tuple[str, str]]]:
    """Groups by line and disambiguates repeated names within the same file.

    Two sentences that say `endpoints` would produce two metrics with the same
    name, and the second's seal would silence the first's. Suffixing is ugly and
    it is honest; the human renames both when filling in the `by=`.
    """
    usados: dict[str, int] = {}
    por_linha: dict[int, list[tuple[str, str]]] = {}
    for af in sorted(afirmacoes, key=lambda a: (a.linha, a.numero)):
        base = af.nome
        usados[base] = usados.get(base, 0) + 1
        nome = base if usados[base] == 1 else f"{base}_{usados[base]}"
        por_linha.setdefault(af.linha, []).append((nome, af.numero))
    return por_linha


def selar_arquivo(
    caminho: Path, afirmacoes: list[Afirmacao], hoje: date, vence: str = VENCE_PADRAO
) -> list[Escrito]:
    """Inserts an `arbitrated:` seal after every line that claims without proof.

    Inserts bottom to top: writing top to bottom shifts every following line
    number, and the second seal would land in the wrong place — silently, which
    is the expensive way to get it wrong here.
    """
    texto = caminho.read_text(encoding="utf-8")
    linhas = texto.splitlines()
    quebra_final = texto.endswith("\n")

    escritos: list[Escrito] = []
    for numero_da_linha, pares in sorted(_nomes_unicos(afirmacoes).items(), reverse=True):
        indice = numero_da_linha - 1
        if indice < 0 or indice >= len(linhas) or _ja_tem_selo(linhas, indice):
            continue
        original = linhas[indice]
        recuo = original[: len(original) - len(original.lstrip())]
        metricas = " ".join(f"{nome}={valor}" for nome, valor in pares)
        selo = (
            f"{recuo}<!-- arbitrated: {metricas} by=? "
            f"on={hoje.isoformat()} expires={vence} -->"
        )
        linhas.insert(indice + 1, selo)
        escritos.append(Escrito(str(caminho), numero_da_linha, selo.strip()))

    if escritos:
        caminho.write_text("\n".join(linhas) + ("\n" if quebra_final else ""), encoding="utf-8")
    return list(reversed(escritos))


def selar(afirmacoes: list[Afirmacao], hoje: date | None = None) -> tuple[list[Escrito], list[str]]:
    """Writes the seals for all of list 3. Returns `(written, problems)`."""
    hoje = hoje or date.today()
    por_arquivo: dict[str, list[Afirmacao]] = {}
    for af in afirmacoes:
        por_arquivo.setdefault(af.arquivo, []).append(af)

    escritos: list[Escrito] = []
    problemas: list[str] = []
    for arquivo, lote in sorted(por_arquivo.items()):
        try:
            escritos.extend(selar_arquivo(Path(arquivo), lote, hoje))
        except (OSError, UnicodeDecodeError, UnicodeEncodeError) as exc:
            problemas.append(f"{arquivo}: could not seal — {exc}")
    return escritos, problemas
