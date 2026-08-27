"""The verdict engine — what to do when the written and the measured disagree.

natureza: correcao — this module classifies and reports; it does not write to
disk and fixes nothing. Accusing without fixing is the contract.

Seven verdicts, and the vocabulary is closed on purpose:

    MATCHES      written == measured, and within the deadline.
    DRIFTED      written != measured. What to do depends on `nature`:
                   count    -> someone wrote. Re-seal and move on.
                   relation -> DEFECT. Investigate BEFORE re-sealing.
    EXPIRED      past `expires`, even with the value matching. Nobody
                 re-checked; the number may be right by accident.
    UNPROVEN     there is no probe for the metric. Never turns green.
    FROZEN       declared history, with a reason. Does not recompute.
    ARBITRATED   number CHOSEN, with a declared owner and within the deadline.
                 Nobody measured, and nobody will — but someone signed it.
    PROSE_DRIFT  the SENTENCE claims a number that no seal in the block covers.

Three are green: `MATCHES`, `FROZEN` and `ARBITRATED`. The three say different
things about the same line — *I measured*, *this is history*, *I chose* — and it
is the distinction between them that makes the report worth more than a boolean.

`DRIFTED` alone says nothing. It is the pair (verdict, nature) that says, and
that is why `nature` is required on a seal with a metric.

`PROSE_DRIFT` is the verdict that closes the hole the other five left: they all
look at the VALUE inside the comment, and none looked at the SENTENCE next to
it. Whoever re-seals touches the comment — which is what fails — and forgets the
text, which is what people read. This project went green for four days with `36`
in the seal and `33` on the line above. See `eco.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from . import registro
from .selo import Selo, SeloMalformado

MATCHES = "MATCHES"
DRIFTED = "DRIFTED"
EXPIRED = "EXPIRED"
UNPROVEN = "UNPROVEN"
FROZEN = "FROZEN"
ARBITRATED = "ARBITRATED"
PROSE_DRIFT = "PROSE_DRIFT"

VERDES = frozenset({MATCHES, FROZEN, ARBITRATED})


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
        """A RELATION divergence is a bug. A count divergence is not."""
        return self.veredito == DRIFTED and self.natureza == "relation"

    @property
    def acao(self) -> str:
        if self.veredito == MATCHES:
            return "nada a fazer"
        if self.veredito == FROZEN:
            return f"histórico, congelado por: {self.selo.reason}"
        if self.veredito == ARBITRATED:
            quem = self.selo.by or "?"
            if quem.strip() in ("?", ""):
                return "escolhido, e ninguém assinou ainda — preencha `by=`"
            derruba = self.selo.breaks
            return (
                f"escolhido por {quem}"
                + (f"; muda se: {derruba}" if derruba else "; sem `breaks=` — o que mudaria isto?")
            )
        if self.veredito == EXPIRED:
            return f"reconfira e resele — ninguém olha isto há {self.detalhe}"
        if self.veredito == UNPROVEN:
            return "escreva uma sonda para esta métrica, ou tire o número"
        if self.veredito == PROSE_DRIFT:
            return (
                "corrija a FRASE, ou nomeie esta grandeza no selo — resselar o "
                "comentário sozinho deixa o número errado no texto que se lê"
            )
        if self.natureza == "relation":
            return "PARE. Relação divergindo é defeito — investigue antes de resselar"
        return "resele: contagem divergindo quer dizer que alguém escreveu"

    def __str__(self) -> str:
        alvo = f"{self.selo.arquivo}:{self.selo.linha}"
        if self.veredito == PROSE_DRIFT:
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
            Achado(FROZEN, m, v, None, selo, selo.nature, selo.reason or "")
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
                Achado(UNPROVEN, m, v, None, selo, selo.nature, str(exc))
                for m, v in (selo.metricas or {"—": "—"}).items()
            ]
        if expirou:
            idade = selo.idade_dias(hoje)
            return [
                Achado(
                    EXPIRED, m, v, None, selo, selo.nature,
                    f"{idade} dias (prazo: {selo.expires}) — escolha vencida, alguém reescolhe",
                )
                for m, v in (selo.metricas or {"—": "—"}).items()
            ]
        return [
            Achado(ARBITRATED, m, v, None, selo, selo.nature, selo.by or "")
            for m, v in (selo.metricas or {"—": "—"}).items()
        ]

    achados: list[Achado] = []
    for metrica, escrito in selo.metricas.items():
        try:
            medido = registro.medir(metrica, selo)
        except registro.SemSonda as exc:
            achados.append(Achado(UNPROVEN, metrica, escrito, None, selo, selo.nature, str(exc)))
            continue
        except Exception as exc:  # sonda quebrada nunca passa como verde
            achados.append(
                Achado(
                    UNPROVEN,
                    metrica,
                    escrito,
                    None,
                    selo,
                    selo.nature,
                    f"a sonda estourou: {type(exc).__name__}: {exc}",
                )
            )
            continue

        if str(medido).strip() != escrito.strip():
            achados.append(Achado(DRIFTED, metrica, escrito, str(medido), selo, selo.nature))
            continue

        try:
            expirou = selo.vencido_em(hoje)
        except SeloMalformado as exc:
            achados.append(Achado(UNPROVEN, metrica, escrito, str(medido), selo, selo.nature, str(exc)))
            continue

        if expirou:
            idade = selo.idade_dias(hoje)
            achados.append(
                Achado(
                    EXPIRED,
                    metrica,
                    escrito,
                    str(medido),
                    selo,
                    selo.nature,
                    f"{idade} dias (prazo: {selo.expires})",
                )
            )
        else:
            achados.append(Achado(MATCHES, metrica, escrito, str(medido), selo, selo.nature))

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
    #: Selos que declararam `echo=no` e ficaram fora do confronto prosa × selo.
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

        Este é o estado que devolvia `PASSA` e código de saída 0 —
        e era *não medido* virando *zero* dentro da ferramenta que existe
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
        # Zero arquivo lido é `não olhei`, e `não olhei` nunca é verde. Sem esta
        # linha, `loadline ./docs` numa pasta real e vazia — ou apontada para o
        # lugar errado — devolvia `PASSA` com código 0: exatamente *não medido*
        # virando *zero*, dentro da ferramenta que existe para proibir isso.
        if not self.arquivos_lidos:
            return 2
        return 2 if self.sem_prova_nenhuma else 0

    @property
    def veredito_da_corrida(self) -> str:
        if self.reprova:
            return "REPROVA"
        if not self.arquivos_lidos:
            return "SEM DENOMINADOR — nenhum arquivo foi lido; confira o caminho"
        return "SEM DENOMINADOR" if self.sem_prova_nenhuma else "PASSA"

    def resumo(self) -> str:
        linhas = [
            f"{len(self.achados)} métricas em {self.arquivos_lidos} arquivos"
            f" · {len(self.arquivos_sem_selo)} arquivos sem selo nenhum"
            f" · {len(self.sem_prova_nenhuma)} afirmações que ninguém confere"
            f" · {len(self.especimes)} com região de espécime",
        ]
        for v in (MATCHES, DRIFTED, EXPIRED, UNPROVEN, FROZEN, ARBITRATED, PROSE_DRIFT):
            n = len(self.por(v))
            if n:
                linhas.append(f"  {v:<10} {n}")
        if self.defeitos:
            linhas.append(f"  ⚠️  {len(self.defeitos)} de RELAÇÃO — isso é defeito, não resselo")
        if self.malformados:
            linhas.append(f"  ⛔ {len(self.malformados)} selos malformados")
        if self.dispensados_do_eco:
            linhas.append(
                f"  ◻️  {len(self.dispensados_do_eco)} selo(s) com `echo=no` — "
                "dispensados do confronto prosa × selo, por declaração"
            )
        return "\n".join(linhas)
