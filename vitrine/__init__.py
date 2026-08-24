"""`vitrine` — a sua skill está na vitrine, ou está no estoque?

Um agente decide carregar uma skill lendo dois campos: `name` e `description`.
O corpo do `SKILL.md` só é lido DEPOIS que a decisão já foi tomada. Esses dois
campos são a vitrine; todo o resto é estoque.

Nenhum compilador confere essa vitrine. A escolha é probabilística, feita por um
modelo, em tempo de execução — e quando ela falha, **não há erro**: a skill
simplesmente nunca é carregada, e ninguém fica sabendo.

Este módulo confere a vitrine por regra, sem chamar modelo nenhum. E ele também sabe CRIAR uma
skill nova — `colher()` recusa nascer skill redundante em vez de auditar a redundância depois do
fato, sem chamar modelo nenhum também.
"""

from .colheita import Recusa as RecusaDeColheita
from .colheita import colher
from .regras import Skill, Achado, ler_skill, ler_pasta, vistoriar

__all__ = ["Skill", "Achado", "ler_skill", "ler_pasta", "vistoriar", "colher", "RecusaDeColheita"]
