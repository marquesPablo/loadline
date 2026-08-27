"""Comparison mode: `forja repoA repoB repoC` — several repositories, ONE table.

nature: fix — the output always lists EVERY target asked for, including the
one with no agents folder; a target that vanished from the table silently is
the same defect that the single-repository survey has refused for a long time.

Formalizes what the 2026-08-24 audit (five GitHub agent catalogs, 567 agents,
86.7% of declarations missing) had to do by hand with a throwaway script — this
module is that script, kept.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .vistoria import Achado, LARGURA, achar_pasta, ler_roster, vistoriar


@dataclass
class Comparado:
    alvo: Path
    agentes: int = 0
    ausentes: int = 0
    possiveis: int = 0
    achados: list[Achado] = field(default_factory=list)
    erro: str | None = None


def comparar(alvos: list[Path]) -> list[Comparado]:
    resultados: list[Comparado] = []
    for alvo in alvos:
        pasta = achar_pasta(alvo)
        if pasta is None:
            resultados.append(Comparado(alvo, erro="no agents folder"))
            continue
        roster = ler_roster(pasta)
        if not roster:
            resultados.append(Comparado(alvo, erro="empty folder"))
            continue
        achados = vistoriar(roster)
        possiveis = len(roster) * 6
        ausentes = sum(len(a.agentes) for a in achados if a.regra != "V6")
        resultados.append(Comparado(alvo, len(roster), ausentes, possiveis, achados))
    return resultados


def _pct(ausentes: int, possiveis: int) -> str:
    return f"{ausentes / possiveis:.0%}" if possiveis else "—"


def codigo_de_saida(resultados: list[Comparado]) -> int:
    """0 only when EVERY target was read and none has a missing declaration.

    A target with no agents folder is not a *defect* of that repository — it is
    *not measured*, the same reading the single-target survey already gives
    (REFUSAL, never green). That is why it never lets the comparison exit 0,
    even when every target READ is clean: saying "PASS" here would hide that a
    fraction of the table was not measured, and that cover-up is exactly what
    this whole project exists to forbid.
    """
    validos = [r for r in resultados if r.erro is None]
    invalidos = [r for r in resultados if r.erro is not None]
    if not validos:
        return 2
    if any(r.ausentes for r in validos):
        return 1
    if invalidos:
        return 2
    return 0


def relatorio(resultados: list[Comparado], hoje: str) -> list[str]:
    linhas = [f"forja · comparison of {len(resultados)} repository(ies) · on {hoje}", "=" * LARGURA, ""]

    col_alvo = max(11, max((len(str(r.alvo)) for r in resultados), default=0))
    cabeca = f"{'repository':<{col_alvo}}  {'agents':>8}  {'missing':>16}  {'% missing':>10}"
    linhas.append(cabeca)
    linhas.append("-" * len(cabeca))

    total_agentes = total_ausentes = total_possiveis = 0
    for r in resultados:
        if r.erro is not None:
            linhas.append(f"{str(r.alvo):<{col_alvo}}  {'—':>8}  {r.erro:>16}  {'—':>10}")
            continue
        total_agentes += r.agentes
        total_ausentes += r.ausentes
        total_possiveis += r.possiveis
        declaracoes = f"{r.ausentes} / {r.possiveis}"
        linhas.append(f"{str(r.alvo):<{col_alvo}}  {r.agentes:>8}  {declaracoes:>16}  {_pct(r.ausentes, r.possiveis):>10}")

    linhas.append("-" * len(cabeca))
    declaracoes_total = f"{total_ausentes} / {total_possiveis}"
    linhas.append(
        f"{'total':<{col_alvo}}  {total_agentes:>8}  {declaracoes_total:>16}  {_pct(total_ausentes, total_possiveis):>10}"
    )
    linhas.append("")

    codigo = codigo_de_saida(resultados)
    invalidos = [r for r in resultados if r.erro is not None]
    if codigo == 2 and not any(r.erro is None for r in resultados):
        linhas.append("REFUSED — none of the targets had an agents folder to read.        (exit 2)")
    elif codigo == 1:
        linhas.append("FAIL — at least one repository has a missing declaration.          (exit 1)")
    elif codigo == 2:
        linhas.append(
            f"REFUSED — {len(invalidos)} of {len(resultados)} target(s) with no agents folder; "
            "the rest is clean, but part was not measured.       (exit 2)"
        )
    else:
        linhas.append("PASS — every agent, in every repository, declares the six things.  (exit 0)")
    return linhas
