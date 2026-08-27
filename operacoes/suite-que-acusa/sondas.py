"""Probes for the `suite-que-acusa` operation.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with
the error written out. It never returns a guess.

COPY THIS FILE to the root of your repository, as `sondas.py`.
To combine with another operation, concatenate the files — no helper name here
collides with the others' (they all start with `_su_`).

⚠️ **This operation's question is not «do the tests pass».** It is: **if someone
deleted the mechanism this test protects, would it still pass?**

A test that only confirms the happy path passes the same after the mechanism is
removed. It proves nothing — and its cost is not zero: it is giving someone the
feeling of being covered. A whole green suite made of those tests is worse than
no suite, because nobody looks for what already seems protected.

The remedy is the **negative control**: the test reintroduces the defect it
exists to catch, and fails if the mechanism does not complain.

⚠️ **And the honest limit, which is large.** `suite.sem_controle_negativo` is a
HEURISTIC. It looks for constructs that indicate an expectation of failure, and
it will get it wrong both ways: a test that reintroduces the defect in a way it
does not recognize is accused for nothing, and a decorative `pytest.raises`
gets past it. **Treat the number as a reading list, never as a verdict.**
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: THE ONE ADJUSTMENT of this operation: where your tests live.
PASTA_DE_TESTES = "tests"

#: Where you declare what the suite does NOT measure — the third list.
ARQUIVO_DE_LACUNAS = "LACUNAS.md"

_SU_NOME_DE_TESTE = re.compile(r"^(test_|_[a-z]{1,3}$|check)", re.I)

#: Constructs that indicate the test EXPECTS a failure — that is, that it
#: reintroduces the defect. The list is open on purpose: every project has its
#: own dialect, and a closed vocabulary here would accuse the whole house.
_SU_CONTROLE_NEGATIVO = (
    "raises",
    "assertraises",
    "expectederror",
    "xfail",
    "pytest.warns",
    "assertwarns",
    "should_fail",
    "must_fail",
    "deve_falhar",
    "reintroduz",
    "reintroduces",
    "controle negativo",
    "negative control",
)

_SU_PULADO = re.compile(r"@(?:pytest\.mark\.)?(skip|xfail)|unittest\.skip|self\.skipTest", re.I)


def _su_base() -> Path:
    base = (RAIZ / PASTA_DE_TESTES).resolve()
    if not base.is_dir():
        raise LookupError(
            f"`{PASTA_DE_TESTES}` does not exist. Adjust PASTA_DE_TESTES at the top of sondas.py. "
            "Zero tests because I did not look is different from zero tests, and the two cannot "
            "come out with the same number"
        )
    return base


def _su_arquivos() -> list[Path]:
    base = _su_base()
    achados: list[Path] = []
    for pasta, subpastas, arquivos in os.walk(base, followlinks=True):
        subpastas[:] = sorted(
            s for s in subpastas if not s.startswith(".") and s != "__pycache__"
        )
        achados += [Path(pasta) / a for a in sorted(arquivos) if a.endswith(".py")]
    if not achados:
        raise LookupError(f"`{PASTA_DE_TESTES}` exists and has no .py file")
    return achados


def _su_funcoes() -> list[tuple[Path, ast.FunctionDef, str]]:
    """(file, node, function source text) for each test function.

    Uses `ast`, not a regular expression over the text: a `def` inside a string,
    in a comment or nested in another function would be counted by regex, and
    the whole suite's denominator would come out wrong — which is the worst
    class of error in a tool that exists to demand a denominator.
    """
    funcoes: list[tuple[Path, ast.FunctionDef, str]] = []
    for arquivo in _su_arquivos():
        texto = arquivo.read_text(encoding="utf-8", errors="replace")
        try:
            arvore = ast.parse(texto)
        except SyntaxError as exc:
            raise LookupError(f"`{arquivo}` does not compile: {exc}") from exc
        for no in ast.walk(arvore):
            if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)) and _SU_NOME_DE_TESTE.match(
                no.name
            ):
                funcoes.append((arquivo, no, ast.get_source_segment(texto, no) or ""))
    if not funcoes:
        raise LookupError(
            f"no test function in `{PASTA_DE_TESTES}`. Looked for names starting with "
            "`test_` or `check`; if your dialect is another, adjust `_SU_NOME_DE_TESTE`"
        )
    return funcoes


def _su_tem_assercao(no: ast.AST) -> bool:
    """An `assert`, or an `assert*`/`raise` call. Without one the test does not fail."""
    for filho in ast.walk(no):
        if isinstance(filho, (ast.Assert, ast.Raise)):
            return True
        if isinstance(filho, ast.Call):
            alvo = filho.func
            nome = getattr(alvo, "attr", None) or getattr(alvo, "id", "")
            if isinstance(nome, str) and nome.lower().startswith("assert"):
                return True
    return False


# ---------------------------------------------------------------------------
# The probes
# ---------------------------------------------------------------------------


@sonda("suite.arquivos", origem=".py files under the tests folder")
def su_arquivos() -> int:
    return len(_su_arquivos())


@sonda("suite.checks", origem="test functions counted by the syntax tree, not by regex")
def su_checks() -> int:
    return len(_su_funcoes())


@sonda(
    "suite.sem_assercao",
    origem="test functions with no assert, assert* or raise in the body",
)
def su_sem_assercao() -> int:
    """A RELATION, and it is the only probe of this operation that is a verdict, not a suspicion.

    A test function with no assertion **cannot fail**. It runs, returns green,
    enters the coverage count and verifies nothing. It is not a heuristic: it is
    a property of the code, and its right number is zero.
    """
    return sum(1 for _, no, _ in _su_funcoes() if not _su_tem_assercao(no))


@sonda(
    "suite.sem_controle_negativo",
    origem="test functions with no construct that EXPECTS a failure (heuristic, see the docstring)",
)
def su_sem_controle_negativo() -> int:
    """A RELATION — and it is a READING LIST, not a verdict.

    The question it tries to answer: *if someone deleted the mechanism this test
    protects, would it still pass?* A test that only walks the happy path passes
    the same, and its cost is not zero — it is the feeling of coverage.

    ⚠️ **It gets it wrong both ways, and that is declared.** A test that
    reintroduces the defect in a way it does not recognize is accused for
    nothing; a decorative `pytest.raises` gets past it. The number serves to
    produce the list of which ones to open — never to fail on its own in CI.
    """
    sem = 0
    for _, _, fonte in _su_funcoes():
        baixa = fonte.lower()
        if not any(marca in baixa for marca in _SU_CONTROLE_NEGATIVO):
            sem += 1
    return sem


@sonda("suite.pulados", origem="tests marked with skip/xfail")
def su_pulados() -> int:
    """A RELATION. A skipped test is a test that does not exist, with the look of existing.

    It counts in the list, shows up in the report, and the only thing it
    measures is how long ago someone gave up on it.
    """
    return sum(1 for _, _, fonte in _su_funcoes() if _SU_PULADO.search(fonte))


@sonda(
    "suite.lacunas_declaradas",
    origem="list items in the gap file — the third list",
)
def su_lacunas_declaradas() -> int:
    """A COUNT. It is the number that decides whether the green of the others is worth anything.

    Every suite publishes what passed and what failed. Almost none publishes
    **what it never looked at** — and without that third list a green only says
    that what was looked at passed, which is far less than it seems.

    ⚠️ Zero here **blows up**, and does not return zero. A suite with no
    declared gaps is not a complete suite: it is a suite that never wrote its
    own limits, and the two are indistinguishable by the number.
    """
    arquivo = RAIZ / ARQUIVO_DE_LACUNAS
    if not arquivo.is_file():
        raise LookupError(
            f"`{ARQUIVO_DE_LACUNAS}` does not exist. It is the third list: what your suite does "
            "NOT measure. Without it, a green only says that what was looked at passed — and "
            "nobody can tell what was not looked at. Create the file with a list of items"
        )
    return len(_su_itens_abertos(arquivo.read_text(encoding="utf-8", errors="replace")))


#: A gap is a list item OR a numbered heading (`## 3 · ...`, `## 3. ...`).
#: Accepting both is not laxity: a list of eight gaps with a paragraph each is
#: written with a heading by almost everyone, and a rule that only recognizes a
#: bullet would count 0 in a well-written file.
_SU_ITEM = re.compile(r"^\s*(?:[-*+]\s+\S|\d+\.\s+\S|#{2,6}\s*\d+\s*[.·)-]\s*\S)", re.M)

#: Where the count STOPS. A closed gap listed with the open ones is the same
#: defect as an unlisted gap — in both cases the reader does not know the real
#: size of the blind spot. And the error is on the optimistic side, which is the worst.
_SU_FECHADAS = re.compile(r"^#{1,6}\s*(fechad|closed|resolvid|encerrad)", re.I | re.M)


def _su_itens_abertos(texto: str) -> list[str]:
    """The declared items, cutting off whatever comes after the "closed" heading."""
    corte = _SU_FECHADAS.search(texto)
    if corte:
        texto = texto[: corte.start()]
    itens = _SU_ITEM.findall(texto)
    if not itens:
        raise LookupError(
            f"`{ARQUIVO_DE_LACUNAS}` exists and declares no OPEN gap. Looked for a list item "
            "and a numbered heading, stopping at the closed section. An empty gap file claims "
            "there is no blind spot — the strongest possible claim, and the least likely"
        )
    return itens
