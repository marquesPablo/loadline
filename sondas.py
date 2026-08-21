"""As sondas deste projeto — de onde cada número do README é recomputado.

natureza: correcao — sonda que estoura vira `SEM_PROVA` no relatório, com o
erro por extenso. Ela nunca devolve um palpite.

⚠️ **A regra que faz o par valer alguma coisa:** o número do README é escrito
à mão, em prosa. A sonda o recomputa do `censo/ecossistema.json`, que é dado.
São dois artefatos independentes — mexer num sem mexer no outro reprova, que é
exatamente o ponto. Se a sonda lesse o próprio README, o par passaria verde
travando o defeito: é check espelho, e ele não verifica nada.

⚠️ **E há um limite honesto, declarado de propósito:** a verdade última das
entradas do censo está *na web*, e nenhuma sonda offline a alcança. Por isso
todo selo do censo carrega `vence=`. A sonda prova a **coerência interna**; o
`vence` é o que obriga alguém a sair da máquina e reconferir o mundo lá fora.
Confundir as duas coisas seria dizer que um JSON coerente é um fato verdadeiro.
"""

from __future__ import annotations

import json
from pathlib import Path

from aferido import sonda

RAIZ = Path(__file__).parent
CENSO = RAIZ / "censo" / "ecossistema.json"


def _censo() -> dict:
    return json.loads(CENSO.read_text(encoding="utf-8"))


@sonda("censo.projetos", origem="len(projetos) em censo/ecossistema.json")
def total_de_projetos() -> int:
    return len(_censo()["projetos"])


@sonda("censo.com_repo_canonico", origem="projetos com campo `repo` não-nulo")
def com_repo() -> int:
    return sum(1 for p in _censo()["projetos"] if p.get("repo"))


@sonda("censo.sem_repo_canonico", origem="projetos sem `repo` e sem `paper`")
def sem_repo() -> int:
    return sum(1 for p in _censo()["projetos"] if not p.get("repo") and not p.get("paper"))


@sonda("censo.licenca.*", origem="contagem por `veredito_licenca` em censo/ecossistema.json")
def por_veredito_de_licenca(metrica: str, _selo) -> int:
    alvo = metrica.rsplit(".", 1)[-1]
    return sum(1 for p in _censo()["projetos"] if p.get("veredito_licenca") == alvo)


@sonda("censo.sem_llm", origem="projetos com `sem_llm: true`")
def sem_llm() -> int:
    return sum(1 for p in _censo()["projetos"] if p.get("sem_llm") is True)


@sonda("censo.clonados_ou_executados", origem="denominador declarado no censo")
def clonados() -> int:
    return _censo()["denominador"]["clonados_ou_executados"]


@sonda("colisao.nomes", origem="projetos com `colide_com` não-vazio")
def nomes_em_colisao() -> int:
    return sum(1 for p in _censo()["projetos"] if p.get("colide_com"))


@sonda("colisao.*", origem="len(colide_com) + 1 se houver repo canônico, por nome")
def tamanho_do_cacho(metrica: str, _selo) -> int:
    alvo = metrica.rsplit(".", 1)[-1].lower()
    for projeto in _censo()["projetos"]:
        if projeto["nome"].lower().replace(" ", "-") == alvo:
            return len(projeto.get("colide_com", [])) + (1 if projeto.get("repo") else 0)
    raise LookupError(f"`{alvo}` não é um nome do censo")


@sonda("nucleo.modulos", origem="arquivos .py em aferido/")
def modulos_do_nucleo() -> int:
    return len(list((RAIZ / "aferido").glob("*.py")))


@sonda("nucleo.dependencias", origem="linhas não-vazias de requisitos.txt (ausente = 0)")
def dependencias() -> int:
    arquivo = RAIZ / "requisitos.txt"
    if not arquivo.exists():
        return 0
    return sum(
        1
        for linha in arquivo.read_text(encoding="utf-8").splitlines()
        if linha.strip() and not linha.strip().startswith("#")
    )


@sonda("nucleo.vereditos", origem="len(ORDEM) em aferido/__main__.py")
def vereditos() -> int:
    from aferido import __main__ as cli

    return len(cli.ORDEM)


@sonda("nucleo.checks", origem="ocorrências de `@check(` em autoteste.py")
def checks_do_autoteste() -> int:
    return (RAIZ / "autoteste.py").read_text(encoding="utf-8").count("@check(")


@sonda("nucleo.lacunas", origem="seções `## N ·` de LACUNAS.md")
def lacunas_declaradas() -> int:
    """O número mora no README; a fonte é o LACUNAS.md. Dois artefatos.

    Selar a contagem DENTRO do próprio LACUNAS.md seria check espelho: os dois
    lados sairiam do mesmo arquivo, e o par passaria verde travando o defeito.
    """
    import re

    texto = (RAIZ / "LACUNAS.md").read_text(encoding="utf-8")
    return len(re.findall(r"^## \d+ ·", texto, re.MULTILINE))


@sonda("nucleo.fora", origem="len(FORA) lido por `ast` em autoteste.py, sem executar")
def checks_fora_do_denominador() -> int:
    """Quantos checks EXISTEM e não rodam. Zero hoje, e declarado mesmo assim.

    ⚠️ Lido por `ast`, nunca importando o módulo: importar `autoteste` roda a
    suíte inteira, e uma sonda que executa o que ela mede é lenta e circular.
    """
    import ast

    arvore = ast.parse((RAIZ / "autoteste.py").read_text(encoding="utf-8"))
    for no in arvore.body:
        alvo = None
        if isinstance(no, ast.AnnAssign) and isinstance(no.target, ast.Name):
            alvo = no.target.id
        elif isinstance(no, ast.Assign) and no.targets and isinstance(no.targets[0], ast.Name):
            alvo = no.targets[0].id
        if alvo == "FORA" and isinstance(no.value, (ast.List, ast.Tuple)):
            return len(no.value.elts)
    raise LookupError("`FORA` não é uma lista literal no topo de autoteste.py")


# --------------------------------------------------------------- o censo ----


@sonda(
    "censo.gerado_em_dia",
    origem="1 se censo/CENSO.md == censo/gerar.py:gerar(), senão 0",
)
def censo_em_dia() -> int:
    """A ÚNICA pergunta legítima sobre um artefato gerado.

    Selar cada número do CENSO.md seria check espelho: os dois lados sairiam do
    mesmo JSON. A pergunta certa não é *"o número está certo?"* — é *"este
    publicado ainda corresponde à fonte?"*, e essa é de RELAÇÃO: ela não anda
    quando alguém escreve no censo, só anda se alguém editou o publicado à mão
    ou mexeu na fonte sem regerar. Divergir ali manda parar, não resselar.
    """
    import sys

    sys.path.insert(0, str(RAIZ))
    from censo import gerar as g

    return int(g.PUBLICADO.exists() and g.PUBLICADO.read_text(encoding="utf-8") == g.gerar())


# ---------------------------------------------------------------- a forja ---


@sonda("forja.modulos", origem="arquivos .py em forja/")
def modulos_da_forja() -> int:
    return len(list((RAIZ / "forja").glob("*.py")))


@sonda("forja.recusas", origem="regras R distintas levantadas em forja/spec.py")
def recusas() -> int:
    import re

    fonte = (RAIZ / "forja" / "spec.py").read_text(encoding="utf-8")
    # `R0` é a falta de campo obrigatório e não é uma das oito regras de fronteira.
    return len({m for m in re.findall(r'raise Recusa\(\s*"(R\d)"', fonte)} - {"R0"})


@sonda("forja.artefatos", origem="len(compilar(spec)) sobre a spec de exemplo")
def artefatos() -> int:
    import sys

    sys.path.insert(0, str(RAIZ))
    from forja import ler
    from forja.__main__ import compilar

    return len(compilar(ler(RAIZ / "forja" / "exemplos" / "revisor-de-licenca.toml")))


# ------------------------------------------------------------ a prateleira ---
# As operações prontas medem o repositório de quem adota. Estas medem a
# prateleira em si — porque um índice que afirma "quatro operações" e nunca é
# recomputado é exatamente o defeito que este projeto existe para pegar, e
# publicá-lo sem selo seria a versão mais literal possível de casa de ferreiro.


def _operacoes() -> list["Path"]:
    pasta = RAIZ / "operacoes"
    if not pasta.is_dir():
        return []
    return sorted(p for p in pasta.iterdir() if p.is_dir() and (p / "RECEITA.md").is_file())


#: Os cinco arquivos que toda operação tem, sempre com o mesmo nome. A lista é
#: fechada: se você aprendeu uma operação, aprendeu todas.
ANATOMIA = ("RECEITA.md", "sondas.py", "agente.toml", "selos.md", "ci.yml")


@sonda("operacoes.total", origem="subpastas de operacoes/ que contêm RECEITA.md")
def operacoes_prontas() -> int:
    return len(_operacoes())


@sonda(
    "operacoes.arquivos_por_operacao",
    origem="tamanho de ANATOMIA, se e somente se TODA operação tiver os cinco",
)
def anatomia_completa() -> int:
    """De RELAÇÃO: ela não anda quando alguém escreve uma operação nova.

    Ela só anda se alguma operação ficou incompleta — e aí a resposta certa é
    parar e completá-la, nunca resselar o número para baixo. Uma prateleira em
    que cada gaveta tem uma forma diferente é uma prateleira que ninguém aprende.
    """
    operacoes = _operacoes()
    if not operacoes:
        raise LookupError("nenhuma operação em operacoes/ — a prateleira não existe neste clone")
    faltando = [
        f"{op.name}/{arquivo}"
        for op in operacoes
        for arquivo in ANATOMIA
        if not (op / arquivo).is_file()
    ]
    if faltando:
        raise LookupError(f"operação incompleta: {', '.join(faltando)}")
    return len(ANATOMIA)


@sonda("operacao.*.sondas", origem="chamadas de @sonda( no sondas.py da operação nomeada")
def sondas_de_uma_operacao(metrica: str, _selo) -> int:
    alvo = metrica.split(".")[1]
    for operacao in _operacoes():
        if operacao.name.startswith(alvo):
            return (operacao / "sondas.py").read_text(encoding="utf-8").count("@sonda(")
    raise LookupError(f"`{alvo}` não é o começo do nome de nenhuma operação em operacoes/")
