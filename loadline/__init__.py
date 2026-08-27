"""loadline — every written claim expires, and this package makes it say when.

    What is not written down does not exist.
    And what is written down and not re-checked lies.

No dependencies. Just the stdlib. No LLM, no embedding, no vector store:
a claim is either recomputable by a function, or it is not claimable.
"""

from .registro import SemSonda, achar, explicar, medir, sonda
from .selo import TIPOS, Selo, SeloMalformado, escrever, ler_linha, ler_texto
from .varredura import varrer
from .eco import PROSE_DRIFT, Afirmacao, afirmacoes_sem_selo
from .selar import selar
from .veredito import (
    ARBITRATED,
    FROZEN,
    DRIFTED,
    UNPROVEN,
    MATCHES,
    EXPIRED,
    Achado,
    Relatorio,
    julgar,
)

__version__ = "0.1.0"

__all__ = [
    "Selo",
    "SeloMalformado",
    "ler_linha",
    "ler_texto",
    "escrever",
    "sonda",
    "medir",
    "achar",
    "explicar",
    "SemSonda",
    "julgar",
    "Achado",
    "Relatorio",
    "varrer",
    "selar",
    "Afirmacao",
    "afirmacoes_sem_selo",
    "TIPOS",
    "MATCHES",
    "DRIFTED",
    "EXPIRED",
    "UNPROVEN",
    "FROZEN",
    "ARBITRATED",
    "PROSE_DRIFT",
    "__version__",
]
