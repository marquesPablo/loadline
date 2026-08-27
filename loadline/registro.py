"""O registro de sondas — quem sabe recomputar cada métrica.

natureza: correcao — sonda que estoura vira veredito `SEM_PROVA`, com o erro
escrito por extenso. Ela nunca derruba a rodada nem, pior, passa como verde.

Uma sonda é uma função que devolve o valor de HOJE para uma métrica. Ela é o
lado independente do par: o selo diz o que estava escrito, a sonda diz o que é.

    from loadline import sonda

    @sonda("colisao.*")
    def contar_colisao(metrica, selo):
        return len(carregar(selo.source)[metrica.split(".")[-1]])

⚠️ A regra que faz isso valer alguma coisa: **a sonda não pode ler a mesma
fonte que produziu o número escrito.** Se os dois lados saem do mesmo lugar,
o par passa verde travando o defeito em vez de achá-lo — é check espelho, e
ele não verifica nada. `explicar()` existe para tornar isso auditável: toda
sonda declara de onde tira o valor, e a declaração fica no relatório.
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
    origem: str  # de onde ela tira o valor — auditável, obrigatório


class SemSonda(LookupError):
    """Nenhuma sonda cobre esta métrica. Vira `SEM_PROVA`, nunca `HOLDS`."""


_SONDAS: list[Sonda] = []


def sonda(padrao: str, origem: str = "") -> Callable[[Callable[..., Valor]], Callable[..., Valor]]:
    """Registra uma função como sonda das métricas que casam com `padrao`.

    `padrao` aceita glob (`colisao.*`). Sondas mais específicas ganham das
    mais genéricas, independente da ordem em que foram registradas.
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
    """Menos curinga ganha; empatou, o padrão mais longo ganha."""
    return (-padrao.count("*") - padrao.count("?"), len(padrao))


def achar(metrica: str) -> Sonda:
    candidatas = [s for s in _SONDAS if fnmatch.fnmatchcase(metrica, s.padrao)]
    if not candidatas:
        raise SemSonda(
            f"nenhuma sonda cobre `{metrica}` — o valor escrito não pode ser confrontado, "
            "e afirmar que ele vale seria inventar"
        )
    return max(candidatas, key=lambda s: _especificidade(s.padrao))


def medir(metrica: str, selo: Selo) -> Valor:
    """Roda a sonda da métrica. Aceita `f(metrica, selo)`, `f(selo)` ou `f()`.

    A aridade sai da assinatura, não de tentativa-e-erro: engolir `TypeError`
    para tentar de novo esconderia um `TypeError` de dentro da própria sonda,
    e o veredito sairia errado sem ninguém ver.
    """
    alvo = achar(metrica).funcao
    posicionais = [
        p
        for p in inspect.signature(alvo).parameters.values()
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.default is p.empty
    ]
    return alvo(*(metrica, selo)[: len(posicionais)])


def explicar() -> list[tuple[str, str]]:
    """(padrão, de onde a sonda tira o valor) — para o relatório de evidência."""
    return sorted((s.padrao, s.origem) for s in _SONDAS)


def limpar() -> None:
    """Só para teste. Zera o registro."""
    _SONDAS.clear()
