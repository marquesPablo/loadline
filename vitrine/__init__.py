"""`vitrine` — is your skill in the window, or in the stockroom?

An agent decides to load a skill by reading two fields: `name` and `description`.
The body of the `SKILL.md` is only read AFTER the decision has already been made.
Those two fields are the window; everything else is stock.

No compiler checks that window. The choice is probabilistic, made by a model, at
runtime — and when it fails, **there is no error**: the skill simply never gets
loaded, and nobody finds out.

This module checks the window rule by rule, calling no model. And it also knows how to CREATE a new
skill — `colher()` refuses to be born a redundant skill instead of auditing the redundancy after the
fact, calling no model either.
"""

from .colheita import Recusa as RecusaDeColheita
from .colheita import colher
from .regras import Skill, Achado, ler_skill, ler_pasta, vistoriar

__all__ = ["Skill", "Achado", "ler_skill", "ler_pasta", "vistoriar", "colher", "RecusaDeColheita"]
