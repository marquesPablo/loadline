"""The seven gates — deterministically, without calling a model.

The vocabulary (`OBJECTIVE` .. `CONTAINMENT`) comes from outside this project:
it is the "Would you ship this AI agent?" list that circulates in the
ecosystem. `placar` does not invent the rule; it checks, one by one, whether
there is EVIDENCE on disk for each question — never opinion.

The absence contract is the same as `forja`'s (`forja/spec.py`, `R1`-`R8`):
**absent and empty mean the same thing, and both block.** A gate with no
declaration at all is not "no data" — it is FAIL, because the question it
answers is always binary: *can you prove it is a yes?* Silence proves nothing.

The only exception is the whole target: if there is no agent harness at all
(no `CLAUDE.md`, `AGENTS.md` or `.claude/` folder), `avaliar` returns `None` —
`placar` is not the right tool for a repository with no harness, and saying
"FAIL" there would be measuring the wrong thing, the same family of defect
this project has paid for once (nailing down a fact of the world instead of a
behavior).

⚠️ **The file scan (Gates 2, 6, 7) PRUNES a junction and a directory symlink —
it never descends through them.** It is the same boundary `blind` measures:
a careless `os.walk` crosses a Windows reparse point anyway, and a `placar`
that read by mistake what is behind a junction would return evidence about a
tree the declared target does not even know it has. The pruning is silent only
up to each gate's summary: when it happens, the report names how many
boundaries were skipped.
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

# --------------------------------------------------------------- finding -----


@dataclass
class Porta:
    numero: int
    id: str
    pergunta: str
    grave: bool
    resumo: str
    itens: list[str] = field(default_factory=list)
    conserto: str = ""
    #: Failing this gate forces NO-GO (rule from the proposal's own scoreboard):
    #: only IDENTITY, AUTHORITY and CONTAINMENT carry this as True.
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


# ------------------------------------------------------------- utilities ---


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
        f" — ⚠️ {len(puladas)} boundary(ies) (junction/symlink) NOT crossed; "
        "run `python -m blind` to see what is behind them"
    )


def _e_fronteira(caminho: Path) -> bool:
    """A Windows junction or a directory symlink — the same check as `blind`.

    `os.path.islink` returns `False` for a junction; what gets it right is
    `os.path.isjunction` (Python ≥ 3.12) or the reparse tag read directly.
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
    """Scans `raiz`, pruning vendor/build folders — never a whole `node_modules`
    — AND pruning a junction / directory symlink, without descending through it.

    `teto` is the per-run file limit: a giant repository must not make `placar`
    hang. Returns `(files, truncated, skipped_boundaries)` — the caller is
    required to decide what to do with the last two, because silence about the
    cut OR about the skipped boundary would be the same `rg`-without-`-L` trap
    this project has already measured.
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
    # one level down — a monorepo with the harness inside a package
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
    """When there is no roster, the root `CLAUDE.md`/`AGENTS.md` is the single manifest."""
    for nome in ("CLAUDE.md", "AGENTS.md"):
        caminho = alvo / nome
        if caminho.exists():
            try:
                return caminho.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
    return ""


#: Every place a repository can register a hook, merged into one.
#: `.claude/settings.json` is what an INSTALL writes on the user's machine; a
#: repository distributed as a PLUGIN never has it, and ships `hooks/hooks.json`
#: instead. Reading only the first said "no `PreToolUse` configured" about a
#: harness carrying eight of them, four of which refuse.
_FONTES_DE_HOOK = (
    Path(".claude") / "settings.json",
    Path(".claude") / "settings.local.json",
    Path(".claude") / "hooks.json",
    Path("hooks") / "hooks.json",
)


def _ler_settings(alvo: Path) -> dict:
    """The hook registration of the target, from every form it can take.

    `hooks` merged per event (`PreToolUse`, `PostToolUse`, …): one side's list
    adds to the other's, because that is how Claude Code applies them — the
    files coexist, and one does not replace the other.
    """
    fundido: dict = {"hooks": {}}
    for relativo in _FONTES_DE_HOOK:
        caminho = alvo / relativo
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
#: Anything in the command line shaped like a script path. Read over the WHOLE
#: command, never just its first token: a plugin wraps its hook in
#: `node -e "<bootstrap>" node scripts/hooks/x.js`, and the first token there is
#: `-e`, which resolves to a file that does not exist.
_TOKEN_SCRIPT = re.compile(r"[\w.:$/\\{}-]*\.(?:js|mjs|cjs|ts|py|sh|ps1)\b")
_VARIAVEIS = (
    "${CLAUDE_PROJECT_DIR}", "$CLAUDE_PROJECT_DIR",
    "${CLAUDE_PLUGIN_ROOT}", "$CLAUDE_PLUGIN_ROOT",
)


def _scripts_do_evento(settings: dict, alvo: Path, evento: str) -> list[Path]:
    """The script files an event (`PreToolUse`…) actually invokes.

    A path only counts when it EXISTS under the target — the command line of a
    plugin bootstrap mentions several, and only some are files. When none does,
    the first token is kept anyway, so a plain `python hook.py` still reports
    the path it names even if that path is missing: naming a script that is not
    there is a finding, not something to swallow.
    """
    caminhos: list[Path] = []
    for entrada in settings.get("hooks", {}).get(evento, []):
        for h in entrada.get("hooks", []):
            comando = (h.get("command") or "").strip()
            if not comando:
                continue
            for variavel in _VARIAVEIS:
                comando = comando.replace(variavel, str(alvo))
            achados = []
            for encontro in _TOKEN_SCRIPT.finditer(comando):
                caminho = Path(encontro.group(0).strip("\"'"))
                if not caminho.is_absolute():
                    caminho = alvo / caminho
                if caminho.is_file():
                    achados.append(caminho)
            if achados:
                caminhos.extend(achados)
                continue
            simples = _PREFIXO_COMANDO.sub("", comando.strip("\"'")).strip("\"'")
            partes = simples.split()
            if not partes:
                continue
            caminho = Path(partes[0])
            if not caminho.is_absolute():
                caminho = alvo / caminho
            caminhos.append(caminho)
    unicos: list[Path] = []
    vistos: set[str] = set()
    for caminho in caminhos:
        chave = str(caminho).lower()
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(caminho)
    return unicos


def _matcher_cobre(settings: dict, alvo: Path, evento: str, ferramentas: frozenset[str]) -> bool:
    for entrada in settings.get("hooks", {}).get(evento, []):
        matcher = entrada.get("matcher", "") or ""
        if matcher == "" or any(f in matcher for f in ferramentas):
            return True
    return False


# ------------------------------------------------------------- Gate 1 ------

MARCAS_OBJECTIVE = (
    "kill_criteria", "condição de parada", "condicao de parada", "quando parar",
    "stop condition", "stop when", "budget", "orçamento", "orcamento",
    "max_turns", "max_iterations", "max_budget", "timeout", "definition of done",
)


def _porta_objective(alvo: Path, roster: list[Lido]) -> Porta:
    if roster:
        sem = [a.nome_curto for a in roster if not _contem_marca(a.descricao + "\n" + a.corpo, MARCAS_OBJECTIVE)]
        grave = bool(sem)
        resumo = f"{len(roster) - len(sem)} of {len(roster)} agent(s) declare a stop condition or a budget"
        itens = sem
    else:
        texto = _manifesto_raiz(alvo)
        grave = not _contem_marca(texto, MARCAS_OBJECTIVE)
        resumo = "the root manifest declares no stop condition and no budget" if grave else "the root manifest declares a stop condition or a budget"
        itens = ["CLAUDE.md / AGENTS.md"] if grave else []
    return Porta(
        1, "OBJECTIVE", "what must it achieve, and when to stop?", grave, resumo, itens,
        conserto="declare `kill_criteria`, a budget or a stop condition in the agent manifest.",
    )


# ------------------------------------------------------------- Gate 2 ------
# A name, a pattern, and why it is not too generic — each entry is a REAL,
# known credential format, not a `password=...` that would match half the
# example files in the world.
_SEGREDOS = (
    ("AWS Access Key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("OpenAI API key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("private key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
)
_PLACEHOLDER = re.compile(
    r"(xxx|your[_-]|changeme|<[a-z_-]+>|\$\{|process\.env|os\.environ|os\.getenv|example|placeholder|fake|dummy)",
    re.IGNORECASE,
)
_SUFIXOS_TEXTO = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml",
    ".md", ".env", ".sh", ".ps1", ".txt", ".cfg", ".ini", ".rb", ".go", ".java",
}

#: The private key is the one entry above that spans MORE THAN ONE LINE, and
#: judging it by the `BEGIN` marker alone is what makes every didactic example
#: score as a leak: a Kubernetes `Secret` snippet writes the two markers with a
#: literal `...` between them, and the word that would clear it — `example`,
#: `placeholder` — sits on a different line than the one being read.
#: The marker is not the secret. The body is.
_PEM_CORPO = re.compile(r"[A-Za-z0-9+/=]{16,}")
_PEM_FIM = re.compile(r"-----END [A-Z ]*PRIVATE KEY-----")
#: The smallest real private key in the wild — an EC P-256 in PEM — carries
#: about 220 base64 characters. 100 sits below every real key and far above
#: every placeholder, which carries `...`, `<your-key>`, or nothing at all.
_PEM_MINIMO = 100
#: How far under the marker to look for the body. A 4096-bit RSA key in PEM is
#: about 50 lines; past that, the `BEGIN` had no `END` belonging to it.
_PEM_JANELA = 60


def _pem_tem_corpo(linhas: list[str], indice: int) -> bool:
    """True when a real key body sits under the `BEGIN` marker at `indice`."""
    corpo = 0
    for linha in linhas[indice + 1 : indice + 1 + _PEM_JANELA]:
        despido = linha.strip()
        if _PEM_FIM.search(despido):
            break
        if _PEM_CORPO.fullmatch(despido):
            corpo += len(despido)
    return corpo >= _PEM_MINIMO


def _porta_identity(alvo: Path) -> Porta:
    arquivos, truncado, puladas = _arquivos_de_texto(alvo, sufixos=_SUFIXOS_TEXTO)
    achados: list[str] = []
    for caminho in arquivos:
        try:
            texto = caminho.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        linhas = texto.splitlines()
        for numero, linha in enumerate(linhas, start=1):
            if _PLACEHOLDER.search(linha):
                continue
            for nome, padrao in _SEGREDOS:
                if not padrao.search(linha):
                    continue
                if nome == "private key" and not _pem_tem_corpo(linhas, numero - 1):
                    continue
                rel = caminho.relative_to(alvo)
                achados.append(f"{rel}:{numero}  {nome}, in the clear")
                break
    grave = bool(achados)
    resumo = f"{len(achados)} secret(s) in the clear found" if grave else "no secret in the clear found"
    if truncado:
        resumo += f" — ⚠️ scan stopped at {len(arquivos)} files, there may be more outside the window"
    resumo += _nota_puladas(puladas)
    return Porta(
        2, "IDENTITY", "whose identity does it use?", grave, resumo,
        achados,
        conserto="move it to an environment variable; revoke the exposed key — it has already leaked into the git history.",
    )


# ------------------------------------------------------------- Gate 3 ------


def _porta_authority(alvo: Path, roster: list[Lido], settings: dict) -> Porta:
    if roster:
        achados = vistoriar(roster)
        graves = [a for a in achados if a.regra in {"V3", "V7"}]
        agentes = sorted({nome for a in graves for nome in a.agentes})
        grave = bool(graves)
        resumo = (
            f"{len(agentes)} of {len(roster)} agent(s) with no declared write/network boundary, "
            "or inheriting every tool"
            if grave
            else f"{len(roster)} agent(s), all with a declared boundary"
        )
        return Porta(
            3, "AUTHORITY", "what can it read, write, execute?", grave, resumo, agentes,
            conserto="declare `tools:` and the write/network fence in each agent — empty inherits everything, and that is the opposite of least privilege.",
        )
    cobre_escrita = _matcher_cobre(settings, alvo, "PreToolUse", ESCRITA)
    cobre_rede = _matcher_cobre(settings, alvo, "PreToolUse", REDE | EXECUCAO)
    faltando = [n for n, ok in (("write", cobre_escrita), ("network/execution", cobre_rede)) if not ok]
    grave = bool(faltando)
    resumo = (
        f"no agent roster — the harness has no `PreToolUse` covering {', '.join(faltando)}"
        if grave
        else "no agent roster — the harness covers write and network/execution with `PreToolUse`"
    )
    return Porta(
        3, "AUTHORITY", "what can it read, write, execute?", grave, resumo, faltando,
        conserto="register a `PreToolUse` in `.claude/settings.json` for the write tools and the network/execution ones.",
    )


# ------------------------------------------------------------- Gate 4 ------

MARCAS_FAILURE = (
    "retry", "fallback", "tenta novamente", "nova tentativa", "circuit breaker",
    "em caso de falha", "se a ferramenta falhar", "on_error", "degrada",
    "on failure", "if the tool fails", "degrade",
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
        partes.append("a hook with a declared `timeout`")
    if tem_palavra:
        partes.append("the manifest mentions retry/fallback")
    resumo = " · ".join(partes) if partes else "no hook declares a `timeout`, and no manifest mentions retry/fallback"
    return Porta(
        4, "FAILURE", "what if the tool fails or lies?", grave, resumo, [] if not grave else ["no evidence"],
        conserto="declare `timeout` on the hooks, and an explicit retry/fallback for the tool that can fail or lie.",
    )


# ------------------------------------------------------------- Gate 5 ------

_MARCA_DENY = (
    ('"permissiondecision"', '"deny"'),
    ('"decision"', '"block"'),
)
_MARCA_EXIT2 = re.compile(r"sys\.exit\(\s*2\s*\)|exit\(\s*2\s*\)|process\.exit\(\s*2\s*\)")

#: The same deny, written ONE INDIRECTION AWAY. The entry point hands the
#: process exit code to a function — `raise SystemExit(main())`, `sys.exit(run())`,
#: `process.exit(main())` — and the refusal is a bare `return 2` inside it.
#: Neither half proves anything alone: plenty of functions return 2, and plenty
#: of entry points delegate without ever denying. Together they are the exact
#: `exit 2` the line above already accepts, and reading only the literal form
#: scored a hook set that denies in production 0 of 4.
_MARCA_SAIDA_DELEGADA = re.compile(
    r"(?:raise\s+systemexit|sys\.exit|process\.exit)\(\s*[a-z_][a-z0-9_.]*\(\s*\)\s*\)"
)
_MARCA_RETURN2 = re.compile(r"^[ \t]*return\s+2\s*(?:#.*)?$", re.MULTILINE)


#: The refusal spelled out in the hook's own output, key next to value. The
#: JSON a hook PRINTS carries `"permissionDecision"` quoted; the JavaScript that
#: BUILDS that JSON writes `permissionDecision: 'deny'` — an unquoted key and a
#: single-quoted value, which is how every hook in the largest catalogue of the
#: ecosystem is written, and which the quoted-only form did not see.
_MARCA_DENY_ADJACENTE = (
    re.compile(r"""["']?permissiondecision["']?\s*[:=]\s*["']deny["']"""),
    re.compile(r"""["']?decision["']?\s*[:=]\s*["']block["']"""),
)
#: A `require`/`import` of a SIBLING file — how a dispatcher reaches the script
#: that actually refuses. Relative targets only: following a package name walks
#: into `node_modules` and never comes back.
_IMPORT_LOCAL = re.compile(
    r"""(?:require|import)\s*\(?\s*['"](\.{1,2}/[\w./-]+)['"]|"""
    r"""from\s+['"](\.{1,2}/[\w./-]+)['"]"""
)
_SUFIXOS_IMPORT = ("", ".js", ".mjs", ".cjs", ".ts", ".py")
#: How many `require` hops to follow. In a small harness the refusal is in the
#: entry script itself — zero hops. In a plugin-shaped one it sits behind a
#: dispatcher that fans out to leaf hooks, measured at two hops in the largest
#: catalogue in the ecosystem. Three covers both, and the visited set ends a cycle.
_IMPORT_PROFUNDIDADE = 3
_IMPORT_TETO = 200


def _nega(texto: str) -> bool:
    """The shapes of a refusal, in one already-lowercased text."""
    if _MARCA_EXIT2.search(texto):
        return True
    if _MARCA_SAIDA_DELEGADA.search(texto) and _MARCA_RETURN2.search(texto):
        return True
    if any(padrao.search(texto) for padrao in _MARCA_DENY_ADJACENTE):
        return True
    return any(a in texto and b in texto for a, b in _MARCA_DENY)


def _vizinhos(caminho: Path, texto: str) -> list[Path]:
    """The sibling files this one requires, resolved on disk."""
    achados: list[Path] = []
    for encontro in _IMPORT_LOCAL.finditer(texto):
        alvo = encontro.group(1) or encontro.group(2)
        if not alvo:
            continue
        base = caminho.parent / alvo
        for sufixo in _SUFIXOS_IMPORT:
            candidato = base if not sufixo else base.with_suffix(sufixo)
            if candidato.is_file():
                achados.append(candidato)
                break
    return achados


def _script_falha_fechado(caminho: Path) -> bool:
    """True when the hook REFUSES — in itself, or in what it dispatches to.

    Stopping at the entry file reads only the harness whose refusal is written
    in the file the settings name. The moment a project grows past that, the
    command points at a dispatcher and the refusal is one or two `require`
    hops away — and a gate that stops at the door reports `0 of 8` about a
    harness that blocks.
    """
    vistos: set[str] = set()
    fila: list[tuple[Path, int]] = [(caminho, 0)]
    while fila and len(vistos) < _IMPORT_TETO:
        atual, profundidade = fila.pop(0)
        chave = str(atual).lower()
        if chave in vistos:
            continue
        vistos.add(chave)
        try:
            texto = atual.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if _nega(texto.lower()):
            return True
        if profundidade < _IMPORT_PROFUNDIDADE:
            fila.extend((v, profundidade + 1) for v in _vizinhos(atual, texto))
    return False


def _porta_approval(alvo: Path, settings: dict) -> Porta:
    scripts = _scripts_do_evento(settings, alvo, "PreToolUse")
    if not scripts:
        return Porta(
            5, "APPROVAL", "which actions need a human?", True,
            "no `PreToolUse` configured in `.claude/settings.json`", [],
            conserto="register at least one `PreToolUse` hook that denies (`permissionDecision: deny` or exit 2) under some condition.",
        )
    falha_fechado = [s for s in scripts if s.exists() and _script_falha_fechado(s)]
    grave = not falha_fechado
    existentes = [s for s in scripts if s.exists()]
    resumo = (
        f"{len(falha_fechado)} of {len(existentes)} `PreToolUse` script(s) show a deny decision"
        if existentes
        else "`PreToolUse` configured, but none of the referenced scripts was found on disk"
    )
    return Porta(
        5, "APPROVAL", "which actions need a human?", grave, resumo,
        [str(s.relative_to(alvo)) if s.is_relative_to(alvo) else str(s) for s in scripts],
        conserto="the hook must emit `permissionDecision: deny` (or exit with code 2) under some condition — a hook that only observes is not approval.",
    )


# ------------------------------------------------------------- Gate 6 ------

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
        resumo = "no decision record found, and no auditing `PostToolUse` configured"
        if truncado:
            resumo += " — ⚠️ `.md` scan stopped at 2000 files"
        resumo += _nota_puladas(puladas)
        return Porta(
            6, "TRACEABILITY", "can every decision be reconstructed?", True,
            resumo, [],
            conserto="create a dated decision record (ADR or similar), or a `PostToolUse` that logs every action taken.",
        )
    datados = sum(1 for a in arquivos if _DATA_ISO.search(a.name) or _DATA_ISO.search(_ler_inicio(a)))
    grave = bool(arquivos) and datados == 0 and not tem_post
    partes = []
    if arquivos:
        partes.append(f"{datados} of {len(arquivos)} decision record(s) dated")
    if tem_post:
        partes.append("an auditing `PostToolUse` configured")
    if truncado:
        partes.append("⚠️ `.md` scan stopped at 2000 files")
    if puladas:
        partes.append(f"⚠️ {len(puladas)} boundary(ies) not crossed")
    return Porta(
        6, "TRACEABILITY", "can every decision be reconstructed?", grave, " · ".join(partes),
        [] if not grave else [a.name for a in arquivos],
        conserto="date every decision record (`data:` in the frontmatter, or in the filename).",
    )


def _ler_inicio(caminho: Path, teto: int = 800) -> str:
    try:
        return caminho.read_text(encoding="utf-8", errors="replace")[:teto]
    except OSError:
        return ""


# ------------------------------------------------------------- Gate 7 ------

_TOKEN_R = re.compile(r"\bR[0-4]\b")
_MARCA_REVERS = ("revers", "irrevers", "rollback", "revert", "desfaz", "catálogo fechado", "catalogo fechado", "undo", "closed catalog")


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
        "no reversibility classification (R0–R4 or equivalent) found"
        if grave
        else f"a reversibility classification found in {len(achados)} file(s)"
    )
    if truncado:
        resumo += f" — ⚠️ scan stopped at {len(arquivos)} files"
    resumo += _nota_puladas(puladas)
    return Porta(
        7, "CONTAINMENT", "can it be stopped and reverted?", grave, resumo, achados,
        conserto="classify actions by reversibility (e.g. R0–R4) and gate the less reversible ones behind approval.",
    )


# --------------------------------------------------------------- run -----

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
