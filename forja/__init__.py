"""forja — uma spec declarativa entra, um agente COM GATE sai.

nature: fix — este módulo só reexporta. As decisões de barrar estão em
`forja.spec`, que é `nature: security` e falha fechada.

    python -m forja exemplos/revisor-de-licenca.toml --saida build/

O que sai não é um prompt. São sete artefatos, e três deles não são texto para
o modelo ler: um guarda `PreToolUse` que nega antes de a ferramenta rodar, um
golden set que pergunta se a RESPOSTA está certa, e a lista do que o agente não
mede. Prompt sem esses três é um agente sem gate com uma descrição melhor.
"""

from .spec import Recusa, Spec, ler, validar

__all__ = ["Recusa", "Spec", "ler", "validar"]
__version__ = "0.1.0"
