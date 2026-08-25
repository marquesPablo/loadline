"""Sondas da operação `nome-da-sua-operacao`.

natureza: correcao — sonda que estoura vira `UNPROVEN` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, use `operacoes/juntar.py` ou concatene à mão —
mas primeiro escolha um prefixo de função auxiliar que não colida com as nove
operações existentes (elas usam `_instr_`, `_repo_`, `_front_`, `_fab_`, `_cer_`,
`_dec_`, `_su_`, `_hand_`, `_vit_`).

⚠️ TODO — a regra anti-espelho, para a SUA operação. O número ESCRITO mora em
algum lugar (um índice, um README, um dashboard). O número MEDIDO tem de sair
de uma fonte DIFERENTE — nunca do mesmo artefato derivado que o número escrito
já resume. Se as duas leituras saem do mesmo lugar, o par passa verde travando
o defeito em vez de achá-lo. Descreva aqui, por extenso, qual é a fonte medida
e por que ela é independente do número escrito.
"""

from __future__ import annotations

from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO (ou os dois, se sua operação precisar) desta operação.
#: TODO — documente o que este campo aponta e por quê.
CAMPO_DE_AJUSTE = "TODO"


@sonda("NOME.exemplo", origem="TODO: descreva a fonte medida, por extenso e verificável")
def _NOME_exemplo(metrica, selo):
    """TODO — o que esta sonda mede, em uma frase.

    Estoura (levanta exceção) se a fonte declarada não existir — nunca devolve
    0 para "não encontrei". "Não olhei" e "olhei e não há" são coisas opostas.
    `metrica` é o nome completo casado pelo padrão; `selo` traz `selo.fonte` e
    o resto do que foi escrito no comentário `measured:`/`arbitrated:`.
    """
    raise NotImplementedError("preencha esta sonda antes de abrir o PR")
