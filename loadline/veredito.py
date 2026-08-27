"""The verdict engine — what to do when the written and the measured disagree.

nature: fix — this module classifies and reports; it does not write to
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
            return "nothing to do"
        if self.veredito == FROZEN:
            return f"history, frozen because: {self.selo.reason}"
        if self.veredito == ARBITRATED:
            quem = self.selo.by or "?"
            if quem.strip() in ("?", ""):
                return "chosen, and nobody has signed it yet — fill in `by=`"
            derruba = self.selo.breaks
            return (
                f"chosen by {quem}"
                + (f"; changes if: {derruba}" if derruba else "; no `breaks=` — what would change this?")
            )
        if self.veredito == EXPIRED:
            return f"re-check and re-seal — nobody has looked at this for {self.detalhe}"
        if self.veredito == UNPROVEN:
            return "write a probe for this metric, or drop the number"
        if self.veredito == PROSE_DRIFT:
            return (
                "fix the SENTENCE, or name this quantity in the seal — re-sealing the "
                "comment alone leaves the wrong number in the text people read"
            )
        if self.natureza == "relation":
            return "STOP. A relation diverging is a defect — investigate before re-sealing"
        return "re-seal: a count diverging means someone wrote"

    def __str__(self) -> str:
        alvo = f"{self.selo.arquivo}:{self.selo.linha}"
        if self.veredito == PROSE_DRIFT:
            return (
                f"{self.veredito:<10} {alvo}  the sentence claims {self.escrito} · "
                f"the block's seal says {self.medido}  → {self.acao}"
            )
        if self.medido is None:
            return f"{self.veredito:<9} {alvo}  {self.metrica}={self.escrito}  → {self.acao}"
        return (
            f"{self.veredito:<9} {alvo}  {self.metrica}: "
            f"written={self.escrito} measured={self.medido}  → {self.acao}"
        )


def julgar(selo: Selo, hoje: date | None = None) -> list[Achado]:
    """Confronts a seal with today's disk. One finding per metric."""
    hoje = hoje or date.today()

    if selo.congelado:
        return [
            Achado(FROZEN, m, v, None, selo, selo.nature, selo.reason or "")
            for m, v in (selo.metricas or {"—": "—"}).items()
        ]

    if selo.arbitrado:
        # There is no probe, and there should not be: the number was chosen.
        # What is checked here is the DEADLINE — is the choice still valid, or
        # is it time for someone to re-choose? Without this the mark would be
        # the easy way out for every awkward number.
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
                    f"{idade} days (deadline: {selo.expires}) — expired choice, someone re-chooses",
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
                    f"{idade} days (deadline: {selo.expires})",
                )
            )
        else:
            achados.append(Achado(MATCHES, metrica, escrito, str(medido), selo, selo.nature))

    return achados


@dataclass
class Relatorio:
    """The evidence report of one run.

    It declares the DENOMINATOR: how many seals were read, how many metrics
    have no probe, and which files have no seal at all. A metric with no probe
    is never counted as green — not measured is not zero.
    """

    achados: list[Achado]
    arquivos_lidos: int = 0
    arquivos_sem_selo: list[str] = None  # type: ignore[assignment]
    malformados: list[str] = None  # type: ignore[assignment]
    especimes: list[str] = None  # type: ignore[assignment]
    #: Seals that declared `echo=no` and stayed out of the prose-vs-seal check.
    #: A DECLARED waiver is named in the report: it is the difference between an
    #: exception and a hole.
    dispensados_do_eco: list[str] = None  # type: ignore[assignment]
    #: LIST 3: numeric claims that no seal covers. They are SUSPECTS, not
    #: defects — a number nobody can verify is not a wrong number. It is this
    #: list that makes the first run worth something before the user writes a
    #: line of configuration.
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
        """List 1 — checked, and matches."""
        return [a for a in self.achados if a.verde]

    @property
    def nao_bate(self) -> list[Achado]:
        """List 2 — checked, and does NOT match."""
        return [a for a in self.achados if not a.verde]

    @property
    def reprova(self) -> bool:
        """Fails on ANYTHING that is not green — including expired.

        Expired fails on purpose. A right number that nobody has re-checked in
        a year is a number that has not been wrong yet, not a verified number.
        """
        return bool(self.malformados) or any(not a.verde for a in self.achados)

    @property
    def sem_denominador(self) -> bool:
        """Nothing fails, and still there is a claim that nobody can verify.

        This is the state that used to return `PASS` and exit code 0 — which
        was *not measured* turning into *zero* inside the tool that exists to
        forbid **not measured turning into zero**. A repository that never
        annotated anything is not approved; it is unmeasured.
        """
        return not self.reprova and bool(self.sem_prova_nenhuma)

    @property
    def codigo_de_saida(self) -> int:
        """0 green · 1 fail · 2 no denominator.

        The order is monotonic on purpose: failing beats having no denominator,
        because a known defect is worse than a known gap. The 2 exists so the CI
        of whoever adopts can tell *"your annotations are wrong"* from *"you
        have not annotated anything yet"*.
        """
        if self.reprova:
            return 1
        # Zero files read is `I did not look`, and `I did not look` is never
        # green. Without this line, `loadline ./docs` on a real empty folder —
        # or pointed at the wrong place — returned `PASS` with code 0: exactly
        # *not measured* turning into *zero*, inside the tool that exists to
        # forbid it.
        if not self.arquivos_lidos:
            return 2
        return 2 if self.sem_prova_nenhuma else 0

    @property
    def veredito_da_corrida(self) -> str:
        if self.reprova:
            return "FAIL"
        if not self.arquivos_lidos:
            return "NO DENOMINATOR — no file was read; check the path"
        return "NO DENOMINATOR" if self.sem_prova_nenhuma else "PASS"

    def resumo(self) -> str:
        linhas = [
            f"{len(self.achados)} metrics in {self.arquivos_lidos} files"
            f" · {len(self.arquivos_sem_selo)} files with no seal at all"
            f" · {len(self.sem_prova_nenhuma)} claims nobody verifies"
            f" · {len(self.especimes)} with a specimen region",
        ]
        for v in (MATCHES, DRIFTED, EXPIRED, UNPROVEN, FROZEN, ARBITRATED, PROSE_DRIFT):
            n = len(self.por(v))
            if n:
                linhas.append(f"  {v:<10} {n}")
        if self.defeitos:
            linhas.append(f"  ⚠️  {len(self.defeitos)} of RELATION — that is a defect, not a re-seal")
        if self.malformados:
            linhas.append(f"  ⛔ {len(self.malformados)} malformed seals")
        if self.dispensados_do_eco:
            linhas.append(
                f"  ◻️  {len(self.dispensados_do_eco)} seal(s) with `echo=no` — "
                "waived from the prose-vs-seal check, by declaration"
            )
        return "\n".join(linhas)
