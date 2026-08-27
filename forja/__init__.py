"""forja — a declarative spec goes in, an agent WITH A GATE comes out.

nature: fix — this module only re-exports. The decisions to block live in
`forja.spec`, which is `nature: security` and fails closed.

    python -m forja exemplos/revisor-de-licenca.toml --saida build/

What comes out is not a prompt. It is seven artifacts, and three of them are
not text for the model to read: a `PreToolUse` guard that denies before the
tool runs, a golden set that asks whether the ANSWER is right, and the list of
what the agent does not measure. A prompt without those three is an agent with
no gate and a better description.
"""

from .spec import Recusa, Spec, ler, validar

__all__ = ["Recusa", "Spec", "ler", "validar"]
__version__ = "0.1.0"
