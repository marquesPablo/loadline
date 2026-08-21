"""Sondas da operação `dependencia-com-veredito`.

natureza: correcao — sonda que estoura vira `SEM_PROVA` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_dep_`).

⚠️ **A regra anti-espelho, e aqui ela é o produto inteiro.** Há duas fontes, e
elas têm donos diferentes: o **manifesto** (`package.json`, `pyproject.toml`, …)
é escrito pela máquina toda vez que alguém instala alguma coisa; a **tabela de
vereditos** é escrita por um humano que foi ler a licença. A sonda mede a
distância entre as duas. Um repositório onde as duas coincidem é um repositório
onde alguém olhou cada dependência.

`deps.sem_veredito` sair de zero significa exatamente uma coisa: **entrou
dependência e ninguém olhou.** É o defeito, não a contagem.

⚠️ **E o limite honesto:** nada aqui LÊ licença. A verdade sobre a licença de um
pacote está na página dele, e nenhuma sonda offline a alcança. A tabela é o que
um humano escreveu depois de ir olhar; o `vence=` é o que obriga alguém a ir
olhar de novo.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from aferido import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO desta operação: onde mora a sua tabela de vereditos.
#: Qualquer arquivo de texto serve. O formato exigido é uma linha por
#: dependência contendo o NOME dela e um dos vereditos abaixo.
TABELA_DE_VEREDITOS = "licencas.md"

#: Vocabulário fechado. Um veredito fora desta lista não é lido — e a dependência
#: conta como SEM veredito, que é a leitura que não vira porta dos fundos.
_DEP_VEREDITOS = (
    "osi",                  # licença aprovada pela OSI, permissiva
    "osi_copyleft_forte",   # OSI, e alcança quem usa em rede
    "nao_osi",              # apresenta-se como aberta e não é
    "proprietaria",
    "dominio_publico",
    "nao_verificado",       # alguém olhou e não conseguiu decidir — vale, e é honesto
)

_DEP_NOME = re.compile(r"^[A-Za-z0-9@._/-]+$")


def _dep_manifesto_python() -> dict:
    arquivo = RAIZ / "pyproject.toml"
    if not arquivo.is_file():
        return {}
    try:
        return tomllib.loads(arquivo.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        return {}


def _dep_manifesto_node() -> dict:
    arquivo = RAIZ / "package.json"
    if not arquivo.is_file():
        return {}
    try:
        return json.loads(arquivo.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _dep_nome_python(requisito: str) -> str:
    """`requests>=2.0,<3` -> `requests`. Extra e marcador ficam de fora."""
    return re.split(r"[<>=!~\[; ]", requisito.strip(), maxsplit=1)[0].strip()


def _dep_declaradas() -> set[str]:
    """Toda dependência declarada, de produção e de desenvolvimento, sem versão."""
    nomes: set[str] = set()

    py = _dep_manifesto_python()
    projeto = py.get("project") or {}
    for requisito in projeto.get("dependencies") or []:
        nomes.add(_dep_nome_python(str(requisito)))
    for grupo in (projeto.get("optional-dependencies") or {}).values():
        nomes.update(_dep_nome_python(str(r)) for r in grupo)
    for grupo in (py.get("dependency-groups") or {}).values():
        nomes.update(_dep_nome_python(str(r)) for r in grupo if isinstance(r, str))

    node = _dep_manifesto_node()
    for chave in ("dependencies", "devDependencies", "peerDependencies"):
        nomes.update((node.get(chave) or {}).keys())

    req = RAIZ / "requirements.txt"
    if req.is_file():
        for linha in req.read_text(encoding="utf-8", errors="replace").splitlines():
            limpa = linha.strip()
            if limpa and not limpa.startswith(("#", "-")):
                nomes.add(_dep_nome_python(limpa))

    gomod = RAIZ / "go.mod"
    if gomod.is_file():
        texto = gomod.read_text(encoding="utf-8", errors="replace")
        nomes.update(re.findall(r"^\s+([\w./-]+)\s+v", texto, re.MULTILINE))

    return {n for n in nomes if n and _DEP_NOME.match(n)}


def _dep_tabela() -> dict[str, str]:
    """Nome -> veredito, lido da tabela escrita à mão. Ausente devolve vazio.

    Ausente NUNCA vira "todas sem veredito por zero dependências": as sondas que
    dependem da tabela estouram quando ela não existe, e viram `SEM_PROVA`.
    """
    arquivo = RAIZ / TABELA_DE_VEREDITOS
    if not arquivo.is_file():
        raise FileNotFoundError(
            f"`{TABELA_DE_VEREDITOS}` não existe. Esta operação compara o manifesto com uma "
            "tabela escrita por um humano que foi ler as licenças — sem ela não há segundo "
            "lado, e um lado só não verifica nada. Crie o arquivo, mesmo vazio, e a sonda "
            "passa a dizer quantas dependências ninguém olhou."
        )
    vereditos: dict[str, str] = {}
    for linha in arquivo.read_text(encoding="utf-8", errors="replace").splitlines():
        # O veredito mais longo ganha: `osi_copyleft_forte` contém `osi`, e ler
        # o curto primeiro classificaria um copyleft forte como permissivo.
        achado = next(
            (
                v
                for v in sorted(_DEP_VEREDITOS, key=len, reverse=True)
                if re.search(rf"(?<![\w-]){v}(?![\w-])", linha)
            ),
            None,
        )
        if not achado:
            continue
        # O nome da dependência vai ENTRE CRASES. É a convenção desta operação, e
        # ela existe para não confundir o nome do pacote com o da licença: numa
        # linha `| react | MIT | osi |` as duas primeiras células são
        # indistinguíveis para qualquer regra que não olhe a marcação.
        for nome in re.findall(r"`([A-Za-z0-9@._/-]{2,})`", linha):
            if nome in _DEP_VEREDITOS or nome.startswith("http"):
                continue
            vereditos.setdefault(nome, achado)
    return vereditos


def _dep_por_veredito(alvo: str) -> int:
    tabela = _dep_tabela()
    declaradas = _dep_declaradas()
    return sum(1 for nome, v in tabela.items() if v == alvo and nome in declaradas)


# ---------------------------------------------------------------------------
# As sondas
# ---------------------------------------------------------------------------


@sonda("deps.declaradas", origem="nomes distintos em pyproject/package.json/requirements/go.mod")
def declaradas() -> int:
    return len(_dep_declaradas())


@sonda(
    "deps.sem_veredito",
    origem="dependências do manifesto que NÃO têm linha na tabela de vereditos",
)
def sem_veredito() -> int:
    tabela = _dep_tabela()
    return sum(1 for nome in _dep_declaradas() if nome not in tabela)


@sonda(
    "deps.veredito_orfao",
    origem="linhas da tabela de vereditos cuja dependência não está mais no manifesto",
)
def veredito_orfao() -> int:
    """O sentido contrário, e ele também é defeito.

    Um veredito sobre uma dependência que saiu do projeto é julgamento que
    envelheceu: ninguém o apagou, e ele continua parecendo cobertura.
    """
    declaradas_agora = _dep_declaradas()
    return sum(1 for nome in _dep_tabela() if nome not in declaradas_agora)


@sonda("deps.osi", origem="dependências do manifesto com veredito `osi` na tabela")
def osi() -> int:
    return _dep_por_veredito("osi")


@sonda("deps.copyleft_forte", origem="dependências com veredito `osi_copyleft_forte` na tabela")
def copyleft_forte() -> int:
    return _dep_por_veredito("osi_copyleft_forte")


@sonda("deps.nao_osi", origem="dependências com veredito `nao_osi` na tabela")
def nao_osi() -> int:
    return _dep_por_veredito("nao_osi")


@sonda("deps.proprietarias", origem="dependências com veredito `proprietaria` na tabela")
def proprietarias() -> int:
    return _dep_por_veredito("proprietaria")


@sonda(
    "deps.nao_verificado",
    origem="dependências que alguém OLHOU e não conseguiu decidir — nunca as que ninguém olhou",
)
def nao_verificado() -> int:
    """A diferença entre esta e `deps.sem_veredito` é a operação inteira.

    `nao_verificado` é um humano que foi lá, tentou e não decidiu — é dado.
    `sem_veredito` é ninguém ter ido. Somá-las apagaria a única informação que
    importa: se alguém olhou.
    """
    return _dep_por_veredito("nao_verificado")
