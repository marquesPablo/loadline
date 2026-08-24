"""loadline — toda afirmação escrita vence, e este pacote faz ela dizer quando.

    Aquilo que não está escrito não existe.
    E aquilo que está escrito e não é reconferido, mente.

Sem dependência. Só a stdlib. Sem LLM, sem embedding, sem banco vetorial:
uma afirmação ou é recomputável por uma função, ou não é afirmável.
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
