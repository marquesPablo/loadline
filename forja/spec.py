"""A spec de um agente, e as oito recusas que impedem de compilar uma ruim.

natureza: seguranca — toda decisão deste módulo é uma RECUSA, e ela falha
fechada. O que a forja não consegue decidir, ela se recusa a emitir; ela nunca
emite "no melhor esforço" com um campo faltando. Um compilador de agente que
falha aberto entrega exatamente o agente sem gate que ele existia para evitar.

A spec é TOML porque `tomllib` é stdlib desde o Python 3.11 — o projeto inteiro
continua com zero dependências. E é declarativa porque um campo com código a
executar seria injeção com convite escrito.

## As oito recusas

    R1  ferramenta de REDE sem `dominios_permitidos`
    R2  ferramenta de ESCRITA sem `saida_cercada`
    R3  `nunca_usar` vazio            — sem anti-descrição, o orquestrador chuta
    R4  `lacunas` vazio               — nada declara o que o agente não mede
    R5  zero caso de golden set       — nenhuma resposta foi conferida
    R6  golden derivado de dentro     — check espelho: os dois lados, a mesma fonte
    R7  `toca_alvo` sem autorização   — recon sem escopo é incidente, não achado
    R8  slug inválido                 — o slug vira nome de arquivo em 4 harnesses

Cada uma existe porque o campo AUSENTE é indistinguível, para um hook, do campo
vazio: ausente-ou-vazio BARRA, e é a única leitura que não vira porta dos fundos.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Ferramentas que saem da máquina, e as que escrevem no disco. A lista é fechada
# e cobre os nomes usados pelos harnesses de hoje; nome desconhecido NÃO é
# tratado como inofensivo — ver `_desconhecidas`.
REDE = frozenset({"WebFetch", "WebSearch", "Fetch", "Browser", "http", "curl"})
ESCRITA = frozenset({"Write", "Edit", "NotebookEdit", "MultiEdit", "apply_patch"})
EXECUCAO = frozenset({"Bash", "PowerShell", "Shell", "Terminal", "Execute"})
CONHECIDAS = REDE | ESCRITA | EXECUCAO | frozenset(
    {"Read", "Grep", "Glob", "TodoWrite", "Task", "AskUserQuestion"}
)

SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class Recusa(ValueError):
    """A forja se recusou a compilar. Sempre com o código da regra e o conserto."""

    def __init__(self, regra: str, motivo: str, conserto: str) -> None:
        self.regra, self.motivo, self.conserto = regra, motivo, conserto
        super().__init__(f"{regra}: {motivo}\n      conserto: {conserto}")


@dataclass(frozen=True)
class Caso:
    """Um caso do golden set. `derivado_de` é o que o torna verificação."""

    pergunta: str
    esperado: str
    derivado_de: str


@dataclass
class Spec:
    slug: str
    nome: str
    uma_frase: str
    usar_quando: list[str]
    nunca_usar: list[str]
    ferramentas: list[str]
    dominios_permitidos: list[str] | None = None
    saida_cercada: list[str] | None = None
    toca_alvo: bool = False
    autorizacao: str | None = None
    lacunas: list[str] = field(default_factory=list)
    golden: list[Caso] = field(default_factory=list)
    precisa: list[str] = field(default_factory=list)
    idioma: str = "pt"
    origem: str = ""

    # ---- as classes de ferramenta que esta spec pediu ---------------------
    @property
    def usa_rede(self) -> bool:
        return bool(REDE & set(self.ferramentas))

    @property
    def usa_escrita(self) -> bool:
        return bool(ESCRITA & set(self.ferramentas))

    @property
    def usa_execucao(self) -> bool:
        return bool(EXECUCAO & set(self.ferramentas))

    @property
    def desconhecidas(self) -> list[str]:
        """Ferramenta fora do vocabulário conhecido.

        Não é erro — harness novo traz nome novo. Mas ela é EXIBIDA na receita,
        porque tratar nome desconhecido como inofensivo é como uma cerca de
        rede deixa de cercar sem ninguém ver.
        """
        return sorted(set(self.ferramentas) - CONHECIDAS)


def _lista(bruto: object) -> list[str]:
    if bruto is None:
        return []
    if isinstance(bruto, str):
        return [bruto]
    return [str(x) for x in bruto]  # type: ignore[union-attr]


def validar(spec: Spec) -> None:
    """Roda as oito recusas. Não devolve nada — ou passa, ou levanta `Recusa`."""
    if not SLUG.match(spec.slug):
        raise Recusa(
            "R8",
            f"`{spec.slug}` não é um slug válido",
            "use minúsculas, números e hífen — ele vira nome de arquivo em 4 harnesses",
        )
    if spec.usa_rede and not spec.dominios_permitidos:
        raise Recusa(
            "R1",
            f"pede ferramenta de rede ({', '.join(sorted(REDE & set(spec.ferramentas)))}) "
            "e não declara `dominios_permitidos`",
            'declare `dominios_permitidos = ["exemplo.com"]`, ou `["nenhum"]` para barrar '
            "sempre — ausente e vazio significam a mesma coisa e as duas BARRAM",
        )
    if spec.usa_escrita and not spec.saida_cercada:
        raise Recusa(
            "R2",
            f"pede ferramenta de escrita ({', '.join(sorted(ESCRITA & set(spec.ferramentas)))}) "
            "e não declara `saida_cercada`",
            'declare `saida_cercada = ["relatorios/"]` — "escrevo num caminho só" escrito '
            "em prosa não é cerca, é intenção",
        )
    if not spec.nunca_usar:
        raise Recusa(
            "R3",
            "não declara `nunca_usar`",
            "escreva pelo menos um caso em que este agente é a escolha ERRADA — sem "
            "anti-descrição o orquestrador despacha por semelhança de tema",
        )
    if not spec.lacunas:
        raise Recusa(
            "R4",
            "não declara `lacunas`",
            "escreva o que este agente NÃO mede — ausência sem dono envelhece calada, "
            "e um agente que não declara limite é lido como se não tivesse nenhum",
        )
    if not spec.golden:
        raise Recusa(
            "R5",
            "não tem nenhum caso de golden set",
            "escreva um caso com a resposta conferida À MÃO no disco — sem isso nada "
            "pergunta se a RESPOSTA está certa, só se o código obedece à spec",
        )
    for caso in spec.golden:
        if not caso.derivado_de.strip():
            raise Recusa(
                "R6",
                f"o caso «{caso.pergunta[:40]}…» não declara `derivado_de`",
                "aponte a fonte, em `caminho:linha` ou URL, de onde a resposta esperada "
                "foi lida à mão",
            )
        if caso.derivado_de.strip().startswith(tuple(spec.saida_cercada or ())):
            raise Recusa(
                "R6",
                f"o caso «{caso.pergunta[:40]}…» deriva de `{caso.derivado_de}`, que está "
                "DENTRO da saída do próprio agente",
                "derive de uma fonte que o agente não escreve — os dois lados saindo do "
                "mesmo lugar é check espelho, e ele passa verde travando o defeito",
            )
    if spec.toca_alvo and not spec.autorizacao:
        raise Recusa(
            "R7",
            "declara `toca_alvo = true` e não declara onde está a autorização de engajamento",
            'declare `autorizacao = "escopo/alvo.md"` com alvo, escopo, autorização e '
            "validade — um comando fora do alvo autorizado é incidente, não achado",
        )


def ler(caminho: str | Path) -> Spec:
    """Lê e valida uma spec. Erro de campo é `Recusa`, nunca `KeyError` cru."""
    caminho = Path(caminho)
    dados = tomllib.loads(caminho.read_text(encoding="utf-8"))
    a = dados.get("agente") or {}
    f = dados.get("fronteira") or {}
    p = dados.get("prova") or {}
    c = dados.get("censo") or {}

    for campo in ("slug", "nome", "uma_frase"):
        if not a.get(campo):
            raise Recusa(
                "R0",
                f"a spec não declara `agente.{campo}`",
                f"acrescente `{campo} = \"...\"` na seção `[agente]`",
            )

    spec = Spec(
        slug=a["slug"],
        nome=a["nome"],
        uma_frase=a["uma_frase"],
        usar_quando=_lista(a.get("usar_quando")),
        nunca_usar=_lista(a.get("nunca_usar")),
        ferramentas=_lista(f.get("ferramentas")),
        dominios_permitidos=_lista(f.get("dominios_permitidos")) or None,
        saida_cercada=_lista(f.get("saida_cercada")) or None,
        toca_alvo=bool(f.get("toca_alvo", False)),
        autorizacao=f.get("autorizacao"),
        lacunas=_lista(p.get("lacunas")),
        golden=[
            Caso(
                pergunta=str(g.get("pergunta", "")),
                esperado=str(g.get("esperado", "")),
                derivado_de=str(g.get("derivado_de", "")),
            )
            for g in (p.get("golden") or [])
        ],
        precisa=_lista(c.get("precisa")),
        idioma=str(a.get("idioma", "pt")),
        origem=str(caminho),
    )
    validar(spec)
    return spec
