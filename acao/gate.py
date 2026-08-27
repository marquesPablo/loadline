"""The gate the composite Action calls last: it decides the job's exit code.

nature: fix — it decides whether the JOB breaks, never whether something is a
bug; that is each tool's exit code, already decided before this script runs.

Why this is Python, and not one more `if` inside the YAML: the logic of "which
combination of tools fails the job" is the only part of the Action with real
BRANCHING — and an Action's YAML has no automated test. Putting the decision
here lets `autoteste.py` confirm it like any other mechanism in this project;
`action.yml` stays thin, just glue.

    python gate.py <fail-on> <forja-code> <placar-code> <loadline-code>

`fail-on` (still spelled `falhar-em` in `action.yml`) is `"nenhuma"` (never
breaks the job — the first run is diagnostic) or a comma-separated combination
of `forja`, `placar`, `loadline`. Each code is 0/1/2 — the SAME contract at the
three entry points of this project (0 pass · 1 fail · 2 refused/not evaluable).
This script treats any non-zero code as "that tool accused something".
"""

from __future__ import annotations

import sys

FERRAMENTAS = ("forja", "placar", "loadline")


class FerramentaDesconhecida(ValueError):
    """`fail-on` named something outside `forja`/`placar`/`loadline`/`nenhuma`."""


def decidir(falhar_em: str, codigos: dict[str, int]) -> int:
    """0 if the gate passes, 1 if a tool named in `fail-on` accused something."""
    if falhar_em.strip().lower() == "nenhuma":
        return 0

    pedidas = {f.strip() for f in falhar_em.split(",") if f.strip()}
    desconhecidas = pedidas - set(FERRAMENTAS)
    if desconhecidas:
        raise FerramentaDesconhecida(
            f"`fail-on` names {', '.join(sorted(desconhecidas))}, outside the vocabulary — "
            f"valid: {', '.join(FERRAMENTAS)}, or 'nenhuma'"
        )

    return 1 if any(codigos.get(f, 0) != 0 for f in pedidas) else 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 4:
        print("usage: gate.py <fail-on> <forja-code> <placar-code> <loadline-code>", file=sys.stderr)
        return 2

    falhar_em, cf, cp, cl = argv
    try:
        codigos = {"forja": int(cf), "placar": int(cp), "loadline": int(cl)}
    except ValueError:
        print(f"⛔ non-numeric exit code received: forja={cf!r} placar={cp!r} loadline={cl!r}", file=sys.stderr)
        return 2

    try:
        codigo = decidir(falhar_em, codigos)
    except FerramentaDesconhecida as exc:
        print(f"⛔ {exc}", file=sys.stderr)
        return 2

    if codigo:
        acusaram = [f for f in falhar_em.split(",") if codigos.get(f.strip(), 0) != 0]
        print(f"FAIL — fail-on={falhar_em!r}, and {', '.join(acusaram)} did not return 0.")
    else:
        print(f"passes the declared gate (fail-on={falhar_em!r}) — codes={codigos}")
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
