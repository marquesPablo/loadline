"""The Census's advice — the forge does not invent a component, it consults the register.

nature: fix — an absent or unreadable census becomes a written warning in the
report, never an invented recommendation. The forge compiles the same way; it
just loses the ability to say what already exists, and it says it lost it.

## Why this is here

An agent compiler that answers *"for memory, use X"* without looking at anything
is the seventh AgentGuard waiting to be born. When the spec declares
`needs = ["memory"]`, the forge opens the census and returns **the real
components** — with the license, with the OSI verdict, and with the collision
warning when the name the person is about to search for identifies six
different projects.

It is the part of the product that serves the notebook's rule: *"both the
billionaire and the cleaner can read, understand and apply it"*. The cleaner
does not need the seventh framework. They need to know **which of the six** and
**whether it still holds**.
"""

from __future__ import annotations

import json
from pathlib import Path

ROTULO = {
    "osi": "✅ OSI — can be vendored",
    "osi_copyleft_forte": "⚠️ OSI, strong copyleft — the choice must be deliberate",
    "nao_osi": "⛔ NOT open source — running it yes, copying it in no",
    "nao_verificado": "◻️ license not verified — check before using",
}


def carregar(caminho: str | Path) -> dict | None:
    """Reads the census. Absent or unreadable returns `None` — never an empty census.

    Returning `{}` would make the forge say *"no component exists for memory"*,
    which is a false claim dressed as an answer. `None` forces the caller to
    treat the case as *not consulted*, which is what actually happened.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def para(estagio: str, censo: dict | None) -> list[dict]:
    if not censo:
        return []
    return [p for p in censo.get("projetos", []) if p.get("estagio") == estagio]


def em_markdown(precisa: list[str], censo: dict | None, caminho_do_censo: str) -> str:
    """The advice block, ready to drop into the run's report."""
    if not precisa:
        return ""
    L = ["## What already exists for what this spec asked for", ""]
    if censo is None:
        L += [
            f"⚠️ **Census not consulted.** `{caminho_do_censo}` does not exist or could not be read.",
            "",
            "The forge compiled anyway — the census advises, it does not gate. But what follows",
            "is **not** an empty list of available components: it is the absence of the lookup, and",
            "the two say opposite things.",
            "",
        ]
        return "\n".join(L)

    for estagio in precisa:
        peças = para(estagio, censo)
        L.append(f"### `{estagio}`")
        L.append("")
        if not peças:
            L += [
                f"The census has **0** entries at stage `{estagio}`.",
                "",
                "That means *nobody has catalogued one yet*, and does **not** mean *it does not exist*.",
                "Before you write your own, open a search — and then add the entry to the",
                "census, because the next person will ask the same question.",
                "",
            ]
            continue
        for p in sorted(peças, key=lambda x: x["nome"].lower()):
            alvo = p.get("repo") or (p.get("paper") and f"`{p['paper']}`") or "⛔ no canonical"
            L.append(f"- **{p['nome']}** — {alvo}")
            L.append(f"  - {ROTULO.get(p.get('veredito_licenca', ''), '◻️')} (`{p.get('licenca', '—')}`)")
            L.append(f"  - {p['faz']}")
            if p.get("custa_dinheiro"):
                L.append("  - 💸 **costs money** — an API key or a paid service")
            if p.get("colide_com"):
                quantos = len(p["colide_com"]) + (1 if p.get("repo") else 0)
                L.append(
                    f"  - ⚠️ **`{p['nome']}` identifies {quantos} independent projects.** "
                    "Installing by name is a lottery — use the URL, not the name."
                )
            L.append(f"  - read on `{p.get('lido_em', '—')}`")
        L.append("")

    L += [
        "> **This advice expires.** Every line came from a page opened on the date next to it, and",
        "> no offline probe knows what changed out there since. Run `python -m loadline` on the",
        "> census before you lean on a decision from it.",
        "",
    ]
    return "\n".join(L)
