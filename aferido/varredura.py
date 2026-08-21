"""Varre arquivos, lê os selos, confronta a prosa, e monta o relatório com denominador.

natureza: correcao — arquivo ilegível vira linha no relatório, nunca uma
exceção que derruba a rodada e deixa o resto sem medir.

A varredura carrega as sondas do projeto por convenção: um `sondas.py` na
raiz do alvo, importado antes de julgar. Convenção em vez de configuração,
porque um campo de config com caminho a executar é convite escrito.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from datetime import date
from pathlib import Path

from .eco import PROSA_MUDA, afirmacoes_sem_selo, confrontar
from .selo import Selo, SeloMalformado, ler_linha
from .veredito import Achado, Relatorio, julgar

EXTENSOES = (".md", ".markdown", ".txt", ".py", ".rst", ".toml", ".yaml", ".yml")
IGNORAR = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".mypy_cache"}

# Um arquivo que ENSINA a sintaxe do selo não pode ser lido como se afirmasse.
# Sem isto, todo texto que documenta a ferramenta a sabota — inclusive o
# exemplo de selo malformado, que precisa poder existir escrito.
DIRETIVA_ESPECIME = "aferido-ignorar-arquivo"
_CERCA = "```"


def _linhas_de_literal(texto: str) -> set[int]:
    """Linhas de um `.py` que estão DENTRO de uma string literal.

    Esta é a regra que separa o código que **declara** um selo do código que o
    **emite**. Um selo num comentário (`# aferido: x=1`) é uma afirmação de
    verdade: alguém escreveu aquele número e ele se recompute. Um selo dentro
    de uma string é outra coisa inteira — é o gerador montando o texto que o
    USUÁRIO vai escrever, ou a documentação ensinando a sintaxe.

    Sem isto, todo emissor de selo sabota a si mesmo: `f"<!-- aferido:
    x={n} -->"` é lido como se afirmasse que `x` vale a string `{n}`. É a mesma
    família de defeito que o controle negativo que sabota a si mesmo, e ela
    reaparece em toda ferramenta que gera a própria sintaxe.

    Usa `ast` — stdlib — em vez de heurística de aspas. Um regex que tentasse
    achar string literal erraria em aspas aninhadas e em f-string com
    expressão, e erraria calado, que é o pior modo de errar aqui.

    ⚠️ **Arquivo que não parseia não vira espécime.** Devolver tudo faria um
    `.py` quebrado passar verde, calado. Devolver nada faz o selo ser julgado e,
    se estiver malformado, a rodada reprova alto. Falhar barulhento é a direção
    certa.
    """
    try:
        arvore = ast.parse(texto)
    except SyntaxError:
        return set()

    dentro: set[int] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Constant) and isinstance(no.value, str):
            dentro.update(range(no.lineno, (no.end_lineno or no.lineno) + 1))
        elif isinstance(no, ast.JoinedStr):  # f-string
            dentro.update(range(no.lineno, (no.end_lineno or no.lineno) + 1))
    return dentro


def _regioes_de_especime(linhas: list[str], markdown: bool, python: bool = False) -> set[int]:
    """Linhas (1-based) que são espécime e não afirmação.

    Três regras, todas declaradas e nenhuma adivinhada:
      1. arquivo com a diretiva `aferido-ignorar-arquivo` — o arquivo inteiro;
      2. em Markdown, o que está dentro de cerca de código — uma cerca É a
         marca universal de "isto é ilustração", e ler ilustração como
         afirmação inventa fatos que ninguém escreveu;
      3. em Python, o que está dentro de string literal — ver
         `_linhas_de_literal`. Comentário continua sendo julgado; a cerca é
         sobre a string, não sobre o arquivo.
    """
    if any(DIRETIVA_ESPECIME in linha for linha in linhas):
        return set(range(1, len(linhas) + 1))
    if python:
        return _linhas_de_literal("\n".join(linhas))
    if not markdown:
        return set()

    dentro = False
    especimes: set[int] = set()
    for n, linha in enumerate(linhas, start=1):
        if linha.lstrip().startswith(_CERCA):
            especimes.add(n)
            dentro = not dentro
        elif dentro:
            especimes.add(n)
    return especimes


def carregar_sondas(raiz: Path) -> Path | None:
    """Importa `sondas.py` da raiz do alvo, se existir. Devolve o caminho usado."""
    alvo = raiz / "sondas.py" if raiz.is_dir() else raiz.parent / "sondas.py"
    if not alvo.exists():
        return None
    spec = importlib.util.spec_from_file_location("sondas_do_projeto", alvo)
    if spec is None or spec.loader is None:
        return None
    modulo = importlib.util.module_from_spec(spec)
    sys.modules["sondas_do_projeto"] = modulo
    spec.loader.exec_module(modulo)
    return alvo


def _arquivos(raiz: Path) -> list[Path]:
    if raiz.is_file():
        return [raiz]
    achados = []
    for caminho in sorted(raiz.rglob("*")):
        if not caminho.is_file() or caminho.suffix.lower() not in EXTENSOES:
            continue
        if IGNORAR & set(caminho.parts):
            continue
        achados.append(caminho)
    return achados


def varrer(raiz: str | Path, hoje: date | None = None) -> Relatorio:
    """Lê todos os selos sob `raiz` e julga cada um contra o disco de hoje."""
    raiz = Path(raiz)
    hoje = hoje or date.today()
    carregar_sondas(raiz)

    relatorio = Relatorio(achados=[])
    for caminho in _arquivos(raiz):
        try:
            texto = caminho.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            relatorio.malformados.append(f"{caminho}: não deu para ler — {exc}")
            continue

        relatorio.arquivos_lidos += 1
        linhas = texto.splitlines()
        sufixo = caminho.suffix.lower()
        especimes = _regioes_de_especime(
            linhas,
            markdown=sufixo in (".md", ".markdown"),
            python=sufixo == ".py",
        )
        if especimes:
            relatorio.especimes.append(f"{caminho}: {len(especimes)} linhas de espécime, não julgadas")

        tinha_selo = False
        do_arquivo: list[Selo] = []
        for n, linha in enumerate(linhas, start=1):
            if n in especimes:
                continue
            try:
                selo = ler_linha(linha, arquivo=str(caminho), linha=n)
            except SeloMalformado as exc:
                relatorio.malformados.append(str(exc))
                tinha_selo = True
                continue
            if selo is None:
                continue
            tinha_selo = True
            do_arquivo.append(selo)
            relatorio.achados.extend(julgar(selo, hoje=hoje))

        # O confronto prosa × selo é só de PROSA: em `.py` o que está ao redor
        # de um selo é código, e cobrar eco de número em código acusaria todo
        # literal vizinho. A estreiteza é declarada, não esquecida.
        if sufixo in (".md", ".markdown", ".txt", ".rst"):
            # A lista 3 — o que NENHUM selo cobre. Ela roda em todo arquivo de
            # prosa, tenha ele selo ou não; num repositório recém-clonado ela é
            # a única coisa que a ferramenta tem a dizer, e é o motivo de a
            # primeira rodada ter deixado de devolver verde (ADR-107).
            relatorio.sem_prova_nenhuma.extend(
                afirmacoes_sem_selo(linhas, do_arquivo, str(caminho), especimes)
            )
            discrepancias, dispensados = confrontar(do_arquivo, linhas, str(caminho))
            for selo, numero, no_selo in discrepancias:
                relatorio.achados.append(
                    Achado(
                        PROSA_MUDA,
                        "/".join(sorted(selo.metricas)) or "—",
                        numero,
                        ", ".join(sorted(no_selo)) or "—",
                        selo,
                        selo.natureza,
                    )
                )
            for selo in dispensados:
                relatorio.dispensados_do_eco.append(f"{selo.arquivo}:{selo.linha}")

        if not tinha_selo:
            relatorio.arquivos_sem_selo.append(str(caminho))

    return relatorio
