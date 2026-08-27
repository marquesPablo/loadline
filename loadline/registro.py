"""The probe registry — who knows how to recompute each metric.

nature: fix — a probe that blows up becomes the verdict `UNPROVEN`, with
the error written out. It never takes down the run nor, worse, passes as green.

A probe is a function that returns TODAY's value for a metric. It is the
independent side of the pair: the seal says what was written, the probe says
what is.

    from loadline import sonda

    @sonda("collision.*")
    def count_collision(metric, seal):
        return len(load(seal.source)[metric.split(".")[-1]])

⚠️ The rule that makes this worth anything: **the probe must not read the same
source that produced the written number.** If both sides come from the same
place, the pair passes green while locking the defect in instead of finding it
— it is a mirror check, and it verifies nothing. `explicar()` exists to make
this auditable: every probe declares where it takes its value from, and the
declaration goes in the report.
"""

from __future__ import annotations

import fnmatch
import inspect
from collections.abc import Callable
from dataclasses import dataclass

from .selo import Selo

Valor = str | int | float


@dataclass(frozen=True)
class Sonda:
    padrao: str
    funcao: Callable[..., Valor]
    origem: str  # where it takes its value from — auditable, required


class SemSonda(LookupError):
    """No probe covers this metric. Becomes `UNPROVEN`, never `MATCHES`."""


_SONDAS: list[Sonda] = []


def sonda(padrao: str, origem: str = "") -> Callable[[Callable[..., Valor]], Callable[..., Valor]]:
    """Registers a function as the probe for the metrics that match `padrao`.

    `padrao` takes a glob (`collision.*`). More specific probes win over more
    generic ones, regardless of the order they were registered in.
    """

    def decorar(funcao: Callable[..., Valor]) -> Callable[..., Valor]:
        _SONDAS.append(
            Sonda(
                padrao=padrao,
                funcao=funcao,
                origem=origem or (funcao.__doc__ or "").strip().splitlines()[0]
                if funcao.__doc__
                else f"{funcao.__module__}.{funcao.__qualname__}",
            )
        )
        return funcao

    return decorar


def _especificidade(padrao: str) -> tuple[int, int]:
    """Fewer wildcards wins; on a tie, the longer pattern wins."""
    return (-padrao.count("*") - padrao.count("?"), len(padrao))


def achar(metrica: str) -> Sonda:
    candidatas = [s for s in _SONDAS if fnmatch.fnmatchcase(metrica, s.padrao)]
    if not candidatas:
        raise SemSonda(
            f"no probe covers `{metrica}` — the written value cannot be confronted, "
            "and claiming it holds would be inventing"
        )
    return max(candidatas, key=lambda s: _especificidade(s.padrao))


def medir(metrica: str, selo: Selo) -> Valor:
    """Runs the metric's probe. Takes `f(metric, seal)`, `f(seal)` or `f()`.

    The arity comes from the signature, not from trial and error: swallowing a
    `TypeError` to try again would hide a `TypeError` from inside the probe
    itself, and the verdict would come out wrong with nobody seeing.
    """
    alvo = achar(metrica).funcao
    posicionais = [
        p
        for p in inspect.signature(alvo).parameters.values()
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.default is p.empty
    ]
    return alvo(*(metrica, selo)[: len(posicionais)])


def explicar() -> list[tuple[str, str]]:
    """(pattern, where the probe takes its value from) — for the evidence report."""
    return sorted((s.padrao, s.origem) for s in _SONDAS)


def limpar() -> None:
    """Test only. Clears the registry."""
    _SONDAS.clear()
