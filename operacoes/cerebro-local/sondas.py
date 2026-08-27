"""Probes for the `cerebro-local` operation.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with
the error written out. It never returns a guess.

COPY THIS FILE to the root of your repository, as `sondas.py`.
To combine with another operation, concatenate the files — no helper name here
collides with the others' (they all start with `_cer_`).

⚠️ **The anti-mirror rule, here.** The written number lives in your
documentation ("we have 340 notes", "the server exposes 4 tools"). The measured
number comes from the **file system** and the **server code** — never from the
`.md` that claims it. The two sides have different owners, which is what makes
the pair worth anything.

⚠️ **The trap that dominates this operation, and it gives no error.** `rg`,
`grep -r` and `find` **do not cross a Windows junction or a directory symlink**,
and do not warn: the answer comes back plausible, with no error, and without the
files inside. In a knowledge vault linked folders are the rule, not the
exception. These probes use `os.walk(followlinks=True)`, which crosses. If you
rewrite any of them calling `grep` via `subprocess`, the number drops and
nothing accuses.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: THE ONE ADJUSTMENT of this operation: where your notes live, relative to this
#: file. `"."` means "the whole repository".
PASTA_DE_NOTAS = "."

#: Must match `EXTENSOES` in `servidor.py`. If they diverge, the probe counts
#: one corpus and the server serves another — and the green seal would be
#: measuring the wrong thing. The `cerebro.ferramentas` probe exists precisely
#: to anchor this.
_CER_EXTENSOES = (".md", ".markdown", ".txt", ".org")
_CER_IGNORAR = {".git", ".obsidian", "node_modules", "__pycache__", ".venv", ".trash", "build"}

_CER_WIKILINK = re.compile(r"\[\[([^\]|#]+)")
_CER_MARKDOWN_LINK = re.compile(r"\]\(([^)]+\.md)\)")


def _cer_base() -> Path:
    base = (RAIZ / PASTA_DE_NOTAS).resolve()
    if not base.is_dir():
        raise LookupError(
            f"`{PASTA_DE_NOTAS}` is not a folder that exists. Adjust PASTA_DE_NOTAS at the top of "
            "sondas.py — a zero because I did not look is worse than no number"
        )
    return base


def _cer_notas() -> list[Path]:
    """`os.walk` with `followlinks=True` — see the warning at the top of the file."""
    base = _cer_base()
    achadas: list[Path] = []
    for pasta, subpastas, arquivos in os.walk(base, followlinks=True):
        subpastas[:] = sorted(
            s for s in subpastas if s not in _CER_IGNORAR and not s.startswith(".")
        )
        achadas += [
            Path(pasta) / a for a in sorted(arquivos) if a.lower().endswith(_CER_EXTENSOES)
        ]
    if not achadas:
        raise LookupError(
            f"no note under `{PASTA_DE_NOTAS}` with extension {_CER_EXTENSOES}. "
            "Either the folder is wrong, or your notes have another extension — in both cases "
            "returning zero would be turning «I did not look» into «there is nothing»"
        )
    return achadas


def _cer_texto(nota: Path) -> str:
    return nota.read_text(encoding="utf-8", errors="replace")


def _cer_alvos_citados() -> dict[str, set[str]]:
    """source note -> names it cites, by wiki-link or markdown link."""
    citados: dict[str, set[str]] = {}
    for nota in _cer_notas():
        texto = _cer_texto(nota)
        alvos = {a.strip() for a in _CER_WIKILINK.findall(texto)}
        alvos |= {Path(a).stem for a in _CER_MARKDOWN_LINK.findall(texto)}
        citados[nota.stem] = {a for a in alvos if a}
    return citados


# ---------------------------------------------------------------------------
# The probes
# ---------------------------------------------------------------------------


@sonda("cerebro.notas", origem="servable files under the notes folder, via os.walk")
def cer_notas() -> int:
    return len(_cer_notas())


@sonda("cerebro.pastas", origem="first-level folders that contain at least one note")
def cer_pastas() -> int:
    base = _cer_base()
    return len({n.relative_to(base).parts[0] for n in _cer_notas() if n.parent != base})


@sonda(
    "cerebro.ferramentas",
    origem="entries in the FERRAMENTAS list in servidor.py — read from the code, not the documentation",
)
def cer_ferramentas() -> int:
    """A RELATION. It does not move when you write a note.

    It only moves when someone adds or removes a tool from the server — and then
    the documentation that promises four has started lying. It is the most
    direct pair of this operation: the number is in the `.md`, the truth is in
    the `.py`.
    """
    servidor = RAIZ / "servidor.py"
    if not servidor.is_file():
        raise LookupError(
            "`servidor.py` is not next to sondas.py. Copy the two together — without the "
            "server this metric has no second side, and one side alone verifies nothing"
        )
    texto = servidor.read_text(encoding="utf-8", errors="replace")
    bloco = re.search(r"^FERRAMENTAS\s*=\s*\[(.*?)^\]", texto, re.MULTILINE | re.DOTALL)
    if not bloco:
        raise LookupError("did not find the `FERRAMENTAS` list in servidor.py")
    return len(re.findall(r'^\s{4}\{\s*$', bloco.group(1), re.MULTILINE))


@sonda(
    "cerebro.orfas",
    origem="notes that no other note cites — neither by wiki-link, nor by markdown link",
)
def cer_orfas() -> int:
    """A RELATION, and it is the number that says whether your vault is a graph or a pile.

    An orphan note is not a bad note: it is a note only the author reaches. It
    shows up in no navigation, and the only way to get to it is to remember it
    exists — which is exactly what an external brain should make unnecessary.
    """
    citados = _cer_alvos_citados()
    alcancados = set().union(*citados.values()) if citados else set()
    return sum(1 for nome in citados if nome not in alcancados)


@sonda(
    "cerebro.links_quebrados",
    origem="targets of [[wiki-link]] and .md links that match no note",
)
def cer_links_quebrados() -> int:
    """A RELATION. A broken link is an edge to the void.

    ⚠️ It counts DISTINCT TARGETS, not occurrences. A wrong name cited in thirty
    notes is ONE broken link, and that is how the fix is measured: one name, one
    fix.
    """
    citados = _cer_alvos_citados()
    existentes = set(citados)
    quebrados = {alvo for alvos in citados.values() for alvo in alvos if alvo not in existentes}
    return len(quebrados)


@sonda("cerebro.sem_titulo", origem="notes whose first non-empty line is not a markdown title")
def cer_sem_titulo() -> int:
    sem = 0
    for nota in _cer_notas():
        linhas = [l for l in _cer_texto(nota).splitlines() if l.strip()]
        corpo = linhas[1:] if linhas and linhas[0].strip() == "---" else linhas
        if not corpo or not corpo[0].lstrip().startswith("#"):
            sem += 1
    return sem


@sonda("cerebro.maior_nota", origem="bytes of the largest servable file")
def cer_maior_nota() -> int:
    return max(n.stat().st_size for n in _cer_notas())


@sonda(
    "cerebro.dependencias",
    origem="third-party imports in servidor.py — it must be zero, and the probe proves it",
)
def cer_dependencias() -> int:
    """A RELATION, and it is the easiest promise to break without noticing.

    *"Zero dependencies"* is the sentence that makes someone run this on a
    machine they do not administer. It dies the day someone adds an `import` for
    convenience, and no code review catches it — the diff shows one line.
    """
    servidor = RAIZ / "servidor.py"
    if not servidor.is_file():
        raise LookupError("`servidor.py` is not next to sondas.py")
    stdlib = {
        "argparse", "json", "os", "sys", "re", "pathlib", "__future__",
        "dataclasses", "typing", "collections", "datetime", "textwrap", "unicodedata",
    }
    externos = set()
    for linha in servidor.read_text(encoding="utf-8", errors="replace").splitlines():
        achado = re.match(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", linha)
        if achado and achado.group(1).split(".")[0] not in stdlib:
            externos.add(achado.group(1).split(".")[0])
    return len(externos)
