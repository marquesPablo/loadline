"""Modo comparação: `forja repoA repoB repoC` — vários repositórios, UMA tabela.

nature: fix — a saída sempre lista TODO alvo pedido, inclusive o que não
tem pasta de agentes; um alvo que desapareceu da tabela em silêncio é o mesmo
defeito que a vistoria de um repositório só já recusa há muito tempo.

Formaliza o que a auditoria de 2026-08-24 (cinco catálogos de agentes do
GitHub, 567 agentes, 86,7% de declarações ausentes) precisou fazer à mão com
um script descartável — este módulo é esse script, mantido.
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
            resultados.append(Comparado(alvo, erro="sem pasta de agentes"))
            continue
        roster = ler_roster(pasta)
        if not roster:
            resultados.append(Comparado(alvo, erro="pasta vazia"))
            continue
        achados = vistoriar(roster)
        possiveis = len(roster) * 6
        ausentes = sum(len(a.agentes) for a in achados if a.regra != "V6")
        resultados.append(Comparado(alvo, len(roster), ausentes, possiveis, achados))
    return resultados


def _pct(ausentes: int, possiveis: int) -> str:
    return f"{ausentes / possiveis:.0%}" if possiveis else "—"


def codigo_de_saida(resultados: list[Comparado]) -> int:
    """0 só quando TODO alvo foi lido e nenhum tem declaração ausente.

    Um alvo sem pasta de agentes não é *defeito* do repositório dele — é
    *não medido*, a mesma leitura que a vistoria de alvo único já dá (RECUSA,
    nunca verde). Por isso ele nunca deixa a comparação sair 0, mesmo quando
    todo alvo LIDO está limpo: dizer "PASSA" aqui esconderia que uma fração da
    tabela não foi medida, e é exatamente esse encobrimento que este projeto
    inteiro existe para proibir.
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
    linhas = [f"forja · comparação de {len(resultados)} repositório(s) · em {hoje}", "=" * LARGURA, ""]

    col_alvo = max(11, max((len(str(r.alvo)) for r in resultados), default=0))
    cabeca = f"{'repositório':<{col_alvo}}  {'agentes':>8}  {'ausentes':>16}  {'% ausente':>10}"
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
        linhas.append("RECUSADO — nenhum dos alvos tinha pasta de agentes para ler.        (exit 2)")
    elif codigo == 1:
        linhas.append("REPROVA — pelo menos um repositório tem declaração ausente.        (exit 1)")
    elif codigo == 2:
        linhas.append(
            f"RECUSADO — {len(invalidos)} de {len(resultados)} alvo(s) sem pasta de agentes; "
            "o resto está limpo, mas parte não foi medida.       (exit 2)"
        )
    else:
        linhas.append("PASSA — todo agente, em todo repositório, declara as seis coisas.  (exit 0)")
    return linhas
