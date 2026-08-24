"""As regras da vitrine — todas aferíveis por parser, nenhuma chama modelo.

Cada regra abaixo sai de uma fonte pública, e a fonte está citada na regra. Onde
a fonte dá um número (1-64 caracteres, 1.024 caracteres, 500 linhas), o número é
o da fonte, não uma preferência desta casa.

O que NÃO está aqui está na `LACUNAS.md` da operação. Em particular: nada aqui
julga se a skill FUNCIONA. Uma vitrine impecável sobre um estoque vazio passa
verde em todas as regras. Medir execução é outro trabalho, e ele exige rodar.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# ------------------------------------------------------------- leitura --------

#: A gramática do `name`, da especificação do formato Agent Skills: de 1 a 64
#: caracteres, só minúsculas, dígitos e hífen — sem hífen duplo, sem hífen nas
#: pontas. Underscore e maiúscula NÃO entram.
NOME_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

#: Teto do `description`. Acima disso o campo é truncado, e o corte cai no meio
#: da frase que decidiria o despacho.
TETO_DESCRICAO = 1024

#: Teto recomendado do corpo. Não é erro de carregamento: é o ponto em que o
#: `SKILL.md` deixa de ser mapa e vira território.
TETO_LINHAS = 500

#: Gatilho POSITIVO — «quando usar». A régua pede uma CLÁUSULA CONDICIONAL, não
#: uma frase específica, e é assim que ela é medida aqui.
#:
#: ⚠️ Esta regra foi reescrita depois de medir. A primeira versão era uma lista
#: de frases literais («use when», «usar quando»…) e acusou `frontend-design`,
#: cuja descrição diz *"…when building new UI or reshaping an existing one"* —
#: cláusula de gatilho perfeita, fora da lista. Lista fechada de frase é frágil
#: e produz falso positivo, que num linter custa mais caro que a regra que ele
#: checa. O detector agora é a conjunção condicional, com fronteira de palavra.
GATILHO_POSITIVO = re.compile(
    r"\b(when|whenever|if|upon|during|quando|sempre que|caso|ao\s+\w+ar)\b",
    re.IGNORECASE,
)

#: Formas que dizem «quando usar» sem conjunção condicional. Cada uma entrou por
#: ter sido vista num arquivo real, nunca por preferência.
GATILHO_POSITIVO_EXTRA = (
    "use for", "use to", "usar para", "use para", "used for",
    "reach for", "invoke for", "ao pedir", "ao solicitar",
)

#: Marcas de gatilho NEGATIVO — «quando NÃO usar». É o campo que separa duas
#: skills do mesmo domínio; sem ele, a escolha entre irmãs vira sorteio.
GATILHO_NEGATIVO = (
    "don't use", "do not use", "never use", "not for", "avoid using",
    "não usar", "nao usar", "nunca usar", "não use", "nao use", "nunca use",
    "não utilize", "nao utilize", "not when", "except when",
)

#: Primeiras palavras que denunciam vitrine em 1ª ou 2ª pessoa. A descrição é
#: lida pelo roteador ao lado de dezenas de outras: «Creates React components»
#: roteia, «I help you with React» não.
PESSOA_ERRADA = (
    "i ", "i'm ", "i'll ", "i can ", "we ", "we'll ", "we can ", "you ",
    "your ", "eu ", "nós ", "nos ", "você ", "voce ", "seu ", "sua ",
)

#: Sinais de ponto de entrada num script. Arquivo sem nenhum deles é módulo de
#: biblioteca, e biblioteca em `scripts/` é contexto que o agente carrega e não
#: sabe rodar.
PONTO_DE_ENTRADA = ("__main__", "argparse", "sys.argv", "click.command", "typer")

#: Palavra de 5+ letras, para o mesmo motivo do `forja/vistoria.py`: string curta
#: (`ui`, `api`, `css`) não distingue nada e infla falso positivo.
_PALAVRA = re.compile(r"[a-z0-9]{5,}")

#: Palavras que aparecem em toda descrição de skill e não distinguem nada. Sem
#: esta lista, duas skills quaisquer "se parecem" e o `S11` vira ruído — a
#: mesma lição que o `V6` da forja já pagou do lado dos agentes.
VAZIAS = frozenset(
    """
    skill skills usar usa used using quando when sempre nunca apenas outro
    outra sobre cada todos todas mesmo mesma porque coisa coisas forma
    partir depois antes ainda tambem projeto arquivo arquivos pasta pastas
    """.split()
)

#: Mesmo limiar do `V6` (`forja/vistoria.py`) — 30% de palavras em comum entre
#: duas `description`. ESCOLHIDO olhando rosters reais, não medido; está aqui
#: com o motivo ao lado, não enterrado num `if`. Ver `LACUNAS.md` §9.
LIMIAR_CONFUSAO = 0.30


@dataclass
class Skill:
    """Uma skill lida do disco. Nada aqui é inferido: tudo foi lido."""

    caminho: Path            #: o próprio SKILL.md
    pasta: Path              #: a pasta que o contém — o `name` tem de bater com ela
    nome: str = ""           #: frontmatter `name:`
    descricao: str = ""      #: frontmatter `description:`
    linhas: int = 0          #: tamanho do corpo, em linhas
    referencias: list[Path] = field(default_factory=list)
    scripts: list[Path] = field(default_factory=list)
    commits: int | None = None   #: None = não medido (sem git, ou fora de repo)

    @property
    def slug(self) -> str:
        """Como a skill aparece no relatório: o nome da pasta, sempre."""
        return self.pasta.name


@dataclass
class Achado:
    regra: str
    titulo: str
    conserto: str
    fonte: str               #: de onde vem a regra — auditável, não opinião
    itens: list[str] = field(default_factory=list)
    grave: bool = True
    skills: set[str] = field(default_factory=set)


def _frontmatter(texto: str) -> tuple[dict[str, str], str]:
    """Frontmatter mínimo, sem dependência: `---` … `---`.

    Não é um parser de YAML e não finge ser — mas LÊ VALOR MULTI-LINHA, porque
    não ler é pior que não medir: a `description` some, e a ferramenta acusa
    «sem description» numa skill que tem uma boa. Falso positivo num linter
    custa mais caro que a regra que ele checa.

    Cobre as três formas que aparecem no disco:

        description: uma linha
        description: >          (dobrado — junta com espaço)
          continua aqui
        description: |          (literal — junta com nova-linha)
          continua aqui
        description:            (escalar simples indentado)
          continua aqui

    O que NÃO cobre está na LACUNAS da operação: lista, mapa aninhado, âncora,
    e aspas que abrem numa linha e fecham noutra.
    """
    if not texto.startswith("---"):
        return {}, texto
    fim = texto.find("\n---", 3)
    if fim == -1:
        return {}, texto

    campos: dict[str, str] = {}
    chave_aberta: str | None = None
    literal = False          # `|` junta com nova-linha; `>` e simples, com espaço
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
            continue  # continuação de uma chave que não abrimos — ignorada

        fechar()
        if ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        chave, valor = chave.strip(), valor.strip()
        if valor in {"|", ">", "|-", ">-", "|+", ">+"}:
            chave_aberta, literal = chave, valor.startswith("|")
            campos[chave] = ""
        else:
            # A chave fica ABERTA mesmo com valor na mesma linha: em YAML um
            # escalar simples continua nas linhas indentadas seguintes, e é
            # assim que a maioria das `description` longas é escrita no disco.
            # Fechar aqui descartava a continuação — e a ferramenta lia metade
            # da vitrine sem dar erro. Achado pelo controle negativo S4.
            chave_aberta, literal = chave, False
            campos[chave] = valor

    fechar()
    return campos, texto[fim + 4 :]


def _desaspar(valor: str) -> str:
    """`description:` costuma vir como string JSON. Aspas soltas não são dado."""
    valor = valor.strip()
    if valor[:1] in {'"', "'"}:
        try:
            return json.loads(valor)
        except (ValueError, TypeError):
            return valor.strip("\"'")
    return valor


def _commits(caminho: Path) -> int | None:
    """Quantos commits tocaram este arquivo. `None` quando não dá para medir.

    Devolver `None` em vez de `0` é deliberado: «não medido» e «nunca commitado»
    são coisas diferentes, e confundir as duas é exatamente o defeito que esta
    ferramenta existe para cobrar.
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
    """Lê um `SKILL.md`. Devolve `None` se o arquivo não puder ser lido."""
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
    """Acha todo `SKILL.md` sob `raiz`, em qualquer profundidade.

    ⚠️ `rglob` NÃO atravessa junction do Windows nem symlink de diretório. Se a
    sua pasta de skills for montada assim, aponte para o alvo real — este é o
    mesmo defeito silencioso que a `LACUNAS.md` desta operação declara.
    """
    if raiz.is_file() and raiz.name == "SKILL.md":
        lida = ler_skill(raiz, com_git)
        return [lida] if lida else []
    achadas = [ler_skill(p, com_git) for p in sorted(raiz.rglob("SKILL.md"))]
    return [s for s in achadas if s is not None]


# --------------------------------------------------------------- as dez --------


def _tem(texto: str, marcas: tuple[str, ...]) -> bool:
    baixo = texto.lower()
    return any(m in baixo for m in marcas)


def _significativas(descricao: str) -> set[str]:
    """As palavras de uma `description` que de fato a distinguem das outras."""
    return {p for p in _PALAVRA.findall(descricao.lower())} - VAZIAS


def _confusao(a: Skill, b: Skill) -> float:
    """Quanto duas `description` disputam o mesmo despacho. Jaccard, sem mistério."""
    pa, pb = _significativas(a.descricao), _significativas(b.descricao)
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / len(pa | pb)


def _um_nomeia_o_outro(a: Skill, b: Skill) -> bool:
    """Gatilho negativo de verdade é nominal: cita o irmão pelo slug."""
    return a.slug in b.descricao.lower() or b.slug in a.descricao.lower()


def _profundidade(arquivo: Path, pasta_ref: Path) -> int:
    """Quantos níveis de pasta abaixo de `references/`. Plano = 0."""
    return len(arquivo.relative_to(pasta_ref).parts) - 1


def vistoriar(skills: list[Skill]) -> list[Achado]:
    """As dez regras. Cada uma cita a fonte pública de onde ela sai."""
    FONTE_SPEC = "spec do formato Agent Skills"
    FONTE_BP = "best-practices oficial de criação de skill"

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

    # S1 — o nome é o endereço, não o título -----------------------------------
    registrar(
        "S1",
        "O NOME NÃO É O DA PASTA",
        "o `name:` é o ENDEREÇO da skill, não o título dela. Ele tem de ser\n"
        "       idêntico ao nome da pasta-mãe: `angular-testing/SKILL.md` exige\n"
        "       `name: angular-testing`. Divergindo, o carregamento é sorte.",
        FONTE_SPEC,
        [
            (s.slug, f"declara `{s.nome}`" if s.nome else "não declara `name:`")
            for s in skills
            if s.nome != s.pasta.name
        ],
    )

    # S2 — a gramática do nome -------------------------------------------------
    registrar(
        "S2",
        "O NOME NÃO CABE NA GRAMÁTICA",
        "1 a 64 caracteres, só minúsculas, dígitos e hífen simples. Maiúscula,\n"
        "       espaço, underscore e hífen duplo quebram o carregamento — e\n"
        "       quebram calados.",
        FONTE_SPEC,
        [
            (
                s.slug,
                f"`{s.nome}` tem {len(s.nome)} caracteres"
                if len(s.nome) > 64
                else f"`{s.nome}` sai da gramática",
            )
            for s in skills
            if s.nome and not (NOME_VALIDO.match(s.nome) and len(s.nome) <= 64)
        ],
    )

    # S3 — quando usar ---------------------------------------------------------
    registrar(
        "S3",
        "NÃO DIZ QUANDO USAR",
        "a `description` é o ÚNICO campo que o roteador lê antes de decidir.\n"
        "       Sem cláusula de gatilho — «Use when…» / «Usar quando…» — o modelo\n"
        "       não liga a skill a nenhuma tarefa. Ela não falha: ela é invisível.",
        FONTE_BP,
        [
            (s.slug, "descrição sem cláusula de gatilho" if s.descricao else "sem `description:`")
            for s in skills
            if not (
                GATILHO_POSITIVO.search(s.descricao) or _tem(s.descricao, GATILHO_POSITIVO_EXTRA)
            )
        ],
    )

    # S4 — quando NÃO usar -----------------------------------------------------
    registrar(
        "S4",
        "NÃO DIZ QUANDO **NÃO** USAR",
        "sem gatilho negativo, duas skills do mesmo domínio disputam o mesmo\n"
        "       despacho e a escolha vira sorteio. Nomeie o irmão por extenso:\n"
        "       «Don't use it for Vue, Svelte, or vanilla CSS.»",
        FONTE_BP,
        [(s.slug, "descrição sem gatilho negativo") for s in skills if not _tem(s.descricao, GATILHO_NEGATIVO)],
    )

    # S5 — a vitrine não cabe na janela ----------------------------------------
    registrar(
        "S5",
        "A VITRINE NÃO CABE NA JANELA",
        f"acima de {TETO_DESCRICAO} caracteres a `description` é truncada, e o corte cai\n"
        "       no meio da frase que decidiria o despacho.",
        FONTE_SPEC,
        [(s.slug, f"{len(s.descricao)} caracteres") for s in skills if len(s.descricao) > TETO_DESCRICAO],
    )

    # S6 — o corpo estourou o teto ---------------------------------------------
    registrar(
        "S6",
        "O CORPO ESTOUROU O TETO",
        f"acima de {TETO_LINHAS} linhas o `SKILL.md` deixa de ser o mapa e vira o\n"
        "       território. Mova o detalhe para `references/`, que só é lido\n"
        "       depois que a skill já foi escolhida.",
        FONTE_BP,
        [(s.slug, f"{s.linhas} linhas") for s in skills if s.linhas > TETO_LINHAS],
        grave=False,
    )

    # S7 — references fundo demais ---------------------------------------------
    fundos: list[tuple[str, str]] = []
    for s in skills:
        pasta_ref = s.pasta / "references"
        for arq in s.referencias:
            if _profundidade(arq, pasta_ref) > 0:
                fundos.append((s.slug, f"references/{arq.relative_to(pasta_ref).as_posix()}"))
    registrar(
        "S7",
        "`references/` FUNDO DEMAIS",
        "`references/` é plano por contrato: `references/schema.md`, nunca\n"
        "       `references/db/v1/schema.md`. O carregamento progressivo desce\n"
        "       exatamente um nível — o que estiver abaixo não é alcançado.",
        FONTE_BP,
        fundos,
    )

    # S8 — script que é biblioteca ---------------------------------------------
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
        "SCRIPT QUE É BIBLIOTECA",
        "`scripts/` é para CLI minúsculo, um trabalho por arquivo. Módulo sem\n"
        "       ponto de entrada é biblioteca — e biblioteca ali é contexto que o\n"
        "       agente carrega e não sabe rodar.",
        FONTE_BP,
        bibliotecas,
        grave=False,
    )

    # S9 — vitrine na pessoa errada --------------------------------------------
    registrar(
        "S9",
        "A VITRINE FALA NA PESSOA ERRADA",
        "a descrição é lida pelo roteador em terceira pessoa, ao lado de dezenas\n"
        "       de outras. «Creates React components» roteia; «I help you with\n"
        "       React» descreve um relacionamento, e não casa com tarefa nenhuma.",
        FONTE_BP,
        [
            (s.slug, f"começa em «{s.descricao.split()[0]}»")
            for s in skills
            if s.descricao and s.descricao.lower().startswith(PESSOA_ERRADA)
        ],
        grave=False,
    )

    # S10 — nunca corrigida depois do primeiro erro ----------------------------
    registrar(
        "S10",
        "NASCEU PRONTA E NUNCA FOI CORRIGIDA",
        "skill com um commit só nunca passou por um erro real. O caminho é\n"
        "       escrever a versão que funciona em dez minutos e corrigir no\n"
        "       primeiro erro do agente — cada erro é uma melhoria da skill.",
        FONTE_BP,
        [(s.slug, "1 commit") for s in skills if s.commits == 1],
        grave=False,
    )

    # S11 — duas skills se confundem --------------------------------------------
    pares = [
        (f"{a.slug} × {b.slug}", f"{round(_confusao(a, b) * 100)}% das palavras em comum")
        for i, a in enumerate(skills)
        for b in skills[i + 1 :]
        if _confusao(a, b) >= LIMIAR_CONFUSAO and not _um_nomeia_o_outro(a, b)
    ]
    registrar(
        "S11",
        "DUAS SKILLS SE CONFUNDEM",
        "descrições disputando o mesmo despacho, e nenhuma nomeia a outra. O\n"
        "       conserto é nominal: cada `description` cita a irmã no que NUNCA\n"
        "       faz — é o mesmo gatilho negativo que o `S4` já cobra, só que\n"
        "       apontado para um nome, não em aberto.",
        FONTE_BP,
        pares,
    )
    if pares:
        achados[-1].skills = set()  # um par não é uma skill; não entra no denominador

    return achados
