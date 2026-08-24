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

        # S11 — duas skills disputando o mesmo despacho, e o escape nominal -------
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
        marca = "ok  " if (acusou and calou) else "FALHA"
        print(f"  {marca} S11  duas description disputando o mesmo despacho")
        if not acusou:
            falhas.append("S11: NÃO acusou duas skills com description quase idêntica")
        if not calou:
            falhas.append("S11: acusou mesmo depois de uma nomear a outra pelo slug")

        # A colheita (`--colher`) — as quatro recusas, e o caminho que escreve ----
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
            marca = "ok  " if obtida == regra else "FALHA"
            print(f"  {marca} {regra}   colheita recusa — {regra}")
            if obtida != regra:
                falhas.append(f"{regra}: colheita devolveu {obtida!r}, esperava {regra!r}")

        # H2 exige uma skill já escrita no destino
        colher("ja-existe", "uma skill qualquer, escrita antes", alvo)
        obtida = _recusa_de("ja-existe", "outra descrição, mesmo slug")
        marca = "ok  " if obtida == "H2" else "FALHA"
        print(f"  {marca} H2   colheita recusa — H2")
        if obtida != "H2":
            falhas.append(f"H2: colheita devolveu {obtida!r}, esperava 'H2'")

        # H3 exige colisão real de description contra o que já está no destino
        colher(
            "revisor-de-licenca",
            "Reviews open source licenses for compatibility before a dependency is added.",
            alvo,
        )
        obtida = _recusa_de(
            "auditor-de-licenca",
            "Reviews open source licenses for compatibility before a dependency is added.",
        )
        marca = "ok  " if obtida == "H3" else "FALHA"
        print(f"  {marca} H3   colheita recusa — H3")
        if obtida != "H3":
            falhas.append(f"H3: colheita devolveu {obtida!r}, esperava 'H3'")

        # E o caminho feliz: nasce, tem os placeholders certos, e some do S3/S4
        # só depois de preenchido — nunca antes.
        escrito = colher("empacotador-de-release", "Packages a release build for distribution.", alvo)
        texto = escrito.read_text(encoding="utf-8")
        regras_pasta = _regras(Path(escrito).parent)
        ok_nasce = "S3" in regras_pasta and "S4" in regras_pasta
        ok_desc = "Packages a release build for distribution." in texto and texto.count("?") == 3
        texto_preenchido = texto.replace(
            "gatilho positivo: ?; gatilho negativo: ?",
            "Use when a release tag is pushed. Don't use it for hotfix builds.",
        ).replace("\n?\n\n<!--", "\n1. Passo real.\n\n<!--")
        escrito.write_text(texto_preenchido, encoding="utf-8")
        regras_depois = _regras(Path(escrito).parent)
        ok_fecha = "S3" not in regras_depois and "S4" not in regras_depois
        ok = ok_nasce and ok_desc and ok_fecha
        marca = "ok  " if ok else "FALHA"
        print(f"  {marca} HC   colheita: nasce ⛔ em S3/S4, preenchida vira ⚪")
        if not ok_nasce:
            falhas.append("HC: a skill colhida não nasceu com S3+S4 acusando (falso verde)")
        if not ok_desc:
            falhas.append("HC: a description colhida não carrega o `--diz` real, ou não tem os 3 '?'")
        if not ok_fecha:
            falhas.append("HC: preencher os '?' não fez S3/S4 pararem de acusar")

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
