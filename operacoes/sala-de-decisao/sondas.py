"""Probes for the `sala-de-decisao` operation.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with
the error written out. It never returns a guess.

COPY THIS FILE to the root of your repository, as `sondas.py`.
To combine with another operation, concatenate the files — no helper name here
collides with the others' (they all start with `_dec_`).

⚠️ **The anti-mirror rule, here.** The written number lives in the decisions
index («we have 44 decisions, 3 revoked»). The measured number comes from the
**files** and their **names** — never from the index. The index is a derived
artifact: sealing its number against itself would be a mirror check, and the
pair would pass green locking the divergence in instead of finding it.

⚠️ **And the most expensive probe of this operation is
`decisao.revogacao_de_um_lado_so`.** When the new decision revokes the old one
and the old one does not get the warning, whoever opens the old one reads a
revoked rule as if it held. No review catches this: both files are right, each
on its own. The defect lives between them.
"""

from __future__ import annotations

import os
import re
from datetime import date, datetime
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: THE ONE ADJUSTMENT of this operation: where your decisions and gates live.
#: A "gate" is a file that waits on one person's decision. The convention is the
#: word `gate` in the file NAME — see the RECEITA for why.
PASTA_DE_DECISOES = "decisoes"

_DEC_ACEITA = re.compile(r"^\s*status\s*:\s*[\"']?(aceito|aceita|accepted)", re.I | re.M)
_DEC_REVOGADA = re.compile(r"^\s*status\s*:\s*[\"']?(revogad|superseded|substitu)", re.I | re.M)
_DEC_REVOGA = re.compile(r"^\s*(?:revoga|supersedes|emenda|amends)\s*:\s*(.+)$", re.I | re.M)
#: Two identifier conventions coexist in the world, and reading only one returns
#: a silent ZERO in the repository that uses the other. `ADR-031-assunto.md` is
#: the prefixed form; `0031-usar-postgres.md` is the original `adr-tools` one,
#: and in it the id has no letter. Which one holds comes from disk, in
#: `_dec_convencao()`.
_DEC_REFERENCIA = re.compile(r"\b([A-Z]{2,5}-\d{1,4})\b")
_DEC_REFERENCIA_NUA = re.compile(r"\b(\d{3,4})\b")
_DEC_NOME_NU = re.compile(r"^(\d{3,4})(?=-)")
_DEC_DATA_NO_NOME = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
#: A gate is `YYYY-MM-DD-gate-assunto.md`: the date AND the token, both in the
#: NAME. Requiring both is not style rigor — looking for just the word `gate`
#: matches every decision that has «gate» in its title, and the queue starts
#: counting files that wait on nobody. Measured against a real archive: 7 false
#: positives.
_DEC_NOME_DE_GATE = re.compile(r"\d{4}-\d{2}-\d{2}.*(?<![a-z])gate(?![a-z])", re.I)
_DEC_DECIDIDO = re.compile(r"^#{1,6}\s+.*\b(?:DECIDIDO|DECIDED)\b", re.M)


def _dec_base() -> Path:
    base = (RAIZ / PASTA_DE_DECISOES).resolve()
    if not base.is_dir():
        raise LookupError(
            f"`{PASTA_DE_DECISOES}` does not exist. This operation measures a decision record in "
            "files; with no folder there is nothing to measure, and returning zero would be saying "
            "you decide nothing — which is different from you not recording"
        )
    return base


def _dec_arquivos() -> list[Path]:
    base = _dec_base()
    achados: list[Path] = []
    for pasta, subpastas, arquivos in os.walk(base, followlinks=True):
        subpastas[:] = sorted(s for s in subpastas if not s.startswith("."))
        achados += [Path(pasta) / a for a in sorted(arquivos) if a.lower().endswith(".md")]
    if not achados:
        raise LookupError(f"`{PASTA_DE_DECISOES}` exists and is empty — no decision recorded")
    return achados


def _dec_decisoes() -> list[Path]:
    """A decision is every file that is NOT a gate. The gate is what still waits on someone."""
    return [a for a in _dec_arquivos() if not _DEC_NOME_DE_GATE.search(a.name)]


def _dec_gates() -> list[Path]:
    """The date AND the `gate` token, both in the file NAME. It is a convention,
    and it is on purpose.

    The name is the only part of the file that shows up in `ls`, in the
    explorer, in the diff and in a search — without opening anything. A `tipo:
    gate` field inside the frontmatter is invisible in all those places, and an
    item that waits on a decision that nobody sees is not waiting: it is
    forgotten.

    ⚠️ Requiring BOTH is not style rigor. Looking for just the word matches
    every decision that has «gate» in its title — measured against a real
    100-file archive, that inflated the queue with 7 items that waited on
    nobody. A queue with a false positive is worse than none: it trains whoever
    reads it to ignore it.
    """
    return [a for a in _dec_arquivos() if _DEC_NOME_DE_GATE.search(a.name)]


def _dec_texto(arquivo: Path) -> str:
    return arquivo.read_text(encoding="utf-8", errors="replace")


def _dec_convencao() -> str:
    """Which of the two identifier conventions this record uses, read from disk.

    Never nailed down: a record that names `0001-record-....md` is as canonical
    as one that names `ADR-001-....md` — it is the original `adr-tools` one.
    Assuming the first and returning zero on the second is *not measured*
    turning into *zero*, which is exactly the defect this operation exists to
    accuse.
    """
    arquivos = _dec_decisoes()
    com_prefixo = sum(1 for a in arquivos if _DEC_REFERENCIA.search(a.name.upper()))
    nus = sum(1 for a in arquivos if _DEC_NOME_NU.match(a.name))
    if com_prefixo and com_prefixo >= nus:
        return "prefixo"
    return "nua" if nus else "nenhuma"


def _dec_identificadores() -> dict[str, Path]:
    """`ADR-042` (or `0042`) -> file, read from the file NAME. One id per file."""
    arquivos = _dec_decisoes()
    convencao = _dec_convencao()

    # ⚠️ A REFUSAL, and never zero. With no readable identifier at all, this
    # probe cannot say everything is fine — it knows it could not look. The two
    # are opposite, and returning `0` for both is the lie the whole operation
    # exists to accuse.
    if arquivos and convencao == "nenhuma":
        raise LookupError(
            f"found {len(arquivos)} decision file(s) and no identifier in any of their names. "
            "This probe reads the id from the file NAME, in one of two conventions: "
            "`ADR-031-assunto.md` or `0031-assunto.md`. Rename them, or remove this probe — what "
            "it will not do is return zero and let you think everything is fine."
        )

    achados: dict[str, Path] = {}
    for arquivo in arquivos:
        if convencao == "prefixo":
            referencia = _DEC_REFERENCIA.search(arquivo.name.upper())
        else:
            referencia = _DEC_NOME_NU.match(arquivo.name)
        if referencia:
            achados.setdefault(referencia.group(1), arquivo)
    return achados


def _dec_citados(linha: str) -> list[str]:
    """The ids cited in a `revoga:`/`emenda:` line, in the record's convention.

    In the bare convention the search is restricted to those lines on purpose:
    looking for three or four loose digits in the whole body would match a year,
    a port and a version number, and the probe would start accusing what nobody
    wrote.
    """
    if _dec_convencao() == "prefixo":
        return _DEC_REFERENCIA.findall(linha.upper())
    return _DEC_REFERENCIA_NUA.findall(linha)


def _dec_aberto(gate: Path) -> bool:
    """A gate is open as long as it has no markdown HEADING with «DECIDIDO».

    A heading, not bold. `**DECIDIDO**` in the middle of a paragraph is the
    easiest way to close a gate with nobody able to find the decision later —
    and a search by heading is how you read the history of a record like this.
    """
    return not _DEC_DECIDIDO.search(_dec_texto(gate))


def _dec_data(arquivo: Path) -> date | None:
    achado = _DEC_DATA_NO_NOME.search(arquivo.name)
    if not achado:
        return None
    try:
        return date(int(achado.group(1)), int(achado.group(2)), int(achado.group(3)))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# The probes
# ---------------------------------------------------------------------------


@sonda("decisao.total", origem=".md files in the decisions folder that are not a gate")
def dec_total() -> int:
    return len(_dec_decisoes())


@sonda("decisao.aceitas", origem="frontmatter `status:` matching aceito/accepted")
def dec_aceitas() -> int:
    return sum(1 for a in _dec_decisoes() if _DEC_ACEITA.search(_dec_texto(a)))


@sonda("decisao.revogadas", origem="frontmatter `status:` matching revogada/superseded")
def dec_revogadas() -> int:
    return sum(1 for a in _dec_decisoes() if _DEC_REVOGADA.search(_dec_texto(a)))


@sonda(
    "decisao.sem_status",
    origem="decisions with no readable `status:` in the frontmatter",
)
def dec_sem_status() -> int:
    """A RELATION. A decision with no status is not read wrong — it is read without knowing.

    Whoever opens it has no way to tell a proposal from a rule in force, and the
    most expensive reading is the optimistic one: treating a proposal as a rule.
    """
    return sum(
        1
        for a in _dec_decisoes()
        if not _DEC_ACEITA.search(_dec_texto(a)) and not _DEC_REVOGADA.search(_dec_texto(a))
    )


@sonda(
    "decisao.revogacao_de_um_lado_so",
    origem="decisions cited in `revoga:`/`emenda:` that do not mention who revoked them",
)
def dec_revogacao_de_um_lado_so() -> int:
    """A RELATION, and it is this operation's expensive probe.

    The new decision declares `revoga: ADR-031`. `ADR-031` says nothing.
    Whoever opens the old one — which is the normal path, because it is the one
    cited in the old places — reads a revoked rule with the look of a live one.

    Both files are right, each on its own. **The defect lives between them**,
    and that is why no code review catches it.
    """
    porid = _dec_identificadores()
    por_arquivo = {caminho: ident for ident, caminho in porid.items()}
    orfas: set[str] = set()
    for arquivo in _dec_decisoes():
        atual = por_arquivo.get(arquivo)
        texto = _dec_texto(arquivo)
        for linha in _DEC_REVOGA.findall(texto):
            for alvo in _dec_citados(linha):
                if alvo not in porid or (atual and alvo == atual):
                    continue
                # The back-pointer: the revoked one has to NAME who revoked it.
                if not (atual and atual in _dec_texto(porid[alvo]).upper()):
                    orfas.add(alvo)
    return len(orfas)


@sonda(
    "decisao.sem_alternativa",
    origem="decisions whose text carries no alternative/rejected section",
)
def dec_sem_alternativa() -> int:
    """A RELATION. With no alternative written, there was no decision — there was a record.

    The value of an archive like this is not remembering what was chosen: it is
    remembering **what was rejected and why**. Without that, a year from now
    someone re-proposes the rejected alternative and nobody can tell it already
    fell.
    """
    marcas = ("alternativa", "descartad", "considerad", "alternative", "rejected")
    return sum(
        1
        for a in _dec_decisoes()
        if not any(m in _dec_texto(a).lower() for m in marcas)
    )


@sonda("decisao.gates_abertos", origem="files with `gate` in the name and no DECIDIDO heading")
def dec_gates_abertos() -> int:
    return sum(1 for g in _dec_gates() if _dec_aberto(g))


@sonda(
    "decisao.gate_mais_velho_dias",
    origem="days between the date in the oldest open gate's NAME and today",
)
def dec_gate_mais_velho_dias() -> int:
    """A COUNT — it moves every day, by construction, and that is the point.

    A stuck item waiting on a decision does not get worse suddenly: it gets
    worse one day at a time, and that is why nobody notices. This number goes up
    on its own until someone decides, and it is the only metric here that **gets
    worse when you do nothing**.

    ⚠️ The date comes from the file NAME, never from `criada_em:` in the
    frontmatter and never from `mtime`: the first nobody fills in with
    discipline, and the second is zeroed by a clone.
    """
    abertos = [g for g in _dec_gates() if _dec_aberto(g)]
    if not abertos:
        return 0
    datas = [d for d in (_dec_data(g) for g in abertos) if d]
    if not datas:
        raise LookupError(
            f"there are {len(abertos)} open gate(s) and none has a date in the file name. "
            "This operation's convention is `YYYY-MM-DD-gate-assunto.md` — with no date in the name "
            "there is no age, and an item with no age never looks old to anyone"
        )
    return (datetime.now().date() - min(datas)).days
