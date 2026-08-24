"""Sondas da operação `suite-que-acusa`.

natureza: correcao — sonda que estoura vira `UNPROVEN` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_su_`).

⚠️ **A pergunta desta operação não é «os testes passam».** É: **se alguém
apagasse o mecanismo que este teste protege, ele ainda passaria?**

Um teste que só confirma o caminho feliz passa igual depois de o mecanismo ser
removido. Ele não prova nada — e o custo dele não é zero: é dar a alguém a
sensação de estar coberto. Uma suíte verde inteira feita desses testes é pior
que nenhuma suíte, porque ninguém vai procurar o que já parece protegido.

O remédio é o **controle negativo**: o teste reintroduz o defeito que existe
para pegar, e falha se o mecanismo não reclamar.

⚠️ **E o limite honesto, que é grande.** `suite.sem_controle_negativo` é
HEURÍSTICA. Ela procura construções que indicam expectativa de falha, e vai
errar nos dois sentidos: um teste que reintroduz o defeito de um jeito que ela
não reconhece é acusado à toa, e um `pytest.raises` decorativo passa por ela.
**Trate o número como uma lista de leitura, nunca como veredito.**
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO desta operação: onde moram os seus testes.
PASTA_DE_TESTES = "tests"

#: Onde você declara o que a suíte NÃO mede — a terceira lista.
ARQUIVO_DE_LACUNAS = "LACUNAS.md"

_SU_NOME_DE_TESTE = re.compile(r"^(test_|_[a-z]{1,3}$|check)", re.I)

#: Construções que indicam que o teste ESPERA uma falha — isto é, que ele
#: reintroduz o defeito. A lista é aberta de propósito: cada projeto tem o
#: próprio dialeto, e um vocabulário fechado aqui acusaria a casa inteira.
_SU_CONTROLE_NEGATIVO = (
    "raises",
    "assertraises",
    "expectederror",
    "xfail",
    "pytest.warns",
    "assertwarns",
    "should_fail",
    "must_fail",
    "deve_falhar",
    "reintroduz",
    "controle negativo",
    "negative control",
)

_SU_PULADO = re.compile(r"@(?:pytest\.mark\.)?(skip|xfail)|unittest\.skip|self\.skipTest", re.I)


def _su_base() -> Path:
    base = (RAIZ / PASTA_DE_TESTES).resolve()
    if not base.is_dir():
        raise LookupError(
            f"`{PASTA_DE_TESTES}` não existe. Ajuste PASTA_DE_TESTES no topo de sondas.py. "
            "Zero testes por eu não ter olhado é diferente de zero testes, e as duas coisas "
            "não podem sair com o mesmo número"
        )
    return base


def _su_arquivos() -> list[Path]:
    base = _su_base()
    achados: list[Path] = []
    for pasta, subpastas, arquivos in os.walk(base, followlinks=True):
        subpastas[:] = sorted(
            s for s in subpastas if not s.startswith(".") and s != "__pycache__"
        )
        achados += [Path(pasta) / a for a in sorted(arquivos) if a.endswith(".py")]
    if not achados:
        raise LookupError(f"`{PASTA_DE_TESTES}` existe e não tem nenhum arquivo .py")
    return achados


def _su_funcoes() -> list[tuple[Path, ast.FunctionDef, str]]:
    """(arquivo, nó, texto-fonte da função) para cada função de teste.

    Usa `ast`, e não expressão regular sobre o texto: um `def` dentro de uma
    string, num comentário ou aninhado noutra função seria contado por regex, e
    o denominador da suíte inteira sairia errado — que é a pior classe de erro
    numa ferramenta que existe para cobrar denominador.
    """
    funcoes: list[tuple[Path, ast.FunctionDef, str]] = []
    for arquivo in _su_arquivos():
        texto = arquivo.read_text(encoding="utf-8", errors="replace")
        try:
            arvore = ast.parse(texto)
        except SyntaxError as exc:
            raise LookupError(f"`{arquivo}` não compila: {exc}") from exc
        for no in ast.walk(arvore):
            if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)) and _SU_NOME_DE_TESTE.match(
                no.name
            ):
                funcoes.append((arquivo, no, ast.get_source_segment(texto, no) or ""))
    if not funcoes:
        raise LookupError(
            f"nenhuma função de teste em `{PASTA_DE_TESTES}`. Procurei nomes começando com "
            "`test_` ou `check`; se o seu dialeto for outro, ajuste `_SU_NOME_DE_TESTE`"
        )
    return funcoes


def _su_tem_assercao(no: ast.AST) -> bool:
    """Um `assert`, ou uma chamada `assert*`/`raise`. Sem isso o teste não falha."""
    for filho in ast.walk(no):
        if isinstance(filho, (ast.Assert, ast.Raise)):
            return True
        if isinstance(filho, ast.Call):
            alvo = filho.func
            nome = getattr(alvo, "attr", None) or getattr(alvo, "id", "")
            if isinstance(nome, str) and nome.lower().startswith("assert"):
                return True
    return False


# ---------------------------------------------------------------------------
# As sondas
# ---------------------------------------------------------------------------


@sonda("suite.arquivos", origem="arquivos .py sob a pasta de testes")
def su_arquivos() -> int:
    return len(_su_arquivos())


@sonda("suite.checks", origem="funções de teste contadas pela árvore sintática, não por regex")
def su_checks() -> int:
    return len(_su_funcoes())


@sonda(
    "suite.sem_assercao",
    origem="funções de teste sem nenhum assert, assert* ou raise no corpo",
)
def su_sem_assercao() -> int:
    """De RELAÇÃO, e é a única sonda desta operação que é veredito, não suspeita.

    Uma função de teste sem asserção **não pode falhar**. Ela roda, devolve
    verde, entra na contagem de cobertura e não verifica nada. Não é heurística:
    é uma propriedade do código, e o número certo dela é zero.
    """
    return sum(1 for _, no, _ in _su_funcoes() if not _su_tem_assercao(no))


@sonda(
    "suite.sem_controle_negativo",
    origem="funções de teste sem construção que ESPERE falha (heurística, ver o docstring)",
)
def su_sem_controle_negativo() -> int:
    """De RELAÇÃO — e é uma LISTA DE LEITURA, não um veredito.

    A pergunta que ela tenta responder: *se alguém apagasse o mecanismo que este
    teste protege, ele ainda passaria?* Um teste que só percorre o caminho feliz
    passa igual, e o custo dele não é zero — é a sensação de cobertura.

    ⚠️ **Ela erra nos dois sentidos, e isso está declarado.** Um teste que
    reintroduz o defeito de um jeito que ela não reconhece é acusado à toa; um
    `pytest.raises` decorativo passa por ela. O número serve para produzir a
    lista de quais abrir — nunca para reprovar sozinho no CI.
    """
    sem = 0
    for _, _, fonte in _su_funcoes():
        baixa = fonte.lower()
        if not any(marca in baixa for marca in _SU_CONTROLE_NEGATIVO):
            sem += 1
    return sem


@sonda("suite.pulados", origem="testes marcados com skip/xfail")
def su_pulados() -> int:
    """De RELAÇÃO. Um teste pulado é um teste que não existe, com aparência de existir.

    Ele conta na lista, aparece no relatório, e a única coisa que ele mede é
    quanto tempo faz que alguém desistiu dele.
    """
    return sum(1 for _, _, fonte in _su_funcoes() if _SU_PULADO.search(fonte))


@sonda(
    "suite.lacunas_declaradas",
    origem="itens de lista no arquivo de lacunas — a terceira lista",
)
def su_lacunas_declaradas() -> int:
    """De CONTAGEM. É o número que decide se o verde dos outros vale alguma coisa.

    Toda suíte publica o que passou e o que falhou. Quase nenhuma publica **o
    que nunca olhou** — e sem essa terceira lista um verde só diz que o que foi
    olhado passou, o que é bem menos do que parece.

    ⚠️ Zero aqui **estoura**, e não devolve zero. Uma suíte sem lacunas
    declaradas não é uma suíte completa: é uma suíte que nunca escreveu os
    próprios limites, e as duas coisas são indistinguíveis pelo número.
    """
    arquivo = RAIZ / ARQUIVO_DE_LACUNAS
    if not arquivo.is_file():
        raise LookupError(
            f"`{ARQUIVO_DE_LACUNAS}` não existe. É a terceira lista: o que a sua suíte NÃO "
            "mede. Sem ela, um verde diz apenas que o que foi olhado passou — e ninguém "
            "consegue saber o que não foi olhado. Crie o arquivo com uma lista de itens"
        )
    return len(_su_itens_abertos(arquivo.read_text(encoding="utf-8", errors="replace")))


#: Uma lacuna é um item de lista OU um título numerado (`## 3 · ...`, `## 3. ...`).
#: Aceitar as duas formas não é frouxidão: uma lista de oito lacunas com um
#: parágrafo cada é escrita com título por quase todo mundo, e uma régua que só
#: reconhece marcador contaria 0 num arquivo bem escrito.
_SU_ITEM = re.compile(r"^\s*(?:[-*+]\s+\S|\d+\.\s+\S|#{2,6}\s*\d+\s*[.·)-]\s*\S)", re.M)

#: Onde a contagem PARA. Uma lacuna fechada listada junto das abertas é o mesmo
#: defeito que uma lacuna não listada — em ambos os casos o leitor não sabe o
#: tamanho real do ponto cego. E o erro é para o lado otimista, que é o pior.
_SU_FECHADAS = re.compile(r"^#{1,6}\s*(fechad|closed|resolvid|encerrad)", re.I | re.M)


def _su_itens_abertos(texto: str) -> list[str]:
    """Os itens declarados, cortando o que vier depois do título de fechadas."""
    corte = _SU_FECHADAS.search(texto)
    if corte:
        texto = texto[: corte.start()]
    itens = _SU_ITEM.findall(texto)
    if not itens:
        raise LookupError(
            f"`{ARQUIVO_DE_LACUNAS}` existe e não declara nenhuma lacuna ABERTA. Procurei "
            "item de lista e título numerado, parando na seção de fechadas. Um arquivo de "
            "lacunas vazio afirma que não há ponto cego — a afirmação mais forte possível, "
            "e a menos provável"
        )
    return itens
