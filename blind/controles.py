"""`blind` negative controls — each one is seen FAILING and GOING QUIET.

    python -m blind.controles

A detector that has never been seen accusing is worth nothing: it may be quiet
because the world is clean, or because it does not look. Each control below
builds a REAL boundary (a real junction via `mklink /J`, a real `.gitignore`
inside a real `git init`), requires the finding, undoes the defect, and
requires the silence — or the downgrade from ⛔ to ⚠️, when that is what should
change.

Fails with exit 1. No dependency, no network, no model.
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
    # `os.rmdir` on a junction removes only the REPARSE POINT — never the target.
    # If this used `shutil.rmtree`, Windows would follow the link and delete the
    # target from outside.
    try:
        os.rmdir(link)
    except OSError:
        pass


def _git_init(pasta: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=str(pasta),
                    capture_output=True, stdin=subprocess.DEVNULL)


def _grave(base: Path, caminho_relativo: str) -> bool | None:
    """`True`/`False` if the boundary exists, `None` if it is gone for good."""
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
    print("blind negative controls")
    print("=" * 74)

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        # --- B1: a real junction hiding CLAUDE.md — accuses SERIOUS, and the
        # severity (not the boundary) goes away when the file leaves it ---
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
            falhas.append("B1: could not create a real junction (mklink /J failed) — "
                           "control could not run")
        marca = "ok   " if (acusou and calou) else "FAIL "
        print(f"  {marca} B1   a junction hides CLAUDE.md — serious, and stops being so when it is gone")
        if criou and not acusou:
            falhas.append("B1: did NOT accuse a junction with CLAUDE.md behind it")
        if criou and not calou:
            falhas.append("B1: stayed serious after CLAUDE.md left the junction")

        # --- B2: a junction with NOTHING sensitive is not serious — a fact of the
        # disk, not a defect. Without this control, every mount would be FAIL. ---
        raiz2 = base / "b2"
        link2 = raiz2 / "vinculo"
        alvo2 = base / "b2-alvo"
        criou2 = _junction(link2, alvo2)
        if criou2:
            (alvo2 / "notas.txt").write_text("no declaration here", encoding="utf-8")
            grave2 = _grave(raiz2, "vinculo")
            _desfazer_junction(link2)
            ok2 = grave2 is False  # exists (not None) and is not serious
        else:
            ok2 = False
            falhas.append("B2: could not create a real junction — control could not run")
        print(f"  {'ok   ' if ok2 else 'FAIL '} B2   a junction with no declaration behind it does not become ⛔")
        if criou2 and not ok2:
            falhas.append("B2: a harmless junction was treated as serious (false positive)")

        # --- B3: a .gitignore inside a real git repo hiding AGENTS.md ---
        raiz3 = base / "b3"
        (raiz3 / "escondida").mkdir(parents=True)
        (raiz3 / "escondida" / "AGENTS.md").write_text("x", encoding="utf-8")
        (raiz3 / ".gitignore").write_text("escondida/\n", encoding="utf-8")
        _git_init(raiz3)
        acusou3 = _algum_gitignore(raiz3)
        (raiz3 / ".gitignore").write_text("", encoding="utf-8")
        calou3 = not _algum_gitignore(raiz3)
        print(f"  {'ok   ' if (acusou3 and calou3) else 'FAIL '} B3   .gitignore hides "
              f"AGENTS.md — accuses, and goes quiet without the rule")
        if not acusou3:
            falhas.append("B3: did NOT accuse a .gitignore hiding AGENTS.md")
        if not calou3:
            falhas.append("B3: kept accusing after the rule was gone from .gitignore")

        # --- B4: the SAME rule, but with NO `.git` nearby — must not accuse.
        # It is cause 2 measured this session: a `.gitignore` is only read by
        # git-aware tools INSIDE a real repository. Without this control, the
        # detector would confuse "there is a file called .gitignore" with
        # "something actually respects this rule". ---
        raiz4 = base / "b4"
        (raiz4 / "escondida").mkdir(parents=True)
        (raiz4 / "escondida" / "AGENTS.md").write_text("x", encoding="utf-8")
        (raiz4 / ".gitignore").write_text("escondida/\n", encoding="utf-8")
        silencioso4 = not _algum_gitignore(raiz4)
        print(f"  {'ok   ' if silencioso4 else 'FAIL '} B4   .gitignore with no `.git` nearby "
              f"does not accuse (the rule does not apply outside a repo)")
        if not silencioso4:
            falhas.append("B4: accused a .gitignore even with no `.git` — cause 2 does not apply there")

        # --- B5: a folder with no boundary at all comes out clean ---
        raiz5 = base / "b5"
        (raiz5 / "comum").mkdir(parents=True)
        (raiz5 / "comum" / "README.md").write_text("x", encoding="utf-8")
        limpo5 = detectar(raiz5) == []
        print(f"  {'ok   ' if limpo5 else 'FAIL '} B5   a folder with no junction/symlink/gitignore "
              f"comes out with zero boundaries")
        if not limpo5:
            falhas.append("B5: found a boundary in a tree with no reparse point and no .gitignore")

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
