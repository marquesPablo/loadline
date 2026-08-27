"""forge CLI: `python -m forja <spec.toml> [--saida DIR] [--conferir]`.

nature: fix — the output is always printed in full, including when the forge
REFUSES. A refusal that does not name the fix is an error; a refusal that names
the fix is the useful half of a compiler.

    python -m forja                          # survey: reads the agents you ALREADY have
    python -m forja --adotar                 # WRITES: one spec per agent read
    python -m forja exemplos/revisor-de-licenca.toml
    python -m forja exemplos/*.toml --saida build/
    python -m forja spec.toml --conferir     # does not write; exits 1 if stale
    python -m forja . --html report.html     # WRITES, on top of the terminal: self-contained page
    python -m forja . --baseline             # diff against .loadline-baseline.json
    python -m forja . --baseline --gravar    # WRITES the baseline with the current state
    python -m forja --explain V3             # explains a finding, citing LACUNAS.md live
    python -m forja repoA repoB repoC        # comparison: one table, several repositories
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import evidencia

from . import alvos, comparar as _comparar, conselho, explicar as _explicar, vistoria
from .baseline import ARQUIVO_PADRAO, diff, gravar, ler as ler_baseline
from .spec import Recusa, Spec, ler

CENSO_PADRAO = Path(__file__).resolve().parent.parent / "censo" / "ecossistema.json"


def _console_em_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError, OSError):
            pass


def compilar(spec: Spec, hoje: date | None = None) -> dict[str, str]:
    """spec → {relative path: content}. Deterministic: same spec, same bytes."""
    saida: dict[str, str] = {}
    for emitir in alvos.TODOS:
        caminho, conteudo = emitir(spec)
        saida[caminho] = conteudo
    caminho, conteudo = alvos.receita(spec, sorted(saida), hoje=hoje)
    saida[caminho] = conteudo
    return saida


def _escrever(raiz: Path, artefatos: dict[str, str]) -> None:
    for relativo, conteudo in sorted(artefatos.items()):
        alvo = raiz / relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")


def _stale(raiz: Path, artefatos: dict[str, str]) -> list[str]:
    fora = []
    for relativo, conteudo in sorted(artefatos.items()):
        alvo = raiz / relativo
        if not alvo.exists():
            fora.append(f"{relativo}: does not exist")
        elif alvo.read_text(encoding="utf-8") != conteudo:
            fora.append(f"{relativo}: diverges from the spec")
    return fora


def _vistoria(
    raiz: Path,
    *,
    adotar: bool,
    saida: Path,
    saida_explicita: bool,
    html: Path | None = None,
    baseline: bool = False,
    baseline_gravar: bool = False,
) -> int:
    """`python -m forja` with no argument: reads the agents that already exist."""
    hoje = date.today().isoformat()
    pasta = vistoria.achar_pasta(raiz)
    linhas: list[str] = []

    def emitir(texto: str = "") -> None:
        linhas.append(texto)
        print(texto)

    def fechar(codigo: int) -> int:
        if html is not None:
            html.write_text(evidencia.pagina("forja", str(raiz), hoje, linhas, codigo), encoding="utf-8")
            emitir(f"\nself-contained HTML report written to {html}")
        return codigo

    # ⚠️ A folder that does not exist is a REFUSAL, and never green. A typo in
    # the path must not leave a gate approving forever — it is *not measured*
    # turning into *zero*, at the entry point.
    if pasta is None:
        emitir(f"survey · {raiz} · on {hoje}")
        emitir("=" * vistoria.LARGURA)
        emitir("Did not find an agents folder here. Looked, in this order:")
        for relativo in vistoria.PASTAS:
            emitir(f"     {raiz / relativo}")
        emitir()
        emitir("REFUSED — I read nothing, and I will not return green for that.      (exit 2)")
        return fechar(2)

    roster = vistoria.ler_roster(pasta)
    if not roster:
        emitir(f"survey · {pasta} · on {hoje}")
        emitir("=" * vistoria.LARGURA)
        emitir("The folder exists and there is no agent inside it.")
        emitir()
        emitir("REFUSED — zero agents read is not zero defects.                 (exit 2)")
        return fechar(2)

    achados = vistoria.vistoriar(roster)
    for linha in vistoria.relatorio(roster, achados, pasta, hoje):
        emitir(linha)

    if baseline:
        raiz_projeto = vistoria.raiz_do_projeto(pasta)
        arquivo_baseline = raiz_projeto / ARQUIVO_PADRAO
        if baseline_gravar:
            gravar(arquivo_baseline, achados, hoje)
            emitir()
            emitir(f"wrote the baseline to {arquivo_baseline} — {sum(len(a.itens) for a in achados)} item(s).")
            emitir("The next run with `--baseline` (no `--gravar`) shows only what CHANGED.")
            return fechar(0)

        anterior = ler_baseline(arquivo_baseline)
        if anterior is None:
            emitir()
            emitir(f"REFUSED — there is no baseline at {arquivo_baseline}.            (exit 2)")
            emitir(f"  Write one with `python -m forja {raiz} --baseline --gravar`, and run again.")
            return fechar(2)

        novos, resolvidos = diff(anterior, achados)
        emitir()
        emitir(f"baseline from {anterior.gravado_em} · {len(novos)} new · {len(resolvidos)} resolved")
        if novos:
            emitir("⛔ NEW SINCE THE BASELINE")
            for item in novos:
                emitir(f"     {item}")
        if resolvidos:
            emitir("✅ RESOLVED SINCE THE BASELINE")
            for item in resolvidos:
                emitir(f"     {item}")
        emitir()
        if novos:
            emitir("FAIL — there is a new finding since the baseline.             (exit 1)")
            return fechar(1)
        emitir("PASS — nothing new since the baseline.                        (exit 0)")
        return fechar(0)

    if adotar:
        # ⚠️ The reader's spec is born next to THEIR agents, and not inside the
        # clone of this tool. Writing relative to the current directory looks
        # harmless until someone runs `forja /path/to/project --adotar` from
        # inside the clone: the specs land here, in a folder this repo's
        # `.gitignore` ignores, and disappear with no error. `--saida` still
        # wins when someone writes it out.
        destino = (saida if saida_explicita else vistoria.raiz_do_projeto(pasta) / "build") / "specs"
        destino.mkdir(parents=True, exist_ok=True)
        emitir()
        emitir(f"wrote {len(roster)} spec(s) in {destino}/ — one per agent read:")
        for lido in roster:
            arquivo = destino / f"{lido.slug}.toml"
            arquivo.write_text(vistoria.adotar(lido, hoje, arquivo), encoding="utf-8")
            emitir(f"  ✓ {arquivo}")
        emitir()
        emitir("  Each `?` is a hole that already existed in the agent and that nobody had")
        emitir("  anywhere to see. Fill it in, and run `python -m forja " + str(destino) + "/*.toml`.")

    emitir()
    if not achados:
        emitir("PASS — every agent read declares the six things.                (exit 0)")
        return fechar(0)
    emitir("FAIL                                                          (exit 1)")
    if not adotar:
        emitir()
        emitir("  `python -m forja --adotar` writes each one's spec from what is already")
        emitir("  there, with a `?` in every hole. Then the forge compiles the artifacts that")
        emitir("  are missing — including the hook that DENIES, which is the only one the runtime reads.")
    return fechar(1)


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(sys.argv[1:] if argv is None else argv)

    saida = Path("build")
    saida_explicita = "--saida" in argv
    if saida_explicita:
        i = argv.index("--saida")
        saida = Path(argv[i + 1])
        del argv[i : i + 2]

    conferir = "--conferir" in argv
    if conferir:
        argv.remove("--conferir")

    adotar_agentes = "--adotar" in argv
    if adotar_agentes:
        argv.remove("--adotar")

    html_arg: Path | None = None
    if "--html" in argv:
        i = argv.index("--html")
        html_arg = Path(argv[i + 1])
        del argv[i : i + 2]

    baseline_arg = "--baseline" in argv
    if baseline_arg:
        argv.remove("--baseline")

    baseline_gravar = "--gravar" in argv
    if baseline_gravar:
        argv.remove("--gravar")

    if "--explain" in argv:
        i = argv.index("--explain")
        if i + 1 >= len(argv):
            print(_explicar.__doc__.strip().splitlines()[0])
            print(f"Valid findings: {', '.join(_explicar.CODIGOS)}")
            return 2
        regra = argv[i + 1]
        del argv[i : i + 2]
        try:
            for linha in _explicar.explicar(regra):
                print(linha)
        except _explicar.RegraDesconhecida as exc:
            print(f"REFUSED — {exc}                                          (exit 2)")
            return 2
        return 0

    especes = [Path(a) for a in argv if not a.startswith("-")]

    # With no argument at all, the forge does NOT print help: it looks at what
    # you already have. Nobody with twelve hand-written agents is going to write
    # twelve specs on faith to find out whether it was worth it — the annotation
    # is the output of the first run, never its toll.
    # A directory is always a survey; a `.toml` is always a compile. The
    # argument says which of the two directions you want, and you never have to
    # remember a flag.
    #
    # Two or more targets, NONE a `.toml`, is COMPARISON mode: each one is
    # surveyed, and the result comes out in one table — never again the old
    # (and never documented) behavior of surveying only the first and SWALLOWING
    # the rest silently.
    if len(especes) >= 2 and all(e.suffix != ".toml" for e in especes):
        faltando = [e for e in especes if not e.exists()]
        if faltando:
            print(f"forja · comparison of {len(especes)} repository(ies) · on {date.today().isoformat()}")
            print("=" * vistoria.LARGURA)
            for e in faltando:
                print(f"`{e}` does not exist.")
            print()
            print("REFUSED — I read nothing, and I will not return green for that.      (exit 2)")
            return 2

        resultados = _comparar.comparar(especes)
        linhas = _comparar.relatorio(resultados, date.today().isoformat())
        for linha in linhas:
            print(linha)
        codigo = _comparar.codigo_de_saida(resultados)
        if html_arg is not None:
            alvo_html = ", ".join(str(e) for e in especes)
            html_arg.write_text(evidencia.pagina("forja", alvo_html, date.today().isoformat(), linhas, codigo), encoding="utf-8")
            print(f"\nself-contained HTML report written to {html_arg}")
        return codigo

    # ⚠️ A target that does not exist is a REFUSAL, never anything else — and
    # this bug was born again here after already being fixed in the scanner:
    # without this line, `forja ./agentez` fell into the compile, died reading
    # the spec and returned 1. The `1` says «your spec is wrong»; the `2` says
    # «I read nothing». A CI typo leaning on the wrong code is not-measured
    # turning into zero.
    if especes and not especes[0].exists():
        print(f"forja · {especes[0]} · on {date.today().isoformat()}")
        print("=" * vistoria.LARGURA)
        print(f"`{especes[0]}` does not exist — neither as an agents folder, nor as a spec.")
        print()
        print("REFUSED — I read nothing, and I will not return green for that.      (exit 2)")
        return 2

    aponta_pasta = bool(especes) and especes[0].is_dir()
    if adotar_agentes or not especes or aponta_pasta or baseline_arg:
        return _vistoria(
            especes[0] if aponta_pasta else Path("."),
            adotar=adotar_agentes,
            saida=saida,
            saida_explicita=saida_explicita,
            html=html_arg,
            baseline=baseline_arg,
            baseline_gravar=baseline_gravar,
        )

    censo = conselho.carregar(CENSO_PADRAO)
    problemas = 0

    for caminho in especes:
        print(f"forja · {caminho}")
        print("=" * 72)
        try:
            spec = ler(caminho)
        except Recusa as recusa:
            print(f"⛔ REFUSED  {recusa}")
            print()
            print("   The forge fails closed. What it cannot decide, it does not emit —")
            print("   an agent compiler that emits anyway ships the ungated agent it")
            print("   existed to prevent.")
            print()
            problemas += 1
            continue
        except (OSError, ValueError) as exc:
            print(f"⛔ could not read the spec: {type(exc).__name__}: {exc}")
            print()
            problemas += 1
            continue

        artefatos = compilar(spec)
        raiz = saida / spec.slug

        if conferir:
            fora = _stale(raiz, artefatos)
            if fora:
                print(f"STALE  {len(fora)} artifact(s) diverge from `{caminho}`:")
                for linha in fora:
                    print(f"  {linha}")
                problemas += 1
            else:
                print(f"up to date  {len(artefatos)} artifacts match the spec")
        else:
            _escrever(raiz, artefatos)
            for relativo in sorted(artefatos):
                print(f"  ✓ {raiz / relativo}")

        print()
        print(f"  boundary: network={spec.usa_rede} write={spec.usa_escrita} "
              f"execution={spec.usa_execucao} touches_target={spec.toca_alvo}")
        print(f"  golden: {len(spec.golden)} case(s) · gaps declared: {len(spec.lacunas)}")
        if spec.desconhecidas:
            print(f"  ⚠️  tools the guard does not classify: {', '.join(spec.desconhecidas)}")

        bloco = conselho.em_markdown(spec.precisa, censo, str(CENSO_PADRAO))
        if bloco:
            print()
            print(bloco)
        print()

    if problemas:
        print(f"FAIL — {problemas} spec(s) refused or stale")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
