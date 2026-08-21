"""aferido — toda afirmação escrita vence, e este pacote faz ela dizer quando.

    Aquilo que não está escrito não existe.
    E aquilo que está escrito e não é reconferido, mente.

Sem dependência. Só a stdlib. Sem LLM, sem embedding, sem banco vetorial:
uma afirmação ou é recomputável por uma função, ou não é afirmável.
"""

from .registro import SemSonda, achar, explicar, medir, sonda
from .selo import TIPOS, Selo, SeloMalformado, escrever, ler_linha, ler_texto
from .varredura import varrer
from .eco import PROSA_MUDA, Afirmacao, afirmacoes_sem_selo
from .selar import selar
from .veredito import (
    ARBITRADO,
    CONGELADO,
    DERIVOU,
    SEM_PROVA,
    VALE,
    VENCIDO,
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
    "VALE",
    "DERIVOU",
    "VENCIDO",
    "SEM_PROVA",
    "CONGELADO",
    "ARBITRADO",
    "PROSA_MUDA",
    "__version__",
]
