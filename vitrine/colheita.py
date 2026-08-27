"""The harvest — turns what worked into a new `SKILL.md`, and refuses to duplicate.

    $ python -m vitrine --harvest skill-name --says "one sentence about what it does"
    $ python -m vitrine --harvest skill-name --says "..." --folder .claude/skills

nature: security — the harvest is a refusal before it is a write: a slug
outside the grammar, a slug already taken, and a description that collides with
a skill that already exists NEVER become a file. A tool that does its "best
effort" and writes anyway produces skill nº2 fighting over the same dispatch —
the same defect the `S11` rule audits AFTER the fact. Here it is caught BEFORE.

## The four refusals

    H1  slug outside the Agent Skills format grammar (the same rule as S2)
    H2  a folder with this slug already exists in the target — never overwrites
    H3  the description collides with a skill that already exists there (same rule as S11)
    H4  no description was passed — nothing to check any collision against

## This is not "Skill Forge" with a model writing behind it

There is no LLM here, and there will not be — the same invariant as the rest of
the project (README: "a verifier that depends on a model is not a verifier").
What it writes is the half that does NOT need a model: a `SKILL.md` that is born
compiling clean against the structural rules (`S1`, `S2`, `S6`…), with a `?`
exactly in the two fields only someone who lived the work can fill in — and the
certainty, checked BEFORE writing, that nobody in the target already occupies
that dispatch. See `LACUNAS.md` §10 for what it does NOT cover.
"""

from __future__ import annotations

from pathlib import Path

from .regras import LIMIAR_CONFUSAO, NOME_VALIDO, Skill, _confusao, _um_nomeia_o_outro, ler_pasta

FALTA = "?"

#: The final `description` carries the real text from `--says` — it never
#: becomes `{falta}` by itself. Two reasons, both measured writing this module:
#:   1. If it became `{falta}`, the NEXT harvest, comparing against this skill
#:      on disk, would have no word to cross-check — the collision check (H3)
#:      would be blind to every not-yet-filled skill.
#:   2. The TWO missing clauses (positive and negative trigger) stay as
#:      `{falta}` inside the SAME description, but without the word "when" next
#:      to them — writing it here would make the S3/S4 rules read the gap's
#:      label as if it were the trigger, and pass green on an empty field.
MODELO = '''---
name: {slug}
description: {descricao} — positive trigger: {falta}; negative trigger: {falta}
---

# {slug}

{falta}

<!-- The harvest left three holes standing, on purpose — it has no model, and
does not write any of them for you:
  1. the positive trigger, above — when to use it, rule S3: write the
     conditional clause ("...when the PR touches authentication", for example).
  2. the negative trigger, above — when NOT to use it, rule S4: name the most
     similar skill, if any, by its slug.
  3. the body, down here — the step-by-step that actually worked.
Run `python -m vitrine {pasta}` after filling them in: the three holes are ⛔
until they become real text, and the rest of the rules (S1, S2, S6…) is already
born clean. -->
'''


class Recusa(ValueError):
    """The harvest refused to write. Always with the rule code and the fix."""

    def __init__(self, regra: str, motivo: str, conserto: str) -> None:
        self.regra, self.motivo, self.conserto = regra, motivo, conserto
        super().__init__(f"{regra}: {motivo}\n      fix: {conserto}")


def colher(slug: str, descricao: str, pasta: Path) -> Path:
    """Writes `<folder>/<slug>/SKILL.md`, or refuses. Never both half-way.

    `descricao` is used ONLY to check for a collision with what already exists
    in `pasta` — it is not copied verbatim into the file: the final
    `description` is born as `?`, because the sentence that passes the collision
    check may not be the sentence that passes `S3`/`S4` (positive and negative
    trigger), and confusing the two is exactly the family of defect this whole
    project exists to demand.
    """
    if not (NOME_VALIDO.match(slug) and len(slug) <= 64):
        raise Recusa(
            "H1",
            f"`{slug}` is not a valid slug",
            "1 to 64 characters, only lowercase, digits and a single hyphen — the "
            "same grammar rule S2 audits after the fact",
        )
    if not descricao.strip():
        raise Recusa(
            "H4",
            "no `--says` was passed",
            "describe in one sentence what the skill does — it is that sentence the "
            "harvest uses to check whether a sibling already occupies the same "
            "dispatch, before writing a byte",
        )

    pasta = Path(pasta)
    destino = pasta / slug
    if (destino / "SKILL.md").exists():
        raise Recusa(
            "H2",
            f"`{destino / 'SKILL.md'}` already exists",
            "the harvest never overwrites — edit the existing one by hand, or "
            "choose another slug",
        )

    existentes = ler_pasta(pasta, com_git=False) if pasta.is_dir() else []
    proposta = Skill(caminho=destino / "SKILL.md", pasta=destino, nome=slug, descricao=descricao)
    colisoes = [
        (s.slug, round(_confusao(proposta, s) * 100))
        for s in existentes
        if _confusao(proposta, s) >= LIMIAR_CONFUSAO and not _um_nomeia_o_outro(proposta, s)
    ]
    if colisoes:
        pares = ", ".join(f"`{slug_}` ({pct}%)" for slug_, pct in colisoes)
        raise Recusa(
            "H3",
            f"the description collides with {pares} — the same rule as S11",
            "extend the existing skill instead of creating a rival, or name it "
            'out loud in your `--says` ("...different from <sibling-slug>...") '
            "so the rule reads the negative trigger as intentional",
        )

    destino.mkdir(parents=True, exist_ok=True)
    (destino / "SKILL.md").write_text(
        MODELO.format(slug=slug, falta=FALTA, pasta=pasta, descricao=descricao.strip()),
        encoding="utf-8",
    )
    return destino / "SKILL.md"
