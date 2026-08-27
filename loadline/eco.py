"""Prose vs seal — does the number in the SENTENCE match the number in the SEAL?

loadline-ignore-file: this file TEACHES the cross-check, and the seals and
sentences written here are specimens, not claims.

nature: fix — this module only reads text and returns findings. It does
not write to disk, does not fix the sentence, and an exception here surfaces
and warns instead of blocking.

The defect it exists to catch, measured in this repository on 2026-08-20:

    33 passed · 0 failed
    <!-- measured: nucleo.checks=36 nature=count on=2026-08-16 expires=never -->

The seal says 36. The probe measures 36. **The verifier returns `MATCHES`** —
and the sentence three lines above says 33, forever, with nothing watching.

It is the structural hole in every seal mechanism: **the seal covers the
VALUE, and nobody covers the SENTENCE.** Whoever re-seals touches the comment,
which is what fails, and forgets the text, which is what people read. The wrong
number survives round after round of re-sealing, green the whole time.

## The rule, and what it deliberately does NOT do

It bites in one direction only: **a number claimed in the prose that no seal
in the block explains.** If the prose claims no number, there is nothing to
contradict and nothing is flagged — the seal stays the only source, and that
is legitimate.

The opposite direction — *the sentence claims a QUANTITY that the seal does not
name* — needs a closed register of quantities and a judgment about what counts
as a claim. It is **not** here, and it is declared as a gap in `LACUNAS.md`
instead of faked.

## What counts as a prose number, and what is declared noise

In: digits with a word boundary, and number words from zero to twenty (in
Portuguese and English) — because *"six projects"* claims as much as *"6"*.

Out, because they are an address and not a claim: a `YYYY-MM-DD` date, an
`N.N.N` version, a colon identifier (`arXiv:2608.10218`, `README.md:12`), a
URL, and a percentage — which is derived, and checking it would need the
denominator.

Each exclusion is a named constant just below, not scattered through
conditions inside the function: a rule you cannot read you cannot audit.

## The declared waiver

A seal can declare `echo=no` and stay out. That is an explicit decision, comes
out NAMED in the report, and is the difference between an exception and a hole.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .selo import SELO_NA_LINHA, Selo

PROSE_DRIFT = "PROSE_DRIFT"

#: Fragments that are an address, not a claim — removed BEFORE looking for a number.
RUIDO = (
    re.compile(r"\d{4}-\d{2}-\d{2}"),          # date
    # version — ⚠️ 2026-08-25: it was `(?:\.\d+)+` (one or more), requiring 3+
    # segments and letting a two-part identifier like `Apache-2.0`/`Python 3.14`
    # through as if it were a real number. Measured against the very examples in
    # the docstring on the line below, before the fix: none matched.
    re.compile(r"\bv?\d+\.\d+(?:\.\d+)*\b"),   # version
    re.compile(r"\bv?\d+\.\d+\+"),             # version range: `3.9+`, `18.0+`
    re.compile(r"\w+:\S*\d\S*"),               # arXiv:2608.10218, README.md:12, http://…
    re.compile(r"\d+(?:[.,]\d+)?\s*%"),        # percentage — derived, no denominator here
    re.compile(r"(?:n[ºo°]|#)\s*\d+", re.IGNORECASE),  # ordinal: `nº 1`, `#3` — address, not a count
)

#: A number word counts as a claim — `six projects` does not escape by having
#: no digit. Only up to twenty: above that nobody writes it out in practice.
#:
#: ⚠️ `um`/`uma`/`one` are OUT, and the absence is a decision, not an oversight:
#: in Portuguese they are an indefinite article before they are a numeral, and
#: *"A record of the ecosystem"* claims no quantity at all. Telling the two uses
#: apart needs syntactic analysis, which this module does not do. **The declared
#: cost:** a sentence that really does claim *"one project has no canonical"*
#: passes uncharged. It is in `LACUNAS.md`, and the way out for whoever needs it
#: is to write the digit.
POR_EXTENSO = {
    "zero": "0", "nenhum": "0", "nenhuma": "0",
    "dois": "2", "duas": "2", "two": "2",
    "três": "3", "tres": "3", "three": "3",
    "quatro": "4", "four": "4",
    "cinco": "5", "five": "5",
    "seis": "6", "six": "6",
    "sete": "7", "seven": "7",
    "oito": "8", "eight": "8",
    "nove": "9", "nine": "9",
    "dez": "10", "ten": "10",
    "onze": "11", "doze": "12", "treze": "13", "catorze": "14", "quatorze": "14",
    "quinze": "15", "dezesseis": "16", "dezessete": "17", "dezoito": "18",
    "dezenove": "19", "vinte": "20",
}

_DIGITO = re.compile(r"(?<![\w.,])(\d+)(?![\w])")

#: A numeral preceded by a DEFINITE article is a pronoun, not a claim: *"os dois
#: lados"* / *"the two sides"* and *"as três formas"* / *"the three ways"* refer
#: back to things already said, they count nothing new. Without this rule, all
#: well-written prose turns into a false positive — and a detector that shouts
#: on the right text is switched off in the first week, which is the most
#: expensive way for a check to fail.
_NUMERAL = "dois|duas|tr[êe]s|tres|quatro|cinco|seis|sete|oito|nove|dez|doze|quinze|vinte"
_NUMERAL_EN = "two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty"
_PRONOMINAL = re.compile(
    r"\b(?:"
    rf"(?:os|as|nos|nas|dos|das|aos|às|pelos|pelas)\s+(?:{_NUMERAL})"
    rf"|(?:the|both|these|those|all)\s+(?:first\s+|last\s+|other\s+|only\s+|same\s+)?(?:{_NUMERAL_EN})"
    r")\b",
    re.IGNORECASE,
)
_PALAVRA = re.compile(r"[a-zà-ÿ]+", re.IGNORECASE)
#: Imported, never rewritten: the list of marks lives in `selo.py` and a copy
#: here already fell behind when the third mark was born.
_SELO_NA_LINHA = SELO_NA_LINHA
_CERCA = "```"


def bloco_selado(linhas: list[str], linha_do_selo: int) -> tuple[int, int]:
    """The lines (1-based, inclusive) that the seal on `linha_do_selo` covers.

    Walks up from the seal skipping blank lines and **other seals** — a stacked
    seal covers the same block, which is how practice actually writes it — and
    joins the contiguous lines up to the previous blank line.

    ⚠️ **A code fence goes INTO the block, on purpose, and this is the opposite
    of the scanning rule.** To READ A SEAL, what is inside a fence is a specimen
    and is ignored. To CROSS-CHECK PROSE, the fence is exactly where the claim
    lives: in the defect that opens this file, the `33` is inside a console
    block. The two rules look at the same fence and ask different things —
    *"did someone declare a seal here?"* and *"did someone claim a number here?"*.
    """
    i = linha_do_selo - 2  # 0-based index of the line just above the seal
    while i >= 0 and (not linhas[i].strip() or _SELO_NA_LINHA.search(linhas[i])):
        i -= 1
    if i < 0:
        return (0, 0)

    fim = i
    if linhas[i].lstrip().startswith(_CERCA):  # closing fence: walk down to the opening
        i -= 1
        while i >= 0 and not linhas[i].lstrip().startswith(_CERCA):
            i -= 1
        return (max(i + 1, 1), fim + 1)

    while i >= 0 and linhas[i].strip() and not _SELO_NA_LINHA.search(linhas[i]):
        i -= 1
    return (i + 2, fim + 1)


def numeros_afirmados(texto: str) -> set[str]:
    """The numbers this text CLAIMS, with the address noise already removed."""
    limpo = texto
    for padrao in RUIDO:
        limpo = padrao.sub(" ", limpo)
    limpo = _PRONOMINAL.sub(" ", limpo)
    achados = set(_DIGITO.findall(limpo))
    for palavra in _PALAVRA.findall(limpo):
        valor = POR_EXTENSO.get(palavra.lower())
        if valor is not None:
            achados.add(valor)
    return achados


@dataclass(frozen=True)
class Afirmacao:
    """A number claimed in the prose that NO seal covers — list 3.

    It is a suspect, not a defect. A number nobody can verify is not a wrong
    number; it is a number the tool has nothing to say about, and saying so out
    loud is the opposite of returning `PASS`.
    """

    arquivo: str
    linha: int
    numero: str
    trecho: str
    #: A SUGGESTED metric name, taken from the word that follows the number in
    #: the sentence (`"12 endpoints"` -> `endpoints`). It is a declared
    #: heuristic, for the human to rename — never a claim that the tool knows
    #: what that is.
    nome: str

    def __str__(self) -> str:
        return (
            f"UNVERIFIED  {self.arquivo}:{self.linha}  "
            f'"{self.trecho.strip()[:60]}" → nobody verifies {self.numero}'
        )


def afirmacoes_da_linha(texto: str) -> list[tuple[str, str]]:
    """`(number, suggested_name)` for a line, with the address noise removed.

    The name comes from the first word after the number — the same heuristic a
    human uses reading *"12 endpoints"*. When there is no word, the name comes
    out generic: inventing a pretty name for what was not understood would be
    the same family of lie the project chases.
    """
    limpo = texto
    for padrao in RUIDO:
        limpo = padrao.sub(" ", limpo)
    limpo = _PRONOMINAL.sub(" ", limpo)

    achados: list[tuple[str, str]] = []
    vistos: set[str] = set()
    for m in _DIGITO.finditer(limpo):
        numero = m.group(1)
        if numero in vistos:
            continue
        vistos.add(numero)
        achados.append((numero, _nome_depois(limpo, m.end())))
    for m in _PALAVRA.finditer(limpo):
        valor = POR_EXTENSO.get(m.group(0).lower())
        if valor is None or valor in vistos:
            continue
        vistos.add(valor)
        achados.append((valor, _nome_depois(limpo, m.end())))
    return achados


def _nome_depois(texto: str, posicao: int) -> str:
    """The word right after the number, normalized — or a generic name."""
    resto = _PALAVRA.search(texto, posicao)
    if resto is None:
        return "YOUR_METRIC"
    palavra = resto.group(0).lower()
    # A preposition or article names nothing: `3 de 5` does not become `de=3`.
    if palavra in {"de", "do", "da", "dos", "das", "em", "no", "na", "e", "ou",
                   "a", "o", "os", "as", "para", "por", "com", "of", "in", "and"}:
        return "YOUR_METRIC"
    return palavra


def afirmacoes_sem_selo(
    linhas: list[str], selos: list[Selo], arquivo: str, especimes: set[int] | None = None
) -> list[Afirmacao]:
    """List 3: numbers claimed OUTSIDE any sealed block.

    This is the function that inverts the cold start. The detector already
    existed — it is the same `numeros_afirmados` the cross-check uses — and it
    was locked behind an `if`: it only ran INSIDE a block that already had a
    seal. In a repository that never annotated anything there is no block, so
    there was nothing to cross-check, so the run returned green over a file full
    of numbers nobody can verify.

    What changes here is only the reach: the same noise rules, the same
    handling of number words and pronouns, pointed at the text that is NOT
    covered.
    """
    especimes = especimes or set()
    cobertas: set[int] = set()
    for selo in selos:
        if not selo.metricas:
            continue
        ini, fim = bloco_selado(linhas, selo.linha)
        if (ini, fim) != (0, 0):
            cobertas.update(range(ini, fim + 1))
        cobertas.add(selo.linha)

    achadas: list[Afirmacao] = []
    for n, linha in enumerate(linhas, start=1):
        if n in cobertas or n in especimes or _SELO_NA_LINHA.search(linha):
            continue
        for numero, nome in afirmacoes_da_linha(linha):
            achadas.append(Afirmacao(arquivo, n, numero, linha, nome))
    return achadas


def confrontar(
    selos: list[Selo], linhas: list[str], arquivo: str
) -> tuple[list[tuple[Selo, str, set[str]]], list[Selo]]:
    """Cross-checks each sealed block against the seals that cover it.

    Returns `(discrepancies, waived)`. A discrepancy is
    `(seal, prose_number, seal_values)` — the number the sentence claims and
    that no seal in the block explains.

    The cross-check is per BLOCK, not per seal: seals stacked over the same
    paragraph are read together, because together is how they cover the
    sentence. Judging them one by one would flag each seal in the stack for the
    others' numbers — false-green in reverse, and just as useless.
    """
    dispensados = [s for s in selos if s.echo == "no"]
    ativos = [s for s in selos if s.echo != "no"]

    por_bloco: dict[tuple[int, int], list[Selo]] = {}
    for selo in ativos:
        if not selo.metricas:
            continue
        bloco = bloco_selado(linhas, selo.linha)
        if bloco == (0, 0):
            continue
        por_bloco.setdefault(bloco, []).append(selo)

    discrepancias: list[tuple[Selo, str, set[str]]] = []
    for (ini, fim), grupo in sorted(por_bloco.items()):
        texto = "\n".join(linhas[ini - 1 : fim])
        na_prosa = numeros_afirmados(texto)
        if not na_prosa:
            continue  # the prose claims no number: nothing to contradict
        no_selo = {v for s in grupo for v in s.metricas.values()}
        orfaos = na_prosa - no_selo
        for numero in sorted(orfaos, key=lambda x: (len(x), x)):
            discrepancias.append((grupo[0], numero, no_selo))
    return discrepancias, dispensados
