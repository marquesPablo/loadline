"""Vistoria: lê os agentes que VOCÊ JÁ TEM, e diz o que falta no SISTEMA.

natureza: correcao — a saída é sempre impressa por inteiro, inclusive quando
reprova. Uma vistoria que só aparece quando passa não é vistoria.

A forja compila spec → artefato. Esta é a direção contrária, e é por onde todo
mundo chega: você já tem doze agentes escritos à mão e não vai escrever doze
specs na fé. A vistoria lê os doze e devolve o que só aparece a partir do
quinto — os defeitos que não moram em nenhum agente, e sim ENTRE eles.

    python -m forja                      # vistoria de `.claude/agents/`
    python -m forja --adotar             # ESCREVE: uma spec por agente lido

Sete achados. Os cinco primeiros são de UM agente; os dois últimos só existem
porque há mais de um, e são a razão de esta ferramenta existir:

    V1  não diz o que NUNCA faz          o orquestrador despacha por tema
    V2  não diz QUANDO usar              agente que ninguém alcança
    V3  fronteira só na prosa            pede escrita/rede sem declarar onde
    V4  não diz o que não cobre          silêncio é lido como cobertura
    V5  nada confere a RESPOSTA          você testa o código, nunca a resposta
    V6  dois se confundem                descrições sobrepostas, e nenhum
                                         nomeia o outro
    V7  ferramenta sem dono              herda tudo o que o harness oferece

Código de saída: 0 nada encontrado · 1 defeito · 2 não havia o que ler.
O 2 é o ponto: pasta que não existe é RECUSA, e nunca verde. Um erro de
digitação no caminho não pode deixar um gate aprovando para sempre.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .spec import CONHECIDAS, ESCRITA, REDE

# Onde os harnesses de hoje guardam agente. A busca é por pasta declarada, e
# nunca por varredura do projeto inteiro: varrer `.` acha `node_modules` e
# devolve uma resposta plausível e errada.
PASTAS = (".claude/agents", ".claude/subagents", "agents", ".cursor/agents")

# Fora do vocabulário: `tools:` ausente NÃO significa "nenhuma ferramenta".
# Nos harnesses de hoje significa **todas** — que é o oposto, e é o defeito V7.
HERDA_TUDO = "«herda todas»"

_ACENTO = re.compile(r"[̀-ͯ]")
_PALAVRA = re.compile(r"[a-z0-9]{5,}")

# Palavras que aparecem em toda descrição de agente e não distinguem nada.
# Sem esta lista, dois agentes quaisquer "se parecem" e o V6 vira ruído.
VAZIAS = frozenset(
    """
    agente agentes usar quando nunca sempre projeto arquivo arquivos pasta
    pastas quando sobre cada todos todas outro outra apenas mesmo mesma
    porque coisa coisas forma partir depois antes ainda entao tambem
    escrever escreve escrito leitura ler nunca_usar deve devem podem
    """.split()
)


def _sem_acento(texto: str) -> str:
    return _ACENTO.sub("", unicodedata.normalize("NFD", texto.lower()))


def _significativas(texto: str) -> set[str]:
    """As palavras de uma descrição que de fato a distinguem das outras."""
    return {p for p in _PALAVRA.findall(_sem_acento(texto))} - VAZIAS


@dataclass
class Lido:
    """Um agente COMO ELE ESTÁ no disco — não como alguém gostaria que fosse."""

    caminho: Path
    slug: str
    descricao: str
    ferramentas: list[str]
    corpo: str
    tools_ausente: bool
    #: A raiz do projeto que contém este agente — de onde os arquivos irmãos
    #: (hook, golden, lacunas) são procurados. `None` quando não dá para dizer.
    raiz: Path | None = None
    #: O frontmatter INTEIRO, `chave: valor` cru — não só `name`/`description`/
    #: `tools`. Existe porque `saida_cercada`/`dominios_permitidos` (as duas
    #: marcas de fronteira que V3 procura) costumam morar AQUI, não na prosa do
    #: corpo — e um campo estruturado é sinal mais forte que a mesma frase
    #: escrita como texto (mesmo raciocínio de `_irmao_declara`).
    campos: dict[str, str] = field(default_factory=dict)

    @property
    def nome_curto(self) -> str:
        return self.caminho.name

    @property
    def usa_rede(self) -> bool:
        return bool(REDE & set(self.ferramentas)) or self.tools_ausente

    @property
    def usa_escrita(self) -> bool:
        return bool(ESCRITA & set(self.ferramentas)) or self.tools_ausente

    @property
    def desconhecidas(self) -> list[str]:
        return sorted(set(self.ferramentas) - CONHECIDAS)


@dataclass
class Achado:
    regra: str
    titulo: str
    conserto: str
    itens: list[str] = field(default_factory=list)
    grave: bool = True
    #: Os agentes DISTINTOS atingidos. Separado de `itens` porque um agente pode
    #: render duas linhas (escrita E rede), e contar linha como agente faria o
    #: denominador dizer «4 de 2» — não medido virando número inventado, dentro
    #: da ferramenta que existe para proibir isso.
    agentes: set[str] = field(default_factory=set)


def _frontmatter(texto: str) -> tuple[dict[str, str], str]:
    """Frontmatter mínimo, sem dependência: `---` … `---`, uma chave por linha.

    Não é um parser de YAML e não finge ser. Ele lê o que os harnesses de hoje
    de fato escrevem — `chave: valor` de uma linha — e devolve o resto como
    corpo. Valor multi-linha não é lido, e isso está declarado em LACUNAS.
    """
    if not texto.startswith("---"):
        return {}, texto
    fim = texto.find("\n---", 3)
    if fim == -1:
        return {}, texto
    campos: dict[str, str] = {}
    for linha in texto[3:fim].splitlines():
        if ":" not in linha or linha.startswith((" ", "\t", "#")):
            continue
        chave, _, valor = linha.partition(":")
        campos[chave.strip()] = valor.strip()
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


def ler_agente(caminho: Path, raiz: Path | None = None) -> Lido | None:
    """Um arquivo → um agente lido. `None` quando o arquivo não é um agente."""
    try:
        texto = caminho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    campos, corpo = _frontmatter(texto)
    if "name" not in campos and "description" not in campos:
        return None  # markdown solto na pasta; não é agente, e não vira número.
    bruto = campos.get("tools", "").strip()
    return Lido(
        caminho=caminho,
        slug=campos.get("name", caminho.stem).strip() or caminho.stem,
        descricao=_desaspar(campos.get("description", "")),
        ferramentas=[f.strip() for f in bruto.split(",") if f.strip()] if bruto else [],
        corpo=corpo,
        tools_ausente="tools" not in campos or not bruto,
        raiz=raiz,
        campos=campos,
    )


def achar_pasta(raiz: Path) -> Path | None:
    for relativo in PASTAS:
        candidato = raiz / relativo
        if candidato.is_dir():
            return candidato
    return None


def raiz_do_projeto(pasta: Path) -> Path:
    """De `<raiz>/.claude/agents` volta para `<raiz>`. É de lá que saem os irmãos."""
    partes = [p.lower() for p in pasta.parts]
    return pasta.parent.parent if ".claude" in partes else pasta.parent


def ler_roster(pasta: Path) -> list[Lido]:
    raiz = raiz_do_projeto(pasta)
    lidos = [ler_agente(p, raiz) for p in sorted(pasta.glob("*.md"))]
    return [x for x in lidos if x is not None]


# ----------------------------------------------------------- os sete --------
#
# ⚠️ Todo achado abaixo é a AUSÊNCIA de uma declaração legível por máquina —
# nunca um julgamento sobre a qualidade do agente. A diferença importa: um
# agente excelente cuja fronteira está escrita em prosa aparece aqui, e deve
# aparecer. Prosa não é cerca; ela é intenção, e nenhum runtime a lê.
#
# Cada marca é uma lista fechada, e ela está escrita aqui para que quem discorde
# possa apontar o que falta em vez de descobrir o limite sendo surpreendido.

DIZ_QUE_NAO_FAZ = ("nunca usar", "nunca use", "não usar para", "nao usar para", "never use")
DIZ_QUANDO_USAR = ("usar quando", "usar para", "use quando", "use when", "use this")
DIZ_ONDE_ESCREVE = ("saida_cercada", "escreve só em", "escreve apenas em", "um caminho só")
DIZ_ONDE_FALA = ("dominios_permitidos", "domínios permitidos", "allowed_domains")
DIZ_O_QUE_NAO_COBRE = ("lacuna", "não mede", "nao mede", "não cobre", "nao cobre", "o que este")
DIZ_QUE_CONFERE_RESPOSTA = ("golden", "resposta esperada", "caso de verificação")

# Acima disto, duas descrições disputam o mesmo despacho. O valor é ESCOLHIDO,
# não medido — e por isso ele está aqui, com o dono, em vez de enterrado num if.
LIMIAR_CONFUSAO = 0.30


# Onde uma declaração pode morar FORA do `.md` do agente. Um hook num arquivo
# irmão é uma cerca de verdade — mais de verdade, aliás, do que a mesma frase
# escrita na prosa do prompt, que nenhum runtime lê. Procurar só dentro do `.md`
# acusaria a saída do próprio compilador, que é a família de defeito em que uma
# ferramenta passa a medir a superfície errada e chama isso de achado.
IRMAOS = {
    "cerca": ("hooks", ".claude/hooks"),
    "golden": ("golden", "evals", "eval", "tests/golden"),
    "lacunas": (".", "docs"),
}
NOMES_DE_LACUNA = ("lacunas.md", "limitacoes.md", "limitations.md", "gaps.md")


def _irmao_declara(raiz: Path | None, slug: str, familia: str) -> bool:
    """Existe, ao lado do agente, um arquivo que o nomeia e faz esta declaração?

    A busca é por PASTA declarada e um nível de profundidade — nunca varredura
    do projeto inteiro. Varrer `.` acha `node_modules` e devolve uma resposta
    plausível e errada, que é pior do que não achar nada.
    """
    if raiz is None:
        return False
    alvo = _sem_acento(slug)
    for relativo in IRMAOS[familia]:
        pasta = raiz / relativo
        if not pasta.is_dir():
            continue
        for arquivo in sorted(pasta.glob("*")):
            if not arquivo.is_file() or arquivo.suffix not in {".py", ".md", ".json", ".toml", ".yaml", ".yml"}:
                continue
            if familia == "lacunas" and arquivo.name.lower() not in NOMES_DE_LACUNA:
                continue
            try:
                if alvo in _sem_acento(arquivo.read_text(encoding="utf-8", errors="replace")):
                    return True
            except OSError:
                continue
    return False


def _contem(lido: Lido, marcas: tuple[str, ...]) -> bool:
    alvo = _sem_acento(lido.descricao + "\n" + lido.corpo)
    return any(_sem_acento(m) in alvo for m in marcas)


def _campo_declarado(lido: Lido, chave: str) -> bool:
    """`chave` existe no FRONTMATTER com valor não-vazio?

    Achado nesta rodada: `_contem` nunca via `saida_cercada`/`dominios_permitidos`
    quando o agente os declara do jeito CERTO — como campo estruturado do
    frontmatter — porque `_frontmatter()` os retira do texto antes de `corpo`
    existir, e `descricao` só carrega o campo `description`. Um agente com
    `saida_cercada: "caminho/"` no YAML reprovava V3 pela MESMA razão que
    reprovaria um agente sem cerca nenhuma — falso negativo na própria marca
    que dá nome à constante. Campo estruturado é sinal mais forte que a mesma
    frase em prosa (mesmo raciocínio de `_irmao_declara`), então ele decide
    sozinho, sem precisar também aparecer no corpo.
    """
    valor = lido.campos.get(chave, "").strip().strip('"').strip("'").strip()
    return bool(valor)


def _confusao(a: Lido, b: Lido) -> float:
    """Quanto duas descrições disputam o mesmo despacho. Jaccard, sem mistério."""
    pa, pb = _significativas(a.descricao), _significativas(b.descricao)
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / len(pa | pb)


def _um_nomeia_o_outro(a: Lido, b: Lido) -> bool:
    """Anti-descrição de verdade é nominal: ela cita o irmão pelo slug."""
    return (
        _sem_acento(b.slug) in _sem_acento(a.descricao + a.corpo)
        or _sem_acento(a.slug) in _sem_acento(b.descricao + b.corpo)
    )


def _fronteiras_abertas(a: Lido) -> tuple[tuple[str, str, bool], ...]:
    """As duas fronteiras de um agente, e se cada uma está declarada."""
    return (
        (
            "escrita",
            "onde pode escrever",
            a.usa_escrita
            and not _campo_declarado(a, "saida_cercada")
            and not _contem(a, DIZ_ONDE_ESCREVE)
            and not _irmao_declara(a.raiz, a.slug, "cerca"),
        ),
        (
            "rede",
            "com quem pode falar",
            a.usa_rede
            and not _campo_declarado(a, "dominios_permitidos")
            and not _contem(a, DIZ_ONDE_FALA)
            and not _irmao_declara(a.raiz, a.slug, "cerca"),
        ),
    )


def vistoriar(roster: list[Lido]) -> list[Achado]:
    achados: list[Achado] = []

    def marcar(
        regra: str,
        titulo: str,
        conserto: str,
        itens: list[str],
        agentes: set[str] | None = None,
        grave: bool = True,
    ) -> None:
        if itens:
            achados.append(Achado(regra, titulo, conserto, itens, grave, agentes or set(itens)))

    marcar(
        "V1",
        "NÃO DIZEM O QUE NUNCA FAZEM",
        "sem anti-descrição, o orquestrador despacha por TEMA — e o tema de dois "
        "agentes se parece muito mais do que o trabalho deles.",
        [a.nome_curto for a in roster if not _contem(a, DIZ_QUE_NAO_FAZ)],
    )
    marcar(
        "V2",
        "NÃO DIZEM QUANDO USAR",
        "um agente que não declara o próprio gatilho é um agente que ninguém "
        "alcança — ele existe no disco e nunca no despacho.",
        [a.nome_curto for a in roster if not _contem(a, DIZ_QUANDO_USAR)],
    )
    marcar(
        "V3",
        "A FRONTEIRA ESTÁ SÓ NA PROSA",
        '"escrevo num caminho só" e "só consulto a documentação" são intenção. '
        "Nenhum runtime lê prosa: sem declaração, o agente alcança tudo o que o "
        "harness alcança.",
        [
            f"{a.nome_curto:<34} pede {classe} e não declara {campo}"
            for a in roster
            for classe, campo, falta in _fronteiras_abertas(a)
            if falta
        ],
        {a.nome_curto for a in roster if any(f for _, _, f in _fronteiras_abertas(a))},
    )
    marcar(
        "V4",
        "NÃO DIZEM O QUE NÃO COBREM",
        "silêncio é lido como cobertura. Quem recebe a resposta não tem como "
        "saber o que o agente nunca olhou — e vai tratar o que faltou como ausente.",
        [
            a.nome_curto
            for a in roster
            if not _contem(a, DIZ_O_QUE_NAO_COBRE) and not _irmao_declara(a.raiz, a.slug, "lacunas")
        ],
    )
    marcar(
        "V5",
        "NADA CONFERE A RESPOSTA DELES",
        "não há nenhuma pergunta cujo acerto esteja escrito à mão. Sem isso você "
        "testa se o agente RODOU, nunca se ele acertou.",
        [
            a.nome_curto
            for a in roster
            if not _contem(a, DIZ_QUE_CONFERE_RESPOSTA) and not _irmao_declara(a.raiz, a.slug, "golden")
        ],
    )
    marcar(
        "V7",
        "HERDAM TODA FERRAMENTA DO HARNESS",
        "`tools:` ausente não quer dizer nenhuma ferramenta — nos harnesses de "
        "hoje quer dizer TODAS, que é o oposto. Um agente de leitura herda a "
        "escrita e a rede sem ninguém decidir isso.",
        [a.nome_curto for a in roster if a.tools_ausente],
    )

    pares = [
        f"{a.nome_curto} × {b.nome_curto}".ljust(46) + f"{_confusao(a, b):.0%} das palavras em comum"
        for i, a in enumerate(roster)
        for b in roster[i + 1 :]
        if _confusao(a, b) >= LIMIAR_CONFUSAO and not _um_nomeia_o_outro(a, b)
    ]
    marcar(
        "V6",
        "SE CONFUNDEM ENTRE SI",
        "descrições disputando o mesmo despacho, e nenhum dos dois nomeia o "
        "outro. O conserto é nominal: cada um cita o irmão no que NUNCA faz.",
        pares,
        agentes=set(),  # um par não é um agente; ele não entra no denominador.
    )
    return achados


# ------------------------------------------------------- o relatório --------
LARGURA = 74


def relatorio(roster: list[Lido], achados: list[Achado], pasta: Path, hoje: str) -> list[str]:
    linhas = [f"vistoria · {pasta} · em {hoje}", "=" * LARGURA]
    linhas.append(f"Li {len(roster)} agente(s).")
    linhas.append("")

    for achado in sorted(achados, key=lambda a: (not a.grave, -len(a.itens))):
        marca = "⛔" if achado.grave else "⚠️"
        contagem = (
            f"{len(achado.itens)} par(es)"
            if achado.regra == "V6"
            else f"{len(achado.agentes)} de {len(roster)}"
        )
        cabeca = f"{marca} {achado.titulo}"
        linhas.append(f"{cabeca}{' ' * max(1, LARGURA - len(cabeca) - len(contagem) - 1)}{contagem}")
        for item in achado.itens[:8]:
            linhas.append(f"     {item}")
        if len(achado.itens) > 8:
            linhas.append(f"     … e mais {len(achado.itens) - 8}")
        linhas.append(f"     → {achado.conserto}")
        linhas.append("")

    # Seis declarações por agente: o que nunca faz · quando usar · onde escreve
    # ou fala · o que não cobre · o que confere a resposta · que ferramenta tem.
    # O denominador está escrito aqui porque um número sem denominador é o que
    # esta ferramenta inteira existe para cobrar.
    declaracoes_possiveis = len(roster) * 6
    ausentes = sum(len(a.agentes) for a in achados if a.regra != "V6")
    linhas.append("-" * LARGURA)
    linhas.append(
        f"{len(roster)} agente(s) · {len(achados)} tipo(s) de defeito · "
        f"{ausentes} de {declaracoes_possiveis} declarações ausentes"
    )
    return linhas


CABECA_TOML = """\
# Spec adotada de `{origem}` em {hoje}, por `python -m forja --adotar`.
#
# ⚠️ Ela NÃO está pronta: cada `?` abaixo é um buraco que já existia no agente e
# que ninguém tinha onde ver. A forja se RECUSA a compilar enquanto houver um,
# e toda recusa traz o conserto escrito.
#
# O que está preenchido foi LIDO do arquivo original, nunca inferido.
#
#     python -m forja {saida}
"""


def _t(valor: str) -> str:
    """String TOML segura, sem dependência: aspas triplas e escape do que quebra."""
    return '"""' + valor.replace("\\", "\\\\").replace('"""', '\\"\\"\\"').strip() + '"""'


def _lista_toml(itens: list[str], recuo: str = "  ") -> str:
    if not itens:
        return "[]"
    return "[\n" + "".join(f"{recuo}{_t(i)},\n" for i in itens) + "]"


def adotar(lido: Lido, hoje: str, saida: Path) -> str:
    """Um agente escrito à mão → a spec dele, com um `?` em cada buraco.

    Este é o ponto em que a ferramenta deixa de ser alarme. A anotação é a SAÍDA
    da primeira rodada, nunca o pedágio dela: ninguém com doze agentes vai
    escrever doze specs na fé para descobrir se valia a pena.
    """
    faltando = "? — escreva aqui; a forja não compila enquanto este `?` estiver de pé"
    nunca = [] if _contem(lido, DIZ_QUE_NAO_FAZ) else [faltando]
    quando = [] if _contem(lido, DIZ_QUANDO_USAR) else [faltando]
    partes = [
        CABECA_TOML.format(origem=lido.caminho, hoje=hoje, saida=saida.name),
        "",
        "[agente]",
        f'slug = "{lido.slug}"',
        f"nome = {_t(lido.slug.replace('-', ' ').capitalize())}",
        f"uma_frase = {_t(lido.descricao or faltando)}",
        f"usar_quando = {_lista_toml(quando or ['(lido do arquivo original — confira e reescreva)'])}",
        f"nunca_usar = {_lista_toml(nunca or ['(lido do arquivo original — confira e reescreva)'])}",
        "",
        "[fronteira]",
        f"ferramentas = {json.dumps(lido.ferramentas, ensure_ascii=False)}"
        + ("  # ⚠️ `tools:` estava AUSENTE: o agente herdava TODAS" if lido.tools_ausente else ""),
    ]
    if lido.usa_rede:
        partes.append(f'dominios_permitidos = ["?"]  # ["nenhum"] barra sempre')
    if lido.usa_escrita:
        partes.append(f'saida_cercada = ["?"]  # o prefixo de caminho onde ele pode escrever')
    partes += [
        "toca_alvo = false",
        "",
        "[prova]",
        f"lacunas = {_lista_toml([faltando])}",
        "",
        "[[prova.golden]]",
        f"pergunta = {_t('?')}",
        f"esperado = {_t('?')}",
        f"derivado_de = {_t('? — e NUNCA da saída deste agente: os dois lados saindo da mesma fonte passam verde travando o defeito')}",
        "",
    ]
    return "\n".join(partes)
