"""Confronto prosa × selo — o número na FRASE bate com o número no SELO?

aferido-ignorar-arquivo: este arquivo ENSINA o confronto, e os selos e frases
escritos aqui são espécimes, não afirmações.

natureza: correcao — este módulo só lê texto e devolve achados. Ele não escreve
no disco, não conserta a frase, e exceção aqui libera e avisa em vez de barrar.

O defeito que ele existe para pegar, medido neste repositório em 2026-08-20:

    33 passaram · 0 reprovaram
    <!-- aferido: nucleo.checks=36 natureza=contagem em=2026-08-16 vence=nunca -->

O selo diz 36. A sonda mede 36. **O verificador devolve `VALE`** — e a frase
três linhas acima diz 33, para sempre, sem nada olhando.

É o buraco estrutural de todo mecanismo de selo: **o selo cobre o VALOR, e
ninguém cobre a FRASE.** Quem resela mexe no comentário, que é o que reprova, e
esquece o texto, que é o que a pessoa lê. O número errado sobrevive a rodada
após rodada de resselo, verde o tempo todo.

## A regra, e o que ela deliberadamente NÃO faz

Ela morde numa direção só: **número afirmado na prosa que nenhum selo do bloco
explica.** Se a prosa não afirma número nenhum, não há o que contradizer e nada
é acusado — o selo continua sendo a única fonte, e isso é legítimo.

A direção contrária — *a frase afirma uma GRANDEZA que o selo não nomeia* —
exige um registro fechado de grandezas e o julgamento de o que conta como
afirmação. Ela **não** está aqui, e está declarada como lacuna em `LACUNAS.md`
em vez de fingida.

## O que conta como número da prosa, e o que é ruído declarado

Entram: dígitos com fronteira de palavra, e numeral por extenso de zero a vinte
(em português e inglês) — porque *"seis projetos"* afirma tanto quanto *"6"*.

Saem, por serem endereço e não asserção: data `AAAA-MM-DD`, versão `N.N.N`,
identificador com dois-pontos (`arXiv:2608.10218`, `README.md:12`), URL, e
percentual — que é derivado, e cobrá-lo exigiria conhecer o denominador.

Cada exclusão está numa constante nomeada logo abaixo, e não espalhada por
condições dentro da função: uma regra que não se lê não se audita.

## A saída declarada

Um selo pode declarar `eco=nao` e ficar de fora. Isso é decisão explícita, sai
NOMEADA no relatório, e é a diferença entre uma exceção e um furo.
"""

from __future__ import annotations

import re

from .selo import Selo

PROSA_MUDA = "PROSA_MUDA"

#: Trechos que são endereço, não asserção — retirados ANTES de procurar número.
RUIDO = (
    re.compile(r"\d{4}-\d{2}-\d{2}"),          # data
    re.compile(r"\bv?\d+\.\d+(?:\.\d+)+\b"),   # versão
    re.compile(r"\w+:\S*\d\S*"),               # arXiv:2608.10218, README.md:12, http://…
    re.compile(r"\d+(?:[.,]\d+)?\s*%"),        # percentual — derivado, sem denominador aqui
)

#: Numeral por extenso conta como asserção — `seis projetos` não escapa por não
#: ter dígito. Só até vinte: acima disso ninguém escreve por extenso na prática.
#:
#: ⚠️ `um`/`uma`/`one` estão FORA, e a ausência é decisão, não esquecimento: em
#: português eles são artigo indefinido antes de serem numeral, e *"Um registro
#: do ecossistema"* não afirma quantidade nenhuma. Distinguir os dois usos exige
#: análise sintática, que este módulo não faz. **O custo declarado:** uma frase
#: que afirme de verdade *"um projeto não tem canônico"* passa sem cobrança.
#: Está em `LACUNAS.md`, e a saída para quem precisa é escrever o dígito.
POR_EXTENSO = {
    "zero": "0", "nenhum": "0", "nenhuma": "0",
    "dois": "2", "duas": "2", "two": "2",
    "três": "3", "tres": "3", "three": "3",
    "quatro": "4", "four": "4",
    "cinco": "5", "five": "5",
    "seis": "6", "six": "6",
    "sete": "7", "seven": "7",
    "oito": "8", "eight": "8",
    "nove": "9", "nine": "9",
    "dez": "10", "ten": "10",
    "onze": "11", "doze": "12", "treze": "13", "catorze": "14", "quatorze": "14",
    "quinze": "15", "dezesseis": "16", "dezessete": "17", "dezoito": "18",
    "dezenove": "19", "vinte": "20",
}

_DIGITO = re.compile(r"(?<![\w.,])(\d+)(?![\w])")

#: Numeral precedido de artigo DEFINIDO é pronome, não asserção: *"os dois
#: lados"* e *"as três formas"* retomam coisas já ditas, não contam nada novo.
#: Sem esta regra, toda prosa bem escrita vira falso positivo — e um detector
#: que grita no texto certo é desligado na primeira semana, que é o modo mais
#: caro de um check falhar.
_PRONOMINAL = re.compile(
    r"\b(?:os|as|nos|nas|dos|das|aos|às|pelos|pelas)\s+"
    r"(?:dois|duas|tr[êe]s|quatro|cinco|seis|sete|oito|nove|dez|doze|quinze|vinte)\b",
    re.IGNORECASE,
)
_PALAVRA = re.compile(r"[a-zà-ÿ]+", re.IGNORECASE)
_SELO_NA_LINHA = re.compile(r"(?:<!--|#|//)\s*(?:aferido|congelado)\s*:", re.IGNORECASE)
_CERCA = "```"


def bloco_selado(linhas: list[str], linha_do_selo: int) -> tuple[int, int]:
    """As linhas (1-based, inclusivas) que o selo da linha `linha_do_selo` cobre.

    Sobe a partir do selo pulando linha em branco e **outros selos** — selo
    empilhado cobre o mesmo bloco, que é como a prática de fato escreve — e
    junta as linhas contíguas até a linha em branco anterior.

    ⚠️ **Cerca de código entra no bloco, de propósito, e isso é o oposto da
    regra da varredura.** Para LER SELO, o que está dentro de cerca é espécime e
    se ignora. Para CONFRONTAR PROSA, a cerca é justamente onde a afirmação
    mora: no defeito que abre este arquivo, o `33` está dentro de um bloco de
    console. As duas regras olham a mesma cerca e perguntam coisas diferentes —
    *"alguém declarou um selo aqui?"* e *"alguém afirmou um número aqui?"*.
    """
    i = linha_do_selo - 2  # índice 0-based da linha logo acima do selo
    while i >= 0 and (not linhas[i].strip() or _SELO_NA_LINHA.search(linhas[i])):
        i -= 1
    if i < 0:
        return (0, 0)

    fim = i
    if linhas[i].lstrip().startswith(_CERCA):  # fechamento de cerca: desce até a abertura
        i -= 1
        while i >= 0 and not linhas[i].lstrip().startswith(_CERCA):
            i -= 1
        return (max(i + 1, 1), fim + 1)

    while i >= 0 and linhas[i].strip() and not _SELO_NA_LINHA.search(linhas[i]):
        i -= 1
    return (i + 2, fim + 1)


def numeros_afirmados(texto: str) -> set[str]:
    """Os números que este texto AFIRMA, já sem o ruído de endereço."""
    limpo = texto
    for padrao in RUIDO:
        limpo = padrao.sub(" ", limpo)
    limpo = _PRONOMINAL.sub(" ", limpo)
    achados = set(_DIGITO.findall(limpo))
    for palavra in _PALAVRA.findall(limpo):
        valor = POR_EXTENSO.get(palavra.lower())
        if valor is not None:
            achados.add(valor)
    return achados


def confrontar(
    selos: list[Selo], linhas: list[str], arquivo: str
) -> tuple[list[tuple[Selo, str, set[str]]], list[Selo]]:
    """Confronta cada bloco selado com os selos que o cobrem.

    Devolve `(discrepancias, dispensados)`. Uma discrepância é
    `(selo, numero_da_prosa, valores_do_selo)` — o número que a frase afirma e
    que nenhum selo do bloco explica.

    O confronto é por BLOCO, não por selo: selos empilhados sobre o mesmo
    parágrafo são lidos juntos, porque juntos é como eles cobrem a frase.
    Julgar um por um acusaria cada selo do empilhamento pelos números dos
    outros — verde-falso ao contrário, e igualmente inútil.
    """
    dispensados = [s for s in selos if s.eco == "nao"]
    ativos = [s for s in selos if s.eco != "nao"]

    por_bloco: dict[tuple[int, int], list[Selo]] = {}
    for selo in ativos:
        if not selo.metricas:
            continue
        bloco = bloco_selado(linhas, selo.linha)
        if bloco == (0, 0):
            continue
        por_bloco.setdefault(bloco, []).append(selo)

    discrepancias: list[tuple[Selo, str, set[str]]] = []
    for (ini, fim), grupo in sorted(por_bloco.items()):
        texto = "\n".join(linhas[ini - 1 : fim])
        na_prosa = numeros_afirmados(texto)
        if not na_prosa:
            continue  # a prosa não afirma número: não há o que contradizer
        no_selo = {v for s in grupo for v in s.metricas.values()}
        orfaos = na_prosa - no_selo
        for numero in sorted(orfaos, key=lambda x: (len(x), x)):
            discrepancias.append((grupo[0], numero, no_selo))
    return discrepancias, dispensados
