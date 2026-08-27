"""Probes for the `instrucao-que-nao-mente` operation.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with
the error written out. It never returns a guess.

COPY THIS FILE to the root of your repository, as `sondas.py`.
To combine with another operation, concatenate the files — no helper name here
collides with the others' (they all start with `_instr_`).

⚠️ **The anti-mirror rule, and how it is respected here.** The written number
lives in the instruction file (`AGENTS.md`, `CLAUDE.md`, …). These probes READ
that same file — but none of them takes the VALUE from it. They extract the
*promises* from there (the command it tells you to run, the path it tells you
to edit) and go check each one against a second independent source:
`package.json`, the `Makefile`, the file system. The pair still has two sides;
what the instruction file provides is the question, never the answer.

The honest limit of this is written in the `LACUNAS.md` the forge emits when it
compiles this operation's agent, and it is worth repeating: if nobody CITES a
command in the instruction file, nothing here finds that it existed and
disappeared.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: The files today's harnesses read as an instruction. The list is closed and
#: grows when a new harness appears — an unknown name is not treated as
#: harmless, it simply is not read, and the denominator says how many were.
NOMES_DE_INSTRUCAO = (
    "AGENTS.md",
    "AGENT.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursorrules",
    ".windsurfrules",
    ".clinerules",
    ".github/copilot-instructions.md",
    ".github/instructions",
)

_CERCA = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
_CRASE = re.compile(r"`([^`\n]{2,120})`")


def _instr_arquivos() -> list[Path]:
    achados = []
    for nome in NOMES_DE_INSTRUCAO:
        caminho = RAIZ / nome
        if caminho.is_file():
            achados.append(caminho)
        elif caminho.is_dir():
            achados.extend(sorted(p for p in caminho.rglob("*.md") if p.is_file()))
    return achados


def _instr_texto() -> str:
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in _instr_arquivos())


def _instr_comandos() -> list[str]:
    """Command lines cited inside a code fence, and only those.

    A command cited in prose does not count: `npm test` in the middle of a
    sentence can be an example, a counter-example or what NOT to do. Inside the
    fence it is an instruction.
    """
    linhas: list[str] = []
    for bloco in _CERCA.findall(_instr_texto()):
        for bruta in bloco.splitlines():
            linha = bruta.strip().lstrip("$").strip()
            if not linha or linha.startswith("#"):
                continue
            linhas.append(linha)
    return linhas


def _instr_scripts_do_pacote() -> set[str]:
    arquivo = RAIZ / "package.json"
    if not arquivo.is_file():
        return set()
    try:
        return set((json.loads(arquivo.read_text(encoding="utf-8")).get("scripts") or {}).keys())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return set()


def _instr_alvos_de_make() -> set[str]:
    alvos: set[str] = set()
    for nome in ("Makefile", "makefile", "GNUmakefile", "justfile", "Justfile"):
        arquivo = RAIZ / nome
        if not arquivo.is_file():
            continue
        for linha in arquivo.read_text(encoding="utf-8", errors="replace").splitlines():
            achado = re.match(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*)\s*:(?!=)", linha)
            if achado:
                alvos.add(achado.group(1))
    return alvos


def _instr_quebrado(comando: str) -> bool:
    """`True` only when it can PROVE the command's target does not exist.

    Conservative on purpose: what it cannot decide, it lets through. A probe
    that cries wolf is a probe someone deletes in the second week.
    """
    palavras = comando.split()
    if len(palavras) < 2:
        return False

    gerenciador, resto = palavras[0], palavras[1:]

    if gerenciador in {"npm", "pnpm", "yarn", "bun"}:
        scripts = _instr_scripts_do_pacote()
        if not scripts:  # no package.json, no way to decide
            return False
        if resto[0] in {"run", "run-script"} and len(resto) > 1:
            return resto[1] not in scripts
        if gerenciador in {"yarn", "bun"} and resto[0] not in {
            "add", "install", "remove", "why", "up", "init", "link", "x", "create",
        }:
            return resto[0] not in scripts
        return False

    if gerenciador in {"make", "just"}:
        alvos = _instr_alvos_de_make()
        if not alvos:
            return False
        nomeados = [p for p in resto if not p.startswith("-")]
        return bool(nomeados) and nomeados[0] not in alvos

    if gerenciador in {"python", "python3", "py"}:
        nomeados = [p for p in resto if not p.startswith("-")]
        if "-m" in resto and nomeados:
            modulo = nomeados[0].replace(".", "/")
            return not (
                (RAIZ / f"{modulo}.py").exists() or (RAIZ / modulo / "__init__.py").exists()
            )
        if nomeados and nomeados[0].endswith(".py"):
            return not (RAIZ / nomeados[0]).exists()

    return False


def _instr_caminhos() -> list[str]:
    """Relative paths cited between backticks. Only what is unambiguously a path."""
    vistos: list[str] = []
    for bruto in _CRASE.findall(_instr_texto()):
        alvo = bruto.strip().rstrip(",.;:)")
        if not alvo or alvo.startswith(("http://", "https://", "/", "~", "-", "$")):
            continue
        if any(c in alvo for c in " <>*?{}|$\\\"'!"):
            continue
        if ":" in alvo:  # `arquivo.py:42` is a line address, not a path
            continue
        tem_pasta = "/" in alvo
        tem_extensao = re.search(r"\.[a-z0-9]{1,5}$", alvo) is not None
        if not (tem_pasta or tem_extensao):
            continue
        if alvo not in vistos:
            vistos.append(alvo)
    return vistos


def _instr_titulos(arquivo: Path) -> set[str]:
    texto = arquivo.read_text(encoding="utf-8", errors="replace")
    return {
        re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
        for t in re.findall(r"^#{1,4}\s+(.+?)\s*$", texto, re.MULTILINE)
    }


# ---------------------------------------------------------------------------
# The probes
# ---------------------------------------------------------------------------


@sonda("instrucao.arquivos", origem="instruction files present at the root, from the closed list")
def arquivos_de_instrucao() -> int:
    return len(_instr_arquivos())


@sonda("instrucao.linhas", origem="the sum of the instruction files' lines")
def linhas_de_instrucao() -> int:
    return sum(
        len(p.read_text(encoding="utf-8", errors="replace").splitlines())
        for p in _instr_arquivos()
    )


@sonda("instrucao.comandos", origem="distinct command lines inside a code fence")
def comandos_citados() -> int:
    return len(set(_instr_comandos()))


@sonda(
    "instrucao.comandos_quebrados",
    origem="cited commands whose script/target does NOT exist in package.json, Makefile or on disk",
)
def comandos_quebrados() -> int:
    return sum(1 for c in set(_instr_comandos()) if _instr_quebrado(c))


@sonda("instrucao.caminhos", origem="distinct relative paths cited between backticks")
def caminhos_citados() -> int:
    return len(_instr_caminhos())


@sonda(
    "instrucao.caminhos_quebrados",
    origem="cited paths that do NOT exist on the file system",
)
def caminhos_quebrados() -> int:
    return sum(1 for alvo in _instr_caminhos() if not (RAIZ / alvo).exists())


@sonda(
    "instrucao.divergencia",
    origem="headings present in one instruction file and absent from another",
)
def divergencia_entre_arquivos() -> int:
    arquivos = [p for p in _instr_arquivos() if p.suffix == ".md"]
    if len(arquivos) < 2:
        return 0
    titulos = [_instr_titulos(p) for p in arquivos]
    uniao: set[str] = set().union(*titulos)
    intersecao: set[str] = set(titulos[0]).intersection(*titulos[1:])
    return len(uniao - intersecao)
