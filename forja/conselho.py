"""O conselho do Censo — a forja não inventa peça, ela consulta o registro.

nature: fix — censo ausente ou ilegível vira aviso escrito no relatório,
nunca uma recomendação inventada. A forja compila do mesmo jeito; ela só perde
a capacidade de dizer o que já existe, e diz que perdeu.

## Por que isto está aqui

Um compilador de agente que responde *"para memória, use X"* sem olhar nada é o
sétimo AgentGuard esperando para nascer. Quando a spec declara
`precisa = ["memoria"]`, a forja abre o censo e devolve **as peças reais** —
com licença, com veredito de OSI, e com o aviso de colisão quando o nome que a
pessoa vai buscar identifica seis projetos diferentes.

É a parte do produto que serve a régua do caderno: *"tanto o bilionário quanto a
tia da limpeza possam ler, entender e aplicar"*. A tia da limpeza não precisa do
sétimo framework. Ela precisa saber **qual dos seis** e **se ainda vale**.
"""

from __future__ import annotations

import json
from pathlib import Path

ROTULO = {
    "osi": "✅ OSI — pode ser vendorizada",
    "osi_copyleft_forte": "⚠️ OSI, copyleft forte — a escolha precisa ser deliberada",
    "nao_osi": "⛔ NÃO é open source — rodar sim, copiar para dentro não",
    "nao_verificado": "◻️ licença não verificada — confira antes de usar",
}


def carregar(caminho: str | Path) -> dict | None:
    """Lê o censo. Ausente ou ilegível devolve `None` — nunca um censo vazio.

    Devolver `{}` faria a forja dizer *"nenhuma peça existe para memória"*, que
    é uma afirmação falsa vestida de resposta. `None` obriga quem chama a
    tratar o caso como *não consultado*, que é o que de fato aconteceu.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def para(estagio: str, censo: dict | None) -> list[dict]:
    if not censo:
        return []
    return [p for p in censo.get("projetos", []) if p.get("estagio") == estagio]


def em_markdown(precisa: list[str], censo: dict | None, caminho_do_censo: str) -> str:
    """O bloco de conselho, pronto para entrar no relatório da corrida."""
    if not precisa:
        return ""
    L = ["## O que já existe para o que esta spec pediu", ""]
    if censo is None:
        L += [
            f"⚠️ **Censo não consultado.** `{caminho_do_censo}` não existe ou não pôde ser lido.",
            "",
            "A forja compilou assim mesmo — o censo aconselha, não gateia. Mas o que segue",
            "**não** é uma lista vazia de peças disponíveis: é a ausência da consulta, e as",
            "duas coisas dizem coisas opostas.",
            "",
        ]
        return "\n".join(L)

    for estagio in precisa:
        peças = para(estagio, censo)
        L.append(f"### `{estagio}`")
        L.append("")
        if not peças:
            L += [
                f"O censo tem **0** entradas no estágio `{estagio}`.",
                "",
                "Isso quer dizer *ninguém catalogou ainda*, e **não** quer dizer *não existe*.",
                "Antes de escrever a sua, abra uma busca — e depois acrescente a entrada ao",
                "censo, porque a próxima pessoa vai fazer a mesma pergunta.",
                "",
            ]
            continue
        for p in sorted(peças, key=lambda x: x["nome"].lower()):
            alvo = p.get("repo") or (p.get("paper") and f"`{p['paper']}`") or "⛔ sem canônico"
            L.append(f"- **{p['nome']}** — {alvo}")
            L.append(f"  - {ROTULO.get(p.get('veredito_licenca', ''), '◻️')} (`{p.get('licenca', '—')}`)")
            L.append(f"  - {p['faz']}")
            if p.get("custa_dinheiro"):
                L.append("  - 💸 **custa dinheiro** — chave de API ou serviço pago")
            if p.get("colide_com"):
                quantos = len(p["colide_com"]) + (1 if p.get("repo") else 0)
                L.append(
                    f"  - ⚠️ **`{p['nome']}` identifica {quantos} projetos independentes.** "
                    "Instalar pelo nome é loteria — use a URL, não o nome."
                )
            L.append(f"  - lido em `{p.get('lido_em', '—')}`")
        L.append("")

    L += [
        "> **Este conselho vence.** Cada linha saiu de uma página aberta na data ao lado, e",
        "> nenhuma sonda offline sabe o que mudou lá fora desde então. Rode `python -m loadline`",
        "> no censo antes de apoiar decisão nele.",
        "",
    ]
    return "\n".join(L)
