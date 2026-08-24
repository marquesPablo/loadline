"""Sondas da operação `cerebro-local`.

natureza: correcao — sonda que estoura vira `UNPROVEN` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_cer_`).

⚠️ **A regra anti-espelho, aqui.** O número escrito mora na sua documentação
("temos 340 notas", "o servidor expõe 4 ferramentas"). O número medido sai do
**sistema de arquivos** e do **código do servidor** — nunca do `.md` que o
afirma. Os dois lados têm donos diferentes, que é o que faz o par valer.

⚠️ **A armadilha que domina esta operação, e ela não dá erro.** `rg`, `grep -r`
e `find` **não atravessam junction do Windows nem symlink de diretório**, e não
avisam: a resposta volta plausível, sem erro, e sem os arquivos de dentro. Num
vault de conhecimento as pastas ligadas são a regra, não a exceção. Estas sondas
usam `os.walk(followlinks=True)`, que atravessa. Se você reescrever qualquer uma
delas chamando `grep` por `subprocess`, o número cai e nada acusa.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO desta operação: onde moram as suas notas, relativo a este arquivo.
#: `"."` significa "o repositório inteiro".
PASTA_DE_NOTAS = "."

#: Precisa bater com `EXTENSOES` do `servidor.py`. Se divergirem, a sonda conta
#: um corpus e o servidor serve outro — e o selo verde estaria medindo a coisa
#: errada. A sonda `cerebro.ferramentas` existe justamente para ancorar isto.
_CER_EXTENSOES = (".md", ".markdown", ".txt", ".org")
_CER_IGNORAR = {".git", ".obsidian", "node_modules", "__pycache__", ".venv", ".trash", "build"}

_CER_WIKILINK = re.compile(r"\[\[([^\]|#]+)")
_CER_MARKDOWN_LINK = re.compile(r"\]\(([^)]+\.md)\)")


def _cer_base() -> Path:
    base = (RAIZ / PASTA_DE_NOTAS).resolve()
    if not base.is_dir():
        raise LookupError(
            f"`{PASTA_DE_NOTAS}` não é uma pasta que existe. Ajuste PASTA_DE_NOTAS no topo de "
            "sondas.py — um zero por eu não ter olhado é pior que nenhum número"
        )
    return base


def _cer_notas() -> list[Path]:
    """`os.walk` com `followlinks=True` — ver o aviso do topo do arquivo."""
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
            f"nenhuma nota sob `{PASTA_DE_NOTAS}` com extensão {_CER_EXTENSOES}. "
            "Ou a pasta está errada, ou as suas notas têm outra extensão — nos dois casos "
            "devolver zero seria transformar «não olhei» em «não há»"
        )
    return achadas


def _cer_texto(nota: Path) -> str:
    return nota.read_text(encoding="utf-8", errors="replace")


def _cer_alvos_citados() -> dict[str, set[str]]:
    """nota de origem -> nomes que ela cita, por wiki-link ou link markdown."""
    citados: dict[str, set[str]] = {}
    for nota in _cer_notas():
        texto = _cer_texto(nota)
        alvos = {a.strip() for a in _CER_WIKILINK.findall(texto)}
        alvos |= {Path(a).stem for a in _CER_MARKDOWN_LINK.findall(texto)}
        citados[nota.stem] = {a for a in alvos if a}
    return citados


# ---------------------------------------------------------------------------
# As sondas
# ---------------------------------------------------------------------------


@sonda("cerebro.notas", origem="arquivos servíveis sob a pasta de notas, via os.walk")
def cer_notas() -> int:
    return len(_cer_notas())


@sonda("cerebro.pastas", origem="pastas de primeiro nível que contêm ao menos uma nota")
def cer_pastas() -> int:
    base = _cer_base()
    return len({n.relative_to(base).parts[0] for n in _cer_notas() if n.parent != base})


@sonda(
    "cerebro.ferramentas",
    origem="entradas da lista FERRAMENTAS em servidor.py — lido do código, não da documentação",
)
def cer_ferramentas() -> int:
    """De RELAÇÃO. Ela não anda quando você escreve uma nota.

    Ela só anda quando alguém acrescenta ou tira uma ferramenta do servidor — e
    aí a documentação que promete quatro passou a mentir. É o par mais direto
    desta operação: o número está no `.md`, a verdade está no `.py`.
    """
    servidor = RAIZ / "servidor.py"
    if not servidor.is_file():
        raise LookupError(
            "`servidor.py` não está ao lado de sondas.py. Copie os dois juntos — sem o "
            "servidor esta métrica não tem segundo lado, e um lado só não verifica nada"
        )
    texto = servidor.read_text(encoding="utf-8", errors="replace")
    bloco = re.search(r"^FERRAMENTAS\s*=\s*\[(.*?)^\]", texto, re.MULTILINE | re.DOTALL)
    if not bloco:
        raise LookupError("não achei a lista `FERRAMENTAS` em servidor.py")
    return len(re.findall(r'^\s{4}\{\s*$', bloco.group(1), re.MULTILINE))


@sonda(
    "cerebro.orfas",
    origem="notas que nenhuma outra nota cita — nem por wiki-link, nem por link markdown",
)
def cer_orfas() -> int:
    """De RELAÇÃO, e é o número que diz se o seu vault é um grafo ou uma pilha.

    Uma nota órfã não é uma nota ruim: é uma nota que só o autor alcança. Ela
    não aparece em navegação nenhuma, e a única forma de chegar nela é lembrar
    que ela existe — que é exatamente o que um cérebro externo deveria dispensar.
    """
    citados = _cer_alvos_citados()
    alcancados = set().union(*citados.values()) if citados else set()
    return sum(1 for nome in citados if nome not in alcancados)


@sonda(
    "cerebro.links_quebrados",
    origem="alvos de [[wiki-link]] e de link .md que não correspondem a nenhuma nota",
)
def cer_links_quebrados() -> int:
    """De RELAÇÃO. Um link quebrado é uma aresta para o vazio.

    ⚠️ Ele conta ALVOS DISTINTOS, não ocorrências. Um nome errado citado em
    trinta notas é UM link quebrado, e é assim que o conserto se mede: um nome,
    um conserto.
    """
    citados = _cer_alvos_citados()
    existentes = set(citados)
    quebrados = {alvo for alvos in citados.values() for alvo in alvos if alvo not in existentes}
    return len(quebrados)


@sonda("cerebro.sem_titulo", origem="notas cuja primeira linha não-vazia não é um título markdown")
def cer_sem_titulo() -> int:
    sem = 0
    for nota in _cer_notas():
        linhas = [l for l in _cer_texto(nota).splitlines() if l.strip()]
        corpo = linhas[1:] if linhas and linhas[0].strip() == "---" else linhas
        if not corpo or not corpo[0].lstrip().startswith("#"):
            sem += 1
    return sem


@sonda("cerebro.maior_nota", origem="bytes do maior arquivo servível")
def cer_maior_nota() -> int:
    return max(n.stat().st_size for n in _cer_notas())


@sonda(
    "cerebro.dependencias",
    origem="imports de terceiros em servidor.py — tem de ser zero, e a sonda prova",
)
def cer_dependencias() -> int:
    """De RELAÇÃO, e é a promessa mais fácil de quebrar sem perceber.

    *"Zero dependências"* é a frase que faz alguém rodar isto numa máquina que
    não administra. Ela morre no dia em que alguém acrescenta um `import` por
    conveniência, e nenhuma revisão de código repara — o diff mostra uma linha.
    """
    servidor = RAIZ / "servidor.py"
    if not servidor.is_file():
        raise LookupError("`servidor.py` não está ao lado de sondas.py")
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
