"""Generates `censo/CENSO.md` — the census reading surface — from `ecossistema.json`.

nature: fix — this generator only reads JSON and writes Markdown. It decides
nothing about security; an error here becomes a visible exception, never a
half-written artifact.

⚠️ **Why CENSO.md has almost no seal, and that is on purpose.**

It is a GENERATED ARTIFACT. Sealing every number in it would be a mirror check:
both sides would come from the same JSON, and the pair would pass green locking
the defect in instead of finding it. The right question for a derived artifact
is not *"is the number right?"* — it is **"does this artifact still match the
source?"**.

That is why CENSO.md carries **one** seal only, `censo.gerado_em_dia`, of
`nature=relation`: it does not move when someone writes to the census, it only
moves if someone edited the published one by hand or touched the source and did
not regenerate. Diverging there is a defect, and the verdict says stop — which
is the right reading for a published list that has fallen out of sync with the
data.

    python censo/gerar.py            # writes censo/CENSO.md
    python censo/gerar.py --conferir # does not write; exits 1 if it is stale
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "censo" / "ecossistema.json"
PUBLICADO = RAIZ / "censo" / "CENSO.md"

# Reading order, and it is an argument: an agent's life cycle, from what it
# understands to who attacks it. Alphabetical would hide which stage has an
# owner and which does not.
ESTAGIOS = [
    ("entendimento", "Understand the repository", "the agent reads the codebase before acting"),
    ("capacidade", "Have capability", "where the skill the agent does not yet have comes from"),
    ("memoria", "Have memory", "what survives the context wiped between sessions"),
    ("ontologia", "Know what is what", "entities, relations and where each fact came from"),
    ("runtime", "Run the loop", "what runs the agent, with sandbox and subagents"),
    ("controle", "Block at runtime", "the guard that decides what the agent does not do"),
    ("prova", "Prove it passed", "the evidence the human reads instead of the diff"),
    ("adversarial", "Attack", "who tries to break the agent on purpose"),
    ("aprendizado", "Learn from failure", "what turns failure into a fix"),
    ("ameaca", "The measured threat", "research, not a tool"),
]

ROTULO_LICENCA = {
    "osi": "✅ OSI",
    "osi_copyleft_forte": "⚠️ OSI, strong copyleft",
    "nao_osi": "⛔ not open source",
    "nao_verificado": "◻️ not verified",
}


def carregar() -> dict:
    return json.loads(FONTE.read_text(encoding="utf-8"))


def _linha_de_projeto(p: dict) -> str:
    alvo = p.get("repo") or (f"`{p['paper']}`" if p.get("paper") else "—")
    if alvo.startswith("http"):
        alvo = f"[{alvo.split('github.com/')[-1]}]({alvo})"
    colisao = len(p.get("colide_com") or [])
    marca_colisao = f"**{colisao + (1 if p.get('repo') else 0)}**" if colisao else "1"
    return (
        f"| **{p['nome']}** | {alvo} | {p.get('licenca', '—')} "
        f"| {ROTULO_LICENCA.get(p.get('veredito_licenca', ''), '◻️')} | {marca_colisao} |"
    )


def _ficha(p: dict) -> list[str]:
    linhas = [f"#### {p['nome']}", ""]
    if p.get("repo"):
        linhas.append(f"- **Repository:** {p['repo']}")
    else:
        linhas.append("- **Canonical repository:** ⛔ **does not exist** — see the collision section")
    if p.get("paper"):
        linhas.append(f"- **Paper:** `{p['paper']}`")
    linhas.append(
        f"- **License:** {p.get('licenca', '—')} — {ROTULO_LICENCA.get(p.get('veredito_licenca', ''), '◻️')}"
    )
    linhas.append(f"- **Does:** {p['faz']}")
    linhas.append(f"- **Depends on:** {p.get('dependencias', 'not verified')}")

    sem = []
    if p.get("sem_llm") is True:
        sem.append("no LLM in the path")
    if p.get("sem_embedding") is True:
        sem.append("no embedding")
    if p.get("custa_dinheiro") is True:
        sem.append("⚠️ **costs money** (API key or paid service)")
    if sem:
        linhas.append(f"- **Weight:** {' · '.join(sem)}")

    if p.get("alegacao_do_autor"):
        linhas.append(
            f"- **Author's claim** (not measured by this census): {p['alegacao_do_autor']}"
        )
    for campo, rotulo in (
        ("responde", "Answers"),
        ("nao_responde", "Does **not** answer"),
        ("achado_principal", "Main finding"),
        ("ressalva_do_proprio_paper", "The paper's own caveat"),
        ("consequencia_da_licenca", "License consequence"),
        ("ressalva_operacional", "Operational caveat"),
        ("nota", "Note"),
        ("nota_de_colisao", "About the collision count"),
        ("limite_desta_leitura", "Limit of this reading"),
    ):
        if p.get(campo):
            linhas.append(f"- **{rotulo}:** {p[campo]}")

    if p.get("colide_com"):
        outros = " · ".join(f"`{x}`" for x in p["colide_com"])
        linhas.append(f"- **Collides with:** {outros}")
    linhas.append(f"- **Read on:** {p.get('lido_em', '—')}")
    linhas.append("")
    return linhas


def gerar(hoje: date | None = None) -> str:
    censo = carregar()
    projetos = censo["projetos"]
    den = censo["denominador"]
    # ⚠️ The seal date is the NEWEST reading in the census, never `date.today()`.
    # Stamping today would make the generated file change on its own at midnight,
    # and `--conferir` would flag "stale" with nobody having touched anything —
    # an alarm that only knows how to fire by the passage of time is noise, not
    # a measurement.
    hoje = hoje or max(
        (date.fromisoformat(p["lido_em"]) for p in projetos if p.get("lido_em")),
        default=date.today(),
    )

    colisoes = sorted(
        (
            (p["nome"], len(p["colide_com"]) + (1 if p.get("repo") else 0))
            for p in projetos
            if p.get("colide_com")
        ),
        key=lambda x: (-x[1], x[0]),
    )

    L: list[str] = []
    A = L.append

    A("# The AI agent ecosystem census")
    A("")
    A("> **This file is generated.** Do not edit it by hand — edit `censo/ecossistema.json` and run")
    A("> `python censo/gerar.py`. The verifier fails if the two fall out of sync.")
    A("")
    A(f"<!-- measured: censo.gerado_em_dia=1 nature=relation on={hoje.isoformat()} expires=never source=censo/gerar.py -->")
    A("")
    A("An `awesome-*` list does not fail when it ages. This census fails.")
    A("")
    A(f"**{len(projetos)} projects.** Every entry was read **on the repository's page**, never in the")
    A("post that cited it. What was not verified is written as not verified — never filled in by")
    A("plausibility, and never turned into a zero.")
    A("")

    # --- the finding, first: it is the reason the census exists ---------------
    # ⚠️ The HEADING and the count below come from `len(colisoes)`, never from a
    # hand-written number — a fixed "five names" in the code survived the first
    # version only because, at the time, `colisoes` had exactly five entries.
    # Adding a sixth collision (measured: `Awesome A2A`, `MateClaw`,
    # `SILENTCHAIN AI`) left the heading lying about its own table — the same
    # family of defect this whole project exists to forbid.
    A("---")
    A("")
    A(f"## The finding: {len(colisoes)} names do not identify a project")
    A("")
    A("These names identify a **cluster of independent projects** — same name, same problem,")
    A("not citing each other:")
    A("")
    A("| Name | Independent projects | Is there a canonical one? |")
    A("|---|---:|---|")
    for nome, quantos in colisoes:
        canonico = next(p for p in projetos if p["nome"] == nome)
        tem = "yes" if canonico.get("repo") else "⛔ **no**"
        A(f"| `{nome}` | **{quantos}** | {tem} |")
    A("")
    pior_nome, pior_quantos = colisoes[0] if colisoes else ("—", 0)
    A(
        f"Someone who hears *\"install `{pior_nome}`\"* has no way to know which of the {pior_quantos}. "
        f"**None of them lists the others.** This is not \"there are many projects\" — it is the same"
    )
    A(f"project built {pior_quantos} times in the dark, in the worst case of this reading.")
    A("")
    A("> **Denominator, and it matters:** this is what **a search by name, on one day** returned.")
    A("> It is not a census of GitHub. **It is a floor, not a ceiling** — the real number is larger, never smaller.")
    A("")

    # --- by stage -----------------------------------------------------------
    A("---")
    A("")
    A("## Who already occupies each stage")
    A("")
    A("Ordered by an agent's life cycle, not by the alphabet — because what matters is **where")
    A("there is already a big owner** and where there is not.")
    A("")
    A("| Stage | What it is | Who occupies it |")
    A("|---|---|---|")
    for chave, titulo, oque in ESTAGIOS:
        nomes = [p["nome"] for p in projetos if p.get("estagio") == chave]
        A(f"| **{titulo}** | {oque} | {' · '.join(nomes) if nomes else '—'} |")
    A("")

    # --- general table ------------------------------------------------------
    A("---")
    A("")
    A("## The projects, with the license read at the source")
    A("")
    A("The column that decides whether you can use it is the **third**, not the second. A license")
    A("that is not OSI does not become open source because the project calls itself open.")
    A("")
    A("| Project | Where | License | Verdict | Names in the cluster |")
    A("|---|---|---|---|---:|")
    for p in sorted(projetos, key=lambda x: x["nome"].lower()):
        A(_linha_de_projeto(p))
    A("")
    A("**The three doors of a non-OSI license**, because treating them as one is the common mistake:")
    A("")
    A("| What to do | Allowed? |")
    A("|---|---|")
    A("| **Run** the tool | ✅ yes — it is what the license grants |")
    A("| **Read the architecture as a specification** and reimplement it | ✅ yes — an API and a model are not the protected expression |")
    A("| **Copy the code into** your project | ⛔ no — the restriction carries across to all of your users |")
    A("")

    # --- entries ----------------------------------------------------------
    A("---")
    A("")
    A("## Each one's entry")
    A("")
    for chave, titulo, _ in ESTAGIOS:
        do_estagio = [p for p in projetos if p.get("estagio") == chave]
        if not do_estagio:
            continue
        A(f"### {titulo}")
        A("")
        for p in sorted(do_estagio, key=lambda x: x["nome"].lower()):
            L.extend(_ficha(p))

    # --- denominator -----------------------------------------------------
    A("---")
    A("")
    A("## The denominator of this reading")
    A("")
    A("Every surface that counts declares **how many** it counted from. Without that, a filter that")
    A("skips silently produces a plausible, empty answer.")
    A("")
    A("| | |")
    A("|---|---:|")
    A(f"| Names searched | {den['nomes_buscados']} |")
    A(f"| With a canonical repository identified and read | {den['com_repo_canonico']} |")
    A(f"| **Without** a canonical repository — and that absence **is** the finding | {den['sem_repo_canonico']} |")
    A(f"| Are a paper, not a repository | {den['sao_paper_nao_repo']} |")
    A(f"| **Cloned, installed or run** | **{den['clonados_ou_executados']}** |")
    if den.get("sem_estagio_classificado"):
        A(
            "| Have a repository (or cluster), but none of the ten stages covers what they do "
            f"| {den['sem_estagio_classificado']} |"
        )
    A("")
    A(f"⚠️ {den['aviso']}")
    A("")
    A("**What this census does NOT measure, declared:**")
    A("")
    A("- **Whether the project works.** Nothing here was run. Performance is the author's claim.")
    A("- **Whether it still exists today.** That is what each seal's `expires=` is for — no offline")
    A("  probe reaches the truth of the world out there, and confusing the two would be saying that")
    A("  a coherent JSON is a true fact.")
    A("- **How many projects really exist.** The collision count is the floor of one search.")
    A("- **Whether the license changed after the reading date.** Each entry's `lido_em` field is")
    A("  the date the page was opened, not today's date.")
    A("")
    A("---")
    A("")
    A("## How to contribute an entry")
    A("")
    A("1. Open the **repository's page** — not the post, not the list, not the screenshot. This")
    A("   house's memory records the cost of attributing by the packaging: one project in this")
    A("   census was credited to whoever posted on LinkedIn, not to whoever wrote the code.")
    A("2. Fill in `censo/ecossistema.json`. **`nao_verificado` is a legitimate value** and never")
    A("   becomes zero.")
    A("3. Run `python censo/gerar.py` and `python -m loadline .`. If either one fails, the entry")
    A("   is not ready yet.")
    A("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    novo = gerar()
    if "--conferir" in argv:
        atual = PUBLICADO.read_text(encoding="utf-8") if PUBLICADO.exists() else ""
        if atual == novo:
            print(f"{PUBLICADO.name}: in sync with {FONTE.name}")
            return 0
        print(f"{PUBLICADO.name}: STALE — run `python censo/gerar.py`")
        return 1
    PUBLICADO.write_text(novo, encoding="utf-8")
    print(f"{PUBLICADO}: {len(novo)} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
