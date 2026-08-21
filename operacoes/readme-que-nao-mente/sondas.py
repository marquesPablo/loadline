"""Sondas da operação `readme-que-nao-mente`.

natureza: correcao — sonda que estoura vira `SEM_PROVA` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_repo_`).

⚠️ **A regra anti-espelho.** O número escrito está no `README.md`, em prosa
escrita à mão. Nenhuma sonda daqui lê `.md` nenhum: elas leem o código, os
manifestos de dependência e o `git`. São dois artefatos independentes — mexer
num sem mexer no outro reprova, que é exatamente o ponto.

⚠️ **E um limite honesto.** Estas sondas contam o que dá para contar sem julgar.
`repo.testes` conta funções que PARECEM teste pela convenção da linguagem; ela
não sabe se o teste testa alguma coisa. Contagem não é qualidade, e o
`LACUNAS.md` do agente desta operação diz isso por extenso.
"""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from pathlib import Path

from aferido import sonda

RAIZ = Path(__file__).resolve().parent

#: Pastas que não são o projeto. Contá-las faria `repo.linhas` medir o npm.
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
    """Todo arquivo do projeto, sem as pastas que não são o projeto."""
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
    """Dependências declaradas, somadas sobre os manifestos que existirem.

    Quatro ecossistemas. Nenhum encontrado devolve `0`, e o `0` aqui é honesto:
    ele diz *este repositório não declara dependência em manifesto que eu leia*,
    não *este repositório não tem dependência*. A diferença está no `LACUNAS.md`.
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
# As sondas
# ---------------------------------------------------------------------------


@sonda("repo.arquivos", origem="arquivos fora das pastas de dependência e de build")
def arquivos() -> int:
    return sum(1 for _ in _repo_andar())


@sonda("repo.fontes", origem="arquivos com extensão de linguagem de programação")
def fontes() -> int:
    return len(_repo_fontes())


@sonda("repo.linhas", origem="linhas somadas dos arquivos de código-fonte")
def linhas() -> int:
    return sum(len(_repo_ler(p).splitlines()) for p in _repo_fontes())


@sonda("repo.linguagens", origem="extensões de linguagem distintas presentes")
def linguagens() -> int:
    return len({p.suffix for p in _repo_fontes()})


@sonda("repo.testes", origem="funções de teste pela convenção de cada linguagem")
def testes() -> int:
    return sum(len(_REPO_TESTE.findall(_repo_ler(p))) for p in _repo_fontes())


@sonda("repo.arquivos_de_teste", origem="arquivos cujo nome segue a convenção de teste")
def arquivos_de_teste() -> int:
    return sum(
        1
        for p in _repo_fontes()
        if p.name.startswith("test_")
        or p.stem.endswith(("_test", ".test", ".spec", "_spec", "Test", "Tests"))
    )


@sonda("repo.dependencias", origem="dependências de produção em pyproject/package.json/requirements/go.mod")
def dependencias() -> int:
    return _repo_dependencias(dev=False)


@sonda("repo.dependencias_dev", origem="dependências de desenvolvimento nos mesmos manifestos")
def dependencias_dev() -> int:
    return _repo_dependencias(dev=True)


@sonda("repo.workflows", origem="arquivos .yml/.yaml em .github/workflows/")
def workflows() -> int:
    pasta = RAIZ / ".github" / "workflows"
    if not pasta.is_dir():
        return 0
    return sum(1 for p in pasta.iterdir() if p.suffix in {".yml", ".yaml"})


@sonda("repo.pendencias", origem="marcas TODO/FIXME/XXX/HACK no código-fonte")
def pendencias() -> int:
    return sum(len(_REPO_PENDENCIA.findall(_repo_ler(p))) for p in _repo_fontes())


@sonda("repo.maior_arquivo", origem="linhas do maior arquivo de código-fonte")
def maior_arquivo() -> int:
    return max((len(_repo_ler(p).splitlines()) for p in _repo_fontes()), default=0)


@sonda("repo.contribuidores", origem="autores distintos em `git shortlog -sne --all`")
def contribuidores() -> int:
    """Sai de `git`. Sem repositório git, ela estoura e vira `SEM_PROVA` — que é
    a resposta certa: *não dá para conferir* nunca deve virar *zero*."""
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
