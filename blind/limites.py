"""Where a naive scan stops without warning, and for which of the two reasons.

nature: fix — a boundary that cannot be classified becomes a "not verified"
item in the report, never an exception that takes down the whole run.

## The two causes, measured, never the same

**Cause 1 — structural.** A reparse point (a Windows junction, a directory
symlink on any system) is not descended into by a scan that does not ask for
it explicitly. It is the founding defect: `rg --files` without `-L` stops at
the boundary, `os.walk(followlinks=False)` stops too — but a Windows junction
**is not** a symlink (`os.path.islink` returns `False` for both; what gets it
right is `os.path.isjunction`, only from Python 3.12 on, or the reparse tag
`0xA0000003` read directly on earlier versions).

**Cause 2 — policy, not structure.** Inside a real git repository, a
`.gitignore` that lists the folder hides its contents from any tool that
respects ignore files — **even with the flag that crosses reparse points on**.
The two causes look the same from outside ("the tool did not see it") and need
a different fix: the first needs you to point at the real root; the second
needs `--no-ignore` or editing the `.gitignore`, and pointing at the real root
does NOT fix it by itself if the new root's own `.gitignore` also hides it.

Measured this session, with a synthetic fixture and a real `.git`:

    rg --files -L <folder-with-no-.git>                     → crosses the link
    rg --files -L <folder-with-.git-and-.gitignore>         → does NOT cross
    rg --files -L --no-ignore <the same, with .gitignore>   → crosses again
"""

from __future__ import annotations

import fnmatch
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

#: Files whose absence from someone's report is the worst possible case: they
#: are the ones that carry the instruction or the gate. An exact name, not a
#: pattern — an agent called "AGENTS.MD.bak" is not this file, and pretending
#: it is would be the same excess `vitrine`'s `V6` already decided not to commit.
ARQUIVOS_DE_DECLARACAO = frozenset({
    "CLAUDE.md", "AGENTS.md", "SKILL.md", "agent.toml", "settings.json",
})

#: A folder whose entire content is a declaration, even if the filename inside
#: it does not match the list above — `.claude/agents/*.md`,
#: `.claude/hooks/*.py`, `.claude/skills/**/SKILL.md`.
PASTA_DE_DECLARACAO = ".claude"

_JUNCTION_TAG = 0xA0000003  # IO_REPARSE_TAG_MOUNT_POINT


@dataclass
class Fronteira:
    """A point where a naive scan and a complete scan diverge."""

    tipo: str                                  #: "junction" · "symlink" · "gitignore"
    caminho: str                                #: relative to the evaluated root
    alvo: str | None = None                     #: for junction/symlink: the destination
    regra: str | None = None                    #: for gitignore: the pattern that matched
    arquivos_atras: list[str] = field(default_factory=list)  #: a hidden declaration, if any

    @property
    def grave(self) -> bool:
        """A boundary becomes a SERIOUS finding when it hides a real declaration.

        A junction with nothing sensitive behind it is a fact of the disk, not
        a defect — that is why it shows up in the report as a warning, never as
        a failure.
        """
        return bool(self.arquivos_atras)


def _tipo_do_link(caminho: Path) -> str | None:
    """"junction" · "symlink" · `None`. Never raises — called on every folder in the tree."""
    try:
        if os.path.islink(caminho):
            return "symlink"
        if hasattr(os.path, "isjunction"):                 # Python ≥ 3.12
            return "junction" if os.path.isjunction(caminho) else None
        tag = getattr(os.lstat(caminho), "st_reparse_tag", 0)
        return "junction" if tag == _JUNCTION_TAG else None
    except OSError:
        return None


def _e_declaracao(caminho: Path) -> bool:
    if caminho.name in ARQUIVOS_DE_DECLARACAO:
        return True
    return PASTA_DE_DECLARACAO in caminho.parts


def _arquivos_de_declaracao_sob(pasta: Path) -> list[str]:
    """An EXPLICIT scan of the boundary inwards — only called after the boundary
    has already been identified. It is not the naive scan; it is the tool
    proving what the naive one would fail to see.

    Returns a path relative TO THE BOUNDARY ITSELF, not to the evaluated root —
    the report already names the boundary once; repeating the prefix on every
    line would only have made the finding harder to read.
    """
    achados: list[str] = []
    try:
        for caminho in pasta.rglob("*"):
            if caminho.is_file() and _e_declaracao(caminho):
                achados.append(str(caminho.relative_to(pasta)))
    except OSError:
        pass
    return sorted(achados)


def _reparse_points(raiz: Path) -> list[Fronteira]:
    fronteiras: list[Fronteira] = []
    pilha = [raiz]
    while pilha:
        pasta = pilha.pop()
        try:
            entradas = sorted(pasta.iterdir())
        except OSError:
            continue
        for entrada in entradas:
            if not entrada.is_dir():
                continue
            tipo = _tipo_do_link(entrada)
            if tipo is None:
                pilha.append(entrada)  # an ordinary folder: descend normally
                continue
            try:
                alvo = str(entrada.resolve())
            except OSError:
                alvo = None
            fronteiras.append(Fronteira(
                tipo=tipo,
                caminho=str(entrada.relative_to(raiz)),
                alvo=alvo,
                arquivos_atras=_arquivos_de_declaracao_sob(entrada),
            ))
            # Do NOT descend into the boundary via the main stack — it was
            # already scanned separately by `_arquivos_de_declaracao_sob`.
            # Descending here too would count the same boundary at different depths.
    return fronteiras


def _raiz_do_git(caminho: Path) -> Path | None:
    """The folder with `.git`, walking up the tree — `None` if there is none.

    A `.gitignore` is only read by git-aware tools WHEN there is a real
    repository nearby (measured this session: the same `.gitignore`, outside a
    `.git`, has no effect at all on `rg`). Without this, the "gitignore hides a
    declaration" finding would fire even in a folder no tool would treat as
    ignored.
    """
    atual = caminho.resolve()
    for candidata in (atual, *atual.parents):
        if (candidata / ".git").exists():
            return candidata
    return None


def _ler_gitignore(caminho: Path) -> list[str]:
    """Raw patterns from a `.gitignore`. It is not git's full parser — it does
    not cover negation (`!pattern`) or `**` — and that is in `LACUNAS.md`."""
    try:
        linhas = caminho.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    return [ln.strip() for ln in linhas if ln.strip() and not ln.strip().startswith("#")]


def _padrao_bate(padrao: str, relativo_da_regra: str) -> bool:
    """A gitignore subset: a plain name, a leading `/` (anchored to the folder
    of the `.gitignore` itself), a trailing `/` (directory only), a wildcard via
    `fnmatch`. Documented as a floor in `LACUNAS.md` — not negation, not `**`."""
    alvo = padrao.rstrip("/")
    ancorado = alvo.startswith("/")
    alvo = alvo.lstrip("/")
    partes = Path(relativo_da_regra).parts
    if ancorado:
        return bool(partes) and fnmatch.fnmatch(partes[0], alvo)
    return any(fnmatch.fnmatch(parte, alvo) for parte in partes)


def _fronteiras_de_gitignore(raiz: Path) -> list[Fronteira]:
    raiz_git = _raiz_do_git(raiz)
    if raiz_git is None:
        return []

    fronteiras: list[Fronteira] = []
    for gitignore in raiz.rglob(".gitignore"):
        padroes = _ler_gitignore(gitignore)
        pasta_da_regra = gitignore.parent
        if not padroes:
            continue

        # Only the SHALLOWEST boundary that matches — a pattern like "vinculo"
        # matches "vinculo" and every descendant of it (`fnmatch` runs per path
        # component). Without this cut, each level below the same junction
        # became a repeated finding citing the same file.
        aceitas: list[Path] = []
        for caminho in sorted(pasta_da_regra.rglob("*"), key=lambda p: len(p.parts)):
            if not caminho.is_dir():
                continue
            if any(a in caminho.parents for a in aceitas):
                continue
            relativo = str(caminho.relative_to(pasta_da_regra))
            if any(_padrao_bate(p, relativo) for p in padroes):
                aceitas.append(caminho)

        for caminho in aceitas:
            atras = _arquivos_de_declaracao_sob(caminho)
            if not atras:
                continue
            relativo = str(caminho.relative_to(pasta_da_regra))
            regra = next(p for p in padroes if _padrao_bate(p, relativo))
            fronteiras.append(Fronteira(
                tipo="gitignore",
                caminho=str(caminho.relative_to(raiz)),
                regra=regra,
                arquivos_atras=atras,
            ))
    return fronteiras


def detectar(raiz: str | Path) -> list[Fronteira]:
    """Every boundary under `raiz` — a reparse point and a `.gitignore` rule
    that hides a declaration. Runs nothing, calls no model, only reads the disk."""
    caminho = Path(raiz).expanduser()
    achadas = _reparse_points(caminho) + _fronteiras_de_gitignore(caminho)
    return sorted(achadas, key=lambda f: (f.tipo, f.caminho))
