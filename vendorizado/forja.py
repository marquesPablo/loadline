"""forja.py — vendorizado, só a vistoria: lê os agentes que você já tem.

Gerado por `vendorizar.py` a partir do pacote `forja` de verdade — editar este
arquivo à mão é editar uma cópia; o original mora em `forja/spec.py` e
`forja/vistoria.py`. Zero dependência: só a biblioteca padrão do Python 3.10+.

    python forja.py /caminho/do/seu/projeto

O pacote inteiro (compilação de spec, `--adotar`, `--html`, `--baseline`,
modo comparação) está em https://github.com/marquesPablo/loadline
"""

from __future__ import annotations


# ====================================================================
# forja\spec.py
# ====================================================================

"""An agent's spec, and the eight refusals that stop a bad one from compiling.

nature: security — every decision in this module is a REFUSAL, and it fails
closed. What the forge cannot decide, it refuses to emit; it never emits
"best effort" with a field missing. An agent compiler that fails open ships
exactly the ungated agent it existed to prevent.

The spec is TOML because `tomllib` is stdlib since Python 3.11 — the whole
project stays at zero dependencies. And it is declarative because a field with
code to execute would be injection with a written invitation.

## The eight refusals

    R1  a NETWORK tool with no `dominios_permitidos`
    R2  a WRITE tool with no `saida_cercada`
    R3  `nunca_usar` empty           — with no anti-description, the orchestrator guesses
    R4  `lacunas` empty              — nothing declares what the agent does not measure
    R5  zero golden-set cases        — no answer has been checked
    R6  golden derived from inside   — mirror check: both sides, the same source
    R7  `toca_alvo` with no authorization  — recon with no scope is an incident, not a finding
    R8  invalid slug                 — the slug becomes a filename in 4 harnesses

(The spec's TOML keys are still Portuguese — that translation is its own step,
like the seal vocabulary was; the prose around them here is English.)

Each exists because an ABSENT field is indistinguishable, to a hook, from an
empty one: absent-or-empty BLOCKS, and it is the only reading that does not
become a back door.
"""


import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Tools that leave the machine, and the ones that write to disk. The list is
# closed and covers the names today's harnesses use; an unknown name is NOT
# treated as harmless — see `desconhecidas`.
REDE = frozenset({"WebFetch", "WebSearch", "Fetch", "Browser", "http", "curl"})
ESCRITA = frozenset({"Write", "Edit", "NotebookEdit", "MultiEdit", "apply_patch"})
EXECUCAO = frozenset({"Bash", "PowerShell", "Shell", "Terminal", "Execute"})
CONHECIDAS = REDE | ESCRITA | EXECUCAO | frozenset(
    {"Read", "Grep", "Glob", "TodoWrite", "Task", "AskUserQuestion"}
)

SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class Recusa(ValueError):
    """The forge refused to compile. Always with the rule code and the fix."""

    def __init__(self, regra: str, motivo: str, conserto: str) -> None:
        self.regra, self.motivo, self.conserto = regra, motivo, conserto
        super().__init__(f"{regra}: {motivo}\n      fix: {conserto}")


@dataclass(frozen=True)
class Caso:
    """A golden-set case. `derived_from` is what makes it a verification."""

    pergunta: str
    esperado: str
    derivado_de: str


@dataclass
class Spec:
    slug: str
    nome: str
    uma_frase: str
    usar_quando: list[str]
    nunca_usar: list[str]
    ferramentas: list[str]
    dominios_permitidos: list[str] | None = None
    saida_cercada: list[str] | None = None
    toca_alvo: bool = False
    autorizacao: str | None = None
    lacunas: list[str] = field(default_factory=list)
    golden: list[Caso] = field(default_factory=list)
    precisa: list[str] = field(default_factory=list)
    idioma: str = "en"
    origem: str = ""

    # ---- the tool classes this spec asked for ----------------------------
    @property
    def usa_rede(self) -> bool:
        return bool(REDE & set(self.ferramentas))

    @property
    def usa_escrita(self) -> bool:
        return bool(ESCRITA & set(self.ferramentas))

    @property
    def usa_execucao(self) -> bool:
        return bool(EXECUCAO & set(self.ferramentas))

    @property
    def desconhecidas(self) -> list[str]:
        """A tool outside the known vocabulary.

        Not an error — a new harness brings a new name. But it is SHOWN in the
        recipe, because treating an unknown name as harmless is how a network
        fence stops fencing without anyone seeing.
        """
        return sorted(set(self.ferramentas) - CONHECIDAS)


def _lista(bruto: object) -> list[str]:
    if bruto is None:
        return []
    if isinstance(bruto, str):
        return [bruto]
    return [str(x) for x in bruto]  # type: ignore[union-attr]


def validar(spec: Spec) -> None:
    """Runs the eight refusals. Returns nothing — it either passes or raises `Recusa`."""
    if not SLUG.match(spec.slug):
        raise Recusa(
            "R8",
            f"`{spec.slug}` is not a valid slug",
            "use lowercase, digits and hyphen — it becomes a filename in 4 harnesses",
        )
    if spec.usa_rede and not spec.dominios_permitidos:
        raise Recusa(
            "R1",
            f"asks for a network tool ({', '.join(sorted(REDE & set(spec.ferramentas)))}) "
            "and does not declare `dominios_permitidos`",
            'declare `dominios_permitidos = ["example.com"]`, or `["nenhum"]` to block '
            "always — absent and empty mean the same thing and both BLOCK",
        )
    if spec.usa_escrita and not spec.saida_cercada:
        raise Recusa(
            "R2",
            f"asks for a write tool ({', '.join(sorted(ESCRITA & set(spec.ferramentas)))}) "
            "and does not declare `saida_cercada`",
            'declare `saida_cercada = ["reports/"]` — "I only write in one path" written '
            "in prose is not a fence, it is intent",
        )
    if not spec.nunca_usar:
        raise Recusa(
            "R3",
            "does not declare `nunca_usar`",
            "write at least one case where this agent is the WRONG choice — with no "
            "anti-description the orchestrator dispatches by topic similarity",
        )
    if not spec.lacunas:
        raise Recusa(
            "R4",
            "does not declare `lacunas`",
            "write what this agent does NOT measure — an absence with no owner ages "
            "silently, and an agent that declares no limit is read as if it had none",
        )
    if not spec.golden:
        raise Recusa(
            "R5",
            "has no golden-set case",
            "write a case with the answer checked BY HAND on disk — without it nothing "
            "asks whether the ANSWER is right, only whether the code obeys the spec",
        )
    for caso in spec.golden:
        if not caso.derivado_de.strip():
            raise Recusa(
                "R6",
                f"the case «{caso.pergunta[:40]}…» does not declare `derived_from`",
                "point to the source, as `path:line` or a URL, where the expected "
                "answer was read by hand",
            )
        if caso.derivado_de.strip().startswith(tuple(spec.saida_cercada or ())):
            raise Recusa(
                "R6",
                f"the case «{caso.pergunta[:40]}…» derives from `{caso.derivado_de}`, which is "
                "INSIDE the agent's own output",
                "derive from a source the agent does not write — both sides coming from "
                "the same place is a mirror check, and it passes green while locking the defect in",
            )
    if spec.toca_alvo and not spec.autorizacao:
        raise Recusa(
            "R7",
            "declares `toca_alvo = true` and does not declare where the engagement authorization is",
            'declare `autorizacao = "scope/target.md"` with target, scope, authorization and '
            "validity — a command outside the authorized target is an incident, not a finding",
        )


def ler(caminho: str | Path) -> Spec:
    """Reads and validates a spec. A field error is a `Recusa`, never a raw `KeyError`."""
    caminho = Path(caminho)
    dados = tomllib.loads(caminho.read_text(encoding="utf-8"))
    a = dados.get("agente") or {}
    f = dados.get("fronteira") or {}
    p = dados.get("prova") or {}
    c = dados.get("censo") or {}

    for campo in ("slug", "nome", "uma_frase"):
        if not a.get(campo):
            raise Recusa(
                "R0",
                f"the spec does not declare `agente.{campo}`",
                f'add `{campo} = "..."` in the `[agente]` section',
            )

    spec = Spec(
        slug=a["slug"],
        nome=a["nome"],
        uma_frase=a["uma_frase"],
        usar_quando=_lista(a.get("usar_quando")),
        nunca_usar=_lista(a.get("nunca_usar")),
        ferramentas=_lista(f.get("ferramentas")),
        dominios_permitidos=_lista(f.get("dominios_permitidos")) or None,
        saida_cercada=_lista(f.get("saida_cercada")) or None,
        toca_alvo=bool(f.get("toca_alvo", False)),
        autorizacao=f.get("autorizacao"),
        lacunas=_lista(p.get("lacunas")),
        golden=[
            Caso(
                pergunta=str(g.get("pergunta", "")),
                esperado=str(g.get("esperado", "")),
                derivado_de=str(g.get("derivado_de", "")),
            )
            for g in (p.get("golden") or [])
        ],
        precisa=_lista(c.get("precisa")),
        idioma=str(a.get("idioma", "en")),
        origem=str(caminho),
    )
    validar(spec)
    return spec



# ====================================================================
# forja\vistoria.py
# ====================================================================

"""Survey: reads the agents YOU ALREADY HAVE, and says what the SYSTEM is missing.

nature: fix — the output is always printed in full, even when it fails. A
survey that only shows up when it passes is not a survey.

The forge compiles spec → artifact. This is the other direction, and it is how
everyone arrives: you already have twelve hand-written agents and you are not
going to write twelve specs on faith. The survey reads the twelve and returns
what only shows up from the fifth on — the defects that live in no single
agent, but BETWEEN them.

    python -m forja                      # survey of `.claude/agents/`
    python -m forja --adotar             # WRITES: one spec per agent read

Seven findings. The first five are about ONE agent; the last two only exist
because there is more than one, and they are the reason this tool exists:

    V1  does not say what it NEVER does   the orchestrator dispatches by topic
    V2  does not say WHEN to use it       an agent nobody reaches
    V3  boundary only in the prose        asks for write/network without declaring where
    V4  does not say what it does not cover   silence is read as coverage
    V5  nothing checks the ANSWER         you test the code, never the answer
    V6  two get confused                  overlapping descriptions, and neither
                                          names the other
    V7  tool with no owner                inherits everything the harness offers

Exit code: 0 nothing found · 1 defect · 2 there was nothing to read.
The 2 is the point: a folder that does not exist is a REFUSAL, and never green.
A typo in the path must not leave a gate approving forever.
"""


import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


# Where today's harnesses keep agents. The search is by declared folder, and
# never by scanning the whole project: scanning `.` finds `node_modules` and
# returns a plausible, wrong answer.
PASTAS = (".claude/agents", ".claude/subagents", "agents", ".cursor/agents")

# Outside the vocabulary: a missing `tools:` does NOT mean "no tools".
# In today's harnesses it means **all** — which is the opposite, and is defect V7.
HERDA_TUDO = "«inherits all»"

_ACENTO = re.compile(r"[̀-ͯ]")
_PALAVRA = re.compile(r"[a-z0-9]{5,}")

# Words that show up in every agent description and distinguish nothing.
# Without this list, any two agents "look alike" and V6 becomes noise.
VAZIAS = frozenset(
    """
    agente agentes usar quando nunca sempre projeto arquivo arquivos pasta
    pastas quando sobre cada todos todas outro outra apenas mesmo mesma
    porque coisa coisas forma partir depois antes ainda entao tambem
    escrever escreve escrito leitura ler nunca_usar deve devem podem
    agent agents when never always project file files folder folders about
    each every other only same because thing things after before still also
    write writes written read never_use must should when should_not this
    """.split()
)


def _sem_acento(texto: str) -> str:
    return _ACENTO.sub("", unicodedata.normalize("NFD", texto.lower()))


def _significativas(texto: str) -> set[str]:
    """The words in a description that actually set it apart from the others."""
    return {p for p in _PALAVRA.findall(_sem_acento(texto))} - VAZIAS


@dataclass
class Lido:
    """An agent AS IT IS on disk — not as someone would like it to be."""

    caminho: Path
    slug: str
    descricao: str
    ferramentas: list[str]
    corpo: str
    tools_ausente: bool
    #: The project root that contains this agent — where the sibling files
    #: (hook, golden, gaps) are looked for. `None` when it cannot be said.
    raiz: Path | None = None
    #: The WHOLE frontmatter, raw `key: value` — not just `name`/`description`/
    #: `tools`. It exists because `write_paths`/`allowed_domains` (the two
    #: boundary marks V3 looks for) usually live HERE, not in the body prose —
    #: and a structured field is a stronger signal than the same sentence
    #: written as text (same reasoning as `_irmao_declara`).
    campos: dict[str, str] = field(default_factory=dict)

    @property
    def nome_curto(self) -> str:
        return self.caminho.name

    @property
    def usa_rede(self) -> bool:
        return bool(REDE & set(self.ferramentas)) or self.tools_ausente

    @property
    def usa_escrita(self) -> bool:
        return bool(ESCRITA & set(self.ferramentas)) or self.tools_ausente

    @property
    def desconhecidas(self) -> list[str]:
        return sorted(set(self.ferramentas) - CONHECIDAS)


@dataclass
class Achado:
    regra: str
    titulo: str
    conserto: str
    itens: list[str] = field(default_factory=list)
    grave: bool = True
    #: The DISTINCT agents hit. Kept apart from `itens` because one agent can
    #: yield two lines (write AND network), and counting a line as an agent
    #: would make the denominator say «4 of 2» — not measured turning into an
    #: invented number, inside the tool that exists to forbid it.
    agentes: set[str] = field(default_factory=set)


def _frontmatter(texto: str) -> tuple[dict[str, str], str]:
    """Minimal frontmatter, no dependency: `---` … `---`, one key per line.

    It is not a YAML parser and does not pretend to be. It reads what today's
    harnesses actually write — one-line `key: value` — and returns the rest as
    the body. A multi-line value is not read, and that is declared in LACUNAS.
    """
    if not texto.startswith("---"):
        return {}, texto
    fim = texto.find("\n---", 3)
    if fim == -1:
        return {}, texto
    campos: dict[str, str] = {}
    for linha in texto[3:fim].splitlines():
        if ":" not in linha or linha.startswith((" ", "\t", "#")):
            continue
        chave, _, valor = linha.partition(":")
        campos[chave.strip()] = valor.strip()
    return campos, texto[fim + 4 :]


def _desaspar(valor: str) -> str:
    """`description:` usually comes as a JSON string. Loose quotes are not data."""
    valor = valor.strip()
    if valor[:1] in {'"', "'"}:
        try:
            return json.loads(valor)
        except (ValueError, TypeError):
            return valor.strip("\"'")
    return valor


def ler_agente(caminho: Path, raiz: Path | None = None) -> Lido | None:
    """One file → one agent read. `None` when the file is not an agent."""
    try:
        texto = caminho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    campos, corpo = _frontmatter(texto)
    if "name" not in campos and "description" not in campos:
        return None  # loose markdown in the folder; not an agent, and not a number.
    bruto = campos.get("tools", "").strip()
    return Lido(
        caminho=caminho,
        slug=campos.get("name", caminho.stem).strip() or caminho.stem,
        descricao=_desaspar(campos.get("description", "")),
        ferramentas=[f.strip() for f in bruto.split(",") if f.strip()] if bruto else [],
        corpo=corpo,
        tools_ausente="tools" not in campos or not bruto,
        raiz=raiz,
        campos=campos,
    )


def achar_pasta(raiz: Path) -> Path | None:
    for relativo in PASTAS:
        candidato = raiz / relativo
        if candidato.is_dir():
            return candidato
    return None


def raiz_do_projeto(pasta: Path) -> Path:
    """From `<root>/.claude/agents` back to `<root>`. That is where the siblings are."""
    partes = [p.lower() for p in pasta.parts]
    return pasta.parent.parent if ".claude" in partes else pasta.parent


def ler_roster(pasta: Path) -> list[Lido]:
    raiz = raiz_do_projeto(pasta)
    lidos = [ler_agente(p, raiz) for p in sorted(pasta.glob("*.md"))]
    return [x for x in lidos if x is not None]


# ----------------------------------------------------------- the seven -----
#
# ⚠️ Every finding below is the ABSENCE of a machine-readable declaration —
# never a judgment about the quality of the agent. The difference matters: an
# excellent agent whose boundary is written in prose shows up here, and should.
# Prose is not a fence; it is intent, and no runtime reads it.
#
# Each mark is a closed list, and it is written here so that whoever disagrees
# can point at what is missing instead of finding the limit by being surprised.

DIZ_QUE_NAO_FAZ = ("nunca usar", "nunca use", "não usar para", "nao usar para",
                   "never use", "do not use", "never used for", "not for")
DIZ_QUANDO_USAR = ("usar quando", "usar para", "use quando", "use when", "use this",
                   "use for", "use it when")
DIZ_ONDE_ESCREVE = ("write_paths", "saida_cercada", "escreve só em", "escreve apenas em",
                    "um caminho só", "writes only in", "writes only to", "one path only")
DIZ_ONDE_FALA = ("allowed_domains", "dominios_permitidos", "domínios permitidos",
                 "allowed domains", "talks only to")
DIZ_O_QUE_NAO_COBRE = ("lacuna", "não mede", "nao mede", "não cobre", "nao cobre", "o que este",
                       "gap", "does not measure", "does not cover", "what this agent does not")
DIZ_QUE_CONFERE_RESPOSTA = ("golden", "resposta esperada", "caso de verificação",
                            "expected answer", "verification case")

# Above this, two descriptions fight over the same dispatch. The value is
# CHOSEN, not measured — and that is why it is here, with its owner, instead of
# buried in an if.
LIMIAR_CONFUSAO = 0.30


# Where a declaration can live OUTSIDE the agent's `.md`. A hook in a sibling
# file is a real fence — more real, in fact, than the same sentence written in
# the prompt prose, which no runtime reads. Searching only inside the `.md`
# would flag the compiler's own output, which is the family of defect where a
# tool starts measuring the wrong surface and calls it a finding.
IRMAOS = {
    "cerca": ("hooks", ".claude/hooks"),
    "golden": ("golden", "evals", "eval", "tests/golden"),
    "lacunas": (".", "docs"),
}
NOMES_DE_LACUNA = ("lacunas.md", "limitacoes.md", "limitations.md", "gaps.md")


def _irmao_declara(raiz: Path | None, slug: str, familia: str) -> bool:
    """Is there, next to the agent, a file that names it and makes this declaration?

    The search is by DECLARED folder and one level deep — never a scan of the
    whole project. Scanning `.` finds `node_modules` and returns a plausible,
    wrong answer, which is worse than finding nothing.
    """
    if raiz is None:
        return False
    alvo = _sem_acento(slug)
    for relativo in IRMAOS[familia]:
        pasta = raiz / relativo
        if not pasta.is_dir():
            continue
        for arquivo in sorted(pasta.glob("*")):
            if not arquivo.is_file() or arquivo.suffix not in {".py", ".md", ".json", ".toml", ".yaml", ".yml"}:
                continue
            if familia == "lacunas" and arquivo.name.lower() not in NOMES_DE_LACUNA:
                continue
            try:
                if alvo in _sem_acento(arquivo.read_text(encoding="utf-8", errors="replace")):
                    return True
            except OSError:
                continue
    return False


def _contem(lido: Lido, marcas: tuple[str, ...]) -> bool:
    alvo = _sem_acento(lido.descricao + "\n" + lido.corpo)
    return any(_sem_acento(m) in alvo for m in marcas)


def _campo_declarado(lido: Lido, *chaves: str) -> bool:
    """Does any of `chaves` exist in the FRONTMATTER with a non-empty value?

    Found this round: `_contem` never saw `saida_cercada`/`dominios_permitidos`
    when the agent declared them the RIGHT way — as a structured frontmatter
    field — because `_frontmatter()` pulls them out of the text before `corpo`
    exists, and `descricao` only carries the `description` field. An agent with
    `saida_cercada: "path/"` in the YAML failed V3 for the SAME reason a
    fenceless agent would — a false negative on the very mark the constant is
    named after. A structured field is a stronger signal than the same
    sentence in prose (same reasoning as `_irmao_declara`), so it decides on
    its own, without also having to show up in the body.
    """
    for chave in chaves:
        valor = lido.campos.get(chave, "").strip().strip('"').strip("'").strip()
        if valor:
            return True
    return False


def _confusao(a: Lido, b: Lido) -> float:
    """How much two descriptions fight over the same dispatch. Jaccard, no mystery."""
    pa, pb = _significativas(a.descricao), _significativas(b.descricao)
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / len(pa | pb)


def _um_nomeia_o_outro(a: Lido, b: Lido) -> bool:
    """A real anti-description is nominal: it names the sibling by its slug."""
    return (
        _sem_acento(b.slug) in _sem_acento(a.descricao + a.corpo)
        or _sem_acento(a.slug) in _sem_acento(b.descricao + b.corpo)
    )


def _fronteiras_abertas(a: Lido) -> tuple[tuple[str, str, bool], ...]:
    """An agent's two boundaries, and whether each one is declared."""
    return (
        (
            "write",
            "where it may write",
            a.usa_escrita
            and not _campo_declarado(a, "saida_cercada")
            and not _contem(a, DIZ_ONDE_ESCREVE)
            and not _irmao_declara(a.raiz, a.slug, "cerca"),
        ),
        (
            "network",
            "who it may talk to",
            a.usa_rede
            and not _campo_declarado(a, "dominios_permitidos")
            and not _contem(a, DIZ_ONDE_FALA)
            and not _irmao_declara(a.raiz, a.slug, "cerca"),
        ),
    )


def vistoriar(roster: list[Lido]) -> list[Achado]:
    achados: list[Achado] = []

    def marcar(
        regra: str,
        titulo: str,
        conserto: str,
        itens: list[str],
        agentes: set[str] | None = None,
        grave: bool = True,
    ) -> None:
        if itens:
            achados.append(Achado(regra, titulo, conserto, itens, grave, agentes or set(itens)))

    marcar(
        "V1",
        "DO NOT SAY WHAT THEY NEVER DO",
        "with no anti-description, the orchestrator dispatches by TOPIC — and the "
        "topic of two agents looks far more alike than their work does.",
        [a.nome_curto for a in roster if not _contem(a, DIZ_QUE_NAO_FAZ)],
    )
    marcar(
        "V2",
        "DO NOT SAY WHEN TO USE THEM",
        "an agent that does not declare its own trigger is an agent nobody "
        "reaches — it exists on disk and never in the dispatch.",
        [a.nome_curto for a in roster if not _contem(a, DIZ_QUANDO_USAR)],
    )
    marcar(
        "V3",
        "THE BOUNDARY IS ONLY IN THE PROSE",
        '"I only write in one path" and "I only read the docs" are intent. '
        "No runtime reads prose: with no declaration, the agent reaches "
        "everything the harness reaches.",
        [
            f"{a.nome_curto:<34} asks for {classe} and does not declare {campo}"
            for a in roster
            for classe, campo, falta in _fronteiras_abertas(a)
            if falta
        ],
        {a.nome_curto for a in roster if any(f for _, _, f in _fronteiras_abertas(a))},
    )
    marcar(
        "V4",
        "DO NOT SAY WHAT THEY DO NOT COVER",
        "silence is read as coverage. Whoever gets the answer has no way to "
        "know what the agent never looked at — and will treat what was missing as absent.",
        [
            a.nome_curto
            for a in roster
            if not _contem(a, DIZ_O_QUE_NAO_COBRE) and not _irmao_declara(a.raiz, a.slug, "lacunas")
        ],
    )
    marcar(
        "V5",
        "NOTHING CHECKS THEIR ANSWER",
        "there is no question whose correct answer is written by hand. Without "
        "that you test whether the agent RAN, never whether it was right.",
        [
            a.nome_curto
            for a in roster
            if not _contem(a, DIZ_QUE_CONFERE_RESPOSTA) and not _irmao_declara(a.raiz, a.slug, "golden")
        ],
    )
    marcar(
        "V7",
        "INHERIT EVERY TOOL FROM THE HARNESS",
        "a missing `tools:` does not mean no tools — in today's harnesses it "
        "means ALL, which is the opposite. A read-only agent inherits write "
        "and network with nobody deciding it.",
        [a.nome_curto for a in roster if a.tools_ausente],
    )

    pares = [
        f"{a.nome_curto} × {b.nome_curto}".ljust(46) + f"{_confusao(a, b):.0%} of the words in common"
        for i, a in enumerate(roster)
        for b in roster[i + 1 :]
        if _confusao(a, b) >= LIMIAR_CONFUSAO and not _um_nomeia_o_outro(a, b)
    ]
    marcar(
        "V6",
        "GET CONFUSED WITH EACH OTHER",
        "descriptions fighting over the same dispatch, and neither one names "
        "the other. The fix is nominal: each cites the sibling in what it NEVER does.",
        pares,
        agentes=set(),  # a pair is not an agent; it does not enter the denominator.
    )
    return achados


# ------------------------------------------------------- the report --------
LARGURA = 74


def relatorio(roster: list[Lido], achados: list[Achado], pasta: Path, hoje: str) -> list[str]:
    linhas = [f"survey · {pasta} · on {hoje}", "=" * LARGURA]
    linhas.append(f"Read {len(roster)} agent(s).")
    linhas.append("")

    for achado in sorted(achados, key=lambda a: (not a.grave, -len(a.itens))):
        marca = "⛔" if achado.grave else "⚠️"
        contagem = (
            f"{len(achado.itens)} pair(s)"
            if achado.regra == "V6"
            else f"{len(achado.agentes)} of {len(roster)}"
        )
        cabeca = f"{marca} {achado.titulo}"
        linhas.append(f"{cabeca}{' ' * max(1, LARGURA - len(cabeca) - len(contagem) - 1)}{contagem}")
        for item in achado.itens[:8]:
            linhas.append(f"     {item}")
        if len(achado.itens) > 8:
            linhas.append(f"     … and {len(achado.itens) - 8} more")
        linhas.append(f"     → {achado.conserto}")
        linhas.append("")

    # Six declarations per agent: what it never does · when to use it · where it
    # writes or talks · what it does not cover · what checks its answer · which
    # tools it has. The denominator is written here because a number with no
    # denominator is what this whole tool exists to demand.
    declaracoes_possiveis = len(roster) * 6
    ausentes = sum(len(a.agentes) for a in achados if a.regra != "V6")
    linhas.append("-" * LARGURA)
    linhas.append(
        f"{len(roster)} agent(s) · {len(achados)} defect type(s) · "
        f"{ausentes} of {declaracoes_possiveis} declarations missing"
    )
    return linhas


CABECA_TOML = """\
# Spec adopted from `{origem}` on {hoje}, by `python -m forja --adotar`.
#
# ⚠️ It is NOT ready: each `?` below is a hole that already existed in the agent
# and that nobody had anywhere to see. The forge REFUSES to compile while one
# stands, and every refusal carries the fix written out.
#
# What is filled in was READ from the original file, never inferred.
#
#     python -m forja {saida}
"""


def _t(valor: str) -> str:
    """A safe TOML string, no dependency: triple quotes and escape what breaks."""
    return '"""' + valor.replace("\\", "\\\\").replace('"""', '\\"\\"\\"').strip() + '"""'


def _lista_toml(itens: list[str], recuo: str = "  ") -> str:
    if not itens:
        return "[]"
    return "[\n" + "".join(f"{recuo}{_t(i)},\n" for i in itens) + "]"


def adotar(lido: Lido, hoje: str, saida: Path) -> str:
    """A hand-written agent → its spec, with a `?` in every hole.

    This is the point where the tool stops being an alarm. The annotation is
    the OUTPUT of the first run, never its toll: nobody with twelve agents is
    going to write twelve specs on faith to find out whether it was worth it.
    """
    faltando = "? — write here; the forge does not compile while this `?` stands"
    nunca = [] if _contem(lido, DIZ_QUE_NAO_FAZ) else [faltando]
    quando = [] if _contem(lido, DIZ_QUANDO_USAR) else [faltando]
    partes = [
        CABECA_TOML.format(origem=lido.caminho, hoje=hoje, saida=saida.name),
        "",
        "[agente]",
        f'slug = "{lido.slug}"',
        f"nome = {_t(lido.slug.replace('-', ' ').capitalize())}",
        f"uma_frase = {_t(lido.descricao or faltando)}",
        f"usar_quando = {_lista_toml(quando or ['(read from the original file — check and rewrite)'])}",
        f"nunca_usar = {_lista_toml(nunca or ['(read from the original file — check and rewrite)'])}",
        "",
        "[fronteira]",
        f"ferramentas = {json.dumps(lido.ferramentas, ensure_ascii=False)}"
        + ("  # ⚠️ `tools:` was ABSENT: the agent inherited ALL" if lido.tools_ausente else ""),
    ]
    if lido.usa_rede:
        partes.append(f'dominios_permitidos = ["?"]  # ["nenhum"] blocks always')
    if lido.usa_escrita:
        partes.append(f'saida_cercada = ["?"]  # the path prefix where it may write')
    partes += [
        "toca_alvo = false",
        "",
        "[prova]",
        f"lacunas = {_lista_toml([faltando])}",
        "",
        "[[prova.golden]]",
        f"pergunta = {_t('?')}",
        f"esperado = {_t('?')}",
        f"derivado_de = {_t('? — and NEVER from this agent output: both sides coming from the same source pass green while locking the defect in')}",
        "",
    ]
    return "\n".join(partes)


# --------------------------------------------------------------- CLI -------
#
# A parte que NÃO veio do pacote: um wrapper fino, só para este arquivo poder
# rodar sozinho. É a mesma lógica de `forja/__main__.py::_vistoria`, sem
# `--adotar`/`--html`/`--baseline` — este arquivo é só a LEITURA, a demo de
# 30 segundos do README. Para o resto, `pip install` ou `git clone` de verdade.

import sys as _sys
from datetime import date as _date


def _console_em_utf8() -> None:
    for stream in (_sys.stdout, _sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(_sys.argv[1:] if argv is None else argv)
    raiz = Path(argv[0]) if argv else Path(".")
    hoje = _date.today().isoformat()

    pasta = achar_pasta(raiz)
    if pasta is None:
        print(f"vistoria · {raiz} · em {hoje}")
        print("=" * LARGURA)
        print("Não achei pasta de agentes aqui. Procurei, nesta ordem:")
        for relativo in PASTAS:
            print(f"     {raiz / relativo}")
        print()
        print("RECUSADO — não li nada, e não vou devolver verde por isso.      (exit 2)")
        return 2

    roster = ler_roster(pasta)
    if not roster:
        print(f"vistoria · {pasta} · em {hoje}")
        print("=" * LARGURA)
        print("A pasta existe e não há nenhum agente dentro dela.")
        print()
        print("RECUSADO — zero agente lido não é zero defeito.                 (exit 2)")
        return 2

    achados = vistoriar(roster)
    for linha in relatorio(roster, achados, pasta, hoje):
        print(linha)

    print()
    if not achados:
        print("PASSA — todo agente lido declara as seis coisas.                (exit 0)")
        return 0
    print("REPROVA                                                        (exit 1)")
    print()
    print("  Este é o `forja.py` vendorizado — só a vistoria. `--adotar`, `--html`,")
    print("  `--baseline` e a compilação de spec → artefato exigem o pacote inteiro:")
    print("  `git clone https://github.com/marquesPablo/loadline && cd loadline`.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
