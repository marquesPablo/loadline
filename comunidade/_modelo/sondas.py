"""Probes for the `your-operation-name` operation.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with the
error written out. It never returns a guess.

COPY THIS FILE to the root of your repository, as `sondas.py`.
To combine with another operation, use `operacoes/juntar.py` or concatenate by
hand — but first pick a helper-function prefix that does not collide with the
seven existing operations (they use `_instr_`, `_repo_`, `_cer_`, `_dec_`,
`_su_`, `_hand_`, `_vit_`).

⚠️ TODO — the anti-mirror rule, for YOUR operation. The WRITTEN number lives
somewhere (an index, a README, a dashboard). The MEASURED number has to come
from a DIFFERENT source — never from the same derived artifact the written
number already summarizes. If both readings come from the same place, the pair
passes green locking the defect in instead of finding it. Describe here, in
full, what the measured source is and why it is independent of the written
number.
"""

from __future__ import annotations

from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: THE ONE ADJUSTMENT (or the two, if your operation needs it) of this operation.
#: TODO — document what this field points at and why.
CAMPO_DE_AJUSTE = "TODO"


@sonda("NOME.exemplo", origem="TODO: describe the measured source, in full and verifiable")
def _NOME_exemplo(metrica, selo):
    """TODO — what this probe measures, in one sentence.

    Blows up (raises an exception) if the declared source does not exist — it
    never returns 0 for "not found". "I did not look" and "I looked and there is
    nothing" are opposite things. `metrica` is the full name matched by the
    pattern; `selo` carries `selo.source` and the rest of what was written in
    the `measured:`/`arbitrated:` comment.
    """
    raise NotImplementedError("fill in this probe before opening the PR")
