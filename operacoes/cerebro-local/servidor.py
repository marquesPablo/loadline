"""A read-only MCP server over YOUR notes. Zero dependencies.

nature: security — every path decision in this module is a REFUSAL, and it
fails closed. A path that leaves the declared root is not read; a path the
server cannot resolve is not read. A file reader that fails open hands the
whole disk to anyone who asks with enough `../`.

    $ python servidor.py --root ~/notes          # speaks MCP over stdin/stdout
    $ python servidor.py --root ~/notes --test    # runs with no client, and prints

Register it in your MCP client (the example is the Claude Code format, in
`.mcp.json`; other clients use the same command/args/env trio):

    {
      "mcpServers": {
        "notes": {
          "command": "python",
          "args": ["servidor.py", "--root", "/path/to/your/notes"]
        }
      }
    }

## The three decisions that make this file fit on a page

1. **Read-only, and it is structural.** There is no tool that writes. It is not
   a promise in the prompt — it is the absence of the code.
2. **No model, no key, no network.** The intelligence belongs to the MCP client
   that is already paid for. This process is a file reader with a contract.
3. **The root is declared and the path is resolved against it.** Everything
   else is a consequence of that.

## The trap that costs dearly, and it gives no error

`rg`, `grep -r` and `find` **do not cross a Windows junction or a directory
symlink**, and they do not warn. The search comes back plausible, with no
error, and without the files inside. Python's `os.walk` **does cross**. If your
notes live in linked folders — and in a knowledge vault they almost always do —
a search done with the wrong tool answers with half the corpus and the same
look of being right.

That is why `search` here is `os.walk`, and not a `subprocess` calling `grep`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

VERSAO = "1.0.0"
PROTOCOLO = "2024-11-05"

#: Served extensions. Closed on purpose: a server that serves any file serves
#: `.env` and a private key. Add to it consciously.
EXTENSOES = (".md", ".markdown", ".txt", ".org")

#: Never descend here, even if it is under the root.
IGNORAR = {".git", ".obsidian", "node_modules", "__pycache__", ".venv", ".trash"}

LIMITE_DE_BUSCA = 200
LIMITE_DE_NOTA = 400_000  # bytes; above this the note comes out truncated WITH A WARNING


class ForaDaRaiz(ValueError):
    """The requested path does not fall under the declared root. A refusal, never a read."""


# ---------------------------------------------------------------------------
# The corpus
# ---------------------------------------------------------------------------


class Corpus:
    def __init__(self, raiz: Path) -> None:
        self.raiz = raiz.expanduser().resolve()
        if not self.raiz.is_dir():
            raise SystemExit(f"the root `{self.raiz}` is not a folder that exists")

    def resolver(self, relativo: str) -> Path:
        """A relative path -> absolute, or `ForaDaRaiz`.

        `resolve()` on BOTH sides before comparing. Comparing the raw string
        would let `..`, a link and uppercase through on a case-insensitive
        system — and that is how a notes reader becomes a reader of `~/.ssh`.
        """
        alvo = (self.raiz / relativo).resolve()
        if alvo != self.raiz and self.raiz not in alvo.parents:
            raise ForaDaRaiz(
                f"`{relativo}` resolves outside the declared root. This server reads "
                f"under `{self.raiz}` and nothing else."
            )
        return alvo

    def notas(self) -> list[Path]:
        """Every servable note, sorted. `os.walk` because it CROSSES a junction."""
        achadas: list[Path] = []
        for pasta, subpastas, arquivos in os.walk(self.raiz, followlinks=True):
            subpastas[:] = sorted(s for s in subpastas if s not in IGNORAR and not s.startswith("."))
            for arquivo in sorted(arquivos):
                if arquivo.lower().endswith(EXTENSOES):
                    achadas.append(Path(pasta) / arquivo)
        return achadas

    def relativo(self, caminho: Path) -> str:
        return caminho.relative_to(self.raiz).as_posix()


# ---------------------------------------------------------------------------
# The four tools
# ---------------------------------------------------------------------------


def mapa(corpus: Corpus) -> str:
    notas = corpus.notas()
    pastas: dict[str, int] = {}
    for nota in notas:
        chave = corpus.relativo(nota).split("/")[0] if "/" in corpus.relativo(nota) else "."
        pastas[chave] = pastas.get(chave, 0) + 1

    linhas = [
        f"root: {corpus.raiz}",
        f"servable notes: {len(notas)}  (extensions: {', '.join(EXTENSOES)})",
        "",
        "by first-level folder:",
    ]
    linhas += [f"  {nome:<40} {n:>5}" for nome, n in sorted(pastas.items(), key=lambda p: -p[1])]
    linhas += [
        "",
        "how to read a whole note:  read_note(path)  — the path comes from list_notes or search",
        "",
        "⚠️ this map counts what THIS server serves. A file with another extension, or inside "
        f"{sorted(IGNORAR)}, exists on disk and does not show up here — it is a declared denominator, not an absence.",
    ]
    return "\n".join(linhas)


def listar_notas(corpus: Corpus, pasta: str = "") -> str:
    alvo = corpus.resolver(pasta) if pasta else corpus.raiz
    dentro = [n for n in corpus.notas() if alvo == n or alvo in n.parents]
    if not dentro:
        return f"no note under `{pasta or '.'}` — the folder exists and is empty for this server"
    return "\n".join(f"{corpus.relativo(n)}  ({n.stat().st_size} bytes)" for n in dentro)


def ler_nota(corpus: Corpus, caminho: str) -> str:
    alvo = corpus.resolver(caminho)
    if not alvo.is_file():
        return f"`{caminho}` is not a file. Use list_notes to see what exists."
    if not alvo.name.lower().endswith(EXTENSOES):
        return (
            f"`{caminho}` has no servable extension ({', '.join(EXTENSOES)}). "
            "This server does not read an arbitrary file — it is the refusal, not a failure."
        )
    bruto = alvo.read_bytes()
    texto = bruto[:LIMITE_DE_NOTA].decode("utf-8", errors="replace")
    if len(bruto) > LIMITE_DE_NOTA:
        texto += (
            f"\n\n⚠️ TRUNCATED — this note has {len(bruto)} bytes and {LIMITE_DE_NOTA} were "
            "served. The rest exists and is not here."
        )
    return texto


def buscar(corpus: Corpus, termo: str) -> str:
    """A literal search, no index. Returns `path:line` and the whole line.

    No index on purpose: an index falls behind, and the lag is silent — it
    answers with yesterday's corpus and today's confidence.
    """
    if not termo.strip():
        return "empty term — I will not return the whole corpus pretending it was a search"
    agulha = termo.lower()
    achados: list[str] = []
    lidas = 0
    for nota in corpus.notas():
        lidas += 1
        try:
            linhas = nota.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for numero, linha in enumerate(linhas, 1):
            if agulha in linha.lower():
                achados.append(f"{corpus.relativo(nota)}:{numero}: {linha.strip()[:200]}")
                if len(achados) >= LIMITE_DE_BUSCA:
                    achados.append(
                        f"⚠️ STOPPED at {LIMITE_DE_BUSCA} matches. There are more, and they are not "
                        "here — refine the term instead of treating this as the complete list."
                    )
                    return "\n".join(achados)
    if not achados:
        return f"did not find `{termo}` in any of the {lidas} served notes."
    return "\n".join(achados)


FERRAMENTAS = [
    {
        "name": "map",
        "description": (
            "The corpus map: the root, how many notes are served and how they are spread across "
            "folders. CALL FIRST, every session — this is where the paths the other tools accept "
            "come from."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_notes",
        "description": "Lists the notes in a folder (or the whole corpus), with the size of each.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "a path relative to the root; empty = everything"}
            },
        },
    },
    {
        "name": "read_note",
        "description": "Returns the full text of a note. The path is relative to the root.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "search",
        "description": (
            "Searches for a literal term across all notes and returns `path:line` with the whole "
            "line. Crosses a junction and a directory symlink, which is where `grep -r` lies."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"term": {"type": "string"}},
            "required": ["term"],
        },
    },
]

DESPACHO = {
    "map": lambda c, a: mapa(c),
    "list_notes": lambda c, a: listar_notas(c, a.get("folder", "")),
    "read_note": lambda c, a: ler_nota(c, a.get("path", "")),
    "search": lambda c, a: buscar(c, a.get("term", "")),
}


# ---------------------------------------------------------------------------
# The protocol
# ---------------------------------------------------------------------------


def responder(corpus: Corpus, pedido: dict) -> dict | None:
    """One JSON-RPC request -> one response, or None when it is a notification.

    A notification (a request with no `id`) does NOT get a response. Answering
    one breaks clients that count messages, and the symptom shows up far from
    the cause.
    """
    metodo = pedido.get("method", "")
    ident = pedido.get("id")

    if metodo == "initialize":
        resultado = {
            "protocolVersion": PROTOCOLO,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "cerebro-local", "version": VERSAO},
        }
    elif metodo == "tools/list":
        resultado = {"tools": FERRAMENTAS}
    elif metodo == "tools/call":
        parametros = pedido.get("params") or {}
        nome = parametros.get("name", "")
        argumentos = parametros.get("arguments") or {}
        if nome not in DESPACHO:
            return _erro(ident, -32601, f"unknown tool: {nome}")
        try:
            texto = DESPACHO[nome](corpus, argumentos)
        except ForaDaRaiz as exc:
            texto = f"REFUSED: {exc}"
        except Exception as exc:  # the tool blew up: say which and why
            texto = f"the tool `{nome}` blew up: {type(exc).__name__}: {exc}"
        resultado = {"content": [{"type": "text", "text": texto}]}
    elif ident is None:
        return None  # a notification we do not care about (`notifications/initialized`)
    else:
        return _erro(ident, -32601, f"method not implemented: {metodo}")

    if ident is None:
        return None
    return {"jsonrpc": "2.0", "id": ident, "result": resultado}


def _erro(ident, codigo: int, mensagem: str) -> dict:
    return {"jsonrpc": "2.0", "id": ident, "error": {"code": codigo, "message": mensagem}}


def servir(corpus: Corpus, entrada=None, saida=None) -> None:
    """The stdio loop. One JSON message per line.

    ⚠️ Nothing here may write to stdout other than a JSON response. A stray
    debug `print` corrupts the protocol channel, and the client reports "the
    server did not answer" without ever showing the text you printed.
    """
    entrada = entrada or sys.stdin
    saida = saida or sys.stdout
    for linha in entrada:
        linha = linha.strip()
        if not linha:
            continue
        try:
            pedido = json.loads(linha)
        except json.JSONDecodeError:
            continue  # junk on the channel does not take the server down
        resposta = responder(corpus, pedido)
        if resposta is not None:
            saida.write(json.dumps(resposta, ensure_ascii=False) + "\n")
            saida.flush()


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("--root", "--raiz", dest="raiz", required=True, help="the folder of your notes")
    analisador.add_argument(
        "--test",
        "--teste",
        dest="teste",
        action="store_true",
        help="does not speak MCP: calls the four tools and prints, so you can see it works",
    )
    argumentos = analisador.parse_args()
    corpus = Corpus(Path(argumentos.raiz))

    if argumentos.teste:
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError, OSError):
                pass
        print("=== map() ===")
        print(mapa(corpus))
        notas = corpus.notas()
        if notas:
            primeira = corpus.relativo(notas[0])
            print(f"\n=== read_note({primeira!r}) — first 15 lines ===")
            print("\n".join(ler_nota(corpus, primeira).splitlines()[:15]))
        print("\n=== search('todo') ===")
        print("\n".join(buscar(corpus, "todo").splitlines()[:10]))
        print("\n=== the refusal, proven ===")
        try:
            corpus.resolver("../../../etc/passwd")
        except ForaDaRaiz as exc:
            print(f"REFUSED, as it must: {exc}")
        else:
            print("⚠️ DID NOT REFUSE — this is a defect, not a detail")
        return 0

    servir(corpus)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
