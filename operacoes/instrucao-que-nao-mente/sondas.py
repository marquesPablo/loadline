"""Sondas da operação `instrucao-que-nao-mente`.

nature: fix — sonda que estoura vira `UNPROVEN` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_instr_`).

⚠️ **A regra anti-espelho, e como ela é respeitada aqui.** O número escrito mora
no arquivo de instrução (`AGENTS.md`, `CLAUDE.md`, …). Estas sondas LEEM esse
mesmo arquivo — mas nenhuma tira o VALOR dele. Elas extraem de lá as *promessas*
(o comando que ele manda rodar, o caminho que ele manda editar) e vão conferir
cada uma numa segunda fonte independente: `package.json`, o `Makefile`, o sistema
de arquivos. O par continua tendo dois lados; o que o arquivo de instrução
fornece é a pergunta, nunca a resposta.

O limite honesto disso está escrito no `LACUNAS.md` que a forja emite ao compilar
o agente desta operação, e vale a pena repetir: se ninguém CITA um comando no
arquivo de instrução, nada aqui descobre que ele existia e sumiu.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: Os arquivos que os harnesses de hoje leem como instrução. A lista é fechada e
#: cresce quando um harness novo aparece — nome desconhecido não é tratado como
#: inofensivo, ele simplesmente não é lido, e o denominador diz quantos foram.
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
    """Linhas de comando citadas dentro de cerca de código, e só elas.

    Comando citado em prosa não conta: `npm test` no meio de uma frase pode ser
    exemplo, contraexemplo ou o que NÃO fazer. Dentro da cerca é instrução.
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
    """`True` só quando dá para PROVAR que o alvo do comando não existe.

    Conservadora de propósito: o que ela não consegue decidir, ela deixa passar.
    Uma sonda que grita lobo é uma sonda que alguém apaga na segunda semana.
    """
    palavras = comando.split()
    if len(palavras) < 2:
        return False

    gerenciador, resto = palavras[0], palavras[1:]

    if gerenciador in {"npm", "pnpm", "yarn", "bun"}:
        scripts = _instr_scripts_do_pacote()
        if not scripts:  # sem package.json não há como decidir
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
    """Caminhos relativos citados entre crases. Só o que é inequivocamente caminho."""
    vistos: list[str] = []
    for bruto in _CRASE.findall(_instr_texto()):
        alvo = bruto.strip().rstrip(",.;:)")
        if not alvo or alvo.startswith(("http://", "https://", "/", "~", "-", "$")):
            continue
        if any(c in alvo for c in " <>*?{}|$\\\"'!"):
            continue
        if ":" in alvo:  # `arquivo.py:42` é endereço de linha, não caminho
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
# As sondas
# ---------------------------------------------------------------------------


@sonda("instrucao.arquivos", origem="arquivos de instrução presentes na raiz, pela lista fechada")
def arquivos_de_instrucao() -> int:
    return len(_instr_arquivos())


@sonda("instrucao.linhas", origem="soma das linhas dos arquivos de instrução")
def linhas_de_instrucao() -> int:
    return sum(
        len(p.read_text(encoding="utf-8", errors="replace").splitlines())
        for p in _instr_arquivos()
    )


@sonda("instrucao.comandos", origem="linhas de comando dentro de cerca de código, distintas")
def comandos_citados() -> int:
    return len(set(_instr_comandos()))


@sonda(
    "instrucao.comandos_quebrados",
    origem="comandos citados cujo script/alvo NÃO existe em package.json, Makefile ou no disco",
)
def comandos_quebrados() -> int:
    return sum(1 for c in set(_instr_comandos()) if _instr_quebrado(c))


@sonda("instrucao.caminhos", origem="caminhos relativos citados entre crases, distintos")
def caminhos_citados() -> int:
    return len(_instr_caminhos())


@sonda(
    "instrucao.caminhos_quebrados",
    origem="caminhos citados que NÃO existem no sistema de arquivos",
)
def caminhos_quebrados() -> int:
    return sum(1 for alvo in _instr_caminhos() if not (RAIZ / alvo).exists())


@sonda(
    "instrucao.divergencia",
    origem="títulos presentes em um arquivo de instrução e ausentes em outro",
)
def divergencia_entre_arquivos() -> int:
    arquivos = [p for p in _instr_arquivos() if p.suffix == ".md"]
    if len(arquivos) < 2:
        return 0
    titulos = [_instr_titulos(p) for p in arquivos]
    uniao: set[str] = set().union(*titulos)
    intersecao: set[str] = set(titulos[0]).intersection(*titulos[1:])
    return len(uniao - intersecao)
