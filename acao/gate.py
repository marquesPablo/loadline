"""O gate que a Action composite chama por último: decide o exit code do job.

nature: fix — decide se o JOB quebra, nunca se algo é bug; isso é do
código de saída de cada ferramenta, já decidido antes deste script rodar.

Por que isto é Python, e não mais um `if` dentro do YAML: a lógica de "qual
combinação de ferramentas reprova o job" é a única parte da Action com
RAMIFICAÇÃO de verdade — e YAML de Action não tem teste automatizado. Pôr a
decisão aqui deixa `autoteste.py` confirmá-la como qualquer outro mecanismo
deste projeto; o `action.yml` fica fino, só glue.

    python gate.py <falhar-em> <codigo-forja> <codigo-placar> <codigo-loadline>

`falhar-em` é `"nenhuma"` (nunca quebra o job — a primeira rodada é
diagnóstico) ou uma combinação separada por vírgula de `forja`, `placar`,
`loadline`. Cada código é 0/1/2 — o MESMO contrato nos três pontos de entrada
deste projeto (0 passa · 1 reprova · 2 recusa/não avaliável). Este script trata
qualquer código diferente de 0 como "essa ferramenta acusou algo".
"""

from __future__ import annotations

import sys

FERRAMENTAS = ("forja", "placar", "loadline")


class FerramentaDesconhecida(ValueError):
    """`falhar-em` citou algo fora de `forja`/`placar`/`loadline`/`nenhuma`."""


def decidir(falhar_em: str, codigos: dict[str, int]) -> int:
    """0 se o gate passa, 1 se alguma ferramenta pedida em `falhar-em` acusou algo."""
    if falhar_em.strip().lower() == "nenhuma":
        return 0

    pedidas = {f.strip() for f in falhar_em.split(",") if f.strip()}
    desconhecidas = pedidas - set(FERRAMENTAS)
    if desconhecidas:
        raise FerramentaDesconhecida(
            f"`falhar-em` cita {', '.join(sorted(desconhecidas))}, fora do vocabulário — "
            f"válidas: {', '.join(FERRAMENTAS)}, ou 'nenhuma'"
        )

    return 1 if any(codigos.get(f, 0) != 0 for f in pedidas) else 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 4:
        print("uso: gate.py <falhar-em> <codigo-forja> <codigo-placar> <codigo-loadline>", file=sys.stderr)
        return 2

    falhar_em, cf, cp, cl = argv
    try:
        codigos = {"forja": int(cf), "placar": int(cp), "loadline": int(cl)}
    except ValueError:
        print(f"⛔ código de saída não-numérico recebido: forja={cf!r} placar={cp!r} loadline={cl!r}", file=sys.stderr)
        return 2

    try:
        codigo = decidir(falhar_em, codigos)
    except FerramentaDesconhecida as exc:
        print(f"⛔ {exc}", file=sys.stderr)
        return 2

    if codigo:
        acusaram = [f for f in falhar_em.split(",") if codigos.get(f.strip(), 0) != 0]
        print(f"REPROVA — falhar-em={falhar_em!r}, e {', '.join(acusaram)} não voltou 0.")
    else:
        print(f"passa o gate declarado (falhar-em={falhar_em!r}) — codigos={codigos}")
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
