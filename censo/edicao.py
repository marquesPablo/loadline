"""Gera uma edição datada e recorrente do censo — `censo/edicoes/AAAA-MM-DD.md`.

natureza: correcao — este gerador só lê `ecossistema.json` e os snapshots já
gravados em `censo/edicoes/*.json`. Não faz rede, não decide nada de segurança;
erro aqui vira exceção visível, nunca edição pela metade.

`censo/gerar.py` responde "o `CENSO.md` publicado ainda corresponde à fonte?" —
uma pergunta de INTEGRIDADE, sobre um artefato que muda toda vez que alguém
edita `ecossistema.json`. Este arquivo responde outra pergunta, sobre outro
eixo: "o que mudou no ecossistema desde a última vez que alguém olhou?" — uma
série no tempo, não um espelho do presente.

Cada edição grava DOIS arquivos, nunca um só:

    censo/edicoes/AAAA-MM-DD.json   # o snapshot bruto — o que a PRÓXIMA edição lê para diferir
    censo/edicoes/AAAA-MM-DD.md     # a leitura publicável — o que um humano lê

⚠️ **Por que o `.json` existe, e não só o `.md`.** Diferir duas edições lendo o
texto do `.md` anterior seria a mesma classe de erro que o `LACUNAS.md` do
núcleo já nomeia para `arbitrado:` — extrair número de prosa é frágil e muda de
sentido com qualquer reformulação de frase. O `.json` é a fonte que a PRÓXIMA
rodada lê; o `.md` é só a vitrine daquela rodada, e nunca é lido de volta.

    python censo/edicao.py             # escreve a edição de hoje
    python censo/edicao.py --conferir  # não escreve; sai 1 se já existe edição hoje
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "censo" / "ecossistema.json"
PASTA_EDICOES = RAIZ / "censo" / "edicoes"

ESTAGIO_SEM_CLASSE = "sem_estagio_classificado"


def _carregar_fonte() -> dict:
    return json.loads(FONTE.read_text(encoding="utf-8"))


def _snapshot(censo: dict) -> dict:
    """Reduz o censo de hoje aos números que uma edição compara — nunca a ficha
    inteira de cada projeto, que já mora em `ecossistema.json` e não precisa de
    uma segunda cópia envelhecendo em paralelo."""
    projetos = censo["projetos"]
    por_estagio: dict[str, int] = {}
    for p in projetos:
        chave = p.get("estagio") or ESTAGIO_SEM_CLASSE
        por_estagio[chave] = por_estagio.get(chave, 0) + 1
    por_licenca: dict[str, int] = {}
    for p in projetos:
        chave = p.get("veredito_licenca") or "nao_verificado"
        por_licenca[chave] = por_licenca.get(chave, 0) + 1
    colisoes = sorted(p["nome"] for p in projetos if p.get("colide_com"))
    return {
        "total": len(projetos),
        "nomes": sorted(p["nome"] for p in projetos),
        "por_estagio": por_estagio,
        "por_licenca": por_licenca,
        "nomes_com_colisao": colisoes,
    }


def _edicoes_existentes() -> list[Path]:
    if not PASTA_EDICOES.exists():
        return []
    return sorted(PASTA_EDICOES.glob("*.json"))


def _edicao_anterior(hoje: date) -> dict | None:
    anteriores = [p for p in _edicoes_existentes() if p.stem < hoje.isoformat()]
    if not anteriores:
        return None
    return json.loads(anteriores[-1].read_text(encoding="utf-8"))


def _diferenca(hoje: dict, ontem: dict) -> list[str]:
    linhas: list[str] = []
    novos = sorted(set(hoje["nomes"]) - set(ontem["nomes"]))
    saidos = sorted(set(ontem["nomes"]) - set(hoje["nomes"]))
    delta_total = hoje["total"] - ontem["total"]
    linhas.append(f"**Total:** {ontem['total']} → {hoje['total']} ({delta_total:+d})")
    if novos:
        linhas.append(f"**Entraram ({len(novos)}):** " + ", ".join(f"`{n}`" for n in novos))
    if saidos:
        linhas.append(
            f"**Saíram do arquivo ({len(saidos)}):** " + ", ".join(f"`{n}`" for n in saidos)
        )
        linhas.append(
            "  ⚠️ saída do arquivo `ecossistema.json` — nunca leia como \"o projeto morreu\"; "
            "pode ter sido reclassificado, fundido, ou removido por decisão editorial"
        )
    if not novos and not saidos and delta_total == 0:
        linhas.append("Nenhum nome novo, nenhum removido, desde a edição anterior.")

    delta_colisao = len(hoje["nomes_com_colisao"]) - len(ontem["nomes_com_colisao"])
    if delta_colisao:
        linhas.append(
            f"**Nomes colidindo:** {len(ontem['nomes_com_colisao'])} → "
            f"{len(hoje['nomes_com_colisao'])} ({delta_colisao:+d})"
        )

    estagios = sorted(set(hoje["por_estagio"]) | set(ontem["por_estagio"]))
    mudou_estagio = [
        (e, ontem["por_estagio"].get(e, 0), hoje["por_estagio"].get(e, 0))
        for e in estagios
        if ontem["por_estagio"].get(e, 0) != hoje["por_estagio"].get(e, 0)
    ]
    if mudou_estagio:
        linhas.append("**Estágios que mudaram de contagem:**")
        for estagio, antes, agora in mudou_estagio:
            linhas.append(f"  - `{estagio}`: {antes} → {agora} ({agora - antes:+d})")
    return linhas


def gerar(hoje: date | None = None) -> tuple[Path, Path]:
    hoje = hoje or date.today()
    censo = _carregar_fonte()
    atual = _snapshot(censo)
    anterior = _edicao_anterior(hoje)
    numero = len(_edicoes_existentes()) + 1

    PASTA_EDICOES.mkdir(parents=True, exist_ok=True)
    caminho_json = PASTA_EDICOES / f"{hoje.isoformat()}.json"
    caminho_md = PASTA_EDICOES / f"{hoje.isoformat()}.md"

    caminho_json.write_text(
        json.dumps(atual, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )

    L: list[str] = []
    A = L.append
    A(f"# Estado do ecossistema de agentes de IA — edição {numero}")
    A("")
    A(f"<!-- measured: censo.edicao={numero} natureza=contagem em={hoje.isoformat()} vence=nunca fonte=censo/edicoes/ -->")
    A("")
    A(
        "Gerado por `censo/edicao.py` a partir de `censo/ecossistema.json` — nenhum número aqui "
        "foi escrito à mão. A leitura completa de cada projeto está em [`CENSO.md`](../CENSO.md)."
    )
    A("")
    A(f"**{atual['total']} projetos catalogados**, {len(atual['nomes_com_colisao'])} nomes " "identificando mais de um projeto independente.")
    A("")
    if anterior is None:
        A("## Primeira edição")
        A("")
        A(
            "Não há edição anterior para comparar — esta é a linha de base. A próxima edição "
            "vai poder dizer o que mudou; esta só pode dizer o que existe hoje."
        )
    else:
        A("## O que mudou desde a edição anterior")
        A("")
        L.extend(_diferenca(atual, anterior))
    A("")
    A("## Por estágio, hoje")
    A("")
    A("| Estágio | Projetos |")
    A("|---|---:|")
    for estagio, contagem in sorted(atual["por_estagio"].items(), key=lambda kv: -kv[1]):
        A(f"| `{estagio}` | {contagem} |")
    A("")
    A(
        "**Isto não é opinião sobre o ecossistema — é a contagem de hoje de um arquivo que "
        "qualquer um pode reconferir.** Nenhuma entrada aqui foi clonada ou executada; ver o "
        "aviso de denominador em `CENSO.md`."
    )
    caminho_md.write_text("\n".join(L) + "\n", encoding="utf-8")
    return caminho_json, caminho_md


def conferir() -> int:
    hoje = date.today()
    ja_existe = (PASTA_EDICOES / f"{hoje.isoformat()}.json").exists()
    if ja_existe:
        print(f"já existe edição de hoje ({hoje.isoformat()}) — rode sem --conferir para regravá-la")
        return 1
    print("nenhuma edição de hoje ainda")
    return 0


if __name__ == "__main__":
    if "--conferir" in sys.argv:
        raise SystemExit(conferir())
    j, m = gerar()
    print(f"escrevi {j.relative_to(RAIZ)} e {m.relative_to(RAIZ)}")
