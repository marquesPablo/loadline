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

from __future__ import annotations

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
