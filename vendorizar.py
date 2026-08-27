"""Gera `vendorizado/forja.py` — a vistoria inteira, sem clone, baixável por `curl -O`.

nature: fix — este gerador só concatena código real do pacote `forja`
(nunca reescreve nada à mão) e falha alto se o resultado não compilar. Um
vendorizado que "quase" funciona é pior que nenhum: alguém confiou nele sem
instalar mais nada.

Por que isto existe: `git clone` é a menor fricção que este projeto já pede, e
ainda é maior que a de concorrentes que rodam por `npx` sem clone nenhum
(medido em 20/08 — 13 estrelas, fricção menor). Isto não reduz a fricção da
FORJA inteira — reduz a fricção da PRIMEIRA leitura, a vistoria, que é a
demonstração de 30 segundos do README. Compilar spec → artefato continua
exigindo o pacote de verdade (usa `censo/ecossistema.json`, que não faz
sentido soltar avulso).

    python vendorizar.py            # escreve vendorizado/forja.py
    python vendorizar.py --conferir # não escreve; sai 1 se o arquivo divergir

Depois de publicado (repositório público — gate à parte, `ADR-104`/`ADR-119`):

    curl -O https://raw.githubusercontent.com/marquesPablo/loadline/main/vendorizado/forja.py
    python forja.py /caminho/do/seu/projeto

Zero dependência, porque `forja/spec.py` e `forja/vistoria.py` já são zero
dependência — o vendorizado herda a mesma propriedade, e o check BZ prova
isso rodando o arquivo GERADO, nunca só compilando ele.

A técnica é a mesma de `operacoes/juntar.py`: `from __future__ import
annotations` só pode ser a PRIMEIRA instrução do arquivo, e concatenar dois
módulos com `cat` (ou `+`) põe o segundo no meio — este gerador hasteia uma
cópia só, no topo, e remove as demais.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
FONTES = (RAIZ / "forja" / "spec.py", RAIZ / "forja" / "vistoria.py")
SAIDA = RAIZ / "vendorizado" / "forja.py"

_FUTURE = re.compile(r"^from __future__ import .*\n", re.M)
_IMPORT_RELATIVO = re.compile(r"^from \.spec import .*\n", re.M)

_CLI = '''

# --------------------------------------------------------------- CLI -------
#
# A parte que NÃO veio do pacote: um wrapper fino, só para este arquivo poder
# rodar sozinho. É a mesma lógica de `forja/__main__.py::_vistoria`, sem
# `--adotar`/`--html`/`--baseline` — este arquivo é só a LEITURA, a demo de
# 30 segundos do README. Para o resto, `pip install` ou `git clone` de verdade.

import sys as _sys
from datetime import date as _date


def _console_em_utf8() -> None:
    for stream in (_sys.stdout, _sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(_sys.argv[1:] if argv is None else argv)
    raiz = Path(argv[0]) if argv else Path(".")
    hoje = _date.today().isoformat()

    pasta = achar_pasta(raiz)
    if pasta is None:
        print(f"vistoria · {raiz} · em {hoje}")
        print("=" * LARGURA)
        print("Não achei pasta de agentes aqui. Procurei, nesta ordem:")
        for relativo in PASTAS:
            print(f"     {raiz / relativo}")
        print()
        print("RECUSADO — não li nada, e não vou devolver verde por isso.      (exit 2)")
        return 2

    roster = ler_roster(pasta)
    if not roster:
        print(f"vistoria · {pasta} · em {hoje}")
        print("=" * LARGURA)
        print("A pasta existe e não há nenhum agente dentro dela.")
        print()
        print("RECUSADO — zero agente lido não é zero defeito.                 (exit 2)")
        return 2

    achados = vistoriar(roster)
    for linha in relatorio(roster, achados, pasta, hoje):
        print(linha)

    print()
    if not achados:
        print("PASSA — todo agente lido declara as seis coisas.                (exit 0)")
        return 0
    print("REPROVA                                                        (exit 1)")
    print()
    print("  Este é o `forja.py` vendorizado — só a vistoria. `--adotar`, `--html`,")
    print("  `--baseline` e a compilação de spec → artefato exigem o pacote inteiro:")
    print("  `git clone https://github.com/marquesPablo/loadline && cd loadline`.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


def gerar() -> str:
    partes = [
        '"""forja.py — vendorizado, só a vistoria: lê os agentes que você já tem.\n\n'
        "Gerado por `vendorizar.py` a partir do pacote `forja` de verdade — editar este\n"
        "arquivo à mão é editar uma cópia; o original mora em `forja/spec.py` e\n"
        '`forja/vistoria.py`. Zero dependência: só a biblioteca padrão do Python 3.10+.\n\n'
        "    python forja.py /caminho/do/seu/projeto\n\n"
        'O pacote inteiro (compilação de spec, `--adotar`, `--html`, `--baseline`,\n'
        "modo comparação) está em https://github.com/marquesPablo/loadline\n"
        '"""\n',
        "from __future__ import annotations\n",
    ]
    for fonte in FONTES:
        texto = fonte.read_text(encoding="utf-8")
        texto = _FUTURE.sub("", texto, count=1)
        texto = _IMPORT_RELATIVO.sub("", texto, count=1)
        partes.append(f"\n# {'=' * 68}\n# {fonte.relative_to(RAIZ)}\n# {'=' * 68}\n")
        partes.append(texto.strip("\n"))
        partes.append("\n")
    partes.append(_CLI.strip("\n") + "\n")
    return "\n".join(partes)


def _console_em_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    _console_em_utf8()
    argv = list(sys.argv[1:] if argv is None else argv)
    conferir = "--conferir" in argv

    gerado = gerar()

    # Falha alto, nunca calado: um vendorizado que não compila é o pior dos
    # dois mundos — parece instalável e não roda. `compile()`, não `ast.parse`
    # — o parser aceita `from __future__` fora do topo; quem reprova é o
    # compilador (a mesma lição do check BJ/`operacoes/juntar.py`).
    compile(gerado, str(SAIDA), "exec")

    if conferir:
        atual = SAIDA.read_text(encoding="utf-8") if SAIDA.is_file() else None
        if atual == gerado:
            print(f"em dia  {SAIDA} bate com o pacote `forja` de verdade")
            return 0
        print(f"DESATUALIZADO  {SAIDA} diverge do pacote `forja` — rode `python vendorizar.py`")
        return 1

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(gerado, encoding="utf-8")
    print(f"✓ {SAIDA}  ·  {len(gerado.encode('utf-8'))} bytes, zero dependência")
    print()
    print("  Confira com:  python vendorizado/forja.py exemplos/roster-de-exemplo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
