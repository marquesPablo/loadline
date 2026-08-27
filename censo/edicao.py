"""Generates a dated, recurring census edition — `censo/edicoes/YYYY-MM-DD.md`.

nature: fix — this generator only reads `ecossistema.json` and the snapshots
already written to `censo/edicoes/*.json`. It does no network, it decides
nothing about security; an error here becomes a visible exception, never a
half-written edition.

`censo/gerar.py` answers "does the published `CENSO.md` still match the
source?" — an INTEGRITY question, about an artifact that changes every time
someone edits `ecossistema.json`. This file answers a different question, on a
different axis: "what changed in the ecosystem since the last time someone
looked?" — a series over time, not a mirror of the present.

Each edition writes TWO files, never just one:

    censo/edicoes/YYYY-MM-DD.json   # the raw snapshot — what the NEXT edition reads to diff
    censo/edicoes/YYYY-MM-DD.md     # the publishable reading — what a human reads

⚠️ **Why the `.json` exists, and not just the `.md`.** Diffing two editions by
reading the previous `.md`'s text would be the same class of error the core's
`LACUNAS.md` already names for `arbitrado:` — pulling a number out of prose is
fragile and shifts meaning with any rewording. The `.json` is the source the
NEXT run reads; the `.md` is just that run's window, and it is never read back.

    python censo/edicao.py             # writes today's edition
    python censo/edicao.py --conferir  # does not write; exits 1 if today already has an edition
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "censo" / "ecossistema.json"
PASTA_EDICOES = RAIZ / "censo" / "edicoes"

ESTAGIO_SEM_CLASSE = "sem_estagio_classificado"


def _carregar_fonte() -> dict:
    return json.loads(FONTE.read_text(encoding="utf-8"))


def _snapshot(censo: dict) -> dict:
    """Reduces today's census to the numbers an edition compares — never the
    whole entry of each project, which already lives in `ecossistema.json` and
    does not need a second copy aging in parallel."""
    projetos = censo["projetos"]
    por_estagio: dict[str, int] = {}
    for p in projetos:
        chave = p.get("estagio") or ESTAGIO_SEM_CLASSE
        por_estagio[chave] = por_estagio.get(chave, 0) + 1
    por_licenca: dict[str, int] = {}
    for p in projetos:
        chave = p.get("veredito_licenca") or "nao_verificado"
        por_licenca[chave] = por_licenca.get(chave, 0) + 1
    colisoes = sorted(p["nome"] for p in projetos if p.get("colide_com"))
    return {
        "total": len(projetos),
        "nomes": sorted(p["nome"] for p in projetos),
        "por_estagio": por_estagio,
        "por_licenca": por_licenca,
        "nomes_com_colisao": colisoes,
    }


def _edicoes_existentes() -> list[Path]:
    if not PASTA_EDICOES.exists():
        return []
    return sorted(PASTA_EDICOES.glob("*.json"))


def _edicao_anterior(hoje: date) -> dict | None:
    anteriores = [p for p in _edicoes_existentes() if p.stem < hoje.isoformat()]
    if not anteriores:
        return None
    return json.loads(anteriores[-1].read_text(encoding="utf-8"))


def _diferenca(hoje: dict, ontem: dict) -> list[str]:
    linhas: list[str] = []
    novos = sorted(set(hoje["nomes"]) - set(ontem["nomes"]))
    saidos = sorted(set(ontem["nomes"]) - set(hoje["nomes"]))
    delta_total = hoje["total"] - ontem["total"]
    linhas.append(f"**Total:** {ontem['total']} → {hoje['total']} ({delta_total:+d})")
    if novos:
        linhas.append(f"**Entered ({len(novos)}):** " + ", ".join(f"`{n}`" for n in novos))
    if saidos:
        linhas.append(
            f"**Left the file ({len(saidos)}):** " + ", ".join(f"`{n}`" for n in saidos)
        )
        linhas.append(
            "  ⚠️ left the `ecossistema.json` file — never read this as \"the project died\"; "
            "it may have been reclassified, merged, or removed by an editorial decision"
        )
    if not novos and not saidos and delta_total == 0:
        linhas.append("No new name, none removed, since the previous edition.")

    delta_colisao = len(hoje["nomes_com_colisao"]) - len(ontem["nomes_com_colisao"])
    if delta_colisao:
        linhas.append(
            f"**Colliding names:** {len(ontem['nomes_com_colisao'])} → "
            f"{len(hoje['nomes_com_colisao'])} ({delta_colisao:+d})"
        )

    estagios = sorted(set(hoje["por_estagio"]) | set(ontem["por_estagio"]))
    mudou_estagio = [
        (e, ontem["por_estagio"].get(e, 0), hoje["por_estagio"].get(e, 0))
        for e in estagios
        if ontem["por_estagio"].get(e, 0) != hoje["por_estagio"].get(e, 0)
    ]
    if mudou_estagio:
        linhas.append("**Stages whose count changed:**")
        for estagio, antes, agora in mudou_estagio:
            linhas.append(f"  - `{estagio}`: {antes} → {agora} ({agora - antes:+d})")
    return linhas


def gerar(hoje: date | None = None) -> tuple[Path, Path]:
    hoje = hoje or date.today()
    censo = _carregar_fonte()
    atual = _snapshot(censo)
    anterior = _edicao_anterior(hoje)
    numero = len(_edicoes_existentes()) + 1

    PASTA_EDICOES.mkdir(parents=True, exist_ok=True)
    caminho_json = PASTA_EDICOES / f"{hoje.isoformat()}.json"
    caminho_md = PASTA_EDICOES / f"{hoje.isoformat()}.md"

    caminho_json.write_text(
        json.dumps(atual, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )

    L: list[str] = []
    A = L.append
    A(f"# The state of the AI agent ecosystem — edition {numero}")
    A("")
    A(f"<!-- measured: censo.edicao={numero} nature=count on={hoje.isoformat()} expires=never source=censo/edicoes/ -->")
    A("")
    A(
        "Generated by `censo/edicao.py` from `censo/ecossistema.json` — no number here was "
        "written by hand. The full reading of each project is in [`CENSO.md`](../CENSO.md)."
    )
    A("")
    A(f"**{atual['total']} projects catalogued**, {len(atual['nomes_com_colisao'])} names " "identifying more than one independent project.")
    A("")
    if anterior is None:
        A("## First edition")
        A("")
        A(
            "There is no previous edition to compare against — this is the baseline. The next "
            "edition will be able to say what changed; this one can only say what exists today."
        )
    else:
        A("## What changed since the previous edition")
        A("")
        L.extend(_diferenca(atual, anterior))
    A("")
    A("## By stage, today")
    A("")
    A("| Stage | Projects |")
    A("|---|---:|")
    for estagio, contagem in sorted(atual["por_estagio"].items(), key=lambda kv: -kv[1]):
        A(f"| `{estagio}` | {contagem} |")
    A("")
    A(
        "**This is not an opinion about the ecosystem — it is today's count of a file anyone can "
        "re-check.** No entry here was cloned or run; see the denominator warning in `CENSO.md`."
    )
    caminho_md.write_text("\n".join(L) + "\n", encoding="utf-8")
    return caminho_json, caminho_md


def conferir() -> int:
    hoje = date.today()
    ja_existe = (PASTA_EDICOES / f"{hoje.isoformat()}.json").exists()
    if ja_existe:
        print(f"today's edition already exists ({hoje.isoformat()}) — run without --conferir to rewrite it")
        return 1
    print("no edition for today yet")
    return 0


if __name__ == "__main__":
    if "--conferir" in sys.argv:
        raise SystemExit(conferir())
    j, m = gerar()
    print(f"wrote {j.relative_to(RAIZ)} and {m.relative_to(RAIZ)}")
