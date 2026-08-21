"""Sondas da operação `fronteira-de-agente`.

natureza: correcao — sonda que estoura vira `SEM_PROVA` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_front_`).

⚠️ **A regra anti-espelho.** O número escrito está no seu `README.md` ou no seu
`AGENTS.md`, em prosa. Estas sondas leem `.claude/agents/*.md` e
`.claude/settings.json` — dois artefatos de configuração que ninguém escreve
pensando no número. E a checagem de cerca cruza os dois: um agente declara a
ferramenta num arquivo, e o hook que a cerca é registrado noutro. **Nenhum dos
dois sozinho responde a pergunta.**

⚠️ **O que esta operação mede é FRONTEIRA DECLARADA, não segurança.** Um hook
registrado pode estar quebrado, ou liberar tudo. A sonda vê que ele existe; se
ele nega de verdade é outra pergunta, e o `LACUNAS.md` do agente a nomeia.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from aferido import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO desta operação: onde moram os seus subagentes.
#: Claude Code usa `.claude/agents/`. Se o seu harness usa outro caminho,
#: acrescente-o aqui — a lista é lida inteira, e pasta ausente não é erro.
PASTAS_DE_AGENTE = (
    ".claude/agents",
    ".config/agents",
    "agents",
)

#: O vocabulário fechado das ferramentas que saem da máquina e das que escrevem
#: no disco. Nome fora desta lista NÃO é tratado como inofensivo — ele entra em
#: `agentes.ferramentas_desconhecidas`, porque tratar desconhecido como seguro é
#: como toda cerca vira porta dos fundos.
_FRONT_REDE = frozenset({"WebFetch", "WebSearch", "Fetch", "Browser", "http", "curl"})
_FRONT_ESCRITA = frozenset({"Write", "Edit", "NotebookEdit", "MultiEdit", "apply_patch"})
_FRONT_EXECUCAO = frozenset({"Bash", "PowerShell", "Shell", "Terminal", "Execute"})
_FRONT_LEITURA = frozenset({"Read", "Grep", "Glob", "TodoWrite", "Task", "AskUserQuestion"})
_FRONT_CONHECIDAS = _FRONT_REDE | _FRONT_ESCRITA | _FRONT_EXECUCAO | _FRONT_LEITURA

#: Palavras que marcam anti-descrição — o «quando NÃO me use» sem o qual um
#: orquestrador despacha por semelhança de tema.
_FRONT_ANTI = re.compile(
    r"\b(nunca|never|não use|nao use|do not use|don't use|avoid using)\b", re.IGNORECASE
)


def _front_arquivos() -> list[Path]:
    """Todo artefato de agente sob as pastas declaradas.

    ⚠️ **Nenhuma das pastas existir ESTOURA, e não devolve lista vazia.** É a
    regra que esta operação existe para aplicar, aplicada a ela mesma: um
    `agentes.rede_sem_cerca = 0` porque ninguém achou a pasta é indistinguível
    de um `0` medido — e o primeiro sai VERDE no CI de quem confia nele.

    *"Não olhei"* e *"olhei e não há"* dizem coisas opostas. Uma pasta que
    existe e está vazia é a segunda, e devolve `0` normalmente.
    """
    achados: list[Path] = []
    achou_pasta = False
    for relativo in PASTAS_DE_AGENTE:
        pasta = RAIZ / relativo
        if pasta.is_dir():
            achou_pasta = True
            achados.extend(sorted(p for p in pasta.rglob("*.md") if p.is_file()))
    if not achou_pasta:
        raise LookupError(
            "nenhuma das pastas de agente existe: "
            f"{', '.join(PASTAS_DE_AGENTE)}. Se os seus agentes moram noutro lugar, ajuste "
            "PASTAS_DE_AGENTE no topo de sondas.py — devolver zero aqui seria dizer que "
            "você não tem agente sem cerca, quando o que houve foi eu não ter achado nenhum"
        )
    return achados


def _front_frontmatter(texto: str) -> dict[str, str]:
    """Frontmatter YAML raso, sem dependência. Só pares `chave: valor` do topo."""
    if not texto.startswith("---"):
        return {}
    fim = texto.find("\n---", 3)
    if fim == -1:
        return {}
    campos: dict[str, str] = {}
    for linha in texto[3:fim].splitlines():
        achado = re.match(r"^([a-zA-Z_][\w-]*)\s*:\s*(.*)$", linha)
        if achado:
            campos[achado.group(1).lower()] = achado.group(2).strip().strip("\"'")
    return campos


def _front_ferramentas(campos: dict[str, str]) -> set[str]:
    bruto = campos.get("tools") or campos.get("ferramentas") or ""
    if not bruto or bruto == "*":
        return set()
    return {t.strip() for t in bruto.strip("[]").split(",") if t.strip()}


def _front_agentes() -> list[tuple[Path, dict[str, str], set[str], str]]:
    lidos = []
    for caminho in _front_arquivos():
        texto = caminho.read_text(encoding="utf-8", errors="replace")
        campos = _front_frontmatter(texto)
        lidos.append((caminho, campos, _front_ferramentas(campos), texto))
    return lidos


def _front_matchers_de_hook() -> set[str]:
    """Ferramentas cobertas por algum `PreToolUse` registrado.

    Lê `.claude/settings.json` e `.claude/settings.local.json`. Um hook é uma
    barreira que roda como processo ANTES da ferramenta; um comentário pedindo
    boa-fé ao modelo não é.
    """
    cobertas: set[str] = set()
    for nome in ("settings.json", "settings.local.json"):
        arquivo = RAIZ / ".claude" / nome
        if not arquivo.is_file():
            continue
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        for entrada in (dados.get("hooks") or {}).get("PreToolUse") or []:
            matcher = str(entrada.get("matcher") or "")
            if not entrada.get("hooks"):
                continue  # matcher sem comando não cerca nada
            if matcher in ("*", ""):
                cobertas |= _FRONT_CONHECIDAS
                continue
            for nome_de_ferramenta in _FRONT_CONHECIDAS:
                if re.search(rf"\b{re.escape(nome_de_ferramenta)}\b", matcher):
                    cobertas.add(nome_de_ferramenta)
    return cobertas


def _front_sem_cerca(classe: frozenset[str]) -> int:
    cobertas = _front_matchers_de_hook()
    return sum(
        1
        for _, _, ferramentas, _ in _front_agentes()
        if (ferramentas & classe) and not (ferramentas & classe) <= cobertas
    )


# ---------------------------------------------------------------------------
# As sondas
# ---------------------------------------------------------------------------


@sonda("agentes.total", origem="arquivos .md nas pastas de agente declaradas")
def total() -> int:
    return len(_front_arquivos())


@sonda("agentes.com_ferramentas", origem="agentes cujo frontmatter declara `tools:`")
def com_ferramentas() -> int:
    return sum(1 for _, campos, _, _ in _front_agentes() if campos.get("tools"))


@sonda("agentes.com_rede", origem="agentes que declaram ferramenta de rede")
def com_rede() -> int:
    return sum(1 for _, _, f, _ in _front_agentes() if f & _FRONT_REDE)


@sonda("agentes.com_escrita", origem="agentes que declaram ferramenta de escrita")
def com_escrita() -> int:
    return sum(1 for _, _, f, _ in _front_agentes() if f & _FRONT_ESCRITA)


@sonda("agentes.com_execucao", origem="agentes que declaram ferramenta de execução")
def com_execucao() -> int:
    return sum(1 for _, _, f, _ in _front_agentes() if f & _FRONT_EXECUCAO)


@sonda("agentes.hooks", origem="entradas PreToolUse com comando em .claude/settings*.json")
def hooks() -> int:
    """Quantas barreiras `PreToolUse` estão registradas de verdade.

    ⚠️ **Zero aqui é uma medida legítima — mas só depois de eu ter achado os
    seus agentes.** Um repositório com agentes e sem nenhum hook registrado tem
    mesmo zero cercas, e esse é o achado. Um repositório onde eu não achei nem a
    pasta de agentes também devolveria zero, e aí o número diria «você não tem
    cerca» quando o que houve foi eu não ter olhado.

    Por isso a chamada abaixo: ela ESTOURA quando a árvore não está onde as
    constantes do topo dizem, e o veredito vira `SEM_PROVA` em vez de verde.
    """
    _front_arquivos()
    total_de_hooks = 0
    for nome in ("settings.json", "settings.local.json"):
        arquivo = RAIZ / ".claude" / nome
        if not arquivo.is_file():
            continue
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        for entrada in (dados.get("hooks") or {}).get("PreToolUse") or []:
            total_de_hooks += len(entrada.get("hooks") or [])
    return total_de_hooks


@sonda(
    "agentes.rede_sem_cerca",
    origem="agentes com ferramenta de rede que nenhum PreToolUse registrado cobre",
)
def rede_sem_cerca() -> int:
    return _front_sem_cerca(_FRONT_REDE)


@sonda(
    "agentes.escrita_sem_cerca",
    origem="agentes com ferramenta de escrita que nenhum PreToolUse registrado cobre",
)
def escrita_sem_cerca() -> int:
    return _front_sem_cerca(_FRONT_ESCRITA)


@sonda(
    "agentes.execucao_sem_cerca",
    origem="agentes com ferramenta de execução que nenhum PreToolUse registrado cobre",
)
def execucao_sem_cerca() -> int:
    return _front_sem_cerca(_FRONT_EXECUCAO)


@sonda(
    "agentes.sem_anti_descricao",
    origem="agentes cuja descrição não diz em que caso NÃO usá-los",
)
def sem_anti_descricao() -> int:
    return sum(
        1
        for _, campos, _, _ in _front_agentes()
        if not _FRONT_ANTI.search(campos.get("description") or campos.get("descricao") or "")
    )


@sonda(
    "agentes.ferramentas_desconhecidas",
    origem="nomes de ferramenta fora do vocabulário fechado, distintos",
)
def ferramentas_desconhecidas() -> int:
    vistas: set[str] = set()
    for _, _, ferramentas, _ in _front_agentes():
        vistas |= ferramentas - _FRONT_CONHECIDAS
    return len(vistas)


@sonda(
    "agentes.reprovariam_na_forja",
    origem="agentes que falhariam R1, R2 ou R3 da forja (rede sem cerca, escrita sem cerca, sem anti-descrição)",
)
def reprovariam_na_forja() -> int:
    cobertas = _front_matchers_de_hook()
    reprovados = 0
    for _, campos, ferramentas, _ in _front_agentes():
        descricao = campos.get("description") or campos.get("descricao") or ""
        r1 = bool(ferramentas & _FRONT_REDE) and not (ferramentas & _FRONT_REDE) <= cobertas
        r2 = bool(ferramentas & _FRONT_ESCRITA) and not (ferramentas & _FRONT_ESCRITA) <= cobertas
        r3 = not _FRONT_ANTI.search(descricao)
        if r1 or r2 or r3:
            reprovados += 1
    return reprovados
