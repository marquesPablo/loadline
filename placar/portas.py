"""As sete portas — deterministicamente, sem chamar modelo.

O vocabulário (`OBJECTIVE` .. `CONTAINMENT`) vem de fora desta casa: é a lista
de "Would you ship this AI agent?" que circula no ecossistema. `placar` não
inventa a régua; ele confere, uma a uma, se há EVIDÊNCIA no disco para cada
pergunta — nunca opinião.

O contrato de ausência é o mesmo da `forja` (`forja/spec.py`, `R1`-`R8`):
**ausente e vazio significam a mesma coisa, e as duas barram.** Uma porta sem
declaração nenhuma não fica "sem dado" — fica REPROVA, porque a pergunta que
ela responde é sempre binária: *dá para provar que sim?* Silêncio não prova.

A única exceção é o alvo inteiro: se não há harness de agente nenhum para ler
(nenhum `CLAUDE.md`, `AGENTS.md` ou pasta `.claude/`), `avaliar` devolve
`None` — placar não é a ferramenta certa para um repositório sem harness, e
dizer "REPROVA" aí seria medir a coisa errada, a mesma família de defeito que
o `C2`/`D4` desta casa já pagou (cravar fato do mundo em vez de comportamento).

⚠️ **A varredura de arquivo (Portas 2, 6, 7) PODA junction e symlink de
diretório — nunca desce por dentro.** É a mesma fronteira que o `blind` desta
casa mede: `os.walk` sem cuidado atravessa reparse point do Windows de
qualquer forma, e um `placar` que lesse por engano o que está atrás de uma
junction devolveria evidência de uma árvore que o alvo declarado nem sabe que
tem. A poda é silenciosa só até o limite do resumo de cada porta: quando ela
acontece, o relatório nomeia quantas fronteiras foram puladas.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from forja.spec import ESCRITA, EXECUCAO, REDE
from forja.vistoria import Lido, achar_pasta, ler_roster, vistoriar

EXCLUIDAS = frozenset(
    {
        ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
        "dist", "build", ".next", "target", ".mypy_cache", ".pytest_cache",
        ".tox", "vendor", ".idea", ".vscode",
    }
)

HARNESS_RAIZ = ("CLAUDE.md", "AGENTS.md", ".claude")

# --------------------------------------------------------------- achado -----


@dataclass
class Porta:
    numero: int
    id: str
    pergunta: str
    grave: bool
    resumo: str
    itens: list[str] = field(default_factory=list)
    conserto: str = ""
    #: Reprovar esta porta força NO-GO (regra do próprio placar da proposta):
    #: só IDENTITY, AUTHORITY e CONTAINMENT carregam isto como True.
    forca_no_go: bool = False


@dataclass
class Placar:
    alvo: Path
    portas: list[Porta]

    @property
    def passam(self) -> int:
        return sum(1 for p in self.portas if not p.grave)

    @property
    def reprova(self) -> bool:
        return any(p.grave for p in self.portas)

    @property
    def no_go(self) -> bool:
        return any(p.grave and p.forca_no_go for p in self.portas)


# ------------------------------------------------------------- utilidades ---


def _sem_acento(texto: str) -> str:
    import unicodedata

    return "".join(
        c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn"
    )


def _contem_marca(texto: str, marcas: tuple[str, ...]) -> bool:
    alvo = _sem_acento(texto)
    return any(_sem_acento(m) in alvo for m in marcas)


def _nota_puladas(puladas: list[str]) -> str:
    if not puladas:
        return ""
    return (
        f" — ⚠️ {len(puladas)} fronteira(s) (junction/symlink) NÃO atravessada(s); "
        "rode `python -m blind` para ver o que está atrás"
    )


def _e_fronteira(caminho: Path) -> bool:
    """Junction do Windows ou symlink de diretório — a mesma checagem do `blind`.

    `os.path.islink` devolve `False` para junction; quem acerta é
    `os.path.isjunction` (Python ≥ 3.12) ou o reparse tag lido direto.
    """
    try:
        if os.path.islink(caminho):
            return True
        if hasattr(os.path, "isjunction"):
            return os.path.isjunction(caminho)
        return False
    except OSError:
        return False


def _arquivos_de_texto(
    raiz: Path, sufixos: set[str] | None = None, teto: int = 4000
) -> tuple[list[Path], bool, list[str]]:
    """Varre `raiz`, podando pasta de vendor/build — nunca `node_modules` inteiro
    — E podando junction/symlink de diretório, sem descer por dentro.

    `teto` é o limite de arquivos por rodada: um repositório gigante não pode
    fazer `placar` travar. Devolve `(arquivos, truncado, fronteiras_puladas)` —
    quem chama é obrigado a decidir o que fazer com os dois últimos, porque
    silêncio sobre o corte OU sobre a fronteira pulada seria a mesma armadilha
    do `rg` sem `-L` que esta casa já mediu.
    """
    achados: list[Path] = []
    puladas: list[str] = []
    for atual, pastas, arquivos in os.walk(raiz):
        restantes = []
        for p in pastas:
            caminho = Path(atual) / p
            if p in EXCLUIDAS or p.startswith("."):
                continue
            if _e_fronteira(caminho):
                puladas.append(str(caminho))
                continue
            restantes.append(p)
        pastas[:] = restantes
        for nome in arquivos:
            if sufixos is not None and Path(nome).suffix not in sufixos:
                continue
            if len(achados) >= teto:
                return achados, True, puladas
            achados.append(Path(atual) / nome)
    return achados, False, puladas


def tem_harness(alvo: Path) -> bool:
    if any((alvo / nome).exists() for nome in HARNESS_RAIZ):
        return True
    # um nível abaixo — monorepo com o harness dentro de um pacote
    if alvo.is_dir():
        for filho in alvo.iterdir():
            if filho.is_dir() and filho.name not in EXCLUIDAS and not filho.name.startswith("."):
                if any((filho / nome).exists() for nome in HARNESS_RAIZ):
                    return True
    return False


def _roster(alvo: Path) -> list[Lido]:
    pasta = achar_pasta(alvo)
    if pasta is None:
        return []
    return ler_roster(pasta)


def _manifesto_raiz(alvo: Path) -> str:
    """Quando não há roster, o `CLAUDE.md`/`AGENTS.md` da raiz é o manifesto único."""
    for nome in ("CLAUDE.md", "AGENTS.md"):
        caminho = alvo / nome
        if caminho.exists():
            try:
                return caminho.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
    return ""


def _ler_settings(alvo: Path) -> dict:
    """`.claude/settings.json` + `.claude/settings.local.json`, mesclados.

    `hooks` fundido por evento (`PreToolUse`, `PostToolUse`, …): a lista de um
    lado soma à do outro, porque é assim que o Claude Code os aplica — os dois
    arquivos coexistem, e um não substitui o outro.
    """
    fundido: dict = {"hooks": {}}
    for nome in ("settings.json", "settings.local.json"):
        caminho = alvo / ".claude" / nome
        if not caminho.exists():
            continue
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            continue
        for evento, entradas in (dados.get("hooks") or {}).items():
            fundido["hooks"].setdefault(evento, []).extend(entradas or [])
    return fundido


_PREFIXO_COMANDO = re.compile(r"^(python3?|node|bash|sh|npx?)\s+", re.IGNORECASE)


def _scripts_do_evento(settings: dict, alvo: Path, evento: str) -> list[Path]:
    """Os arquivos de script que um evento (`PreToolUse`…) de fato invoca."""
    caminhos: list[Path] = []
    for entrada in settings.get("hooks", {}).get(evento, []):
        for h in entrada.get("hooks", []):
            comando = (h.get("command") or "").strip()
            if not comando:
                continue
            comando = comando.replace("$CLAUDE_PROJECT_DIR", str(alvo)).strip("\"'")
            comando = _PREFIXO_COMANDO.sub("", comando).strip("\"'")
            caminho = Path(comando.split()[0]) if comando.split() else None
            if caminho is None:
                continue
            if not caminho.is_absolute():
                caminho = alvo / caminho
            caminhos.append(caminho)
    return caminhos


def _matcher_cobre(settings: dict, alvo: Path, evento: str, ferramentas: frozenset[str]) -> bool:
    for entrada in settings.get("hooks", {}).get(evento, []):
        matcher = entrada.get("matcher", "") or ""
        if matcher == "" or any(f in matcher for f in ferramentas):
            return True
    return False


# ------------------------------------------------------------- Porta 1 ------

MARCAS_OBJECTIVE = (
    "kill_criteria", "condição de parada", "condicao de parada", "quando parar",
    "stop condition", "stop when", "budget", "orçamento", "orcamento",
    "max_turns", "max_iterations", "max_budget", "timeout", "definition of done",
)


def _porta_objective(alvo: Path, roster: list[Lido]) -> Porta:
    if roster:
        sem = [a.nome_curto for a in roster if not _contem_marca(a.descricao + "\n" + a.corpo, MARCAS_OBJECTIVE)]
        grave = bool(sem)
        resumo = f"{len(roster) - len(sem)} de {len(roster)} agente(s) declaram condição de parada ou orçamento"
        itens = sem
    else:
        texto = _manifesto_raiz(alvo)
        grave = not _contem_marca(texto, MARCAS_OBJECTIVE)
        resumo = "o manifesto da raiz não declara condição de parada nem orçamento" if grave else "o manifesto da raiz declara condição de parada ou orçamento"
        itens = ["CLAUDE.md / AGENTS.md"] if grave else []
    return Porta(
        1, "OBJECTIVE", "o que deve realizar, e quando parar?", grave, resumo, itens,
        conserto="declare `kill_criteria`, orçamento ou condição de parada no manifesto do agente.",
    )


# ------------------------------------------------------------- Porta 2 ------
# Nome, padrão, e o porquê de não ser genérico demais — cada entrada é um
# formato REAL e conhecido de credencial, não um `senha=...` que casaria com
# metade dos arquivos de exemplo do mundo.
_SEGREDOS = (
    ("AWS Access Key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("OpenAI API key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("chave privada", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
)
_PLACEHOLDER = re.compile(
    r"(xxx|your[_-]|changeme|<[a-z_-]+>|\$\{|process\.env|os\.environ|os\.getenv|example|placeholder|fake|dummy)",
    re.IGNORECASE,
)
_SUFIXOS_TEXTO = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml",
    ".md", ".env", ".sh", ".ps1", ".txt", ".cfg", ".ini", ".rb", ".go", ".java",
}


def _porta_identity(alvo: Path) -> Porta:
    arquivos, truncado, puladas = _arquivos_de_texto(alvo, sufixos=_SUFIXOS_TEXTO)
    achados: list[str] = []
    for caminho in arquivos:
        try:
            texto = caminho.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for numero, linha in enumerate(texto.splitlines(), start=1):
            if _PLACEHOLDER.search(linha):
                continue
            for nome, padrao in _SEGREDOS:
                if padrao.search(linha):
                    rel = caminho.relative_to(alvo)
                    achados.append(f"{rel}:{numero}  {nome}, em claro")
                    break
    grave = bool(achados)
    resumo = f"{len(achados)} segredo(s) em claro encontrado(s)" if grave else "nenhum segredo em claro encontrado"
    if truncado:
        resumo += f" — ⚠️ varredura parou em {len(arquivos)} arquivos, pode haver mais fora da janela"
    resumo += _nota_puladas(puladas)
    return Porta(
        2, "IDENTITY", "de quem é a identidade que usa?", grave, resumo,
        achados,
        conserto="mova para variável de ambiente; revogue a chave exposta — ela já vazou para o histórico do git.",
    )


# ------------------------------------------------------------- Porta 3 ------


def _porta_authority(alvo: Path, roster: list[Lido], settings: dict) -> Porta:
    if roster:
        achados = vistoriar(roster)
        graves = [a for a in achados if a.regra in {"V3", "V7"}]
        agentes = sorted({nome for a in graves for nome in a.agentes})
        grave = bool(graves)
        resumo = (
            f"{len(agentes)} de {len(roster)} agente(s) sem fronteira de escrita/rede declarada, "
            "ou herdando toda ferramenta"
            if grave
            else f"{len(roster)} agente(s), todos com fronteira declarada"
        )
        return Porta(
            3, "AUTHORITY", "o que pode ler, escrever, executar?", grave, resumo, agentes,
            conserto="declare `tools:` e a cerca de escrita/rede em cada agente — vazio herda tudo, e isso é o oposto de menor privilégio.",
        )
    cobre_escrita = _matcher_cobre(settings, alvo, "PreToolUse", ESCRITA)
    cobre_rede = _matcher_cobre(settings, alvo, "PreToolUse", REDE | EXECUCAO)
    faltando = [n for n, ok in (("escrita", cobre_escrita), ("rede/execução", cobre_rede)) if not ok]
    grave = bool(faltando)
    resumo = (
        f"sem roster de agente — harness não tem `PreToolUse` cobrindo {', '.join(faltando)}"
        if grave
        else "sem roster de agente — harness cobre escrita e rede/execução com `PreToolUse`"
    )
    return Porta(
        3, "AUTHORITY", "o que pode ler, escrever, executar?", grave, resumo, faltando,
        conserto="registre um `PreToolUse` em `.claude/settings.json` para as ferramentas de escrita e as de rede/execução.",
    )


# ------------------------------------------------------------- Porta 4 ------

MARCAS_FAILURE = (
    "retry", "fallback", "tenta novamente", "nova tentativa", "circuit breaker",
    "em caso de falha", "se a ferramenta falhar", "on_error", "degrada",
)


def _porta_failure(alvo: Path, roster: list[Lido], settings: dict) -> Porta:
    tem_timeout = any(
        h.get("timeout") is not None
        for evento in settings.get("hooks", {}).values()
        for entrada in evento
        for h in entrada.get("hooks", [])
    )
    if roster:
        corpo = "\n".join(a.descricao + "\n" + a.corpo for a in roster)
    else:
        corpo = _manifesto_raiz(alvo)
    tem_palavra = _contem_marca(corpo, MARCAS_FAILURE)
    grave = not (tem_timeout or tem_palavra)
    partes = []
    if tem_timeout:
        partes.append("hook com `timeout` declarado")
    if tem_palavra:
        partes.append("manifesto menciona retry/fallback")
    resumo = " · ".join(partes) if partes else "nenhum hook declara `timeout`, e nenhum manifesto menciona retry/fallback"
    return Porta(
        4, "FAILURE", "e se a ferramenta falhar ou mentir?", grave, resumo, [] if not grave else ["nenhuma evidência"],
        conserto="declare `timeout` nos hooks, e retry/fallback explícito para a ferramenta que pode falhar ou mentir.",
    )


# ------------------------------------------------------------- Porta 5 ------

_MARCA_DENY = (
    ('"permissiondecision"', '"deny"'),
    ('"decision"', '"block"'),
)
_MARCA_EXIT2 = re.compile(r"sys\.exit\(\s*2\s*\)|exit\(\s*2\s*\)|process\.exit\(\s*2\s*\)")


def _script_falha_fechado(caminho: Path) -> bool:
    try:
        texto = caminho.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return False
    if _MARCA_EXIT2.search(texto):
        return True
    return any(a in texto and b in texto for a, b in _MARCA_DENY)


def _porta_approval(alvo: Path, settings: dict) -> Porta:
    scripts = _scripts_do_evento(settings, alvo, "PreToolUse")
    if not scripts:
        return Porta(
            5, "APPROVAL", "quais ações exigem humano?", True,
            "nenhum `PreToolUse` configurado em `.claude/settings.json`", [],
            conserto="registre ao menos um hook `PreToolUse` que negue (`permissionDecision: deny` ou exit 2) sob alguma condição.",
        )
    falha_fechado = [s for s in scripts if s.exists() and _script_falha_fechado(s)]
    grave = not falha_fechado
    existentes = [s for s in scripts if s.exists()]
    resumo = (
        f"{len(falha_fechado)} de {len(existentes)} script(s) de `PreToolUse` mostram decisão de negar"
        if existentes
        else "`PreToolUse` configurado, mas nenhum script referenciado foi encontrado no disco"
    )
    return Porta(
        5, "APPROVAL", "quais ações exigem humano?", grave, resumo,
        [str(s.relative_to(alvo)) if s.is_relative_to(alvo) else str(s) for s in scripts],
        conserto="o hook precisa emitir `permissionDecision: deny` (ou sair com código 2) sob alguma condição — um hook que só observa não é aprovação.",
    )


# ------------------------------------------------------------- Porta 6 ------

PASTAS_DECISAO = ("decisoes", "decisions", "adr", "decision-records", "docs/adr", "docs/decisions", "doc/adr")
_NOME_DECISAO = re.compile(r"^(ADR|adr)[-_]?\d+|^\d{4}-\d{2}-\d{2}")
_DATA_ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def _pasta_de_decisao(alvo: Path) -> Path | None:
    for relativo in PASTAS_DECISAO:
        candidato = alvo / relativo
        if candidato.is_dir():
            return candidato
    return None


def _porta_traceability(alvo: Path, settings: dict) -> Porta:
    pasta = _pasta_de_decisao(alvo)
    arquivos: list[Path] = []
    truncado = False
    puladas: list[str] = []
    if pasta is not None:
        arquivos = sorted(pasta.glob("*.md"))
    else:
        candidatos, truncado, puladas = _arquivos_de_texto(alvo, sufixos={".md"}, teto=2000)
        arquivos = [c for c in candidatos if _NOME_DECISAO.match(c.stem)]

    tem_post = bool(settings.get("hooks", {}).get("PostToolUse"))

    if not arquivos and not tem_post:
        resumo = "nenhum registro de decisão encontrado, e nenhum `PostToolUse` de auditoria configurado"
        if truncado:
            resumo += " — ⚠️ varredura de `.md` parou em 2000 arquivos"
        resumo += _nota_puladas(puladas)
        return Porta(
            6, "TRACEABILITY", "dá para reconstruir toda decisão?", True,
            resumo, [],
            conserto="crie um registro de decisão datado (ADR ou similar), ou um `PostToolUse` que grave cada ação tomada.",
        )
    datados = sum(1 for a in arquivos if _DATA_ISO.search(a.name) or _DATA_ISO.search(_ler_inicio(a)))
    grave = bool(arquivos) and datados == 0 and not tem_post
    partes = []
    if arquivos:
        partes.append(f"{datados} de {len(arquivos)} registro(s) de decisão datados")
    if tem_post:
        partes.append("`PostToolUse` de auditoria configurado")
    if truncado:
        partes.append("⚠️ varredura de `.md` parou em 2000 arquivos")
    if puladas:
        partes.append(f"⚠️ {len(puladas)} fronteira(s) não atravessada(s)")
    return Porta(
        6, "TRACEABILITY", "dá para reconstruir toda decisão?", grave, " · ".join(partes),
        [] if not grave else [a.name for a in arquivos],
        conserto="date cada registro de decisão (`data:` no frontmatter, ou no nome do arquivo).",
    )


def _ler_inicio(caminho: Path, teto: int = 800) -> str:
    try:
        return caminho.read_text(encoding="utf-8", errors="replace")[:teto]
    except OSError:
        return ""


# ------------------------------------------------------------- Porta 7 ------

_TOKEN_R = re.compile(r"\bR[0-4]\b")
_MARCA_REVERS = ("revers", "irrevers", "rollback", "revert", "desfaz", "catálogo fechado", "catalogo fechado")


def _porta_containment(alvo: Path) -> Porta:
    arquivos, truncado, puladas = _arquivos_de_texto(
        alvo, sufixos={".md", ".py", ".toml", ".json", ".yaml", ".yml"}
    )
    achados: list[str] = []
    for caminho in arquivos:
        try:
            texto = caminho.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if _TOKEN_R.search(texto) and _contem_marca(texto, _MARCA_REVERS):
            achados.append(str(caminho.relative_to(alvo)))
    grave = not achados
    resumo = (
        "nenhuma classificação de reversibilidade (R0–R4 ou equivalente) encontrada"
        if grave
        else f"classificação de reversibilidade encontrada em {len(achados)} arquivo(s)"
    )
    if truncado:
        resumo += f" — ⚠️ varredura parou em {len(arquivos)} arquivos"
    resumo += _nota_puladas(puladas)
    return Porta(
        7, "CONTAINMENT", "dá para parar e reverter?", grave, resumo, achados,
        conserto="classifique ações por reversibilidade (ex.: R0–R4) e gate as menos reversíveis atrás de aprovação.",
    )


# --------------------------------------------------------------- rodada -----

NO_GO = frozenset({"IDENTITY", "AUTHORITY", "CONTAINMENT"})


def avaliar(alvo: Path) -> Placar | None:
    if not tem_harness(alvo):
        return None

    roster = _roster(alvo)
    settings = _ler_settings(alvo)

    portas = [
        _porta_objective(alvo, roster),
        _porta_identity(alvo),
        _porta_authority(alvo, roster, settings),
        _porta_failure(alvo, roster, settings),
        _porta_approval(alvo, settings),
        _porta_traceability(alvo, settings),
        _porta_containment(alvo),
    ]
    for p in portas:
        if p.id in NO_GO:
            p.forca_no_go = True
    return Placar(alvo, portas)
