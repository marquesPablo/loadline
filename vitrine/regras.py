"""The vitrine rules — all parser-checkable, none calls a model.

Each rule below comes from a public source, and the source is cited in the
rule. Where the source gives a number (1-64 characters, 1,024 characters, 500
lines), the number is the source's, not this project's preference.

What is NOT here is in the operation's `LACUNAS.md`. In particular: nothing here
judges whether the skill WORKS. A flawless vitrine over an empty stockroom
passes every rule green. Measuring execution is another job, and it requires
running.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# ------------------------------------------------------------- reading --------

#: The `name` grammar, from the Agent Skills format spec: 1 to 64 characters,
#: only lowercase, digits and hyphen — no double hyphen, no hyphen at the ends.
#: Underscore and uppercase are NOT allowed.
NOME_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

#: The `description` ceiling. Above it the field is truncated, and the cut lands
#: in the middle of the sentence that would have decided the dispatch.
TETO_DESCRICAO = 1024

#: The recommended body ceiling. It is not a loading error: it is the point
#: where the `SKILL.md` stops being a map and becomes the territory.
TETO_LINHAS = 500

#: The POSITIVE trigger — "when to use it". The rule asks for a CONDITIONAL
#: CLAUSE, not a specific phrase, and that is how it is measured here.
#:
#: ⚠️ This rule was rewritten after measuring. The first version was a list of
#: literal phrases ("use when", "usar quando"…) and it flagged `frontend-design`,
#: whose description says *"…when building new UI or reshaping an existing one"* —
#: a perfect trigger clause, outside the list. A closed list of phrases is
#: fragile and produces a false positive, which in a linter costs more than the
#: rule it checks. The detector is now the conditional conjunction, with a word
#: boundary.
GATILHO_POSITIVO = re.compile(
    r"\b(when|whenever|if|upon|during|quando|sempre que|caso|ao\s+\w+ar)\b",
    re.IGNORECASE,
)

#: Forms that say "when to use it" without a conditional conjunction. Each one
#: got in for having been seen in a real file, never for a preference.
GATILHO_POSITIVO_EXTRA = (
    "use for", "use to", "usar para", "use para", "used for",
    "reach for", "invoke for", "ao pedir", "ao solicitar",
)

#: Marks of a NEGATIVE trigger — "when NOT to use it". It is the field that
#: separates two skills in the same domain; without it, the choice between
#: siblings becomes a coin toss.
GATILHO_NEGATIVO = (
    "don't use", "do not use", "never use", "not for", "avoid using",
    "não usar", "nao usar", "nunca usar", "não use", "nao use", "nunca use",
    "não utilize", "nao utilize", "not when", "except when",
)

#: First words that give away a vitrine in the 1st or 2nd person. The
#: description is read by the router next to dozens of others: "Creates React
#: components" routes, "I help you with React" does not.
PESSOA_ERRADA = (
    "i ", "i'm ", "i'll ", "i can ", "we ", "we'll ", "we can ", "you ",
    "your ", "eu ", "nós ", "nos ", "você ", "voce ", "seu ", "sua ",
)

#: Signs of an entry point in a script. A file with none of them is a library
#: module, and a library in `scripts/` is context the agent loads and does not
#: know how to run.
PONTO_DE_ENTRADA = ("__main__", "argparse", "sys.argv", "click.command", "typer")

#: A word of 5+ letters, for the same reason as `forja/vistoria.py`: a short
#: string (`ui`, `api`, `css`) distinguishes nothing and inflates false positives.
_PALAVRA = re.compile(r"[a-z0-9]{5,}")

#: Words that show up in every skill description and distinguish nothing.
#: Without this list, any two skills "look alike" and `S11` becomes noise — the
#: same lesson `forja`'s `V6` already paid on the agent side.
VAZIAS = frozenset(
    """
    skill skills usar usa used using quando when sempre nunca apenas outro
    outra sobre cada todos todas mesmo mesma porque coisa coisas forma
    partir depois antes ainda tambem projeto arquivo arquivos pasta pastas
    always never only other about each every after before still also project
    file files folder folders because thing things
    """.split()
)

#: The same threshold as `V6` (`forja/vistoria.py`) — 30% of words in common
#: between two `description`s. CHOSEN by looking at real rosters, not measured;
#: it is here with the reason next to it, not buried in an `if`. See `LACUNAS.md` §9.
LIMIAR_CONFUSAO = 0.30


@dataclass
class Skill:
    """A skill read from disk. Nothing here is inferred: everything was read."""

    caminho: Path            #: the SKILL.md itself
    pasta: Path              #: the folder that contains it — `name` must match it
    nome: str = ""           #: frontmatter `name:`
    descricao: str = ""      #: frontmatter `description:`
    linhas: int = 0          #: the body size, in lines
    referencias: list[Path] = field(default_factory=list)
    scripts: list[Path] = field(default_factory=list)
    commits: int | None = None   #: None = not measured (no git, or outside a repo)

    @property
    def slug(self) -> str:
        """How the skill shows up in the report: the folder name, always."""
        return self.pasta.name


@dataclass
class Achado:
    regra: str
    titulo: str
    conserto: str
    fonte: str               #: where the rule comes from — auditable, not opinion
    itens: list[str] = field(default_factory=list)
    grave: bool = True
    skills: set[str] = field(default_factory=set)


def _frontmatter(texto: str) -> tuple[dict[str, str], str]:
    """Minimal frontmatter, no dependency: `---` … `---`.

    It is not a YAML parser and does not pretend to be — but it DOES READ A
    MULTI-LINE VALUE, because not reading it is worse than not measuring: the
    `description` disappears, and the tool flags "no description" on a skill
    that has a good one. A false positive in a linter costs more than the rule
    it checks.

    It covers the three forms that show up on disk:

        description: one line
        description: >          (folded — joins with a space)
          continues here
        description: |          (literal — joins with a newline)
          continues here
        description:            (a plain indented scalar)
          continues here

    What it does NOT cover is in the operation's LACUNAS: a list, a nested map,
    an anchor, and quotes that open on one line and close on another.
    """
    if not texto.startswith("---"):
        return {}, texto
    fim = texto.find("\n---", 3)
    if fim == -1:
        return {}, texto

    campos: dict[str, str] = {}
    chave_aberta: str | None = None
    literal = False          # `|` joins with a newline; `>` and plain, with a space
    pedacos: list[str] = []

    def fechar() -> None:
        nonlocal chave_aberta, pedacos, literal
        if chave_aberta is not None:
            junta = "\n" if literal else " "
            corpo = junta.join(pedacos).strip()
            campos[chave_aberta] = (campos[chave_aberta] + " " + corpo).strip() if campos.get(chave_aberta) else corpo
        chave_aberta, pedacos, literal = None, [], False

    for linha in texto[3:fim].splitlines():
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        indentada = linha[:1] in {" ", "\t"}

        if indentada and chave_aberta is not None:
            pedacos.append(linha.strip())
            continue
        if indentada:
            continue  # continuation of a key we did not open — ignored

        fechar()
        if ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        chave, valor = chave.strip(), valor.strip()
        if valor in {"|", ">", "|-", ">-", "|+", ">+"}:
            chave_aberta, literal = chave, valor.startswith("|")
            campos[chave] = ""
        else:
            # The key stays OPEN even with a value on the same line: in YAML a
            # plain scalar continues on the following indented lines, and that
            # is how most long `description`s are written on disk. Closing here
            # discarded the continuation — and the tool read half the vitrine
            # with no error. Found by the S4 negative control.
            chave_aberta, literal = chave, False
            campos[chave] = valor

    fechar()
    return campos, texto[fim + 4 :]


def _desaspar(valor: str) -> str:
    """`description:` usually comes as a JSON string. Loose quotes are not data."""
    valor = valor.strip()
    if valor[:1] in {'"', "'"}:
        try:
            return json.loads(valor)
        except (ValueError, TypeError):
            return valor.strip("\"'")
    return valor


def _commits(caminho: Path) -> int | None:
    """How many commits touched this file. `None` when it cannot be measured.

    Returning `None` instead of `0` is deliberate: "not measured" and "never
    committed" are different things, and confusing the two is exactly the
    defect this tool exists to demand.
    """
    try:
        saida = subprocess.run(
            ["git", "log", "--oneline", "--follow", "--", caminho.name],
            cwd=caminho.parent,
            capture_output=True,
            text=True,
            timeout=10,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if saida.returncode != 0:
        return None
    return len([l for l in saida.stdout.splitlines() if l.strip()])


def ler_skill(caminho: Path, com_git: bool = True) -> Skill | None:
    """Reads a `SKILL.md`. Returns `None` if the file cannot be read."""
    try:
        texto = caminho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    campos, corpo = _frontmatter(texto)
    pasta = caminho.parent

    referencias: list[Path] = []
    pasta_ref = pasta / "references"
    if pasta_ref.is_dir():
        referencias = sorted(p for p in pasta_ref.rglob("*") if p.is_file())

    scripts: list[Path] = []
    pasta_scr = pasta / "scripts"
    if pasta_scr.is_dir():
        scripts = sorted(p for p in pasta_scr.rglob("*.py") if p.is_file())

    return Skill(
        caminho=caminho,
        pasta=pasta,
        nome=_desaspar(campos.get("name", "")),
        descricao=_desaspar(campos.get("description", "")),
        linhas=len(corpo.splitlines()),
        referencias=referencias,
        scripts=scripts,
        commits=_commits(caminho) if com_git else None,
    )


def ler_pasta(raiz: Path, com_git: bool = True) -> list[Skill]:
    """Finds every `SKILL.md` under `raiz`, at any depth.

    ⚠️ `rglob` does NOT cross a Windows junction or a directory symlink. If your
    skills folder is mounted that way, point at the real target — this is the
    same silent defect the operation's `LACUNAS.md` declares.
    """
    if raiz.is_file() and raiz.name == "SKILL.md":
        lida = ler_skill(raiz, com_git)
        return [lida] if lida else []
    achadas = [ler_skill(p, com_git) for p in sorted(raiz.rglob("SKILL.md"))]
    return [s for s in achadas if s is not None]


# --------------------------------------------------------------- the ten --------


def _tem(texto: str, marcas: tuple[str, ...]) -> bool:
    baixo = texto.lower()
    return any(m in baixo for m in marcas)


def _significativas(descricao: str) -> set[str]:
    """The words in a `description` that actually set it apart from the others."""
    return {p for p in _PALAVRA.findall(descricao.lower())} - VAZIAS


def _confusao(a: Skill, b: Skill) -> float:
    """How much two `description`s fight over the same dispatch. Jaccard, no mystery."""
    pa, pb = _significativas(a.descricao), _significativas(b.descricao)
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / len(pa | pb)


def _um_nomeia_o_outro(a: Skill, b: Skill) -> bool:
    """A real negative trigger is nominal: it names the sibling by its slug."""
    return a.slug in b.descricao.lower() or b.slug in a.descricao.lower()


def _profundidade(arquivo: Path, pasta_ref: Path) -> int:
    """How many folder levels below `references/`. Flat = 0."""
    return len(arquivo.relative_to(pasta_ref).parts) - 1


def vistoriar(skills: list[Skill]) -> list[Achado]:
    """The ten rules. Each one cites the public source it comes from."""
    FONTE_SPEC = "the Agent Skills format spec"
    FONTE_BP = "the official skill-authoring best practices"

    achados: list[Achado] = []

    def registrar(
        regra: str, titulo: str, conserto: str, fonte: str, itens: list[tuple[str, str]],
        grave: bool = True,
    ) -> None:
        if not itens:
            return
        achados.append(
            Achado(
                regra=regra,
                titulo=titulo,
                conserto=conserto,
                fonte=fonte,
                itens=[f"{slug:<34} {motivo}" for slug, motivo in itens],
                grave=grave,
                skills={slug for slug, _ in itens},
            )
        )

    # S1 — the name is the address, not the title ----------------------------
    registrar(
        "S1",
        "THE NAME IS NOT THE FOLDER'S",
        "the `name:` is the skill's ADDRESS, not its title. It has to be\n"
        "       identical to the parent folder's name: `angular-testing/SKILL.md`\n"
        "       requires `name: angular-testing`. Diverging, the load is luck.",
        FONTE_SPEC,
        [
            (s.slug, f"declares `{s.nome}`" if s.nome else "does not declare `name:`")
            for s in skills
            if s.nome != s.pasta.name
        ],
    )

    # S2 — the name grammar --------------------------------------------------
    registrar(
        "S2",
        "THE NAME DOES NOT FIT THE GRAMMAR",
        "1 to 64 characters, only lowercase, digits and a single hyphen.\n"
        "       Uppercase, a space, an underscore and a double hyphen break the\n"
        "       load — and they break it silently.",
        FONTE_SPEC,
        [
            (
                s.slug,
                f"`{s.nome}` has {len(s.nome)} characters"
                if len(s.nome) > 64
                else f"`{s.nome}` is outside the grammar",
            )
            for s in skills
            if s.nome and not (NOME_VALIDO.match(s.nome) and len(s.nome) <= 64)
        ],
    )

    # S3 — when to use it --------------------------------------------------
    registrar(
        "S3",
        "DOES NOT SAY WHEN TO USE IT",
        "the `description` is the ONLY field the router reads before deciding.\n"
        "       With no trigger clause — \"Use when…\" — the model does not link the\n"
        "       skill to any task. It does not fail: it is invisible.",
        FONTE_BP,
        [
            (s.slug, "description with no trigger clause" if s.descricao else "no `description:`")
            for s in skills
            if not (
                GATILHO_POSITIVO.search(s.descricao) or _tem(s.descricao, GATILHO_POSITIVO_EXTRA)
            )
        ],
    )

    # S4 — when NOT to use it ---------------------------------------------
    registrar(
        "S4",
        "DOES NOT SAY WHEN **NOT** TO USE IT",
        "with no negative trigger, two skills in the same domain fight over the\n"
        "       same dispatch and the choice becomes a coin toss. Name the sibling\n"
        "       out loud: \"Don't use it for Vue, Svelte, or vanilla CSS.\"",
        FONTE_BP,
        [(s.slug, "description with no negative trigger") for s in skills if not _tem(s.descricao, GATILHO_NEGATIVO)],
    )

    # S5 — the vitrine does not fit the window --------------------------------
    registrar(
        "S5",
        "THE VITRINE DOES NOT FIT THE WINDOW",
        f"above {TETO_DESCRICAO} characters the `description` is truncated, and the cut\n"
        "       lands in the middle of the sentence that would have decided the dispatch.",
        FONTE_SPEC,
        [(s.slug, f"{len(s.descricao)} characters") for s in skills if len(s.descricao) > TETO_DESCRICAO],
    )

    # S6 — the body blew past the ceiling -----------------------------------
    registrar(
        "S6",
        "THE BODY BLEW PAST THE CEILING",
        f"above {TETO_LINHAS} lines the `SKILL.md` stops being the map and becomes the\n"
        "       territory. Move the detail to `references/`, which is only read\n"
        "       after the skill has already been chosen.",
        FONTE_BP,
        [(s.slug, f"{s.linhas} lines") for s in skills if s.linhas > TETO_LINHAS],
        grave=False,
    )

    # S7 — references too deep -------------------------------------------
    fundos: list[tuple[str, str]] = []
    for s in skills:
        pasta_ref = s.pasta / "references"
        for arq in s.referencias:
            if _profundidade(arq, pasta_ref) > 0:
                fundos.append((s.slug, f"references/{arq.relative_to(pasta_ref).as_posix()}"))
    registrar(
        "S7",
        "`references/` TOO DEEP",
        "`references/` is flat by contract: `references/schema.md`, never\n"
        "       `references/db/v1/schema.md`. Progressive loading descends exactly\n"
        "       one level — what is below that is not reached.",
        FONTE_BP,
        fundos,
    )

    # S8 — a script that is a library -------------------------------------
    bibliotecas: list[tuple[str, str]] = []
    for s in skills:
        for arq in s.scripts:
            try:
                fonte = arq.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not any(m in fonte for m in PONTO_DE_ENTRADA):
                bibliotecas.append((s.slug, f"scripts/{arq.relative_to(s.pasta / 'scripts').as_posix()}"))
    registrar(
        "S8",
        "A SCRIPT THAT IS A LIBRARY",
        "`scripts/` is for a tiny CLI, one job per file. A module with no entry\n"
        "       point is a library — and a library there is context the agent\n"
        "       loads and does not know how to run.",
        FONTE_BP,
        bibliotecas,
        grave=False,
    )

    # S9 — a vitrine in the wrong person -----------------------------------
    registrar(
        "S9",
        "THE VITRINE SPEAKS IN THE WRONG PERSON",
        "the description is read by the router in the third person, next to\n"
        "       dozens of others. \"Creates React components\" routes; \"I help you\n"
        "       with React\" describes a relationship, and matches no task.",
        FONTE_BP,
        [
            (s.slug, f"starts with \"{s.descricao.split()[0]}\"")
            for s in skills
            if s.descricao and s.descricao.lower().startswith(PESSOA_ERRADA)
        ],
        grave=False,
    )

    # S10 — never fixed after the first error ------------------------------
    registrar(
        "S10",
        "BORN READY AND NEVER FIXED",
        "a skill with a single commit has never been through a real error. The\n"
        "       way is to write the version that works in ten minutes and fix it\n"
        "       on the agent's first mistake — every error is an improvement to the skill.",
        FONTE_BP,
        [(s.slug, "1 commit") for s in skills if s.commits == 1],
        grave=False,
    )

    # S11 — two skills get confused ----------------------------------------
    pares = [
        (f"{a.slug} × {b.slug}", f"{round(_confusao(a, b) * 100)}% of the words in common")
        for i, a in enumerate(skills)
        for b in skills[i + 1 :]
        if _confusao(a, b) >= LIMIAR_CONFUSAO and not _um_nomeia_o_outro(a, b)
    ]
    registrar(
        "S11",
        "TWO SKILLS GET CONFUSED",
        "descriptions fighting over the same dispatch, and neither names the\n"
        "       other. The fix is nominal: each `description` cites the sibling in\n"
        "       what it NEVER does — the same negative trigger `S4` already asks\n"
        "       for, only pointed at a name instead of left open.",
        FONTE_BP,
        pares,
    )
    if pares:
        achados[-1].skills = set()  # a pair is not a skill; it does not enter the denominator

    return achados
