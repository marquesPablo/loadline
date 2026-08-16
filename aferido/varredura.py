"""Varre arquivos, lê os selos e monta o relatório com denominador.

natureza: correcao — arquivo ilegível vira linha no relatório, nunca uma
exceção que derruba a rodada e deixa o resto sem medir.

A varredura carrega as sondas do projeto por convenção: um `sondas.py` na
raiz do alvo, importado antes de julgar. Convenção em vez de configuração,
porque um campo de config com caminho a executar é convite escrito.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

from .selo import SeloMalformado, ler_linha
from .veredito import Relatorio, julgar

EXTENSOES = (".md", ".markdown", ".txt", ".py", ".rst", ".toml", ".yaml", ".yml")
IGNORAR = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".mypy_cache"}

# Um arquivo que ENSINA a sintaxe do selo não pode ser lido como se afirmasse.
# Sem isto, todo texto que documenta a ferramenta a sabota — inclusive o
# exemplo de selo malformado, que precisa poder existir escrito.
DIRETIVA_ESPECIME = "aferido-ignorar-arquivo"
_CERCA = "```"


def _regioes_de_especime(linhas: list[str], markdown: bool) -> set[int]:
    """Linhas (1-based) que são espécime e não afirmação.

    Duas regras, ambas declaradas e nenhuma adivinhada:
      1. arquivo com a diretiva `aferido-ignorar-arquivo` — o arquivo inteiro;
      2. em Markdown, o que está dentro de cerca de código — uma cerca É a
         marca universal de "isto é ilustração", e ler ilustração como
         afirmação inventa fatos que ninguém escreveu.
    """
    if any(DIRETIVA_ESPECIME in linha for linha in linhas):
        return set(range(1, len(linhas) + 1))
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
        especimes = _regioes_de_especime(linhas, markdown=caminho.suffix.lower() in (".md", ".markdown"))
        if especimes:
            relatorio.especimes.append(f"{caminho}: {len(especimes)} linhas de espécime, não julgadas")

        tinha_selo = False
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
            relatorio.achados.extend(julgar(selo, hoje=hoje))

        if not tinha_selo:
            relatorio.arquivos_sem_selo.append(str(caminho))

    return relatorio
