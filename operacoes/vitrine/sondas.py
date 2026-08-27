"""Probes for the `vitrine` operation.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with the
error written out. It never returns a guess.

COPY THIS FILE **AND** THE `vitrine/` FOLDER (the one at the root of this
repository, next to `loadline/` and `forja/`) to the root of your repository. It
is the only operation on the shelf that ships a whole package beyond `sondas.py`
— the same way `cerebro-local` ships `servidor.py`.

⚠️ **The anti-mirror rule, and how it is respected here.** Each skill's
`SKILL.md` is the source of everything — there are not two independent places
where «this name is right» could be written twice. The independence here is not
of SOURCE, it is of MOMENT: the seal you paste in the README freezes «today
there are N skills and 0 fail»; the probe RECOMPUTES that from scratch, on every
run, reading the disk again. Diverging means the disk changed since the seal was
written — exactly what the `count`/`relation` nature of each metric below
distinguishes.
"""

from __future__ import annotations

from pathlib import Path

from loadline import sonda
from vitrine import ler_pasta, vistoriar

RAIZ = Path(__file__).resolve().parent

#: Where this repository's skills live. The one field this operation asks you to
#: adjust — change it to the real path, relative to the repository root.
CAMINHO_DE_SKILLS = RAIZ / ".claude" / "skills"


def _skills():
    return ler_pasta(CAMINHO_DE_SKILLS, com_git=True)


@sonda("vitrine.skills", origem="vitrine.ler_pasta over CAMINHO_DE_SKILLS")
def vitrine_skills() -> int:
    """A COUNT. Goes up when someone writes a new skill — normal, re-seal."""
    return len(_skills())


@sonda(
    "vitrine.reprovas",
    origem="vitrine.vistoriar — grave findings (⛔), distinct skills, not lines",
)
def vitrine_reprovas() -> int:
    """A RELATION. It only leaves zero if a skill ended up with the wrong name,
    no trigger, or outside the grammar — and then the answer is to fix the
    skill, never to re-seal the number upward.
    """
    achados = vistoriar(_skills())
    graves = {slug for a in achados if a.grave for slug in a.skills}
    return len(graves)
