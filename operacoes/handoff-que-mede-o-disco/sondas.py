"""Probes for the `handoff-que-mede-o-disco` operation.

nature: fix — a probe that blows up becomes `UNPROVEN` in the report, with
the error written out. It never returns a guess.

COPY THIS FILE to the root of your repository, as `sondas.py`.
To combine with another operation, concatenate the files — no helper name here
collides with the others' (they all start with `_hand_`).

⚠️ **THIS PROBE NEVER EXECUTES WHAT THE DOCUMENT TELLS YOU TO.** The handoff file
is a document; it could have been written by anyone, pasted from anywhere, or
edited by an agent. A probe that ran the commands cited in it would be arbitrary
execution from text — injection with a written invitation.

What it does is **check whether the TARGET exists**: the script file, the `make`
target, the key in `package.json`'s `scripts`. A command whose target
disappeared is the defect that matters, and finding it does not require running it.

⚠️ **The anti-mirror rule, here.** The written number lives in the handoff file
("three checks pass", "the repository is clean"). The measured number comes from
**git** and the **file system** — never from the document that claims it. It is
the whole separation: a handoff is a claim about the disk, and only the disk
confirms it.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: THE ONE ADJUSTMENT of this operation: what your handoff file is called.
#: The first one that exists wins. If yours has another name, put it in front.
NOMES_DE_HANDOFF = ("CONTINUAR.md", "HANDOFF.md", "RETOMAR.md", "CONTEXT.md", "STATE.md")

#: Extensions that count as a citable script. Closed on purpose: a citation to
#: `dados.csv` is a path, not a command, and confusing the two would inflate the
#: command count with files nobody runs.
_HAND_SCRIPT = (".py", ".sh", ".ps1", ".js", ".ts", ".rb", ".go", ".bat", ".cmd")

#: `python scripts/verificar.py`, `bash scripts/deploy.sh`, `./run.sh`
_HAND_COMANDO = re.compile(
    r"`([^`\n]{3,160})`|^\s{0,3}\$\s+([^\n]{3,160})$", re.M
)
_HAND_INTERPRETADOR = re.compile(
    r"^(?:python3?|py|bash|sh|zsh|pwsh|powershell|node|npx|ruby|go\s+run|deno)\s+(\S+)", re.I
)
_HAND_NPM = re.compile(r"^(?:npm|pnpm|yarn|bun)\s+run\s+([\w:.-]+)", re.I)
_HAND_MAKE = re.compile(r"^make\s+([\w:.-]+)", re.I)

#: A cited path: it has a slash AND either ends in `/`, or the last segment has
#: an extension. Requiring both is not rigor — it is what separates a path from
#: everything else that carries a slash in a technical document.
#:
#: ⚠️ Measured against a real 667-line handoff file: the loose version (just
#: «has a slash») flagged 20 dead paths, and MOST were false positives —
#: `Q10/Q11/Q12` (enumerated check names), `origin/feat/algo` and `feat/algo`
#: (git references), `grupo/subpasta` (a vault folder name, relative to another
#: root). A probe that shouts twenty times is a probe the person switches off in
#: the second week — and then it stops catching the three real ones along with
#: the seventeen false.
_HAND_CAMINHO = re.compile(r"`([\w.@-]+(?:[/\\][\w.@-]+)*[/\\][\w.@-]+\.\w{1,6}|[\w.@-]+(?:[/\\][\w.@-]+)*[/\\])`")

#: A git reference is never a file path, and the two look alike.
_HAND_REF_DE_GIT = re.compile(
    r"^(?:origin|upstream|refs|HEAD)[/@]|^(?:feat|fix|chore|docs|hotfix|release)/", re.I
)

#: What the document CLAIMS about the git state.
_HAND_DIZ_LIMPO = re.compile(
    r"\b(?:tudo\s+)?(?:commitado|comitado|limpo|sem\s+pend[êe]ncia|nothing\s+to\s+commit|"
    r"working\s+tree\s+clean|sem\s+altera[çc][õo]es|committed|all\s+committed|no\s+changes)\b",
    re.I,
)


def _hand_arquivo() -> Path:
    for nome in NOMES_DE_HANDOFF:
        alvo = RAIZ / nome
        if alvo.is_file():
            return alvo
    raise LookupError(
        f"did not find a handoff file. Looked for {', '.join(NOMES_DE_HANDOFF)} at the root. "
        "If yours has another name, put it in NOMES_DE_HANDOFF at the top of sondas.py — returning "
        "zero here would be saying your handoff is flawless, when what happened is I did not find "
        "any"
    )


def _hand_texto() -> str:
    return _hand_arquivo().read_text(encoding="utf-8", errors="replace")


def _hand_git(*argumentos: str) -> str:
    """`git` at the root, with stdin closed.

    ⚠️ `stdin=DEVNULL` is not fussiness: a `git` that decides to ask for a
    credential or open an editor hangs the process forever, and the symptom —
    the suite hanging with no message — shows up far from the cause.
    """
    try:
        saida = subprocess.run(
            ["git", "-C", str(RAIZ), *argumentos],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise LookupError(f"could not run git: {exc}") from exc
    if saida.returncode != 0:
        raise LookupError(
            f"`git {' '.join(argumentos)}` failed: {(saida.stderr or '').strip()[:200]}. "
            "This operation measures a document against the history; with no git there is no second side"
        )
    return saida.stdout


def _hand_comandos() -> list[str]:
    """Commands cited in the document, in backticks or after a `$`."""
    achados: list[str] = []
    for cheio, cifrao in _HAND_COMANDO.findall(_hand_texto()):
        bruto = (cheio or cifrao or "").strip()
        if not bruto or bruto.startswith(("#", "//", "<!--")):
            continue
        if (
            _HAND_INTERPRETADOR.match(bruto)
            or _HAND_NPM.match(bruto)
            or _HAND_MAKE.match(bruto)
            or (bruto.startswith("./") and bruto.split()[0].endswith(_HAND_SCRIPT))
        ):
            achados.append(bruto)
    return achados


def _hand_alvo_existe(comando: str) -> bool:
    """Does the command's target exist? **Without executing anything** — see the top warning."""
    npm = _HAND_NPM.match(comando)
    if npm:
        pacote = RAIZ / "package.json"
        if not pacote.is_file():
            return False
        try:
            dados = json.loads(pacote.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            return False
        return npm.group(1) in (dados.get("scripts") or {})

    alvo_make = _HAND_MAKE.match(comando)
    if alvo_make:
        arquivo = next((RAIZ / n for n in ("Makefile", "makefile", "GNUmakefile") if (RAIZ / n).is_file()), None)
        if arquivo is None:
            return False
        regra = re.compile(rf"^{re.escape(alvo_make.group(1))}\s*:", re.M)
        return bool(regra.search(arquivo.read_text(encoding="utf-8", errors="replace")))

    interpretado = _HAND_INTERPRETADOR.match(comando)
    caminho = interpretado.group(1) if interpretado else comando.split()[0]
    caminho = caminho.strip("\"'").lstrip("./")
    if not caminho.endswith(_HAND_SCRIPT):
        # `python -m package` and the like: there is no file to check, and
        # inventing a verdict would be worse than declaring that this probe does
        # not reach the case.
        return True
    return (RAIZ / caminho).is_file()


def _hand_caminhos() -> list[str]:
    vistos: list[str] = []
    for bruto in _HAND_CAMINHO.findall(_hand_texto()):
        limpo = bruto.strip().replace("\\", "/")
        if limpo.startswith(("http", "//")) or "..." in limpo:
            continue  # a URL, and a path abbreviated in prose (`.../ADR-008-...md`)
        if _HAND_REF_DE_GIT.match(limpo):
            continue
        if limpo not in vistos:
            vistos.append(limpo)
    return vistos


# ---------------------------------------------------------------------------
# The probes
# ---------------------------------------------------------------------------


@sonda(
    "handoff.commits_desde",
    origem="repository commits later than the last touch on the handoff file",
)
def hand_commits_desde() -> int:
    """A COUNT, and it is the number that opens the conversation.

    It answers the only question that matters about a handoff document: **how
    much happened since someone wrote it?** A handoff with 40 commits on top of
    it is not wrong — it is out of date, which is different and worse, because it
    still looks like the current state.

    ⚠️ It reads the file's `mtime`, and `git` does not preserve `mtime`: in a
    clean clone everything is born with the same instant and this number blows up
    to the repository's total commits. **It is a measure of the working tree of
    whoever edits**, and `RECEITA.md` says so out loud.
    """
    arquivo = _hand_arquivo()
    quando = arquivo.stat().st_mtime
    linhas = _hand_git("log", "--format=%ct", "-n", "500").splitlines()
    if not linhas:
        raise LookupError("the repository has no commit at all — there is nothing to measure against")
    return sum(1 for l in linhas if l.strip().isdigit() and int(l) > quando)


@sonda(
    "handoff.caminhos_citados",
    origem="distinct paths between backticks in the handoff file",
)
def hand_caminhos_citados() -> int:
    return len(_hand_caminhos())


@sonda(
    "handoff.caminhos_mortos",
    origem="paths cited in the document that do NOT exist on disk",
)
def hand_caminhos_mortos() -> int:
    """A RELATION. A dead path is the cheapest way a document lies.

    It does not look wrong: it looks specific. Whoever reads it goes there, does
    not find it, and the natural conclusion is «I must be in the wrong place» —
    not «the document is old».

    ⚠️ **It resolves everything from the repository ROOT, and that is a decision,
    not a limitation.** A path cited as `notas/x.md`, that only exists under
    `outra-pasta/`, counts as dead here — because it counts as dead for whoever
    copies the line and pastes it into the terminal. The fix is to write the
    whole path, and it is the same fix that serves the reader. Measured in a real
    file: 11 of the 44 cited paths were of this class.
    """
    return sum(1 for c in _hand_caminhos() if not (RAIZ / c).exists())


@sonda("handoff.comandos_citados", origem="executable commands cited in the document")
def hand_comandos_citados() -> int:
    return len(_hand_comandos())


@sonda(
    "handoff.comandos_sem_alvo",
    origem="commands whose script, make target or package script does NOT exist — without executing anything",
)
def hand_comandos_sem_alvo() -> int:
    """A RELATION. The document tells you to run something that is no longer there.

    ⚠️ **Nothing is executed to find this out.** See the warning at the top of
    the file: running a command read from a document is arbitrary execution from
    text. Checking the EXISTENCE of the target catches the defect without opening
    that door.
    """
    return sum(1 for c in _hand_comandos() if not _hand_alvo_existe(c))


@sonda(
    "handoff.deriva_de_git",
    origem="what the document CLAIMS about the state of the repository × today's `git status`",
)
def hand_deriva_de_git() -> int:
    """A RELATION, and it is 0 or 1 — not a disguised count.

    The document says «everything is committed» and there are twelve dirty files.
    Or the opposite. It is the easiest claim to write in a handoff and the one
    that ages fastest: it can go false before you close the editor.

    If the document **claims nothing** about the state, the result is 0 — silence
    is not an assertion, and accusing it would turn the probe into a style demand.
    """
    sujo = bool(_hand_git("status", "--porcelain").strip())
    diz_limpo = bool(_HAND_DIZ_LIMPO.search(_hand_texto()))
    return 1 if (diz_limpo and sujo) else 0


@sonda(
    "handoff.linhas",
    origem="non-empty lines of the handoff file",
)
def hand_linhas() -> int:
    """A COUNT, and it exists for a specific reason.

    A handoff document dies in two ways: by aging, and by **bloating**. The
    second is quieter — nobody rejects it, nobody reads it, and it starts taking
    up the beginning of every session without giving anything back. Measured
    here: a handoff file grew to take up most of the boot path.

    There is no threshold here, on purpose: the right number depends on the
    project. Seal it as `arbitrated:` with a ceiling of yours, and `expires=`
    forces a re-look.
    """
    return sum(1 for l in _hand_texto().splitlines() if l.strip())


@sonda(
    "handoff.sessoes_desde",
    origem="harness transcript files modified after the handoff file",
)
def hand_sessoes_desde() -> int:
    """A COUNT. How many sessions ran without anyone updating the handoff.

    ⚠️ **It blows up when it does not find the transcripts folder**, instead of
    returning zero — and the difference matters: *no session since then* and *I
    do not know where your sessions are* are opposite readings, and the second
    disguised as the first is an invented green.
    """
    candidatas = [
        Path.home() / ".claude" / "projects",
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "claude",
    ]
    base = next((c for c in candidatas if c.is_dir()), None)
    if base is None:
        raise LookupError(
            "did not find the harness transcripts folder. This probe is the only one here that "
            "looks outside the repository; if your harness keeps sessions somewhere else, adjust "
            "the `candidatas` list — zero here would be «no session», which is another thing"
        )
    quando = _hand_arquivo().stat().st_mtime
    return sum(
        1
        for arquivo in base.rglob("*.jsonl")
        if arquivo.is_file() and arquivo.stat().st_mtime > quando
    )
