"""Sondas da operação `sala-de-decisao`.

natureza: correcao — sonda que estoura vira `SEM_PROVA` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_dec_`).

⚠️ **A regra anti-espelho, aqui.** O número escrito mora no índice de decisões
(«temos 44 decisões, 3 revogadas»). O número medido sai dos **arquivos** e do
**nome deles** — nunca do índice. Índice é artefato derivado: selar o número
dele contra ele mesmo seria check espelho, e o par passaria verde travando a
divergência em vez de achá-la.

⚠️ **E a sonda mais cara desta operação é `decisao.revogacao_de_um_lado_so`.**
Quando a decisão nova revoga a antiga e a antiga não ganha o aviso, quem abre a
antiga lê uma regra revogada como se ela valesse. Nenhuma revisão pega isso: os
dois arquivos estão certos, cada um por si. O defeito mora entre eles.
"""

from __future__ import annotations

import os
import re
from datetime import date, datetime
from pathlib import Path

from aferido import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO desta operação: onde moram as suas decisões e os seus gates.
#: Um "gate" é um arquivo que espera decisão de uma pessoa. A convenção é a
#: palavra `gate` no NOME do arquivo — ver a RECEITA para o porquê.
PASTA_DE_DECISOES = "decisoes"

_DEC_ACEITA = re.compile(r"^\s*status\s*:\s*[\"']?(aceito|aceita|accepted)", re.I | re.M)
_DEC_REVOGADA = re.compile(r"^\s*status\s*:\s*[\"']?(revogad|superseded|substitu)", re.I | re.M)
_DEC_REVOGA = re.compile(r"^\s*(?:revoga|supersedes|emenda)\s*:\s*(.+)$", re.I | re.M)
#: Duas convenções de identificador coexistem no mundo, e ler só uma devolve
#: ZERO calado no repositório que usa a outra. `ADR-031-assunto.md` é a forma
#: com prefixo; `0031-usar-postgres.md` é a do `adr-tools` original, e nela o id
#: não tem letra nenhuma. Qual delas vale sai do disco, em `_dec_convencao()`.
_DEC_REFERENCIA = re.compile(r"\b([A-Z]{2,5}-\d{1,4})\b")
_DEC_REFERENCIA_NUA = re.compile(r"\b(\d{3,4})\b")
_DEC_NOME_NU = re.compile(r"^(\d{3,4})(?=-)")
_DEC_DATA_NO_NOME = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
#: Um gate é `AAAA-MM-DD-gate-assunto.md`: a data E o token, os dois no NOME.
#: Exigir os dois não é rigor de estilo — procurar só a palavra `gate` casa com
#: toda decisão que tenha «gate» no título, e a fila passa a contar arquivos que
#: não esperam ninguém. Medido contra um acervo real: 7 falsos positivos.
_DEC_NOME_DE_GATE = re.compile(r"\d{4}-\d{2}-\d{2}.*(?<![a-z])gate(?![a-z])", re.I)
_DEC_DECIDIDO = re.compile(r"^#{1,6}\s+.*\bDECIDIDO\b", re.M)


def _dec_base() -> Path:
    base = (RAIZ / PASTA_DE_DECISOES).resolve()
    if not base.is_dir():
        raise LookupError(
            f"`{PASTA_DE_DECISOES}` não existe. Esta operação mede um registro de decisões em "
            "arquivos; sem a pasta não há o que medir, e devolver zero seria dizer que você "
            "não decide nada — que é diferente de você não registrar"
        )
    return base


def _dec_arquivos() -> list[Path]:
    base = _dec_base()
    achados: list[Path] = []
    for pasta, subpastas, arquivos in os.walk(base, followlinks=True):
        subpastas[:] = sorted(s for s in subpastas if not s.startswith("."))
        achados += [Path(pasta) / a for a in sorted(arquivos) if a.lower().endswith(".md")]
    if not achados:
        raise LookupError(f"`{PASTA_DE_DECISOES}` existe e está vazia — nenhuma decisão registrada")
    return achados


def _dec_decisoes() -> list[Path]:
    """Decisão é todo arquivo que NÃO é gate. O gate é o que ainda espera alguém."""
    return [a for a in _dec_arquivos() if not _DEC_NOME_DE_GATE.search(a.name)]


def _dec_gates() -> list[Path]:
    """A data E o token `gate`, os dois no NOME do arquivo. É convenção, e é
    de propósito.

    O nome é a única parte do arquivo que aparece em `ls`, no explorador, no
    diff e na busca — sem abrir nada. Um campo `tipo: gate` dentro do
    frontmatter é invisível em todos esses lugares, e um item que espera
    decisão que ninguém vê não está esperando: está esquecido.

    ⚠️ Exigir os DOIS não é rigor de estilo. Procurar só a palavra casa com
    toda decisão que tenha «gate» no título — medido contra um acervo real de
    100 arquivos, isso inflou a fila com 7 itens que não esperavam ninguém. Uma
    fila com falso positivo é pior que nenhuma: ela treina quem a lê a ignorá-la.
    """
    return [a for a in _dec_arquivos() if _DEC_NOME_DE_GATE.search(a.name)]


def _dec_texto(arquivo: Path) -> str:
    return arquivo.read_text(encoding="utf-8", errors="replace")


def _dec_convencao() -> str:
    """Qual das duas convenções de identificador este registro usa, lida do disco.

    Nunca cravada: um registro que nomeia `0001-record-....md` é tão canônico
    quanto um que nomeia `ADR-001-....md` — ele é o do `adr-tools` original.
    Assumir a primeira e devolver zero na segunda é *não medido* virando *zero*,
    que é exatamente o defeito que esta operação existe para acusar.
    """
    arquivos = _dec_decisoes()
    com_prefixo = sum(1 for a in arquivos if _DEC_REFERENCIA.search(a.name.upper()))
    nus = sum(1 for a in arquivos if _DEC_NOME_NU.match(a.name))
    if com_prefixo and com_prefixo >= nus:
        return "prefixo"
    return "nua" if nus else "nenhuma"


def _dec_identificadores() -> dict[str, Path]:
    """`ADR-042` (ou `0042`) -> arquivo, lido do NOME do arquivo. Um id por arquivo."""
    arquivos = _dec_decisoes()
    convencao = _dec_convencao()

    # ⚠️ RECUSA, e nunca zero. Sem nenhum identificador legível, esta sonda não
    # sabe dizer que está tudo bem — ela sabe que não conseguiu olhar. As duas
    # coisas são opostas, e devolver `0` para as duas é a mentira que a operação
    # inteira existe para acusar.
    if arquivos and convencao == "nenhuma":
        raise LookupError(
            f"achei {len(arquivos)} arquivo(s) de decisão e nenhum identificador no nome de "
            "nenhum deles. Esta sonda lê o id do NOME do arquivo, em uma de duas convenções: "
            "`ADR-031-assunto.md` ou `0031-assunto.md`. Renomeie, ou tire esta sonda — o que "
            "ela não vai fazer é devolver zero e deixar você achar que está tudo certo."
        )

    achados: dict[str, Path] = {}
    for arquivo in arquivos:
        if convencao == "prefixo":
            referencia = _DEC_REFERENCIA.search(arquivo.name.upper())
        else:
            referencia = _DEC_NOME_NU.match(arquivo.name)
        if referencia:
            achados.setdefault(referencia.group(1), arquivo)
    return achados


def _dec_citados(linha: str) -> list[str]:
    """Os ids citados numa linha de `revoga:`/`emenda:`, na convenção do registro.

    Na convenção nua a busca é restrita a essas linhas de propósito: procurar
    três ou quatro dígitos soltos no corpo inteiro casaria com ano, porta e
    número de versão, e a sonda passaria a acusar o que ninguém escreveu.
    """
    if _dec_convencao() == "prefixo":
        return _DEC_REFERENCIA.findall(linha.upper())
    return _DEC_REFERENCIA_NUA.findall(linha)


def _dec_aberto(gate: Path) -> bool:
    """Um gate está aberto enquanto não tiver um TÍTULO markdown com «DECIDIDO».

    Título, e não negrito. `**DECIDIDO**` no meio de um parágrafo é a forma mais
    fácil de fechar um gate sem ninguém conseguir achar a decisão depois — e uma
    busca por títulos é como se lê o histórico de um registro destes.
    """
    return not _DEC_DECIDIDO.search(_dec_texto(gate))


def _dec_data(arquivo: Path) -> date | None:
    achado = _DEC_DATA_NO_NOME.search(arquivo.name)
    if not achado:
        return None
    try:
        return date(int(achado.group(1)), int(achado.group(2)), int(achado.group(3)))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# As sondas
# ---------------------------------------------------------------------------


@sonda("decisao.total", origem="arquivos .md na pasta de decisões que não são gate")
def dec_total() -> int:
    return len(_dec_decisoes())


@sonda("decisao.aceitas", origem="frontmatter `status:` casando com aceito/accepted")
def dec_aceitas() -> int:
    return sum(1 for a in _dec_decisoes() if _DEC_ACEITA.search(_dec_texto(a)))


@sonda("decisao.revogadas", origem="frontmatter `status:` casando com revogada/superseded")
def dec_revogadas() -> int:
    return sum(1 for a in _dec_decisoes() if _DEC_REVOGADA.search(_dec_texto(a)))


@sonda(
    "decisao.sem_status",
    origem="decisões sem nenhum `status:` legível no frontmatter",
)
def dec_sem_status() -> int:
    """De RELAÇÃO. Uma decisão sem status não é lida errado — ela é lida sem saber.

    Quem abre não tem como distinguir uma proposta de uma regra em vigor, e
    a leitura mais cara é a otimista: tratar proposta como regra.
    """
    return sum(
        1
        for a in _dec_decisoes()
        if not _DEC_ACEITA.search(_dec_texto(a)) and not _DEC_REVOGADA.search(_dec_texto(a))
    )


@sonda(
    "decisao.revogacao_de_um_lado_so",
    origem="decisões citadas em `revoga:`/`emenda:` que não mencionam quem as revogou",
)
def dec_revogacao_de_um_lado_so() -> int:
    """De RELAÇÃO, e é a sonda cara desta operação.

    A decisão nova declara `revoga: ADR-031`. A `ADR-031` não diz nada. Quem
    abre a antiga — que é o caminho normal, porque ela é a que está citada nos
    lugares antigos — lê uma regra revogada com cara de regra viva.

    Os dois arquivos estão certos, cada um por si. **O defeito mora entre
    eles**, e é por isso que nenhuma revisão de código o pega.
    """
    porid = _dec_identificadores()
    por_arquivo = {caminho: ident for ident, caminho in porid.items()}
    orfas: set[str] = set()
    for arquivo in _dec_decisoes():
        atual = por_arquivo.get(arquivo)
        texto = _dec_texto(arquivo)
        for linha in _DEC_REVOGA.findall(texto):
            for alvo in _dec_citados(linha):
                if alvo not in porid or (atual and alvo == atual):
                    continue
                # O contra-ponteiro: a revogada tem de NOMEAR quem a revogou.
                if not (atual and atual in _dec_texto(porid[alvo]).upper()):
                    orfas.add(alvo)
    return len(orfas)


@sonda(
    "decisao.sem_alternativa",
    origem="decisões cujo texto não traz nenhuma seção de alternativa/descartad",
)
def dec_sem_alternativa() -> int:
    """De RELAÇÃO. Sem alternativa escrita, não houve decisão — houve um registro.

    O valor de um acervo destes não é lembrar o que foi escolhido: é lembrar
    **o que foi recusado e por quê**. Sem isso, daqui a um ano alguém repropõe
    a alternativa descartada e ninguém tem como saber que ela já caiu.
    """
    marcas = ("alternativa", "descartad", "considerad", "alternative", "rejected")
    return sum(
        1
        for a in _dec_decisoes()
        if not any(m in _dec_texto(a).lower() for m in marcas)
    )


@sonda("decisao.gates_abertos", origem="arquivos com `gate` no nome e sem título DECIDIDO")
def dec_gates_abertos() -> int:
    return sum(1 for g in _dec_gates() if _dec_aberto(g))


@sonda(
    "decisao.gate_mais_velho_dias",
    origem="dias entre a data no NOME do gate aberto mais antigo e hoje",
)
def dec_gate_mais_velho_dias() -> int:
    """De CONTAGEM — ela anda todo dia, por construção, e é essa a graça.

    Um item parado esperando decisão não fica pior de repente: ele fica pior um
    dia por vez, e é por isso que ninguém repara. Este número sobe sozinho até
    alguém decidir, e é a única métrica daqui que **piora quando você não faz
    nada**.

    ⚠️ A data sai do NOME do arquivo, nunca de `criada_em:` no frontmatter e
    nunca do `mtime`: o primeiro ninguém preenche com disciplina, e o segundo
    é zerado por um clone.
    """
    abertos = [g for g in _dec_gates() if _dec_aberto(g)]
    if not abertos:
        return 0
    datas = [d for d in (_dec_data(g) for g in abertos) if d]
    if not datas:
        raise LookupError(
            f"há {len(abertos)} gate(s) aberto(s) e nenhum tem data no nome do arquivo. "
            "A convenção desta operação é `AAAA-MM-DD-gate-assunto.md` — sem a data no nome "
            "não existe idade, e um item sem idade nunca fica velho aos olhos de ninguém"
        )
    return (datetime.now().date() - min(datas)).days
