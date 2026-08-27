"""Reading and writing seals — the grammar of a claim that re-checks itself.

loadline-ignore-file: this file TEACHES the syntax, and the seals written
here are specimens, not claims. Without this line the module reads its own
documentation as if it declared facts — and the MALFORMED seal example,
which has to be able to exist written out, would fail the run.

nature: fix — this module only reads text and returns structure. It
decides nothing about security, and an exception here surfaces and warns
instead of blocking.

A seal is a machine-readable comment, glued to the claim it covers:

    Six independent projects use the name AgentGuard.
    <!-- measured: collision.agentguard=6 nature=count on=2026-08-16 expires=90d -->

Three marks, and the difference between them is WHO produced the number:

    measured:    someone MEASURED, and it can be measured again. Has a probe.
    frozen:      this is history, and it does not recompute. Requires `reason=`.
    arbitrated:  someone CHOSE. Nobody measured, and nobody ever will.

`arbitrated:` is the mark that was missing, and its absence was the deepest gap
in this project: the other two **assume the number was measured at some point**.
Threshold, ceiling, deadline, `expires=90d` — all of them are choices dressed up
as measurements, and a number chosen without an owner is a guess wearing the
face of a fact:

    The retry limit is 3.
    <!-- arbitrated: retry.max=3 by="platform team" on=2026-08-20 expires=180d
         breaks="any incident where 3 was not enough" -->

Reserved keys (not metrics):

    nature   count | relation    — decides what DIVERGING means
    on       YYYY-MM-DD          — when it was last checked
    expires  Nd | Nm | never     — validity; without this the seal never expires
    source   path or URL         — where the metric is recomputed from
    reason   text                — required on `frozen:`
    by       who chose it        — required on `arbitrated:`
    breaks   what would overturn the choice — optional, and the most valuable part
    echo     no                  — waives the prose-vs-seal cross-check

Everything else is `metric=value`, and that is what the verifier recomputes.

The difference between `count` and `relation` is the heart of it, and it was
learned the hard way before this project: a COUNT quantity moves when someone
writes — diverging is normal, re-seal and move on. A RELATION quantity only
moves if the meter or the corpus broke — diverging is a DEFECT, and re-sealing
hides the bug.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

RESERVADAS = frozenset({"nature", "on", "expires", "source", "reason", "by", "breaks", "echo"})
NATUREZAS = frozenset({"count", "relation"})
TIPOS = ("measured", "frozen", "arbitrated")

#: The alternation of the marks, DERIVED from the tuple above and never written
#: out by hand twice. It is used here and in the prose cross-check (`eco.py`),
#: and the second copy already desynced once: when `arbitrated` was born, the
#: block recognizer kept seeing only two marks and started merging paragraphs
#: that the new seal separated — false-green on the wrong side. A fourth mark
#: must not be able to repeat this.
MARCAS_RE = "|".join(TIPOS)

# `<!-- measured: ... -->` in Markdown/HTML, `# measured: ...` in code.
_PADRAO = re.compile(
    rf"(?:<!--|#|//)\s*(?P<tipo>{MARCAS_RE})\s*:\s*(?P<corpo>.*?)\s*(?:-->|$)",
    re.IGNORECASE,
)

#: "does this line carry a seal?" — without capturing the body. Same source of truth.
SELO_NA_LINHA = re.compile(rf"(?:<!--|#|//)\s*(?:{MARCAS_RE})\s*:", re.IGNORECASE)

# `key=value` or `key="value with spaces"`.
_PAR = re.compile(r'(?P<k>[\w.\-]+)\s*=\s*(?:"(?P<qv>[^"]*)"|(?P<v>\S+))')

_DURACAO = re.compile(r"^(?P<n>\d+)(?P<u>[dm])$")


class SeloMalformado(ValueError):
    """The seal exists but will not be read. It never becomes 'no seal'."""


@dataclass(frozen=True)
class Selo:
    """A seal read from disk, with the line it came from."""

    tipo: str  # "measured" | "frozen" | "arbitrated"
    metricas: dict[str, str]
    nature: str | None = None
    on: date | None = None
    expires: str | None = None
    source: str | None = None
    reason: str | None = None
    by: str | None = None
    breaks: str | None = None
    echo: str | None = None
    arquivo: str = ""
    linha: int = 0
    bruto: str = ""

    @property
    def congelado(self) -> bool:
        return self.tipo == "frozen"

    @property
    def arbitrado(self) -> bool:
        """The number was CHOSEN. There is no probe, and there never will be.

        It does not recompute — but it EXPIRES, and that is what separates the
        mark from an excuse: a choice with no deadline is a forgotten choice,
        and it would be enough to call every awkward number arbitrated to never
        look at it again.
        """
        return self.tipo == "arbitrated"

    def vencido_em(self, hoje: date) -> bool:
        """Expiry is the seal's, not the value's.

        A seal can have the RIGHT number and still be expired: nobody re-checked
        within the deadline the seal itself declared. It is the half that every
        `awesome-*` list is missing — they age without ever failing.
        """
        prazo = self.prazo()
        if prazo is None or self.on is None:
            return False
        return hoje > self.on + prazo

    def prazo(self) -> timedelta | None:
        """`90d` -> 90 days. `6m` -> 180 days. `never` / absent -> None."""
        if not self.expires or self.expires.lower() == "never":
            return None
        m = _DURACAO.match(self.expires.strip())
        if not m:
            raise SeloMalformado(
                f"{self.arquivo}:{self.linha}: `expires={self.expires}` is not `Nd`, `Nm` or `never`"
            )
        n = int(m.group("n"))
        return timedelta(days=n if m.group("u") == "d" else n * 30)

    def idade_dias(self, hoje: date) -> int | None:
        return None if self.on is None else (hoje - self.on).days


def _data(bruta: str, onde: str) -> date:
    try:
        return date.fromisoformat(bruta)
    except ValueError as exc:
        raise SeloMalformado(f"{onde}: `on={bruta}` is not a YYYY-MM-DD date") from exc


def ler_linha(texto: str, arquivo: str = "", linha: int = 0) -> Selo | None:
    """Reads ONE seal from a line. Returns None if there is no seal at all."""
    m = _PADRAO.search(texto)
    if not m:
        return None

    onde = f"{arquivo}:{linha}"
    corpo = m.group("corpo")
    campos: dict[str, str] = {}
    for par in _PAR.finditer(corpo):
        valor = par.group("qv")
        campos[par.group("k").lower()] = valor if valor is not None else par.group("v")

    if not campos:
        raise SeloMalformado(f"{onde}: seal with no `key=value` at all")

    metricas = {k: v for k, v in campos.items() if k not in RESERVADAS}
    tipo = m.group("tipo").lower()

    nature = campos.get("nature")
    if nature is not None and nature not in NATUREZAS:
        raise SeloMalformado(
            f"{onde}: `nature={nature}` is outside the closed vocabulary {sorted(NATUREZAS)}"
        )
    if tipo == "measured" and metricas and nature is None:
        raise SeloMalformado(
            f"{onde}: a seal with a metric must declare `nature=count` or `nature=relation` "
            "— without it nobody knows whether diverging means 're-seal' or 'investigate'"
        )
    if tipo == "frozen" and not campos.get("reason"):
        raise SeloMalformado(
            f'{onde}: `frozen:` requires `reason="..."` — freezing without saying why '
            "is the same as deleting the measurement"
        )
    if tipo == "arbitrated" and not campos.get("by"):
        raise SeloMalformado(
            f'{onde}: `arbitrated:` requires `by="..."` — a number chosen with no owner is '
            "a guess dressed as a measurement, which is exactly what this mark exists to unmask"
        )

    return Selo(
        tipo=tipo,
        metricas=metricas,
        nature=nature,
        on=_data(campos["on"], onde) if "on" in campos else None,
        expires=campos.get("expires"),
        source=campos.get("source"),
        reason=campos.get("reason"),
        by=campos.get("by"),
        breaks=campos.get("breaks"),
        echo=campos.get("echo"),
        arquivo=arquivo,
        linha=linha,
        bruto=m.group(0),
    )


def ler_texto(texto: str, arquivo: str = "") -> list[Selo]:
    """Every seal in a text, in the order they appear."""
    achados: list[Selo] = []
    for n, linha in enumerate(texto.splitlines(), start=1):
        selo = ler_linha(linha, arquivo=arquivo, linha=n)
        if selo is not None:
            achados.append(selo)
    return achados


def escrever(selo: Selo, **mudancas: object) -> str:
    """Returns the text of a seal with fields swapped — for the re-seal.

    Rewrites the WHOLE seal from the structure. Editing the comment with a
    string replace is how half of the pair gets lost: you touch the header and
    forget the prose, or the other way around.
    """
    metricas = dict(selo.metricas)
    reservadas = {
        "nature": selo.nature,
        "on": selo.on.isoformat() if selo.on else None,
        "expires": selo.expires,
        "source": selo.source,
        "reason": selo.reason,
        "by": selo.by,
        "breaks": selo.breaks,
    }
    for chave, valor in mudancas.items():
        alvo = reservadas if chave in RESERVADAS else metricas
        alvo[chave] = None if valor is None else str(valor)

    partes = [f"{k}={v}" for k, v in metricas.items() if v is not None]
    for chave in ("nature", "by", "on", "expires", "source"):
        if reservadas.get(chave) is not None:
            valor = str(reservadas[chave])
            partes.append(f'{chave}="{valor}"' if " " in valor else f"{chave}={valor}")
    for chave in ("reason", "breaks"):
        if reservadas.get(chave) is not None:
            partes.append(f'{chave}="{reservadas[chave]}"')

    return f"<!-- {selo.tipo}: {' '.join(partes)} -->"
