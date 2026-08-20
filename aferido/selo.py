"""Leitura e escrita de selos — a gramática de uma afirmação que se reconfere.

aferido-ignorar-arquivo: este arquivo ENSINA a sintaxe, e os selos escritos
aqui são espécimes, não afirmações. Sem esta linha o módulo lê a própria
documentação como se ela declarasse fatos — e o exemplo de selo MALFORMADO,
que precisa poder existir escrito, derrubaria a rodada.

natureza: correcao — este módulo só lê texto e devolve estrutura. Ele não
decide nada de segurança, e exceção aqui libera e avisa em vez de barrar.

Um selo é um comentário legível por máquina, colado à afirmação que ele cobre:

    Seis projetos independentes usam o nome AgentGuard.
    <!-- aferido: colisao.agentguard=6 natureza=contagem em=2026-08-16 vence=90d -->

Chaves reservadas (não são métrica):

    natureza  contagem | relacao   — decide o QUE significa divergir
    em        AAAA-MM-DD           — quando foi conferido pela última vez
    vence     Nd | Nm | nunca      — validade; sem isto o selo nunca expira
    fonte     caminho ou URL       — de onde a métrica é recomputada
    motivo    texto                — obrigatório em `congelado:`
    eco       nao                  — dispensa o bloco do confronto prosa × selo

Todo o resto é `metrica=valor`, e é isso que o verificador recomputa.

A diferença entre `contagem` e `relacao` é o coração da coisa, e ela foi
aprendida caro antes deste projeto: grandeza de CONTAGEM anda quando alguém
escreve — divergir é normal, resele e siga. Grandeza de RELAÇÃO só anda se o
medidor ou o corpus quebrou — divergir é DEFEITO, e resselar esconde o bug.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

RESERVADAS = frozenset({"natureza", "em", "vence", "fonte", "motivo", "eco"})
NATUREZAS = frozenset({"contagem", "relacao"})

# `<!-- aferido: ... -->` em Markdown/HTML, `# aferido: ...` em código.
_PADRAO = re.compile(
    r"(?:<!--|#|//)\s*(?P<tipo>aferido|congelado)\s*:\s*(?P<corpo>.*?)\s*(?:-->|$)",
    re.IGNORECASE,
)

# `chave=valor` ou `chave="valor com espaço"`.
_PAR = re.compile(r'(?P<k>[\w.\-]+)\s*=\s*(?:"(?P<qv>[^"]*)"|(?P<v>\S+))')

_DURACAO = re.compile(r"^(?P<n>\d+)(?P<u>[dm])$")


class SeloMalformado(ValueError):
    """O selo existe mas não se deixa ler. Nunca vira 'sem selo'."""


@dataclass(frozen=True)
class Selo:
    """Um selo lido do disco, com a linha de onde ele saiu."""

    tipo: str  # "aferido" | "congelado"
    metricas: dict[str, str]
    natureza: str | None = None
    em: date | None = None
    vence: str | None = None
    fonte: str | None = None
    motivo: str | None = None
    eco: str | None = None
    arquivo: str = ""
    linha: int = 0
    bruto: str = ""

    @property
    def congelado(self) -> bool:
        return self.tipo == "congelado"

    def vencido_em(self, hoje: date) -> bool:
        """Vencimento é do selo, não do valor.

        Um selo pode estar com o número CERTO e ainda assim vencido: ninguém
        reconferiu dentro do prazo que o próprio selo declarou. É a metade que
        falta em toda lista `awesome-*` — elas envelhecem sem nunca reprovar.
        """
        prazo = self.prazo()
        if prazo is None or self.em is None:
            return False
        return hoje > self.em + prazo

    def prazo(self) -> timedelta | None:
        """`90d` -> 90 dias. `6m` -> 180 dias. `nunca` / ausente -> None."""
        if not self.vence or self.vence.lower() == "nunca":
            return None
        m = _DURACAO.match(self.vence.strip())
        if not m:
            raise SeloMalformado(
                f"{self.arquivo}:{self.linha}: `vence={self.vence}` não é `Nd`, `Nm` nem `nunca`"
            )
        n = int(m.group("n"))
        return timedelta(days=n if m.group("u") == "d" else n * 30)

    def idade_dias(self, hoje: date) -> int | None:
        return None if self.em is None else (hoje - self.em).days


def _data(bruta: str, onde: str) -> date:
    try:
        return date.fromisoformat(bruta)
    except ValueError as exc:
        raise SeloMalformado(f"{onde}: `em={bruta}` não é uma data AAAA-MM-DD") from exc


def ler_linha(texto: str, arquivo: str = "", linha: int = 0) -> Selo | None:
    """Lê UM selo de uma linha. Devolve None se não houver selo nenhum."""
    m = _PADRAO.search(texto)
    if not m:
        return None

    onde = f"{arquivo}:{linha}"
    corpo = m.group("corpo")
    campos: dict[str, str] = {}
    for par in _PAR.finditer(corpo):
        valor = par.group("qv")
        campos[par.group("k").lower()] = valor if valor is not None else par.group("v")

    if not campos:
        raise SeloMalformado(f"{onde}: selo sem nenhum `chave=valor`")

    metricas = {k: v for k, v in campos.items() if k not in RESERVADAS}
    tipo = m.group("tipo").lower()

    natureza = campos.get("natureza")
    if natureza is not None and natureza not in NATUREZAS:
        raise SeloMalformado(
            f"{onde}: `natureza={natureza}` fora do vocabulário fechado {sorted(NATUREZAS)}"
        )
    if tipo == "aferido" and metricas and natureza is None:
        raise SeloMalformado(
            f"{onde}: selo com métrica precisa declarar `natureza=contagem` ou `natureza=relacao` "
            "— sem isso ninguém sabe se divergir quer dizer 'resele' ou 'investigue'"
        )
    if tipo == "congelado" and not campos.get("motivo"):
        raise SeloMalformado(
            f"{onde}: `congelado:` exige `motivo=\"...\"` — congelar sem dizer por quê "
            "é o mesmo que apagar a medida"
        )

    return Selo(
        tipo=tipo,
        metricas=metricas,
        natureza=natureza,
        em=_data(campos["em"], onde) if "em" in campos else None,
        vence=campos.get("vence"),
        fonte=campos.get("fonte"),
        motivo=campos.get("motivo"),
        eco=campos.get("eco"),
        arquivo=arquivo,
        linha=linha,
        bruto=m.group(0),
    )


def ler_texto(texto: str, arquivo: str = "") -> list[Selo]:
    """Todos os selos de um texto, na ordem em que aparecem."""
    achados: list[Selo] = []
    for n, linha in enumerate(texto.splitlines(), start=1):
        selo = ler_linha(linha, arquivo=arquivo, linha=n)
        if selo is not None:
            achados.append(selo)
    return achados


def escrever(selo: Selo, **mudancas: object) -> str:
    """Devolve o texto de um selo com campos trocados — para o resselo.

    Reescreve o selo INTEIRO a partir da estrutura. Editar o comentário com
    replace de string é como se perde a metade do par: mexe-se no cabeçalho e
    esquece-se a prosa, ou o contrário.
    """
    metricas = dict(selo.metricas)
    reservadas = {
        "natureza": selo.natureza,
        "em": selo.em.isoformat() if selo.em else None,
        "vence": selo.vence,
        "fonte": selo.fonte,
        "motivo": selo.motivo,
    }
    for chave, valor in mudancas.items():
        alvo = reservadas if chave in RESERVADAS else metricas
        alvo[chave] = None if valor is None else str(valor)

    partes = [f"{k}={v}" for k, v in metricas.items() if v is not None]
    for chave in ("natureza", "em", "vence", "fonte"):
        if reservadas.get(chave) is not None:
            partes.append(f"{chave}={reservadas[chave]}")
    if reservadas.get("motivo") is not None:
        partes.append(f'motivo="{reservadas["motivo"]}"')

    return f"<!-- {selo.tipo}: {' '.join(partes)} -->"
