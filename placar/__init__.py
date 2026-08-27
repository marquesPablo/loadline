"""`placar` — the seven gates of "Would you ship this AI agent?", checked.

nature: fix — this module only reads and reports; it never writes to the
target repository and never calls a model.

    python -m placar <path>

Each gate answers ONE question with disk evidence, never with opinion:
`OBJECTIVE` (until when?) · `IDENTITY` (which secret is exposed?) ·
`AUTHORITY` (what does it reach?) · `FAILURE` (what if the tool lies?) ·
`APPROVAL` (which action needs a human?) · `TRACEABILITY` (can it be
reconstructed?) · `CONTAINMENT` (can it be reverted?). Failing `IDENTITY`,
`AUTHORITY` or `CONTAINMENT` is NO-GO — the three are about what the agent
REACHES, not about what it declares it intends to do.

`placar` does not replace `forja`'s `vistoria` — it USES it (Gate 3 is, in
part, `V3`/`V7` re-read). See `placar/LACUNAS.md` for what each gate does NOT
prove.
"""

from __future__ import annotations

from .portas import NO_GO, Placar, Porta, avaliar, tem_harness

__all__ = ["NO_GO", "Placar", "Porta", "avaliar", "tem_harness"]
