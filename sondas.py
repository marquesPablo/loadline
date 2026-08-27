"""This project's probes — where each number in the README is recomputed from.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with
the error written out. It never returns a guess.

⚠️ **The rule that makes the pair worth anything:** the README number is
written by hand, in prose. The probe recomputes it from `censo/ecossistema.json`,
which is data. They are two independent artifacts — touching one without
touching the other fails, which is exactly the point. If the probe read the
README itself, the pair would pass green while locking the defect in: it is a
mirror check, and it verifies nothing.

⚠️ **And there is an honest limit, declared on purpose:** the ultimate truth of
the census entries is *on the web*, and no offline probe reaches it. That is
why every census seal carries `expires=`. The probe proves **internal
coherence**; the `expires` is what forces someone to leave the machine and
re-check the world out there. Confusing the two would be saying a coherent JSON
is a true fact.
"""

from __future__ import annotations

import json
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).parent
CENSO = RAIZ / "censo" / "ecossistema.json"


def _censo() -> dict:
    return json.loads(CENSO.read_text(encoding="utf-8"))


@sonda("censo.projetos", origem="len(projetos) in censo/ecossistema.json")
def total_de_projetos() -> int:
    return len(_censo()["projetos"])


@sonda("censo.com_repo_canonico", origem="projects with a non-null `repo` field")
def com_repo() -> int:
    return sum(1 for p in _censo()["projetos"] if p.get("repo"))


@sonda("censo.sem_repo_canonico", origem="projects with no `repo` and no `paper`")
def sem_repo() -> int:
    return sum(1 for p in _censo()["projetos"] if not p.get("repo") and not p.get("paper"))


@sonda("censo.licenca.*", origem="count by `veredito_licenca` in censo/ecossistema.json")
def por_veredito_de_licenca(metrica: str, _selo) -> int:
    alvo = metrica.rsplit(".", 1)[-1]
    return sum(1 for p in _censo()["projetos"] if p.get("veredito_licenca") == alvo)


@sonda("censo.sem_llm", origem="projects with `sem_llm: true`")
def sem_llm() -> int:
    return sum(1 for p in _censo()["projetos"] if p.get("sem_llm") is True)


@sonda("censo.clonados_ou_executados", origem="the declared denominator in the census")
def clonados() -> int:
    return _censo()["denominador"]["clonados_ou_executados"]


@sonda("colisao.nomes", origem="projects with a non-empty `colide_com`")
def nomes_em_colisao() -> int:
    return sum(1 for p in _censo()["projetos"] if p.get("colide_com"))


@sonda("colisao.*", origem="len(colide_com) + 1 if there is a canonical repo, by name")
def tamanho_do_cacho(metrica: str, _selo) -> int:
    alvo = metrica.rsplit(".", 1)[-1].lower()
    for projeto in _censo()["projetos"]:
        if projeto["nome"].lower().replace(" ", "-") == alvo:
            return len(projeto.get("colide_com", [])) + (1 if projeto.get("repo") else 0)
    raise LookupError(f"`{alvo}` is not a name in the census")


@sonda("nucleo.modulos", origem=".py files in loadline/")
def modulos_do_nucleo() -> int:
    return len(list((RAIZ / "loadline").glob("*.py")))


@sonda("nucleo.dependencias", origem="non-empty lines of requisitos.txt (absent = 0)")
def dependencias() -> int:
    arquivo = RAIZ / "requisitos.txt"
    if not arquivo.exists():
        return 0
    return sum(
        1
        for linha in arquivo.read_text(encoding="utf-8").splitlines()
        if linha.strip() and not linha.strip().startswith("#")
    )


@sonda("nucleo.vereditos", origem="len(ORDEM) in loadline/__main__.py")
def vereditos() -> int:
    from loadline import __main__ as cli

    return len(cli.ORDEM)


@sonda("nucleo.checks", origem="occurrences of `@check(` in autoteste.py")
def checks_do_autoteste() -> int:
    return (RAIZ / "autoteste.py").read_text(encoding="utf-8").count("@check(")


@sonda("nucleo.lacunas", origem="`## N ·` sections of LACUNAS.md")
def lacunas_declaradas() -> int:
    """The number lives in the README; the source is LACUNAS.md. Two artifacts.

    Sealing the count INSIDE LACUNAS.md itself would be a mirror check: both
    sides would come from the same file, and the pair would pass green while
    locking the defect in.
    """
    import re

    texto = (RAIZ / "LACUNAS.md").read_text(encoding="utf-8")
    return len(re.findall(r"^## \d+ ·", texto, re.MULTILINE))


@sonda("nucleo.fora", origem="len(FORA) read by `ast` in autoteste.py, without running it")
def checks_fora_do_denominador() -> int:
    """How many checks EXIST and do not run. Zero today, and declared anyway.

    ⚠️ Read by `ast`, never by importing the module: importing `autoteste`
    runs the whole suite, and a probe that runs what it measures is slow and
    circular.
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
    raise LookupError("`FORA` is not a literal list at the top of autoteste.py")


# --------------------------------------------------------------- the census ----


@sonda(
    "censo.gerado_em_dia",
    origem="1 if censo/CENSO.md == censo/gerar.py:gerar(), else 0",
)
def censo_em_dia() -> int:
    """The ONLY legitimate question about a generated artifact.

    Sealing every number in CENSO.md would be a mirror check: both sides would
    come from the same JSON. The right question is not *"is the number right?"*
    — it is *"does this published one still match the source?"*, and that is a
    RELATION: it does not move when someone writes to the census, it only moves
    if someone edited the published one by hand or touched the source without
    regenerating. Diverging there means stop, not re-seal.
    """
    import sys

    sys.path.insert(0, str(RAIZ))
    from censo import gerar as g

    return int(g.PUBLICADO.exists() and g.PUBLICADO.read_text(encoding="utf-8") == g.gerar())


# ---------------------------------------------------------------- the forge ---


@sonda("forja.modulos", origem=".py files in forja/")
def modulos_da_forja() -> int:
    return len(list((RAIZ / "forja").glob("*.py")))


@sonda("forja.recusas", origem="distinct R rules raised in forja/spec.py")
def recusas() -> int:
    import re

    fonte = (RAIZ / "forja" / "spec.py").read_text(encoding="utf-8")
    # `R0` is a missing required field and is not one of the eight boundary rules.
    return len({m for m in re.findall(r'raise Recusa\(\s*"(R\d)"', fonte)} - {"R0"})


@sonda("forja.artefatos", origem="len(compilar(spec)) over the example spec")
def artefatos() -> int:
    import sys

    sys.path.insert(0, str(RAIZ))
    from forja import ler
    from forja.__main__ import compilar

    return len(compilar(ler(RAIZ / "forja" / "exemplos" / "revisor-de-licenca.toml")))


# ------------------------------------------------------------ the shelf ---
# The ready-made operations measure the adopter's repository. These measure the
# shelf itself — because an index that claims "four operations" and is never
# recomputed is exactly the defect this project exists to catch, and publishing
# it without a seal would be the most literal possible version of the
# cobbler's-children-have-no-shoes.


def _operacoes() -> list["Path"]:
    pasta = RAIZ / "operacoes"
    if not pasta.is_dir():
        return []
    return sorted(p for p in pasta.iterdir() if p.is_dir() and (p / "RECEITA.md").is_file())


#: The five files every operation has, always with the same name. The list is
#: closed: if you learned one operation, you learned them all.
ANATOMIA = ("RECEITA.md", "sondas.py", "agente.toml", "selos.md", "ci.yml")


@sonda("operacoes.total", origem="subfolders of operacoes/ that contain a RECEITA.md")
def operacoes_prontas() -> int:
    return len(_operacoes())


@sonda(
    "operacoes.arquivos_por_operacao",
    origem="the size of ANATOMIA, if and only if EVERY operation has all five",
)
def anatomia_completa() -> int:
    """A RELATION: it does not move when someone writes a new operation.

    It only moves if some operation ended up incomplete — and then the right
    answer is to stop and complete it, never to re-seal the number down. A
    shelf where every drawer has a different shape is a shelf nobody learns.
    """
    operacoes = _operacoes()
    if not operacoes:
        raise LookupError("no operation in operacoes/ — the shelf does not exist in this clone")
    faltando = [
        f"{op.name}/{arquivo}"
        for op in operacoes
        for arquivo in ANATOMIA
        if not (op / arquivo).is_file()
    ]
    if faltando:
        raise LookupError(f"incomplete operation: {', '.join(faltando)}")
    return len(ANATOMIA)


@sonda("operacao.*.sondas", origem="@sonda( calls in the named operation's sondas.py")
def sondas_de_uma_operacao(metrica: str, _selo) -> int:
    alvo = metrica.split(".")[1]
    for operacao in _operacoes():
        if operacao.name.startswith(alvo):
            return (operacao / "sondas.py").read_text(encoding="utf-8").count("@sonda(")
    raise LookupError(f"`{alvo}` is not the start of any operation name in operacoes/")


@sonda("vistoria.achados", origem="distinct `V<n>` rules passed to marcar() in forja/vistoria.py")
def achados_da_vistoria() -> int:
    """How many defects the survey knows how to find.

    Read from the CODE that emits them, never from the README that narrates
    them — both sides coming from the same text would pass green while locking
    the defect in instead of finding it. It is a RELATION: the vocabulary is
    closed on purpose and only moves when someone DECIDES it should, which
    means stop and investigate before re-sealing.
    """
    import re

    texto = (RAIZ / "forja" / "vistoria.py").read_text(encoding="utf-8")
    return len(set(re.findall(r'^\s+"(V\d+)",$', texto, re.MULTILINE)))


# ----------------------------------------------------------------- blind ---
# `blind` claims two numbers in its own `blind/LACUNAS.md` and neither had a
# probe — it was one of the four `UNPROVEN` that made `python -m loadline .`
# fail its own repository. The two sides are independent: the number lives in
# prose in `LACUNAS.md`, the probe recomputes it from the structure of
# `blind/limites.py`, which is what the seal's `source=` field already declares.


@sonda("blind.causas", origem="`**Cause N —` paragraphs in the blind/limites.py docstring")
def blind_causas() -> int:
    """The named causes of a boundary a naive scan does not see —
    structural (a reparse point) and policy (`.gitignore`).

    Read from the module that implements them, never from the `blind/LACUNAS.md`
    that narrates them. It is a count: it goes up when someone documents a
    third cause.
    """
    import re

    texto = (RAIZ / "blind" / "limites.py").read_text(encoding="utf-8")
    return len(re.findall(r"(?m)^\*\*Cause \d+ ", texto))


@sonda("blind.declaracao", origem="len(ARQUIVOS_DE_DECLARACAO), read by ast in blind/limites.py")
def blind_declaracao() -> int:
    """How many FILENAMES `blind` recognizes as a declaration.

    ⚠️ Read by `ast`, without importing the module. The `.claude/` folder is
    handled separately (`PASTA_DE_DECLARACAO`) and does not count here — the
    number in `LACUNAS.md` is just the `frozenset` of five names.
    """
    import ast

    arvore = ast.parse((RAIZ / "blind" / "limites.py").read_text(encoding="utf-8"))
    for no in arvore.body:
        if (
            isinstance(no, ast.Assign)
            and no.targets
            and isinstance(no.targets[0], ast.Name)
            and no.targets[0].id == "ARQUIVOS_DE_DECLARACAO"
            and isinstance(no.value, ast.Call)
            and no.value.args
            and isinstance(no.value.args[0], (ast.Set, ast.List, ast.Tuple))
        ):
            return len(no.value.args[0].elts)
    raise LookupError(
        "`ARQUIVOS_DE_DECLARACAO` is not a literal `frozenset({...})` at the top of blind/limites.py"
    )


# ---------------------------------------------------------------- placar ---


@sonda("placar.portas", origem="the size of the `portas` list in placar.portas.avaliar(), read by ast")
def placar_portas() -> int:
    """The seven gates of "Would you ship this AI agent?".

    Read from the list `avaliar()` builds — the authoritative source of what
    actually runs — never from the README that announces them. It is a count:
    it goes up if an eighth gate is wired in.
    """
    import ast

    arvore = ast.parse((RAIZ / "placar" / "portas.py").read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name == "avaliar":
            for filho in ast.walk(no):
                if (
                    isinstance(filho, ast.Assign)
                    and any(getattr(t, "id", "") == "portas" for t in filho.targets)
                    and isinstance(filho.value, (ast.List, ast.Tuple))
                ):
                    return len(filho.value.elts)
    raise LookupError("`portas = [...]` is not a literal list inside placar.portas.avaliar()")


# ----------------------------------------------------------- the dated census ---


@sonda("censo.edicao", origem="1-based position of this file's date among censo/edicoes/*.json")
def censo_edicao(metrica: str, selo) -> int:
    """The ordinal number of a census edition.

    The `.md` writes the number in prose; this probe derives it from the list
    of `.json` snapshots — the OTHER file `censo/edicao.py` writes per edition,
    and the only one the next run reads back. Counting the `.md` would be a
    mirror check.
    """
    arquivo = Path(selo.arquivo)
    datas = sorted(p.stem for p in arquivo.parent.glob("*.json"))
    if arquivo.stem not in datas:
        raise LookupError(f"there is no snapshot `{arquivo.stem}.json` next to {arquivo.name}")
    return datas.index(arquivo.stem) + 1
