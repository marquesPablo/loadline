"""`vitrine` negative controls — each rule is seen FAILING and PASSING.

    python -m vitrine.controles

A check that has never been seen accusing is worth nothing: it may be green
because the world is right, or because it does not look. Each control below
builds a fake skill **with** the defect, requires the ⛔, fixes the defect, and
requires the silence.

Fails with exit 1. No dependency, no network, no model.
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

Short body, on purpose.
"""


def _montar(raiz: Path, pasta: str, texto: str) -> Path:
    alvo = raiz / pasta
    alvo.mkdir(parents=True, exist_ok=True)
    (alvo / "SKILL.md").write_text(texto, encoding="utf-8")
    return alvo


def _regras(raiz: Path) -> set[str]:
    return {a.regra for a in vistoriar(ler_pasta(raiz, com_git=False))}


# ------------------------------------------------------------ the controls ----

def controles() -> list[tuple[str, str, str, str]]:
    """(rule, what the defect is, text WITH defect, text WITHOUT defect)."""
    return [
        (
            "S1",
            "name diverges from the folder",
            BOA.format(nome="outro-nome"),
            BOA.format(nome="minha-skill"),
        ),
        (
            "S2",
            "name with uppercase and underscore",
            BOA.replace("name: {nome}", "name: Minha_Skill").format(nome="x"),
            BOA.format(nome="minha-skill"),
        ),
        (
            "S3",
            "description with no trigger clause",
            "---\nname: minha-skill\ndescription: A helper for React things. Don't use it for Vue.\n---\n\n# x\n",
            BOA.format(nome="minha-skill"),
        ),
        (
            "S4",
            "description with no negative trigger",
            "---\nname: minha-skill\ndescription: Builds React components. Use when the user asks for UI.\n---\n\n# x\n",
            BOA.format(nome="minha-skill"),
        ),
        (
            "S5",
            "description above 1024 characters",
            "---\nname: minha-skill\ndescription: Use when x. Don't use for y. " + ("z" * 1100) + "\n---\n\n# x\n",
            BOA.format(nome="minha-skill"),
        ),
        (
            "S6",
            "body above 500 lines",
            BOA.format(nome="minha-skill") + ("\nline\n" * 520),
            BOA.format(nome="minha-skill"),
        ),
        (
            "S9",
            "description in the first person",
            "---\nname: minha-skill\ndescription: I help you build React components when you need UI. Don't use for Vue.\n---\n\n# x\n",
            BOA.format(nome="minha-skill"),
        ),
    ]


def _controle_estrutural(raiz: Path, regra: str, montar) -> tuple[bool, bool]:
    """Controls that depend on the FOLDER, not on the SKILL.md text."""
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
    (alvo / "utils.py").write_text("def helper():\n    return 1\n", encoding="utf-8")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover
        pass

    falhas: list[str] = []
    print("vitrine negative controls")
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

            marca = "ok   " if (acusou and calou) else "FAIL "
            print(f"  {marca} {regra:<4} {defeito}")
            if not acusou:
                falhas.append(f"{regra}: did NOT accuse the defect «{defeito}»")
            if not calou:
                falhas.append(f"{regra}: accused the CORRECT skill (false positive)")

        for regra, defeito, montar in (
            ("S7", "references/ with two levels", _fundo),
            ("S8", "a script with no entry point", _biblioteca),
        ):
            raiz = base / regra
            raiz.mkdir()
            acusou, calou = _controle_estrutural(raiz, regra, montar)
            marca = "ok   " if (acusou and calou) else "FAIL "
            print(f"  {marca} {regra:<4} {defeito}")
            if not acusou:
                falhas.append(f"{regra}: did NOT accuse the defect «{defeito}»")
            if not calou:
                falhas.append(f"{regra}: accused the CORRECT skill (false positive)")

        # The control born from a real mistake: a multi-line `description` exists
        # on disk (the official `math-olympiad` uses one), and the first version
        # of this tool read it as empty — accusing «no description» on a good skill.
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
        print(f"  {'ok   ' if ok else 'FAIL '} MLN  a multi-line description is read (was a false positive)")
        if not ok:
            falhas.append("MLN: a multi-line description is being read as empty again")

        # S11 — two skills fighting over the same dispatch, and the nominal escape ---
        raiz = base / "S11"
        raiz.mkdir()
        colide = (
            "---\nname: {n}\ndescription: Reviews pull requests looking for bugs and "
            "regressions before merge. Use when the user opens a PR.\n---\n\n# x\n"
        )
        _montar(raiz, "revisor-de-pr", colide.format(n="revisor-de-pr"))
        _montar(raiz, "auditor-de-pr", colide.format(n="auditor-de-pr"))
        acusou = "S11" in _regras(raiz)
        _montar(
            raiz,
            "auditor-de-pr",
            colide.format(n="auditor-de-pr").replace(
                "Use when the user opens a PR.",
                "Use when the user opens a PR. Different from revisor-de-pr, which "
                "only checks style.",
            ),
        )
        calou = "S11" not in _regras(raiz)
        marca = "ok   " if (acusou and calou) else "FAIL "
        print(f"  {marca} S11  two descriptions fighting over the same dispatch")
        if not acusou:
            falhas.append("S11: did NOT accuse two skills with a near-identical description")
        if not calou:
            falhas.append("S11: accused even after one named the other by its slug")

        # The harvest (`--harvest`) — the four refusals, and the path that writes ---
        from .colheita import Recusa, colher

        alvo = base / "colheita"
        alvo.mkdir()

        def _recusa_de(slug: str, diz: str, pasta: Path = alvo) -> str | None:
            try:
                colher(slug, diz, pasta)
            except Recusa as recusa:
                return recusa.regra
            return None

        casos_h = [
            ("H1", lambda: _recusa_de("Nome_Ruim", "x")),
            ("H4", lambda: _recusa_de("skill-sem-diz", "")),
        ]
        for regra, chamar in casos_h:
            obtida = chamar()
            marca = "ok   " if obtida == regra else "FAIL "
            print(f"  {marca} {regra}   harvest refuses — {regra}")
            if obtida != regra:
                falhas.append(f"{regra}: harvest returned {obtida!r}, expected {regra!r}")

        # H2 needs a skill already written in the target
        colher("ja-existe", "some skill, written earlier", alvo)
        obtida = _recusa_de("ja-existe", "another description, same slug")
        marca = "ok   " if obtida == "H2" else "FAIL "
        print(f"  {marca} H2   harvest refuses — H2")
        if obtida != "H2":
            falhas.append(f"H2: harvest returned {obtida!r}, expected 'H2'")

        # H3 needs a real description collision against what is already in the target
        colher(
            "revisor-de-licenca",
            "Reviews open source licenses for compatibility before a dependency is added.",
            alvo,
        )
        obtida = _recusa_de(
            "auditor-de-licenca",
            "Reviews open source licenses for compatibility before a dependency is added.",
        )
        marca = "ok   " if obtida == "H3" else "FAIL "
        print(f"  {marca} H3   harvest refuses — H3")
        if obtida != "H3":
            falhas.append(f"H3: harvest returned {obtida!r}, expected 'H3'")

        # And the happy path: it is born, has the right placeholders, and leaves
        # S3/S4 only after being filled in — never before.
        escrito = colher("empacotador-de-release", "Packages a release build for distribution.", alvo)
        texto = escrito.read_text(encoding="utf-8")
        regras_pasta = _regras(Path(escrito).parent)
        ok_nasce = "S3" in regras_pasta and "S4" in regras_pasta
        ok_desc = "Packages a release build for distribution." in texto and texto.count("?") == 3
        texto_preenchido = texto.replace(
            "positive trigger: ?; negative trigger: ?",
            "Use when a release tag is pushed. Don't use it for hotfix builds.",
        ).replace("\n?\n\n<!--", "\n1. A real step.\n\n<!--")
        escrito.write_text(texto_preenchido, encoding="utf-8")
        regras_depois = _regras(Path(escrito).parent)
        ok_fecha = "S3" not in regras_depois and "S4" not in regras_depois
        ok = ok_nasce and ok_desc and ok_fecha
        marca = "ok   " if ok else "FAIL "
        print(f"  {marca} HC   harvest: born ⛔ on S3/S4, filled in becomes ⚪")
        if not ok_nasce:
            falhas.append("HC: the harvested skill was not born with S3+S4 accusing (false green)")
        if not ok_desc:
            falhas.append("HC: the harvested description does not carry the real `--says`, or lacks the 3 '?'")
        if not ok_fecha:
            falhas.append("HC: filling in the '?' did not make S3/S4 stop accusing")

    print("-" * 74)
    if falhas:
        for f in falhas:
            print(f"  ⛔ {f}")
        print(f"\nFAIL — {len(falhas)} control(s)                                       (exit 1)")
        return 1
    print("PASS — every rule was seen accusing AND going quiet         (exit 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
