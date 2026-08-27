"""`--baseline`: o achado de hoje vira "o que MUDOU desde a última vez".

nature: fix — sem baseline gravado, a ferramenta RECUSA (não inventa
"nada mudou" comparando com o vazio); com baseline, ela nunca esconde um item
novo atrás dos que já eram conhecidos.

Por que isto existe: numa vistoria com centenas de agentes (86,7% de
declarações ausentes, medido em 2026-08-24 contra os cinco catálogos mais
populares do GitHub), a lista inteira a cada rodada é ruído depois da primeira
leitura — ninguém relê 300 linhas iguais toda vez só para achar as 4 novas.

    python -m forja . --baseline --gravar   # ESCREVE .loadline-baseline.json
    python -m forja . --baseline            # mostra só o que mudou desde lá

O arquivo é local do usuário — não pertence a este pacote, e cada repositório
que adota `loadline` tem o seu. Comitá-lo ou não é escolha de quem adota.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .vistoria import Achado

ARQUIVO_PADRAO = ".loadline-baseline.json"


@dataclass(frozen=True)
class Baseline:
    gravado_em: str
    itens: frozenset[str]


def _chaves(achados: list[Achado]) -> list[str]:
    """Cada achado vira `REGRA: item` — a mesma chave nos dois lados do diff."""
    return sorted(f"{a.regra}: {item}" for a in achados for item in a.itens)


def gravar(caminho: Path, achados: list[Achado], hoje: str) -> None:
    dados = {"gravado_em": hoje, "itens": _chaves(achados)}
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ler(caminho: Path) -> Baseline | None:
    """`None` quando o arquivo não existe — RECUSA é do chamador, não daqui."""
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        # Baseline corrompido é a MESMA leitura de baseline ausente: o chamador
        # recusa e manda gravar de novo, em vez de fingir que não há defeito.
        return None
    if not isinstance(dados, dict) or "itens" not in dados:
        return None
    return Baseline(
        gravado_em=str(dados.get("gravado_em", "?")),
        itens=frozenset(str(i) for i in dados.get("itens", [])),
    )


def diff(baseline: Baseline, achados: list[Achado]) -> tuple[list[str], list[str]]:
    """`(novos, resolvidos)` — o que apareceu, e o que sumiu, desde o baseline."""
    atual = frozenset(_chaves(achados))
    novos = sorted(atual - baseline.itens)
    resolvidos = sorted(baseline.itens - atual)
    return novos, resolvidos
