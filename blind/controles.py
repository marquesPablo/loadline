"""Controles negativos do `blind` — cada um é visto REPROVANDO e CALANDO.

    python -m blind.controles

Um detector que nunca foi visto acusar não vale nada: ele pode estar quieto
porque o mundo está limpo, ou porque ele não olha. Cada controle abaixo monta
uma fronteira DE VERDADE (junction real via `mklink /J`, `.gitignore` real
dentro de um `git init` real), exige o achado, desfaz o defeito, e exige o
silêncio — ou o rebaixamento de ⛔ para ⚠️, quando é isso que deveria mudar.

Reprova com exit 1. Sem dependência, sem rede, sem modelo.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .limites import detectar


def _junction(link: Path, alvo: Path) -> bool:
    alvo.mkdir(parents=True, exist_ok=True)
    link.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(alvo)],
        capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )
    return r.returncode == 0


def _desfazer_junction(link: Path) -> None:
    # `os.rmdir` numa junction remove só o REPARSE POINT — nunca o alvo.
    # Mesma técnica e mesmo motivo do Y-de-junção desta casa: se isto usasse
    # `shutil.rmtree`, o Windows seguiria o link e apagaria o alvo de fora.
    try:
        os.rmdir(link)
    except OSError:
        pass


def _git_init(pasta: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=str(pasta),
                    capture_output=True, stdin=subprocess.DEVNULL)


def _grave(base: Path, caminho_relativo: str) -> bool | None:
    """`True`/`False` se a fronteira existe, `None` se sumiu de vez."""
    for f in detectar(base):
        if f.caminho == caminho_relativo:
            return f.grave
    return None


def _algum_gitignore(base: Path) -> bool:
    return any(f.tipo == "gitignore" for f in detectar(base))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):  # pragma: no cover
        pass

    falhas: list[str] = []
    print("controles negativos do blind")
    print("=" * 74)

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        # --- B1: junction real escondendo CLAUDE.md — acusa GRAVE, e some
        # a gravidade (não a fronteira) quando o arquivo sai de trás dela ---
        raiz1 = base / "b1"
        link1 = raiz1 / "vinculo"
        alvo1 = base / "b1-alvo"
        criou = _junction(link1, alvo1)
        if criou:
            (alvo1 / "CLAUDE.md").write_text("x", encoding="utf-8")
            acusou = _grave(raiz1, "vinculo") is True
            (alvo1 / "CLAUDE.md").unlink()
            calou = _grave(raiz1, "vinculo") is False
            _desfazer_junction(link1)
        else:
            acusou = calou = False
            falhas.append("B1: não deu para criar junction real (mklink /J falhou) — "
                           "controle não pôde rodar")
        marca = "ok  " if (acusou and calou) else "FALHA"
        print(f"  {marca} B1   junction esconde CLAUDE.md — grave, e deixa de ser quando some")
        if criou and not acusou:
            falhas.append("B1: NÃO acusou junction com CLAUDE.md atrás")
        if criou and not calou:
            falhas.append("B1: continuou grave depois de o CLAUDE.md sair de trás da junction")

        # --- B2: junction SEM nada sensível não é grave — fato do disco,
        # não defeito. Sem este controle, todo mount ficaria REPROVA. ---
        raiz2 = base / "b2"
        link2 = raiz2 / "vinculo"
        alvo2 = base / "b2-alvo"
        criou2 = _junction(link2, alvo2)
        if criou2:
            (alvo2 / "notas.txt").write_text("nada de declaração aqui", encoding="utf-8")
            grave2 = _grave(raiz2, "vinculo")
            _desfazer_junction(link2)
            ok2 = grave2 is False  # existe (não é None) e não é grave
        else:
            ok2 = False
            falhas.append("B2: não deu para criar junction real — controle não pôde rodar")
        print(f"  {'ok  ' if ok2 else 'FALHA'} B2   junction sem declaração atrás não vira ⛔")
        if criou2 and not ok2:
            falhas.append("B2: junction inofensiva foi tratada como grave (falso positivo)")

        # --- B3: .gitignore dentro de repo git real escondendo AGENTS.md ---
        raiz3 = base / "b3"
        (raiz3 / "escondida").mkdir(parents=True)
        (raiz3 / "escondida" / "AGENTS.md").write_text("x", encoding="utf-8")
        (raiz3 / ".gitignore").write_text("escondida/\n", encoding="utf-8")
        _git_init(raiz3)
        acusou3 = _algum_gitignore(raiz3)
        (raiz3 / ".gitignore").write_text("", encoding="utf-8")
        calou3 = not _algum_gitignore(raiz3)
        print(f"  {'ok  ' if (acusou3 and calou3) else 'FALHA'} B3   .gitignore esconde "
              f"AGENTS.md — acusa, e cala sem a regra")
        if not acusou3:
            falhas.append("B3: NÃO acusou .gitignore escondendo AGENTS.md")
        if not calou3:
            falhas.append("B3: continuou acusando depois de a regra sumir do .gitignore")

        # --- B4: a MESMA regra, mas SEM `.git` por perto — não deve acusar.
        # É a causa 2 medida nesta sessão: `.gitignore` só é lido por
        # ferramentas cientes de git DENTRO de um repositório de verdade.
        # Sem este controle, o detector confundiria "existe um arquivo
        # chamado .gitignore" com "algo de fato respeita esta regra". ---
        raiz4 = base / "b4"
        (raiz4 / "escondida").mkdir(parents=True)
        (raiz4 / "escondida" / "AGENTS.md").write_text("x", encoding="utf-8")
        (raiz4 / ".gitignore").write_text("escondida/\n", encoding="utf-8")
        silencioso4 = not _algum_gitignore(raiz4)
        print(f"  {'ok  ' if silencioso4 else 'FALHA'} B4   .gitignore sem `.git` por perto "
              f"não acusa (a regra não vale fora de repo)")
        if not silencioso4:
            falhas.append("B4: acusou .gitignore mesmo sem `.git` — a causa 2 não se aplica aí")

        # --- B5: pasta sem fronteira nenhuma sai limpa ---
        raiz5 = base / "b5"
        (raiz5 / "comum").mkdir(parents=True)
        (raiz5 / "comum" / "README.md").write_text("x", encoding="utf-8")
        limpo5 = detectar(raiz5) == []
        print(f"  {'ok  ' if limpo5 else 'FALHA'} B5   pasta sem junction/symlink/gitignore "
              f"sai com zero fronteiras")
        if not limpo5:
            falhas.append("B5: achou fronteira numa árvore sem reparse point e sem .gitignore")

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
