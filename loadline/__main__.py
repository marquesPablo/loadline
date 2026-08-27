"""CLI: `python -m loadline <path>` — the evidence report of one run.

nature: fix — the output is always printed in full, even when it
fails. A report that only shows up when it passes is not evidence.

    python -m loadline .              # scans the project
    python -m loadline README.md      # scans one file
    python -m loadline . --sondas     # shows where each probe reads its value
    python -m loadline . --selar      # WRITES: annotates what nobody can verify
    python -m loadline . --html report.html  # WRITES, on top of the terminal
    python -m loadline . --hoje 2027-01-01   # simulates the future; this is how
                                             # you prove that expiry fails

Every run returns THREE lists, and the third is what makes the first run worth
something in a repository that never annotated anything:

    ✅ checked and matches       what a probe recomputed
    ❌ checked and does NOT match  drifted, expired, no probe, prose drift
    ⚠️  nobody verifies this      a claim that no seal covers — SUSPECT

Exit code: 0 all green · 1 fail · 2 no denominator (nothing fails, and there
is a claim nobody can verify). The 2 separates *"your annotations are wrong"*
from *"you have not annotated anything yet"* — and before it both returned 0,
which was not-measured turning into zero inside the tool that exists to
forbid exactly that.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import evidencia

from .registro import explicar
from .selar import selar
from .varredura import carregar_sondas, varrer
from .veredito import ARBITRATED, FROZEN, DRIFTED, PROSE_DRIFT, UNPROVEN, MATCHES, EXPIRED

ORDEM = (DRIFTED, PROSE_DRIFT, EXPIRED, UNPROVEN, FROZEN, ARBITRATED, MATCHES)


def _console_em_utf8() -> None:
    """The Windows console opens in cp1252 and blows up on `→`, `←`, `⚠️`.

    An evidence report that dies over an arrow is not evidence. Reconfigure
    fails open: if the stream will not take it, we carry on with what we get.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(sys.argv[1:] if argv is None else argv)

    hoje = date.today()
    if "--hoje" in argv:
        i = argv.index("--hoje")
        hoje = date.fromisoformat(argv[i + 1])
        del argv[i : i + 2]

    mostrar_sondas = "--sondas" in argv
    if mostrar_sondas:
        argv.remove("--sondas")

    escrever_selos = "--selar" in argv
    if escrever_selos:
        argv.remove("--selar")

    html_arg: Path | None = None
    if "--html" in argv:
        i = argv.index("--html")
        html_arg = Path(argv[i + 1])
        del argv[i : i + 2]

    alvo = argv[0] if argv else "."
    linhas: list[str] = []

    def emitir(texto: str = "") -> None:
        linhas.append(texto)
        print(texto)

    def fechar(codigo: int) -> int:
        if html_arg is not None:
            html_arg.write_text(evidencia.pagina("loadline", alvo, hoje.isoformat(), linhas, codigo), encoding="utf-8")
            emitir(f"\nself-contained HTML report written to {html_arg}")
        return codigo

    # ⚠️ A path that does not exist is a REFUSAL, never `PASS`.
    #
    # Without this, `loadline ./sr` (for `./src`) scanned zero files, found no
    # claims, and exited **green with code 0** — a typo in CI left the gate
    # approving forever. It is exactly *not measured* turning into *zero*, at
    # the entry point of the tool whose whole thesis is that this must not
    # happen. An unknown flag lands here the same way: it is read as a path,
    # and no path called `--sondaz` exists.
    caminho_do_alvo = Path(alvo)
    if not caminho_do_alvo.exists():
        emitir(f"loadline · {alvo} · on {hoje.isoformat()}")
        emitir("=" * 72)
        if alvo.startswith("-"):
            emitir(f"`{alvo}` is not a known flag, and does not exist as a path.")
            emitir("Flags: --selar · --sondas · --html FILE · --hoje YYYY-MM-DD")
        else:
            emitir(f"`{alvo}` does not exist.")
        emitir()
        emitir("REFUSED — I scanned nothing, and I will not return green for that.   (exit 2)")
        return fechar(2)

    usado = carregar_sondas(caminho_do_alvo)
    if mostrar_sondas:
        emitir(f"probes loaded from: {usado or '(no sondas.py found)'}")
        for padrao, origem in explicar():
            emitir(f"  {padrao:<28} ← {origem}")
        emitir()

    relatorio = varrer(alvo, hoje=hoje)

    emitir(f"loadline · {alvo} · on {hoje.isoformat()}")
    emitir("=" * 72)
    for veredito in ORDEM:
        for achado in relatorio.por(veredito):
            emitir(str(achado))
    for problema in relatorio.malformados:
        emitir(f"MALFORMED {problema}")

    if relatorio.sem_prova_nenhuma:
        emitir()
        emitir("⚠️  NOBODY CAN VERIFY THIS — these are suspects, not defects.")
        emitir("    A number nobody verifies is not a wrong number; it is a number")
        emitir("    this tool has nothing to say about. `--selar` annotates all of them.")
        for afirmacao in relatorio.sem_prova_nenhuma:
            emitir(f"      {afirmacao}")

    emitir("-" * 72)
    emitir(str(relatorio.resumo()))

    if relatorio.defeitos:
        emitir()
        emitir("⚠️  A RELATION divergence is not re-sealed. It only moves if the meter or")
        emitir("    the corpus broke — re-sealing here hides the defect, it does not fix it:")
        for achado in relatorio.defeitos:
            emitir(f"      {achado.selo.arquivo}:{achado.selo.linha}  {achado.metrica}")

    if escrever_selos:
        escritos, problemas = selar(relatorio.sem_prova_nenhuma, hoje=hoje)
        emitir()
        if escritos:
            arquivos = len({e.arquivo for e in escritos})
            emitir(
                f"wrote {len(escritos)} seal(s) in {arquivos} file(s), all as "
                "`arbitrated:` — nobody has measured anything yet."
            )
            for e in escritos:
                emitir(f"  {e.arquivo}:{e.linha}  {e.texto}")
            emitir()
            emitir("  Now replace each `by=?` with whoever chose the number, and rename the")
            emitir("  metric if the name I guessed is not right — it came from the word next")
            emitir("  to the number, not from understanding what it means.")
        else:
            emitir("nothing to seal: either there is no unverified claim, or the spot already has a seal.")
        for problema in problemas:
            emitir(f"  ⛔ {problema}")

    emitir()
    emitir(str(relatorio.veredito_da_corrida))
    return fechar(relatorio.codigo_de_saida)


if __name__ == "__main__":
    raise SystemExit(main())
