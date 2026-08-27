"""`--baseline`: today's finding becomes "what CHANGED since last time".

nature: fix — with no baseline recorded, the tool REFUSES (it does not
invent "nothing changed" by comparing against the void); with a baseline, it
never hides a new item behind the ones already known.

Why this exists: in a survey with hundreds of agents (86.7% of declarations
missing, measured on 2026-08-24 against the five most popular GitHub catalogs),
the whole list on every run is noise after the first read — nobody re-reads 300
identical lines every time just to find the 4 new ones.

    python -m forja . --baseline --gravar   # WRITES .loadline-baseline.json
    python -m forja . --baseline            # shows only what changed since then

The file is the user's local file — it does not belong to this package, and
every repository that adopts `loadline` has its own. Committing it or not is the
adopter's choice.
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
    """Each finding becomes `RULE: item` — the same key on both sides of the diff."""
    return sorted(f"{a.regra}: {item}" for a in achados for item in a.itens)


def gravar(caminho: Path, achados: list[Achado], hoje: str) -> None:
    dados = {"gravado_em": hoje, "itens": _chaves(achados)}
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ler(caminho: Path) -> Baseline | None:
    """`None` when the file does not exist — the REFUSAL is the caller's, not here."""
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        # A corrupt baseline is the SAME reading as an absent one: the caller
        # refuses and asks for it to be written again, instead of pretending
        # there is no defect.
        return None
    if not isinstance(dados, dict) or "itens" not in dados:
        return None
    return Baseline(
        gravado_em=str(dados.get("gravado_em", "?")),
        itens=frozenset(str(i) for i in dados.get("itens", [])),
    )


def diff(baseline: Baseline, achados: list[Achado]) -> tuple[list[str], list[str]]:
    """`(new, resolved)` — what appeared, and what disappeared, since the baseline."""
    atual = frozenset(_chaves(achados))
    novos = sorted(atual - baseline.itens)
    resolvidos = sorted(baseline.itens - atual)
    return novos, resolvidos
