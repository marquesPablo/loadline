"""Scans files, reads the seals, cross-checks the prose, and builds the report with a denominator.

nature: fix — an unreadable file becomes a line in the report, never an
exception that takes down the run and leaves the rest unmeasured.

The scan loads the project's probes by convention: a `sondas.py` at the root
of the target, imported before judging. Convention instead of configuration,
because a config field with a path to execute is a written invitation.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from datetime import date
from pathlib import Path

from .eco import PROSE_DRIFT, afirmacoes_sem_selo, confrontar
from .selo import Selo, SeloMalformado, ler_linha
from .veredito import Achado, Relatorio, julgar

EXTENSOES = (".md", ".markdown", ".txt", ".py", ".rst", ".toml", ".yaml", ".yml")
IGNORAR = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".mypy_cache"}

# A file that TEACHES the seal syntax must not be read as if it were claiming.
# Without this, every text that documents the tool sabotages it — including the
# malformed-seal example, which has to be able to exist written out.
DIRETIVA_ESPECIME = "loadline-ignore-file"
_CERCA = "```"


def _linhas_de_literal(texto: str) -> set[int]:
    """Lines of a `.py` that are INSIDE a string literal.

    This is the rule that separates code that **declares** a seal from code that
    **emits** one. A seal in a comment (`# measured: x=1`) is a real claim:
    someone wrote that number and it recomputes. A seal inside a string is a
    whole other thing — it is the generator assembling the text the USER will
    write, or the documentation teaching the syntax.

    Without this, every seal emitter sabotages itself: `f"<!-- measured:
    x={n} -->"` is read as claiming that `x` equals the string `{n}`. It is the
    same family of defect as the negative control that sabotages itself, and it
    reappears in every tool that generates its own syntax.

    Uses `ast` — stdlib — instead of a quote heuristic. A regex trying to find a
    string literal would get it wrong on nested quotes and on an f-string with
    an expression, and it would get it wrong silently, which is the worst way to
    get it wrong here.

    ⚠️ **A file that does not parse does not become a specimen.** Returning
    everything would make a broken `.py` pass green, silently. Returning nothing
    makes the seal get judged and, if it is malformed, the run fails loudly.
    Failing noisily is the right direction.
    """
    try:
        arvore = ast.parse(texto)
    except SyntaxError:
        return set()

    dentro: set[int] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Constant) and isinstance(no.value, str):
            dentro.update(range(no.lineno, (no.end_lineno or no.lineno) + 1))
        elif isinstance(no, ast.JoinedStr):  # f-string
            dentro.update(range(no.lineno, (no.end_lineno or no.lineno) + 1))
    return dentro


def _regioes_de_especime(linhas: list[str], markdown: bool, python: bool = False) -> set[int]:
    """Lines (1-based) that are a specimen and not a claim.

    Three rules, all declared and none guessed:
      1. a file with the `loadline-ignore-file` directive — the whole file;
      2. in Markdown, what is inside a code fence — a fence IS the universal
         mark for "this is an illustration", and reading an illustration as a
         claim invents facts nobody wrote;
      3. in Python, what is inside a string literal — see `_linhas_de_literal`.
         A comment is still judged; the fence is about the string, not about the
         file.
    """
    if any(DIRETIVA_ESPECIME in linha for linha in linhas):
        return set(range(1, len(linhas) + 1))
    if python:
        return _linhas_de_literal("\n".join(linhas))
    if not markdown:
        return set()

    dentro = False
    especimes: set[int] = set()
    for n, linha in enumerate(linhas, start=1):
        if linha.lstrip().startswith(_CERCA):
            especimes.add(n)
            dentro = not dentro
        elif dentro:
            especimes.add(n)
    return especimes


def carregar_sondas(raiz: Path) -> Path | None:
    """Imports `sondas.py` from the target root, if it exists. Returns the path used."""
    alvo = raiz / "sondas.py" if raiz.is_dir() else raiz.parent / "sondas.py"
    if not alvo.exists():
        return None
    spec = importlib.util.spec_from_file_location("sondas_do_projeto", alvo)
    if spec is None or spec.loader is None:
        return None
    modulo = importlib.util.module_from_spec(spec)
    sys.modules["sondas_do_projeto"] = modulo
    spec.loader.exec_module(modulo)
    return alvo


def _arquivos(raiz: Path) -> list[Path]:
    if raiz.is_file():
        return [raiz]
    achados = []
    for caminho in sorted(raiz.rglob("*")):
        if not caminho.is_file() or caminho.suffix.lower() not in EXTENSOES:
            continue
        if IGNORAR & set(caminho.parts):
            continue
        achados.append(caminho)
    return achados


def varrer(raiz: str | Path, hoje: date | None = None) -> Relatorio:
    """Reads every seal under `raiz` and judges each against today's disk."""
    raiz = Path(raiz)
    hoje = hoje or date.today()
    carregar_sondas(raiz)

    relatorio = Relatorio(achados=[])
    for caminho in _arquivos(raiz):
        try:
            texto = caminho.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            relatorio.malformados.append(f"{caminho}: could not read — {exc}")
            continue

        relatorio.arquivos_lidos += 1
        linhas = texto.splitlines()
        sufixo = caminho.suffix.lower()
        especimes = _regioes_de_especime(
            linhas,
            markdown=sufixo in (".md", ".markdown"),
            python=sufixo == ".py",
        )
        if especimes:
            relatorio.especimes.append(f"{caminho}: {len(especimes)} specimen lines, not judged")

        tinha_selo = False
        do_arquivo: list[Selo] = []
        for n, linha in enumerate(linhas, start=1):
            if n in especimes:
                continue
            try:
                selo = ler_linha(linha, arquivo=str(caminho), linha=n)
            except SeloMalformado as exc:
                relatorio.malformados.append(str(exc))
                tinha_selo = True
                continue
            if selo is None:
                continue
            tinha_selo = True
            do_arquivo.append(selo)
            relatorio.achados.extend(julgar(selo, hoje=hoje))

        # The prose-vs-seal cross-check is PROSE only: in a `.py` what surrounds
        # a seal is code, and demanding a prose echo of a number in code would
        # flag every neighboring literal. The narrowness is declared, not
        # forgotten.
        if sufixo in (".md", ".markdown", ".txt", ".rst"):
            # List 3 — what NO seal covers. It runs on every prose file, seal or
            # not; in a freshly cloned repository it is the only thing the tool
            # has to say, and it is why the first run stopped returning green.
            relatorio.sem_prova_nenhuma.extend(
                afirmacoes_sem_selo(linhas, do_arquivo, str(caminho), especimes)
            )
            discrepancias, dispensados = confrontar(do_arquivo, linhas, str(caminho))
            for selo, numero, no_selo in discrepancias:
                relatorio.achados.append(
                    Achado(
                        PROSE_DRIFT,
                        "/".join(sorted(selo.metricas)) or "—",
                        numero,
                        ", ".join(sorted(no_selo)) or "—",
                        selo,
                        selo.nature,
                    )
                )
            for selo in dispensados:
                relatorio.dispensados_do_eco.append(f"{selo.arquivo}:{selo.linha}")

        if not tinha_selo:
            relatorio.arquivos_sem_selo.append(str(caminho))

    return relatorio
