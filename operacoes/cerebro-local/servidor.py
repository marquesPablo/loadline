"""Um servidor MCP somente-leitura sobre as SUAS notas. Zero dependências.

natureza: seguranca — toda decisão de caminho deste módulo é uma RECUSA, e ela
falha fechada. Caminho que sai da raiz declarada não é lido; caminho que o
servidor não consegue resolver não é lido. Um leitor de arquivos que falha
aberto entrega o disco inteiro para quem pedir com `../` suficiente.

    $ python servidor.py --raiz ~/notas          # fala MCP por stdin/stdout
    $ python servidor.py --raiz ~/notas --teste  # roda sem cliente, e imprime

Registre no seu cliente MCP (o exemplo é o formato do Claude Code, em
`.mcp.json`; outros clientes usam o mesmo trio comando/argumentos/ambiente):

    {
      "mcpServers": {
        "notas": {
          "command": "python",
          "args": ["servidor.py", "--raiz", "/caminho/das/suas/notas"]
        }
      }
    }

## As três decisões que fazem este arquivo caber numa página

1. **Somente leitura, e isso é estrutural.** Não há ferramenta que escreva. Não
   é uma promessa no prompt — é a ausência do código.
2. **Sem modelo, sem chave, sem rede.** A inteligência é do cliente MCP que já
   está pago. Este processo é um leitor de arquivos com contrato.
3. **A raiz é declarada e o caminho é resolvido contra ela.** Tudo o mais é
   consequência disso.

## A armadilha que custa caro, e ela não dá erro

`rg`, `grep -r` e `find` **não atravessam junction do Windows nem symlink de
diretório**, e não avisam. A busca volta plausível, sem erro, e sem os arquivos
de dentro. `os.walk` do Python **atravessa**. Se as suas notas moram em pastas
ligadas — e num vault de conhecimento elas quase sempre moram —, uma busca feita
com a ferramenta errada responde com metade do corpus e a mesma cara de certa.

Por isso `buscar` aqui é `os.walk`, e não um `subprocess` chamando `grep`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

VERSAO = "1.0.0"
PROTOCOLO = "2024-11-05"

#: Extensões servidas. Fechada de propósito: um servidor que serve qualquer
#: arquivo serve `.env` e chave privada. Acrescente conscientemente.
EXTENSOES = (".md", ".markdown", ".txt", ".org")

#: Nunca descer aqui, mesmo que esteja sob a raiz.
IGNORAR = {".git", ".obsidian", "node_modules", "__pycache__", ".venv", ".trash"}

LIMITE_DE_BUSCA = 200
LIMITE_DE_NOTA = 400_000  # bytes; acima disso a nota sai truncada COM AVISO


class ForaDaRaiz(ValueError):
    """O caminho pedido não cai sob a raiz declarada. Recusa, nunca leitura."""


# ---------------------------------------------------------------------------
# O corpus
# ---------------------------------------------------------------------------


class Corpus:
    def __init__(self, raiz: Path) -> None:
        self.raiz = raiz.expanduser().resolve()
        if not self.raiz.is_dir():
            raise SystemExit(f"a raiz `{self.raiz}` não é uma pasta que existe")

    def resolver(self, relativo: str) -> Path:
        """Caminho relativo -> absoluto, ou `ForaDaRaiz`.

        `resolve()` nos DOIS lados antes de comparar. Comparar a string crua
        deixaria passar `..`, link e maiúsculas em sistema que não diferencia —
        e é assim que um leitor de notas vira um leitor de `~/.ssh`.
        """
        alvo = (self.raiz / relativo).resolve()
        if alvo != self.raiz and self.raiz not in alvo.parents:
            raise ForaDaRaiz(
                f"`{relativo}` resolve para fora da raiz declarada. Este servidor lê "
                f"debaixo de `{self.raiz}` e nada mais."
            )
        return alvo

    def notas(self) -> list[Path]:
        """Toda nota servível, ordenada. `os.walk` porque ele ATRAVESSA junction."""
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
# As quatro ferramentas
# ---------------------------------------------------------------------------


def mapa(corpus: Corpus) -> str:
    notas = corpus.notas()
    pastas: dict[str, int] = {}
    for nota in notas:
        chave = corpus.relativo(nota).split("/")[0] if "/" in corpus.relativo(nota) else "."
        pastas[chave] = pastas.get(chave, 0) + 1

    linhas = [
        f"raiz: {corpus.raiz}",
        f"notas servíveis: {len(notas)}  (extensões: {', '.join(EXTENSOES)})",
        "",
        "por pasta de primeiro nível:",
    ]
    linhas += [f"  {nome:<40} {n:>5}" for nome, n in sorted(pastas.items(), key=lambda p: -p[1])]
    linhas += [
        "",
        "como ler uma nota inteira:  ler_nota(caminho)  — o caminho sai de listar_notas ou buscar",
        "",
        "⚠️ este mapa conta o que ESTE servidor serve. Arquivo de outra extensão, ou dentro de "
        f"{sorted(IGNORAR)}, existe no disco e não aparece aqui — é denominador declarado, não ausência.",
    ]
    return "\n".join(linhas)


def listar_notas(corpus: Corpus, pasta: str = "") -> str:
    alvo = corpus.resolver(pasta) if pasta else corpus.raiz
    dentro = [n for n in corpus.notas() if alvo == n or alvo in n.parents]
    if not dentro:
        return f"nenhuma nota sob `{pasta or '.'}` — a pasta existe e está vazia para este servidor"
    return "\n".join(f"{corpus.relativo(n)}  ({n.stat().st_size} bytes)" for n in dentro)


def ler_nota(corpus: Corpus, caminho: str) -> str:
    alvo = corpus.resolver(caminho)
    if not alvo.is_file():
        return f"`{caminho}` não é um arquivo. Use listar_notas para ver o que existe."
    if not alvo.name.lower().endswith(EXTENSOES):
        return (
            f"`{caminho}` não tem extensão servível ({', '.join(EXTENSOES)}). "
            "Este servidor não lê arquivo arbitrário — é a recusa, não uma falha."
        )
    bruto = alvo.read_bytes()
    texto = bruto[:LIMITE_DE_NOTA].decode("utf-8", errors="replace")
    if len(bruto) > LIMITE_DE_NOTA:
        texto += (
            f"\n\n⚠️ TRUNCADA — esta nota tem {len(bruto)} bytes e foram servidos "
            f"{LIMITE_DE_NOTA}. O resto existe e não está aqui."
        )
    return texto


def buscar(corpus: Corpus, termo: str) -> str:
    """Busca literal, sem índice. Devolve `caminho:linha` e a linha inteira.

    Sem índice de propósito: um índice defasa, e a defasagem é silenciosa —
    ele responde com o corpus de ontem e com a confiança de hoje.
    """
    if not termo.strip():
        return "termo vazio — não vou devolver o corpus inteiro fingindo que foi uma busca"
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
                        f"⚠️ PAREI em {LIMITE_DE_BUSCA} ocorrências. Há mais, e elas não estão "
                        "aqui — refine o termo em vez de tratar isto como a lista completa."
                    )
                    return "\n".join(achados)
    if not achados:
        return f"não encontrei `{termo}` em nenhuma das {lidas} notas servidas."
    return "\n".join(achados)


FERRAMENTAS = [
    {
        "name": "mapa",
        "description": (
            "O mapa do corpus: a raiz, quantas notas são servidas e como elas se distribuem por "
            "pasta. CHAME PRIMEIRO, em toda sessão — é de aqui que saem os caminhos que as outras "
            "ferramentas aceitam."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "listar_notas",
        "description": "Lista as notas de uma pasta (ou de todo o corpus), com o tamanho de cada uma.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pasta": {"type": "string", "description": "caminho relativo à raiz; vazio = tudo"}
            },
        },
    },
    {
        "name": "ler_nota",
        "description": "Devolve o texto integral de uma nota. O caminho é relativo à raiz.",
        "inputSchema": {
            "type": "object",
            "properties": {"caminho": {"type": "string"}},
            "required": ["caminho"],
        },
    },
    {
        "name": "buscar",
        "description": (
            "Procura um termo literal em todas as notas e devolve `caminho:linha` com a linha "
            "inteira. Atravessa junction e symlink de diretório, que é onde `grep -r` mente."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"termo": {"type": "string"}},
            "required": ["termo"],
        },
    },
]

DESPACHO = {
    "mapa": lambda c, a: mapa(c),
    "listar_notas": lambda c, a: listar_notas(c, a.get("pasta", "")),
    "ler_nota": lambda c, a: ler_nota(c, a.get("caminho", "")),
    "buscar": lambda c, a: buscar(c, a.get("termo", "")),
}


# ---------------------------------------------------------------------------
# O protocolo
# ---------------------------------------------------------------------------


def responder(corpus: Corpus, pedido: dict) -> dict | None:
    """Um pedido JSON-RPC -> uma resposta, ou None quando é notificação.

    Notificação (pedido sem `id`) NÃO recebe resposta. Responder a uma quebra
    clientes que contam mensagens, e o sintoma aparece longe da causa.
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
            return _erro(ident, -32601, f"ferramenta desconhecida: {nome}")
        try:
            texto = DESPACHO[nome](corpus, argumentos)
        except ForaDaRaiz as exc:
            texto = f"RECUSADO: {exc}"
        except Exception as exc:  # a ferramenta estourou: diga qual e por quê
            texto = f"a ferramenta `{nome}` estourou: {type(exc).__name__}: {exc}"
        resultado = {"content": [{"type": "text", "text": texto}]}
    elif ident is None:
        return None  # notificação que não nos interessa (`notifications/initialized`)
    else:
        return _erro(ident, -32601, f"método não implementado: {metodo}")

    if ident is None:
        return None
    return {"jsonrpc": "2.0", "id": ident, "result": resultado}


def _erro(ident, codigo: int, mensagem: str) -> dict:
    return {"jsonrpc": "2.0", "id": ident, "error": {"code": codigo, "message": mensagem}}


def servir(corpus: Corpus, entrada=None, saida=None) -> None:
    """O laço stdio. Uma mensagem JSON por linha.

    ⚠️ Nada aqui pode escrever em stdout além de resposta JSON. Um `print` de
    depuração perdido corrompe o canal do protocolo, e o cliente relata «servidor
    não respondeu» sem nunca mostrar o texto que você imprimiu.
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
            continue  # lixo no canal não derruba o servidor
        resposta = responder(corpus, pedido)
        if resposta is not None:
            saida.write(json.dumps(resposta, ensure_ascii=False) + "\n")
            saida.flush()


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("--raiz", required=True, help="a pasta das suas notas")
    analisador.add_argument(
        "--teste",
        action="store_true",
        help="não fala MCP: chama as quatro ferramentas e imprime, para você ver que funciona",
    )
    argumentos = analisador.parse_args()
    corpus = Corpus(Path(argumentos.raiz))

    if argumentos.teste:
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError, OSError):
                pass
        print("=== mapa() ===")
        print(mapa(corpus))
        notas = corpus.notas()
        if notas:
            primeira = corpus.relativo(notas[0])
            print(f"\n=== ler_nota({primeira!r}) — primeiras 15 linhas ===")
            print("\n".join(ler_nota(corpus, primeira).splitlines()[:15]))
        print("\n=== buscar('todo') ===")
        print("\n".join(buscar(corpus, "todo").splitlines()[:10]))
        print("\n=== a recusa, provada ===")
        try:
            corpus.resolver("../../../etc/passwd")
        except ForaDaRaiz as exc:
            print(f"RECUSADO, como tem de ser: {exc}")
        else:
            print("⚠️ NÃO RECUSOU — isto é um defeito, não um detalhe")
        return 0

    servir(corpus)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
