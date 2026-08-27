"""Probes for the `readme-que-nao-mente` operation.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with
the error written out. It never returns a guess.

COPY THIS FILE to the root of your repository, as `sondas.py`.
To combine with another operation, concatenate the files — no helper name here
collides with the others' (they all start with `_repo_`).

⚠️ **The anti-mirror rule.** The written number is in the `README.md`, in prose
written by hand. No probe here reads any `.md`: they read the code, the
dependency manifests and `git`. They are two independent artifacts — touching
one without touching the other fails, which is exactly the point.

⚠️ **And an honest limit.** These probes count what can be counted without
judging. `repo.testes` counts functions that LOOK LIKE a test by the language's
convention; it does not know whether the test tests anything. A count is not
quality, and this operation's agent `LACUNAS.md` says so in full.
"""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: Folders that are not the project. Counting them would make `repo.linhas` measure npm.
_REPO_IGNORAR = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env", "__pycache__",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", "dist", "build",
    "target", "vendor", ".next", ".nuxt", "coverage", "htmlcov", ".gradle",
    "site-packages", ".idea", ".vscode", ".terraform", "Pods", ".dart_tool",
}

_REPO_FONTE = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".rb", ".java", ".kt",
    ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".php", ".swift", ".scala",
    ".ex", ".exs", ".sh", ".sql", ".vue", ".svelte", ".dart", ".lua", ".zig",
}

_REPO_TESTE = re.compile(
    r"(?:^\s*(?:async\s+)?def\s+test_)"          # Python
    r"|(?:^\s*func\s+Test[A-Z])"                 # Go
    r"|(?:\b(?:it|test)\s*\(\s*[\"'`])"          # JS/TS: it(...) / test(...)
    r"|(?:^\s*#\[test\])"                        # Rust
    r"|(?:^\s*@Test\b)",                         # Java/Kotlin
    re.MULTILINE,
)

_REPO_PENDENCIA = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b[:( ]")


def _repo_andar():
    """Every project file, without the folders that are not the project."""
    pilha = [RAIZ]
    while pilha:
        pasta = pilha.pop()
        try:
            entradas = list(pasta.iterdir())
        except (PermissionError, OSError):
            continue
        for entrada in entradas:
            if entrada.is_dir():
                if entrada.name not in _REPO_IGNORAR and not entrada.is_symlink():
                    pilha.append(entrada)
            elif entrada.is_file():
                yield entrada


def _repo_fontes() -> list[Path]:
    return [p for p in _repo_andar() if p.suffix in _REPO_FONTE]


def _repo_ler(caminho: Path) -> str:
    try:
        return caminho.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return ""


def _repo_manifesto_python() -> dict:
    arquivo = RAIZ / "pyproject.toml"
    if not arquivo.is_file():
        return {}
    try:
        return tomllib.loads(arquivo.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        return {}


def _repo_manifesto_node() -> dict:
    arquivo = RAIZ / "package.json"
    if not arquivo.is_file():
        return {}
    try:
        return json.loads(arquivo.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _repo_dependencias(dev: bool) -> int:
    """Declared dependencies, summed over whatever manifests exist.

    Four ecosystems. None found returns `0`, and the `0` here is honest: it says
    *this repository declares no dependency in a manifest I read*, not *this
    repository has no dependency*. The difference is in `LACUNAS.md`.
    """
    total = 0

    py = _repo_manifesto_python()
    projeto = py.get("project") or {}
    if dev:
        for grupo in (projeto.get("optional-dependencies") or {}).values():
            total += len(grupo)
        total += sum(
            len(g) for g in ((py.get("dependency-groups") or {}).values())
        )
    else:
        total += len(projeto.get("dependencies") or [])

    node = _repo_manifesto_node()
    total += len(node.get("devDependencies" if dev else "dependencies") or {})

    if not dev:
        req = RAIZ / "requirements.txt"
        if req.is_file():
            total += sum(
                1
                for linha in _repo_ler(req).splitlines()
                if linha.strip() and not linha.lstrip().startswith(("#", "-"))
            )
        gomod = RAIZ / "go.mod"
        if gomod.is_file():
            total += len(re.findall(r"^\s+[\w./-]+\s+v", _repo_ler(gomod), re.MULTILINE))

    return total


# ---------------------------------------------------------------------------
# The probes
# ---------------------------------------------------------------------------


@sonda("repo.arquivos", origem="files outside the dependency and build folders")
def arquivos() -> int:
    return sum(1 for _ in _repo_andar())


@sonda("repo.fontes", origem="files with a programming-language extension")
def fontes() -> int:
    return len(_repo_fontes())


@sonda("repo.linhas", origem="summed lines of the source files")
def linhas() -> int:
    return sum(len(_repo_ler(p).splitlines()) for p in _repo_fontes())


@sonda("repo.linguagens", origem="distinct language extensions present")
def linguagens() -> int:
    return len({p.suffix for p in _repo_fontes()})


@sonda("repo.testes", origem="test functions by each language's convention")
def testes() -> int:
    return sum(len(_REPO_TESTE.findall(_repo_ler(p))) for p in _repo_fontes())


@sonda("repo.arquivos_de_teste", origem="files whose name follows the test convention")
def arquivos_de_teste() -> int:
    return sum(
        1
        for p in _repo_fontes()
        if p.name.startswith("test_")
        or p.stem.endswith(("_test", ".test", ".spec", "_spec", "Test", "Tests"))
    )


@sonda("repo.dependencias", origem="production dependencies in pyproject/package.json/requirements/go.mod")
def dependencias() -> int:
    return _repo_dependencias(dev=False)


@sonda("repo.dependencias_dev", origem="development dependencies in the same manifests")
def dependencias_dev() -> int:
    return _repo_dependencias(dev=True)


@sonda("repo.workflows", origem=".yml/.yaml files in .github/workflows/")
def workflows() -> int:
    pasta = RAIZ / ".github" / "workflows"
    if not pasta.is_dir():
        return 0
    return sum(1 for p in pasta.iterdir() if p.suffix in {".yml", ".yaml"})


@sonda("repo.pendencias", origem="TODO/FIXME/XXX/HACK marks in the source code")
def pendencias() -> int:
    return sum(len(_REPO_PENDENCIA.findall(_repo_ler(p))) for p in _repo_fontes())


@sonda("repo.maior_arquivo", origem="lines of the largest source file")
def maior_arquivo() -> int:
    return max((len(_repo_ler(p).splitlines()) for p in _repo_fontes()), default=0)


@sonda("repo.contribuidores", origem="distinct authors in `git shortlog -sne --all`")
def contribuidores() -> int:
    """Comes from `git`. With no git repository it blows up and becomes
    `UNPROVEN` — which is the right answer: *cannot be verified* must never
    become *zero*."""
    saida = subprocess.run(
        ["git", "-C", str(RAIZ), "shortlog", "-sne", "--all", "--no-merges"],
        capture_output=True, text=True, timeout=30, check=True, stdin=subprocess.DEVNULL,
    )
    return len([linha for linha in saida.stdout.splitlines() if linha.strip()])


@sonda("repo.commits", origem="`git rev-list --count HEAD`")
def commits() -> int:
    saida = subprocess.run(
        ["git", "-C", str(RAIZ), "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, timeout=30, check=True, stdin=subprocess.DEVNULL,
    )
    return int(saida.stdout.strip())
