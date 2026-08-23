"""`blind` — acha fronteira que uma varredura ingênua atravessa em silêncio.

Duas causas, sempre confundidas como uma: reparse point (junction do Windows,
symlink de diretório) que a ferramenta não segue estruturalmente, e regra de
`.gitignore` que esconde a fronteira mesmo quando a ferramenta segue. Ver
`blind/limites.py` para a distinção medida.
"""

from __future__ import annotations

from .limites import ARQUIVOS_DE_DECLARACAO, Fronteira, detectar

__all__ = ["ARQUIVOS_DE_DECLARACAO", "Fronteira", "detectar"]
