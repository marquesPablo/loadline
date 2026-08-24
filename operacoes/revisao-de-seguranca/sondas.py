"""Sondas da operação `revisao-de-seguranca`.

natureza: correcao — sonda que estoura vira `UNPROVEN` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_seg_`).

⚠️ **O que estas sondas medem, e o que elas NÃO medem.** Elas não procuram
vulnerabilidade. Elas medem se os achados que você já tem são **acionáveis**:
se cada um diz ONDE (`caminho:linha`), sob QUAL classificação (com versão do
framework), e COMO CONFERIR se é verdade.

A razão é aritmética. Um scanner devolve 400 achados; um relatório em que cada
item exige vinte minutos de investigação para saber se é real custa mais do que
a equipe tem, e o resultado é o arquivo inteiro sendo ignorado. **Um achado que
ninguém consegue conferir não é um achado: é uma suspeita cara.**

⚠️ **A regra anti-espelho, aqui.** O número escrito mora no relatório-resumo. O
número medido sai dos **arquivos de achado**, um a um. Contar do resumo seria
perguntar ao resumo se ele está certo.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO desta operação: onde moram os seus achados, um arquivo por achado.
PASTA_DE_ACHADOS = "achados"

#: Frameworks aceitos, e o formato do identificador de cada um. A lista é
#: fechada de propósito: «vulnerabilidade de injeção» não é uma classificação,
#: é um adjetivo. Sem identificador não há como duas pessoas confirmarem que
#: estão falando da mesma coisa, nem como comparar dois relatórios.
_SEG_FRAMEWORKS = {
    "CWE": re.compile(r"\bCWE[-\s]?\d{1,4}\b"),
    "OWASP": re.compile(r"\bA\d{1,2}:20\d{2}\b|\bOWASP\s+Top\s+10\b", re.I),
    "ASVS": re.compile(r"\bASVS\b", re.I),
    "CAPEC": re.compile(r"\bCAPEC[-\s]?\d{1,4}\b"),
    "ATTACK": re.compile(r"\bT\d{4}(\.\d{3})?\b"),
}

#: A VERSÃO do framework, ao lado do identificador. Um `CWE-89` sem versão do
#: catálogo é um endereço sem data: a numeração do CWE muda entre versões, e um
#: relatório de 2023 comparado com um de hoje pode estar falando de coisas
#: diferentes com o mesmo número.
_SEG_VERSAO = re.compile(
    r"\b(?:CWE|ASVS|CAPEC|ATT&CK|ATLAS|D3FEND)\s*v?\.?\s*\d+\.\d+"
    r"|\bOWASP[^.\n]{0,20}:\s*20\d{2}\b"
    r"|\bTop\s+10:\s*20\d{2}\b",
    re.I,
)

#: `caminho/arquivo.ext:123` — onde o achado mora.
_SEG_CAMINHO_LINHA = re.compile(r"[\w./\\-]+\.\w{1,6}:\d+")

#: Vocabulário FECHADO de veredito. Um achado sem veredito explícito é lido
#: como confirmado por quem tem pressa, e é assim que um falso positivo entra
#: num relatório entregue ao cliente.
_SEG_VEREDITOS = (
    "CONFIRMADO NO CODIGO",
    "CONFIRMADO NO CÓDIGO",
    "PRECISA DE EXECUCAO",
    "PRECISA DE EXECUÇÃO",
    "DESCARTADO",
    "SEM CLASSE",
)

#: Como conferir. Sem isto o leitor não tem como derrubar o achado — e um
#: achado que não pode ser derrubado não pode ser confirmado.
_SEG_VERIFICACAO = re.compile(
    r"^#{1,6}\s*.*(verifica|reproduz|como conferir|passo a passo|prova de conceito|repro)",
    re.I | re.M,
)


def _seg_base() -> Path:
    base = (RAIZ / PASTA_DE_ACHADOS).resolve()
    if not base.is_dir():
        raise LookupError(
            f"`{PASTA_DE_ACHADOS}` não existe. Esta operação mede a QUALIDADE dos achados que "
            "você já tem — ela não procura vulnerabilidade. Crie a pasta e ponha um arquivo "
            "por achado; sem isso não há denominador, e zero achados sem denominador significa "
            "«não olhei», nunca «está limpo»"
        )
    return base


def _seg_achados() -> list[Path]:
    base = _seg_base()
    achados: list[Path] = []
    for pasta, subpastas, arquivos in os.walk(base, followlinks=True):
        subpastas[:] = sorted(s for s in subpastas if not s.startswith("."))
        achados += [
            Path(pasta) / a
            for a in sorted(arquivos)
            if a.lower().endswith(".md") and a.upper() != "README.MD"
        ]
    if not achados:
        raise LookupError(
            f"`{PASTA_DE_ACHADOS}` existe e está vazia. Zero achados NÃO é «está limpo» — "
            "é «ninguém olhou», e as duas coisas dizem o oposto"
        )
    return achados


def _seg_texto(achado: Path) -> str:
    return achado.read_text(encoding="utf-8", errors="replace")


def _seg_tem_framework(texto: str) -> bool:
    return any(padrao.search(texto) for padrao in _SEG_FRAMEWORKS.values())


# ---------------------------------------------------------------------------
# As sondas
# ---------------------------------------------------------------------------


@sonda("seguranca.achados", origem="arquivos .md na pasta de achados, exceto o README")
def seg_achados() -> int:
    return len(_seg_achados())


@sonda(
    "seguranca.sem_framework",
    origem="achados sem nenhum identificador de CWE/OWASP/ASVS/CAPEC/ATT&CK",
)
def seg_sem_framework() -> int:
    """De RELAÇÃO. «Vulnerabilidade de injeção» não é classificação: é adjetivo.

    Sem identificador, duas pessoas não conseguem confirmar que falam da mesma
    coisa, dois relatórios não se comparam, e nada liga o achado à literatura
    que já explica como corrigi-lo.
    """
    return sum(1 for a in _seg_achados() if not _seg_tem_framework(_seg_texto(a)))


@sonda(
    "seguranca.sem_versao_de_framework",
    origem="achados que citam framework e NÃO dizem qual versão do catálogo",
)
def seg_sem_versao() -> int:
    """De RELAÇÃO, e é a mais sutil das oito.

    Um `CWE-89` sem versão é um endereço sem data. A numeração dos catálogos
    muda entre versões: um relatório de 2023 e um de hoje podem estar falando de
    coisas diferentes com o mesmo número, e ninguém tem como saber qual.

    ⚠️ Só conta achados que JÁ citam framework. Somar os que não citam nenhum
    contaria o mesmo defeito duas vezes, e o número deixaria de dizer qual
    conserto é qual.
    """
    return sum(
        1
        for a in _seg_achados()
        if _seg_tem_framework(texto := _seg_texto(a)) and not _SEG_VERSAO.search(texto)
    )


@sonda(
    "seguranca.sem_caminho_linha",
    origem="achados sem nenhuma ocorrência do padrão `arquivo.ext:123`",
)
def seg_sem_caminho_linha() -> int:
    """De RELAÇÃO. Um achado sem endereço obriga quem lê a procurar.

    E procurar é o passo em que a maioria dos relatórios morre: ninguém tem
    vinte minutos por item para descobrir do que o item está falando.
    """
    return sum(1 for a in _seg_achados() if not _SEG_CAMINHO_LINHA.search(_seg_texto(a)))


@sonda(
    "seguranca.sem_passo_de_verificacao",
    origem="achados sem seção de verificação/reprodução",
)
def seg_sem_verificacao() -> int:
    """De RELAÇÃO, e é a que separa achado de suspeita.

    Sem o passo, o leitor não tem como DERRUBAR o achado — e um achado que não
    pode ser derrubado também não pode ser confirmado. Ele só pode ser
    acreditado, que é outra coisa e não pertence a um relatório técnico.
    """
    return sum(1 for a in _seg_achados() if not _SEG_VERIFICACAO.search(_seg_texto(a)))


@sonda(
    "seguranca.sem_veredito",
    origem="achados sem nenhum veredito do vocabulário fechado",
)
def seg_sem_veredito() -> int:
    """De RELAÇÃO. Achado sem veredito é lido como confirmado por quem tem pressa.

    É assim que um falso positivo entra num relatório entregue — não por
    má-fé, mas porque a ausência de ressalva foi lida como certeza.
    """
    sem = 0
    for achado in _seg_achados():
        texto = _seg_texto(achado).upper()
        if not any(veredito in texto for veredito in _SEG_VEREDITOS):
            sem += 1
    return sem


@sonda(
    "seguranca.confirmados",
    origem="achados cujo veredito é CONFIRMADO NO CÓDIGO",
)
def seg_confirmados() -> int:
    return sum(
        1
        for a in _seg_achados()
        if "CONFIRMADO NO CODIGO" in (t := _seg_texto(a).upper()) or "CONFIRMADO NO CÓDIGO" in t
    )


@sonda(
    "seguranca.acionaveis",
    origem="achados que têm framework, versão, caminho:linha, verificação E veredito — os cinco",
)
def seg_acionaveis() -> int:
    """De RELAÇÃO, e é o único número desta operação que alguém de fora entende.

    Os cinco requisitos ao mesmo tempo. Não é a soma das outras sondas: um
    achado pode falhar em dois e é contado uma vez aqui, o que faz deste o
    número honesto para pôr num resumo — e das outras seis, o diagnóstico de
    qual conserto falta.
    """
    acionaveis = 0
    for achado in _seg_achados():
        texto = _seg_texto(achado)
        maiusculo = texto.upper()
        if (
            _seg_tem_framework(texto)
            and _SEG_VERSAO.search(texto)
            and _SEG_CAMINHO_LINHA.search(texto)
            and _SEG_VERIFICACAO.search(texto)
            and any(v in maiusculo for v in _SEG_VEREDITOS)
        ):
            acionaveis += 1
    return acionaveis
