"""Sondas da operação `vitrine`.

natureza: correcao — sonda que estoura vira `SEM_PROVA` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO **E** A PASTA `vitrine/` (a que fica na raiz deste repositório,
ao lado de `aferido/` e `forja/`) para a raiz do seu repositório. É a única
operação da prateleira que traz um pacote inteiro além do `sondas.py` — como a
`cerebro-local` traz `servidor.py`.

⚠️ **A regra anti-espelho, e como ela é respeitada aqui.** O `SKILL.md` de cada
skill é a fonte de tudo — não há dois lugares independentes onde «este nome está
certo» poderia estar escrito duas vezes. A independência aqui não é de FONTE, é
de MOMENTO: o selo que você cola no README congela «hoje há N skills e 0
reprovam»; a sonda RECOMPUTA isso do zero, a cada rodada, lendo o disco de novo.
Divergir significa que o disco mudou desde que o selo foi escrito — exatamente
o que a natureza `contagem`/`relacao` de cada métrica abaixo distingue.
"""

from __future__ import annotations

from pathlib import Path

from aferido import sonda
from vitrine import ler_pasta, vistoriar

RAIZ = Path(__file__).resolve().parent

#: Onde ficam as skills deste repositório. O único campo que esta operação pede
#: para ser ajustado — troque pelo caminho real, relativo à raiz do repositório.
CAMINHO_DE_SKILLS = RAIZ / ".claude" / "skills"


def _skills():
    return ler_pasta(CAMINHO_DE_SKILLS, com_git=True)


@sonda("vitrine.skills", origem="vitrine.ler_pasta sobre CAMINHO_DE_SKILLS")
def vitrine_skills() -> int:
    """De CONTAGEM. Sobe quando alguém escreve uma skill nova — normal, resele."""
    return len(_skills())


@sonda(
    "vitrine.reprovas",
    origem="vitrine.vistoriar — achados graves (⛔), skills distintas, não linhas",
)
def vitrine_reprovas() -> int:
    """De RELAÇÃO. Só sai de zero se uma skill ficou com o nome errado, sem
    gatilho, ou fora da gramática — e aí a resposta é consertar a skill, nunca
    resselar o número para cima.
    """
    achados = vistoriar(_skills())
    graves = {slug for a in achados if a.grave for slug in a.skills}
    return len(graves)
