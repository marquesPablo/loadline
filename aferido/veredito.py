"""O motor de veredito — o que fazer quando o escrito e o medido discordam.

natureza: correcao — este módulo classifica e relata; ele não escreve no
disco e não conserta nada. Acusar sem consertar é o contrato.

Sete vereditos, e o vocabulário é fechado de propósito:

    VALE        escrito == medido, e dentro do prazo.
    DERIVOU     escrito != medido. O que fazer depende da `natureza`:
                  contagem -> alguém escreveu. Resele e siga.
                  relacao  -> DEFEITO. Investigue ANTES de resselar.
    VENCIDO     passou do `vence`, mesmo com o valor batendo. Ninguém
                reconferiu; o número pode estar certo por acidente.
    SEM_PROVA   não há sonda para a métrica. Nunca vira verde.
    CONGELADO   histórico declarado, com motivo. Não se recomputa.
    ARBITRADO   número ESCOLHIDO, com dono declarado e dentro do prazo.
                Ninguém mediu, e ninguém vai medir — mas alguém assinou.
    PROSA_MUDA  a FRASE afirma um número que nenhum selo do bloco cobre.

Três são verdes: `VALE`, `CONGELADO` e `ARBITRADO`. Os três dizem coisas
diferentes sobre a mesma linha — *eu medi*, *isto é história*, *eu escolhi* — e
é a distinção entre eles que faz o relatório valer mais que um booleano.

`DERIVOU` sozinho não diz nada. É o par (veredito, natureza) que diz, e é por
isso que `natureza` é obrigatória em selo com métrica.

`PROSA_MUDA` é o veredito que fecha o buraco que os outros cinco deixavam: eles
todos olham o VALOR dentro do comentário, e nenhum olhava a FRASE ao lado dele.
Quem resela mexe no comentário — que é o que reprova — e esquece o texto, que é
o que a pessoa lê. Este projeto passou verde por quatro dias com `36` no selo e
`33` na linha de cima. Ver `eco.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from . import registro
from .selo import Selo, SeloMalformado

VALE = "VALE"
DERIVOU = "DERIVOU"
VENCIDO = "VENCIDO"
SEM_PROVA = "SEM_PROVA"
CONGELADO = "CONGELADO"
ARBITRADO = "ARBITRADO"
PROSA_MUDA = "PROSA_MUDA"

VERDES = frozenset({VALE, CONGELADO, ARBITRADO})


@dataclass(frozen=True)
class Achado:
    veredito: str
    metrica: str
    escrito: str
    medido: str | None
    selo: Selo
    natureza: str | None = None
    detalhe: str = ""

    @property
    def verde(self) -> bool:
        return self.veredito in VERDES

    @property
    def e_defeito(self) -> bool:
        """Divergência de RELAÇÃO é bug. Divergência de contagem não é."""
        return self.veredito == DERIVOU and self.natureza == "relacao"

    @property
    def acao(self) -> str:
        if self.veredito == VALE:
            return "nada a fazer"
        if self.veredito == CONGELADO:
            return f"histórico, congelado por: {self.selo.motivo}"
        if self.veredito == ARBITRADO:
            quem = self.selo.por or "?"
            if quem.strip() in ("?", ""):
                return "escolhido, e ninguém assinou ainda — preencha `por=`"
            derruba = self.selo.derruba
            return (
                f"escolhido por {quem}"
                + (f"; muda se: {derruba}" if derruba else "; sem `derruba=` — o que mudaria isto?")
            )
        if self.veredito == VENCIDO:
            return f"reconfira e resele — ninguém olha isto há {self.detalhe}"
        if self.veredito == SEM_PROVA:
            return "escreva uma sonda para esta métrica, ou tire o número"
        if self.veredito == PROSA_MUDA:
            return (
                "corrija a FRASE, ou nomeie esta grandeza no selo — resselar o "
                "comentário sozinho deixa o número errado no texto que se lê"
            )
        if self.natureza == "relacao":
            return "PARE. Relação divergindo é defeito — investigue antes de resselar"
        return "resele: contagem divergindo quer dizer que alguém escreveu"

    def __str__(self) -> str:
        alvo = f"{self.selo.arquivo}:{self.selo.linha}"
        if self.veredito == PROSA_MUDA:
            return (
                f"{self.veredito:<10} {alvo}  a frase afirma {self.escrito} · "
                f"o selo do bloco diz {self.medido}  → {self.acao}"
            )
        if self.medido is None:
            return f"{self.veredito:<9} {alvo}  {self.metrica}={self.escrito}  → {self.acao}"
        return (
            f"{self.veredito:<9} {alvo}  {self.metrica}: "
            f"escrito={self.escrito} medido={self.medido}  → {self.acao}"
        )


def julgar(selo: Selo, hoje: date | None = None) -> list[Achado]:
    """Confronta um selo com o disco de hoje. Um achado por métrica."""
    hoje = hoje or date.today()

    if selo.congelado:
        return [
            Achado(CONGELADO, m, v, None, selo, selo.natureza, selo.motivo or "")
            for m, v in (selo.metricas or {"—": "—"}).items()
        ]

    if selo.arbitrado:
        # Não há sonda, e não deve haver: o número foi escolhido. O que se
        # confere aqui é o PRAZO — a escolha continua valendo, ou já é hora de
        # alguém reescolher? Sem isto a marca viraria a saída fácil para todo
        # número incômodo.
        try:
            expirou = selo.vencido_em(hoje)
        except SeloMalformado as exc:
            return [
                Achado(SEM_PROVA, m, v, None, selo, selo.natureza, str(exc))
                for m, v in (selo.metricas or {"—": "—"}).items()
            ]
        if expirou:
            idade = selo.idade_dias(hoje)
            return [
                Achado(
                    VENCIDO, m, v, None, selo, selo.natureza,
                    f"{idade} dias (prazo: {selo.vence}) — escolha vencida, alguém reescolhe",
                )
                for m, v in (selo.metricas or {"—": "—"}).items()
            ]
        return [
            Achado(ARBITRADO, m, v, None, selo, selo.natureza, selo.por or "")
            for m, v in (selo.metricas or {"—": "—"}).items()
        ]

    achados: list[Achado] = []
    for metrica, escrito in selo.metricas.items():
        try:
            medido = registro.medir(metrica, selo)
        except registro.SemSonda as exc:
            achados.append(Achado(SEM_PROVA, metrica, escrito, None, selo, selo.natureza, str(exc)))
            continue
        except Exception as exc:  # sonda quebrada nunca passa como verde
            achados.append(
                Achado(
                    SEM_PROVA,
                    metrica,
                    escrito,
                    None,
                    selo,
                    selo.natureza,
                    f"a sonda estourou: {type(exc).__name__}: {exc}",
                )
            )
            continue

        if str(medido).strip() != escrito.strip():
            achados.append(Achado(DERIVOU, metrica, escrito, str(medido), selo, selo.natureza))
            continue

        try:
            expirou = selo.vencido_em(hoje)
        except SeloMalformado as exc:
            achados.append(Achado(SEM_PROVA, metrica, escrito, str(medido), selo, selo.natureza, str(exc)))
            continue

        if expirou:
            idade = selo.idade_dias(hoje)
            achados.append(
                Achado(
                    VENCIDO,
                    metrica,
                    escrito,
                    str(medido),
                    selo,
                    selo.natureza,
                    f"{idade} dias (prazo: {selo.vence})",
                )
            )
        else:
            achados.append(Achado(VALE, metrica, escrito, str(medido), selo, selo.natureza))

    return achados


@dataclass
class Relatorio:
    """O relatório de evidência de uma corrida.

    Ele declara o DENOMINADOR: quantos selos foram lidos, quantas métricas
    ficaram sem sonda, e quais arquivos não têm selo nenhum. Métrica sem sonda
    nunca é contada como verde — não medido não é zero.
    """

    achados: list[Achado]
    arquivos_lidos: int = 0
    arquivos_sem_selo: list[str] = None  # type: ignore[assignment]
    malformados: list[str] = None  # type: ignore[assignment]
    especimes: list[str] = None  # type: ignore[assignment]
    #: Selos que declararam `eco=nao` e ficaram fora do confronto prosa × selo.
    #: Dispensa DECLARADA sai nomeada no relatório: é a diferença entre uma
    #: exceção e um furo.
    dispensados_do_eco: list[str] = None  # type: ignore[assignment]
    #: A LISTA 3: afirmações numéricas que nenhum selo cobre. São SUSPEITAS, não
    #: defeitos — um número que ninguém consegue conferir não é um número errado.
    #: É esta lista que faz a primeira rodada valer alguma coisa antes de o
    #: usuário escrever uma linha de configuração.
    sem_prova_nenhuma: list = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.arquivos_sem_selo = self.arquivos_sem_selo or []
        self.malformados = self.malformados or []
        self.especimes = self.especimes or []
        self.dispensados_do_eco = self.dispensados_do_eco or []
        self.sem_prova_nenhuma = self.sem_prova_nenhuma or []

    def por(self, veredito: str) -> list[Achado]:
        return [a for a in self.achados if a.veredito == veredito]

    @property
    def defeitos(self) -> list[Achado]:
        return [a for a in self.achados if a.e_defeito]

    @property
    def bate(self) -> list[Achado]:
        """Lista 1 — conferido, e bate."""
        return [a for a in self.achados if a.verde]

    @property
    def nao_bate(self) -> list[Achado]:
        """Lista 2 — conferido, e NÃO bate."""
        return [a for a in self.achados if not a.verde]

    @property
    def reprova(self) -> bool:
        """Reprova com QUALQUER coisa que não seja verde — inclusive vencido.

        Vencido reprova de propósito. Um número certo que ninguém reconfere há
        um ano é um número que ainda não errou, não um número verificado.
        """
        return bool(self.malformados) or any(not a.verde for a in self.achados)

    @property
    def sem_denominador(self) -> bool:
        """Nada reprova, e mesmo assim há afirmação que ninguém consegue conferir.

        Este é o estado que devolvia `PASSA` e código de saída 0 até o ADR-107 —
        e era o `ADR-013` violado dentro da ferramenta que existe para cobrá-lo:
        **não medido virando zero**. Um repositório que nunca anotou nada não
        está aprovado; ele está por medir.
        """
        return not self.reprova and bool(self.sem_prova_nenhuma)

    @property
    def codigo_de_saida(self) -> int:
        """0 verde · 1 reprova · 2 sem denominador.

        A ordem é monotônica de propósito: reprovar ganha de não ter
        denominador, porque um defeito conhecido é pior que uma lacuna
        conhecida. O 2 existe para o CI de quem adota distinguir *"suas
        anotações estão erradas"* de *"você ainda não anotou nada"*.
        """
        if self.reprova:
            return 1
        return 2 if self.sem_prova_nenhuma else 0

    @property
    def veredito_da_corrida(self) -> str:
        if self.reprova:
            return "REPROVA"
        return "SEM DENOMINADOR" if self.sem_prova_nenhuma else "PASSA"

    def resumo(self) -> str:
        linhas = [
            f"{len(self.achados)} métricas em {self.arquivos_lidos} arquivos"
            f" · {len(self.arquivos_sem_selo)} arquivos sem selo nenhum"
            f" · {len(self.sem_prova_nenhuma)} afirmações que ninguém confere"
            f" · {len(self.especimes)} com região de espécime",
        ]
        for v in (VALE, DERIVOU, VENCIDO, SEM_PROVA, CONGELADO, ARBITRADO, PROSA_MUDA):
            n = len(self.por(v))
            if n:
                linhas.append(f"  {v:<10} {n}")
        if self.defeitos:
            linhas.append(f"  ⚠️  {len(self.defeitos)} de RELAÇÃO — isso é defeito, não resselo")
        if self.malformados:
            linhas.append(f"  ⛔ {len(self.malformados)} selos malformados")
        if self.dispensados_do_eco:
            linhas.append(
                f"  ◻️  {len(self.dispensados_do_eco)} selo(s) com `eco=nao` — "
                "dispensados do confronto prosa × selo, por declaração"
            )
        return "\n".join(linhas)
