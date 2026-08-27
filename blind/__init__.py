"""`blind` — finds a boundary a naive scan crosses silently.

Two causes, always confused as one: a reparse point (a Windows junction, a
directory symlink) the tool does not follow structurally, and a `.gitignore`
rule that hides the boundary even when the tool does follow it. See
`blind/limites.py` for the measured distinction.
"""

from __future__ import annotations

from .limites import ARQUIVOS_DE_DECLARACAO, Fronteira, detectar

__all__ = ["ARQUIVOS_DE_DECLARACAO", "Fronteira", "detectar"]
