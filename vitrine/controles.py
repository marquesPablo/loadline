"""Controles negativos da `vitrine` — cada regra é vista REPROVANDO e PASSANDO.

    python -m vitrine.controles

Um check que nunca foi visto acusar não vale nada: ele pode estar verde porque o
mundo está certo, ou porque ele não olha. Cada controle abaixo monta uma skill de
mentira **com** o defeito, exige o ⛔, conserta o defeito, e exige o silêncio.

Reprova com exit 1. Sem dependência, sem rede, sem modelo.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from .regras import ler_pasta, vistoriar

BOA = """\
---
name: {nome}
description: Creates and builds React components using Tailwind CSS. Use when the
  user wants to update component styles or UI logic. Don't use it for Vue, Svelte,
  or vanilla CSS projects.
---

# {nome}

Corpo curto, de propósito.
"""


def _montar(raiz: Path, pasta: str, texto: str) -> Path:
    alvo = raiz / pasta
    alvo.mkdir(parents=True, exist_ok=True)
    (alvo / "SKILL.md").write_text(texto, encoding="utf-8")
    return alvo


def _regras(raiz: Path) -> set[str]:
    return {a.regra for a in vistoriar(ler_pasta(raiz, com_git=False))}


# ------------------------------------------------------------ os controles ----

def controles() -> list[tuple[str, str, str, str]]:
    """(regra, o que o defeito é, texto COM defeito, texto SEM defeito)."""
    return [
        (
            "S1",
            "name diverge da pasta",
            BOA.format(nome="outro-nome"),
            BOA.format(nome="minha-skill"),
        ),
        (
            "S2",
            "name com maiúscula e underscore",
            BOA.replace("name: {nome}", "name: Minha_Skill").format(nome="x"),
            BOA.format(nome="minha-skill"),
        ),
        (
            "S3",
            "descrição sem cláusula de gatilho",
            "---\nname: minha-skill\ndescription: A helper for React things. Don't use it for Vue.\n---\n\n# x\n",
            BOA.format(nome="minha-skill"),
        ),
        (
            "S4",
            "descrição sem gatilho negativo",
            "---\nname: minha-skill\ndescription: Builds React components. Use when the user asks for UI.\n---\n\n# x\n",
            BOA.format(nome="minha-skill"),
        ),
        (
            "S5",
            "descrição acima de 1024 caracteres",
            "---\nname: minha-skill\ndescription: Use when x. Don't use for y. " + ("z" * 1100) + "\n---\n\n# x\n",
            BOA.format(nome="minha-skill"),
        ),
        (
            "S6",
            "corpo acima de 500 linhas",
            BOA.format(nome="minha-skill") + ("\nlinha\n" * 520),
            BOA.format(nome="minha-skill"),
        ),
        (
            "S9",
            "descrição em primeira pessoa",
            "---\nname: minha-skill\ndescription: I help you build React components when you need UI. Don't use for Vue.\n---\n\n# x\n",
            BOA.format(nome="minha-skill"),
        ),
    ]


def _controle_estrutural(raiz: Path, regra: str, montar) -> tuple[bool, bool]:
    """Controles que dependem de PASTA, não do texto do SKILL.md."""
    _montar(raiz, "minha-skill", BOA.format(nome="minha-skill"))
    montar(raiz / "minha-skill")
    com = regra in _regras(raiz)
    shutil.rmtree(raiz / "minha-skill")
    _montar(raiz, "minha-skill", BOA.format(nome="minha-skill"))
    sem = regra not in _regras(raiz)
    return com, sem


def _fundo(pasta: Path) -> None:
    alvo = pasta / "references" / "db" / "v1"
    alvo.mkdir(parents=True, exist_ok=True)
    (alvo / "schema.md").write_text("x", encoding="utf-8")


def _biblioteca(pasta: Path) -> None:
    alvo = pasta / "scripts"
    alvo.mkdir(parents=True, exist_ok=True)
    (alvo / "utils.py").write_text("def ajuda():\n    return 1\n", encoding="utf-8")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover
        pass

    falhas: list[str] = []
    print("controles negativos da vitrine")
    print("=" * 74)

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        for regra, defeito, com_defeito, sem_defeito in controles():
            raiz = base / regra
            raiz.mkdir()
            _montar(raiz, "minha-skill", com_defeito)
            acusou = regra in _regras(raiz)

            _montar(raiz, "minha-skill", sem_defeito)
            calou = regra not in _regras(raiz)

            marca = "ok  " if (acusou and calou) else "FALHA"
            print(f"  {marca} {regra:<4} {defeito}")
            if not acusou:
                falhas.append(f"{regra}: NÃO acusou o defeito «{defeito}»")
            if not calou:
                falhas.append(f"{regra}: acusou a skill CORRETA (falso positivo)")

        for regra, defeito, montar in (
            ("S7", "references/ com dois níveis", _fundo),
            ("S8", "script sem ponto de entrada", _biblioteca),
        ):
            raiz = base / regra
            raiz.mkdir()
            acusou, calou = _controle_estrutural(raiz, regra, montar)
            marca = "ok  " if (acusou and calou) else "FALHA"
            print(f"  {marca} {regra:<4} {defeito}")
            if not acusou:
                falhas.append(f"{regra}: NÃO acusou o defeito «{defeito}»")
            if not calou:
                falhas.append(f"{regra}: acusou a skill CORRETA (falso positivo)")

        # O controle que nasceu de um erro real: `description` multi-linha existe
        # no disco (a `math-olympiad` oficial usa), e a primeira versão desta
        # ferramenta a leu como vazia — acusando «sem description» numa skill boa.
        raiz = base / "multilinha"
        raiz.mkdir()
        _montar(
            raiz,
            "minha-skill",
            '---\nname: minha-skill\ndescription:\n  "Builds React components. Use when the user\n'
            '  asks for UI. Don\'t use it for Vue."\n---\n\n# x\n',
        )
        regras = _regras(raiz)
        ok = "S3" not in regras and "S4" not in regras
        print(f"  {'ok  ' if ok else 'FALHA'} MLN  description multi-linha é lida (era falso positivo)")
        if not ok:
            falhas.append("MLN: description multi-linha voltou a ser lida como vazia")

    print("-" * 74)
    if falhas:
        for f in falhas:
            print(f"  ⛔ {f}")
        print(f"\nREPROVA — {len(falhas)} controle(s)                                   (exit 1)")
        return 1
    print("PASSA — toda regra foi vista acusando E calando            (exit 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
