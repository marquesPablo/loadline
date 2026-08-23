"""Sondas da operação `handoff-que-mede-o-disco`.

natureza: correcao — sonda que estoura vira `SEM_PROVA` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_hand_`).

⚠️ **ESTA SONDA NUNCA EXECUTA O QUE O DOCUMENTO MANDA.** O arquivo de retomada é
um documento; ele pode ter sido escrito por qualquer pessoa, colado de qualquer
lugar, ou editado por um agente. Uma sonda que rodasse os comandos citados nele
seria execução arbitrária a partir de texto — injeção com convite escrito.

O que ela faz é **checar se o ALVO existe**: o arquivo de script, o alvo do
`make`, a chave em `scripts` do `package.json`. Um comando cujo alvo sumiu é o
defeito que interessa, e descobri-lo não exige rodá-lo.

⚠️ **A regra anti-espelho, aqui.** O número escrito mora no arquivo de retomada
("três verificações passam", "o repositório está limpo"). O número medido sai do
**git** e do **sistema de arquivos** — nunca do documento que o afirma. É a
separação inteira: um handoff é uma afirmação sobre o disco, e só o disco a
confirma.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from aferido import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO desta operação: como se chama o seu arquivo de retomada.
#: O primeiro que existir ganha. Se o seu tem outro nome, ponha-o na frente.
NOMES_DE_HANDOFF = ("CONTINUAR.md", "HANDOFF.md", "RETOMAR.md", "CONTEXT.md", "STATE.md")

#: Extensões que contam como script citável. Fechada de propósito: uma citação a
#: `dados.csv` é um caminho, não um comando, e confundir os dois inflaria a
#: contagem de comandos com arquivos que ninguém executa.
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

#: Um caminho citado: tem barra E ou termina em `/`, ou o último segmento tem
#: extensão. Exigir os dois não é rigor — é o que separa caminho de tudo o mais
#: que leva barra num documento técnico.
#:
#: ⚠️ Medido contra um arquivo de retomada real de 667 linhas: a versão frouxa
#: (só «tem barra») acusou 20 caminhos mortos, e a MAIORIA era falso positivo —
#: `Q10/Q11/Q12` (nomes de check enumerados), `origin/feat/algo` e
#: `feat/algo` (referências de git), `grupo/subpasta` (nome de pasta de
#: vault, relativo a outra raiz). Uma sonda que grita vinte vezes é uma sonda
#: que a pessoa desliga na segunda semana — e aí ela deixa de pegar as três
#: reais junto com as dezessete falsas.
_HAND_CAMINHO = re.compile(r"`([\w.@-]+(?:[/\\][\w.@-]+)*[/\\][\w.@-]+\.\w{1,6}|[\w.@-]+(?:[/\\][\w.@-]+)*[/\\])`")

#: Referência de git nunca é caminho de arquivo, e as duas se parecem.
_HAND_REF_DE_GIT = re.compile(
    r"^(?:origin|upstream|refs|HEAD)[/@]|^(?:feat|fix|chore|docs|hotfix|release)/", re.I
)

#: O que o documento AFIRMA sobre o estado do git.
_HAND_DIZ_LIMPO = re.compile(
    r"\b(?:tudo\s+)?(?:commitado|comitado|limpo|sem\s+pend[êe]ncia|nothing\s+to\s+commit|"
    r"working\s+tree\s+clean|sem\s+altera[çc][õo]es)\b",
    re.I,
)


def _hand_arquivo() -> Path:
    for nome in NOMES_DE_HANDOFF:
        alvo = RAIZ / nome
        if alvo.is_file():
            return alvo
    raise LookupError(
        f"não achei arquivo de retomada. Procurei por {', '.join(NOMES_DE_HANDOFF)} na raiz. "
        "Se o seu tem outro nome, ponha-o em NOMES_DE_HANDOFF no topo de sondas.py — devolver "
        "zero aqui seria dizer que o seu handoff está impecável, quando o que houve foi eu não "
        "ter encontrado nenhum"
    )


def _hand_texto() -> str:
    return _hand_arquivo().read_text(encoding="utf-8", errors="replace")


def _hand_git(*argumentos: str) -> str:
    """`git` na raiz, com stdin fechado.

    ⚠️ `stdin=DEVNULL` não é preciosismo: um `git` que resolva pedir credencial
    ou abrir editor trava o processo para sempre, e o sintoma — a suíte pendurada
    sem mensagem — aparece longe da causa.
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
        raise LookupError(f"não consegui rodar o git: {exc}") from exc
    if saida.returncode != 0:
        raise LookupError(
            f"`git {' '.join(argumentos)}` falhou: {(saida.stderr or '').strip()[:200]}. "
            "Esta operação mede um documento contra o histórico; sem git não há segundo lado"
        )
    return saida.stdout


def _hand_comandos() -> list[str]:
    """Comandos citados no documento, em crase ou depois de `$`."""
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
    """O alvo do comando existe? **Sem executar nada** — ver o aviso do topo."""
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
        # `python -m pacote` e afins: não há arquivo para conferir, e inventar um
        # veredito seria pior que declarar que esta sonda não alcança o caso.
        return True
    return (RAIZ / caminho).is_file()


def _hand_caminhos() -> list[str]:
    vistos: list[str] = []
    for bruto in _HAND_CAMINHO.findall(_hand_texto()):
        limpo = bruto.strip().replace("\\", "/")
        if limpo.startswith(("http", "//")) or "..." in limpo:
            continue  # URL, e caminho abreviado em prosa (`.../ADR-008-...md`)
        if _HAND_REF_DE_GIT.match(limpo):
            continue
        if limpo not in vistos:
            vistos.append(limpo)
    return vistos


# ---------------------------------------------------------------------------
# As sondas
# ---------------------------------------------------------------------------


@sonda(
    "handoff.commits_desde",
    origem="commits do repositório posteriores ao último toque no arquivo de retomada",
)
def hand_commits_desde() -> int:
    """De CONTAGEM, e é o número que abre a conversa.

    Ele responde a única pergunta que importa sobre um documento de retomada:
    **quanta coisa aconteceu desde que alguém o escreveu?** Um handoff com 40
    commits em cima não está errado — está desatualizado, que é diferente e é
    pior, porque ele continua parecendo o estado atual.

    ⚠️ Ele lê o `mtime` do arquivo, e o `git` não preserva `mtime`: num clone
    limpo tudo nasce com o mesmo instante e este número estoura para o total de
    commits do repositório. **É medida da árvore de trabalho de quem edita**, e
    a `RECEITA.md` diz isso em voz alta.
    """
    arquivo = _hand_arquivo()
    quando = arquivo.stat().st_mtime
    linhas = _hand_git("log", "--format=%ct", "-n", "500").splitlines()
    if not linhas:
        raise LookupError("o repositório não tem commit nenhum — não há contra o que medir")
    return sum(1 for l in linhas if l.strip().isdigit() and int(l) > quando)


@sonda(
    "handoff.caminhos_citados",
    origem="caminhos entre crases no arquivo de retomada, distintos",
)
def hand_caminhos_citados() -> int:
    return len(_hand_caminhos())


@sonda(
    "handoff.caminhos_mortos",
    origem="caminhos citados no documento que NÃO existem no disco",
)
def hand_caminhos_mortos() -> int:
    """De RELAÇÃO. Um caminho morto é a forma mais barata de um documento mentir.

    Ele não parece errado: parece específico. Quem lê vai até lá, não encontra,
    e a conclusão natural é «devo estar no lugar errado» — não «o documento
    está velho».

    ⚠️ **Resolve tudo a partir da RAIZ do repositório, e isso é decisão, não
    limitação.** Um caminho citado como `00-mapa/vazios.md`, que só existe sob
    `cerebro/`, conta como morto aqui — porque conta como morto para quem
    copiar a linha e colar no terminal. O conserto é escrever o caminho inteiro,
    e é o mesmo conserto que serve ao leitor. Medido num arquivo real: 11 dos 44
    caminhos citados eram desta classe.
    """
    return sum(1 for c in _hand_caminhos() if not (RAIZ / c).exists())


@sonda("handoff.comandos_citados", origem="comandos executáveis citados no documento")
def hand_comandos_citados() -> int:
    return len(_hand_comandos())


@sonda(
    "handoff.comandos_sem_alvo",
    origem="comandos cujo script, alvo de make ou script de pacote NÃO existe — sem executar nada",
)
def hand_comandos_sem_alvo() -> int:
    """De RELAÇÃO. O documento manda rodar uma coisa que não está mais lá.

    ⚠️ **Nada é executado para descobrir isso.** Ver o aviso no topo do arquivo:
    rodar comando lido de um documento é execução arbitrária a partir de texto.
    Conferir a EXISTÊNCIA do alvo pega o defeito sem abrir essa porta.
    """
    return sum(1 for c in _hand_comandos() if not _hand_alvo_existe(c))


@sonda(
    "handoff.deriva_de_git",
    origem="o que o documento AFIRMA sobre o estado do repositório × `git status` de agora",
)
def hand_deriva_de_git() -> int:
    """De RELAÇÃO, e é 0 ou 1 — não é uma contagem disfarçada.

    O documento diz «está tudo commitado» e há doze arquivos sujos. Ou o
    contrário. É a asserção mais fácil de escrever num handoff e a que envelhece
    mais rápido: ela pode ficar falsa antes de você fechar o editor.

    Se o documento **não afirma nada** sobre o estado, o resultado é 0 — silêncio
    não é asserção, e acusá-lo transformaria a sonda numa cobrança de estilo.
    """
    sujo = bool(_hand_git("status", "--porcelain").strip())
    diz_limpo = bool(_HAND_DIZ_LIMPO.search(_hand_texto()))
    return 1 if (diz_limpo and sujo) else 0


@sonda(
    "handoff.linhas",
    origem="linhas não vazias do arquivo de retomada",
)
def hand_linhas() -> int:
    """De CONTAGEM, e ela existe por um motivo específico.

    Um documento de retomada morre de duas formas: envelhecendo, e **inchando**.
    O segundo é mais silencioso — ninguém o rejeita, ninguém o lê, e ele passa a
    ocupar o começo de toda sessão sem devolver nada. Medido nesta casa: um
    arquivo de retomada chegou a ocupar a maior parte do caminho de boot.

    Não há limiar aqui, de propósito: o número certo depende do projeto. Sele-o
    como `arbitrado:` com um teto seu, e o `vence=` obriga a reolhar.
    """
    return sum(1 for l in _hand_texto().splitlines() if l.strip())


@sonda(
    "handoff.sessoes_desde",
    origem="arquivos de transcrito do harness modificados depois do arquivo de retomada",
)
def hand_sessoes_desde() -> int:
    """De CONTAGEM. Quantas sessões rodaram sem ninguém atualizar a retomada.

    ⚠️ **Ela estoura quando não acha a pasta de transcritos**, em vez de devolver
    zero — e a diferença importa: *nenhuma sessão desde então* e *não sei onde
    ficam as suas sessões* são leituras opostas, e a segunda disfarçada de
    primeira é um verde inventado.
    """
    candidatas = [
        Path.home() / ".claude" / "projects",
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "claude",
    ]
    base = next((c for c in candidatas if c.is_dir()), None)
    if base is None:
        raise LookupError(
            "não achei a pasta de transcritos do harness. Esta sonda é a única daqui que olha "
            "para fora do repositório; se o seu harness guarda sessão noutro lugar, ajuste a "
            "lista `candidatas` — zero aqui seria «nenhuma sessão», que é outra coisa"
        )
    quando = _hand_arquivo().stat().st_mtime
    return sum(
        1
        for arquivo in base.rglob("*.jsonl")
        if arquivo.is_file() and arquivo.stat().st_mtime > quando
    )
