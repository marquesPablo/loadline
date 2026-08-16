"""Os alvos de emissão — uma spec entra, sete artefatos saem.

natureza: correcao — este módulo só formata texto a partir de uma spec JÁ
validada. Quem barra é `spec.validar`; aqui, exceção é defeito de formatação e
aparece por inteiro em vez de virar artefato pela metade.

    .claude/agents/<slug>.md   subagente de Claude Code (frontmatter + prompt)
    AGENTS.md                  o formato agnóstico de harness
    <slug>.system.md           system prompt cru, para SDK ou harness próprio
    hooks/cerca_<slug>.py      o guarda PreToolUse, que FALHA FECHADO
    golden/<slug>.md           o golden set, com a regra de derivação
    LACUNAS.md                 o que este agente não mede
    RECEITA.md                 o que foi emitido, de que spec, quando

O que separa isto de um gerador de prompt: **três dos sete não são texto para o
modelo ler.** O hook é código que roda antes da ferramenta e nega; o golden set
é a pergunta que confere a RESPOSTA; as lacunas são a ausência com dono. Prompt
bonito sem esses três é um agente sem gate com uma descrição melhor.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from . import vacina
from .spec import ESCRITA, EXECUCAO, REDE, Spec


def _lista_md(itens: list[str], marca: str = "-") -> str:
    return "\n".join(f"{marca} {x}" for x in itens) if itens else "_(nenhum)_"


def _data_da_spec(spec: Spec) -> date:
    """A data da última escrita da spec. Estável enquanto a spec não mudar."""
    try:
        return date.fromtimestamp(Path(spec.origem).stat().st_mtime)
    except (OSError, ValueError):
        return date.today()


def _fronteira_em_prosa(spec: Spec) -> list[str]:
    L = []
    if spec.usa_rede:
        alvos = ", ".join(f"`{d}`" for d in (spec.dominios_permitidos or []))
        if spec.dominios_permitidos == ["nenhum"]:
            L.append(
                "- **Rede: BARRADA sempre.** Esta spec declara `nenhum`, e o guarda nega "
                "toda saída, sem exceção."
            )
        else:
            L.append(
                f"- **Rede: só {alvos}.** Qualquer outro domínio é negado pelo guarda antes "
                "de a chamada sair — inclusive um subdomínio que pareça óbvio."
            )
    if spec.usa_escrita:
        alvos = ", ".join(f"`{c}`" for c in (spec.saida_cercada or []))
        L.append(
            f"- **Escrita: só sob {alvos}.** O guarda compara o caminho REAL (resolvendo "
            "link e junction) — escrever fora disso é negado, não avisado."
        )
    if spec.usa_execucao:
        L.append(
            "- **Execução:** esta spec pede shell. Todo comando fica no registro da corrida, "
            "com o argv exato."
        )
    if spec.toca_alvo:
        L.append(
            f"- **Toca alvo externo.** Exige autorização válida em `{spec.autorizacao}`, com "
            "alvo, escopo, autorização e validade. **Um comando fora do alvo autorizado é "
            "incidente, não achado.**"
        )
    if spec.desconhecidas:
        L.append(
            "- ⚠️ **Ferramentas fora do vocabulário conhecido:** "
            + ", ".join(f"`{f}`" for f in spec.desconhecidas)
            + ". O guarda **não sabe classificá-las** e por isso não as cerca. Isto está "
            "escrito aqui em vez de ficar calado."
        )
    if not L:
        L.append("- Só leitura. Esta spec não pede rede, escrita nem shell.")
    return L


# ---------------------------------------------------------------- prompt ----
def corpo_do_prompt(spec: Spec) -> str:
    """O miolo que todo alvo compartilha — o que o modelo lê."""
    return f"""# {spec.nome}

{spec.uma_frase}

## Use este agente quando

{_lista_md(spec.usar_quando)}

## NUNCA use este agente para

{_lista_md(spec.nunca_usar)}

> A anti-descrição não é educação, é mecanismo. Um orquestrador que só lê o que o
> agente FAZ despacha por semelhança de tema, e o agente errado responde com
> confiança sobre o que não é dele.

## A sua fronteira

{chr(10).join(_fronteira_em_prosa(spec))}

**A fronteira acima não depende de você obedecer.** Ela está implementada em
`hooks/cerca_{spec.slug.replace("-", "_")}.py`, que roda ANTES da ferramenta e nega.
Se você tentar sair dela, a chamada não acontece — e a recusa traz o conserto escrito.

## O que você NÃO mede

{_lista_md(spec.lacunas)}

Quando a pergunta cair numa dessas, **diga que não mede** e diga quem mede. Preencher
lacuna com plausibilidade é o defeito que esta seção existe para impedir.

## Como você responde

- **Verifique antes de afirmar.** Rode, leia o arquivo, cheque a saída. Se não
  verificou, diga que não verificou. Se não achou, escreva **"não encontrei"**.
- **Declare o denominador.** Toda vez que você contar alguma coisa, diga de quantos
  contou. Um filtro que pula em silêncio devolve resposta plausível e vazia.
- **Datas absolutas** (`AAAA-MM-DD`), nunca "semana passada" — o leitor da sua resposta
  não sabe quando você a escreveu.
- Cite `caminho:linha` para tudo que você afirmar sobre o disco.

{vacina.paragrafo(spec.idioma)}"""


# --------------------------------------------------------------- alvos ------
def claude_code(spec: Spec) -> tuple[str, str]:
    """Subagente de Claude Code: frontmatter + prompt no corpo."""
    descricao = (
        f"{spec.uma_frase} "
        + (f"Usar quando: {'; '.join(spec.usar_quando)}. " if spec.usar_quando else "")
        + f"NUNCA usar para: {'; '.join(spec.nunca_usar)}."
    ).replace("\n", " ")
    frontmatter = "\n".join(
        [
            "---",
            f"name: {spec.slug}",
            f"description: {json.dumps(descricao, ensure_ascii=False)}",
            f"tools: {', '.join(spec.ferramentas)}" if spec.ferramentas else "tools:",
            "---",
            "",
        ]
    )
    return f".claude/agents/{spec.slug}.md", frontmatter + corpo_do_prompt(spec)


def agents_md(spec: Spec) -> tuple[str, str]:
    """`AGENTS.md` — o formato que harness nenhum é dono."""
    return "AGENTS.md", (
        f"# AGENTS.md — {spec.nome}\n\n"
        "> Este arquivo é lido por harnesses que não são o Claude Code. Ele diz a mesma\n"
        "> coisa que `.claude/agents/`, de propósito: um agente cuja fronteira muda de\n"
        "> harness para harness não tem fronteira, tem sorte.\n\n"
        + corpo_do_prompt(spec)
    )


def system_prompt(spec: Spec) -> tuple[str, str]:
    """System prompt cru, para SDK ou harness próprio."""
    return f"{spec.slug}.system.md", corpo_do_prompt(spec)


def hook(spec: Spec) -> tuple[str, str]:
    """O guarda `PreToolUse`, gerado da fronteira declarada. Falha FECHADO."""
    sub = spec.slug.replace("-", "_")
    config = json.dumps(
        {
            "slug": spec.slug,
            "rede": sorted(REDE),
            "escrita": sorted(ESCRITA),
            "dominios_permitidos": spec.dominios_permitidos or [],
            "saida_cercada": spec.saida_cercada or [],
        },
        ensure_ascii=False,
        indent=4,
    )
    corpo = '''"""Guarda PreToolUse de `%(slug)s` — GERADO pela forja, não editar à mão.

natureza: seguranca — toda exceção BARRA. O que este guarda não consegue
decidir, ele nega: um guarda que libera quando quebra não é guarda, e a hora em
que ele quebra é exatamente a hora em que alguém está tentando passar.

Instale-o como `PreToolUse` no settings do harness. Ele lê o evento em JSON no
stdin e responde no formato de decisão de permissão.

⚠️ **Jurisdição estreita, e ela é declarada.** Este guarda só age quando
consegue identificar o agente — pelo `agent_type` do evento ou pela variável de
ambiente `FORJA_AGENTE`. Sessão principal sem subagente segue sob o que o
harness já fazia. Isso NÃO é falha aberta: é o guarda dizendo de quem ele é.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

CONFIG = %(config)s


def _negar(motivo: str, conserto: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"{motivo}\\n\\nConserto: {conserto}",
                }
            }
        )
    )
    raise SystemExit(0)


def _sou_eu(evento: dict) -> bool:
    identidade = evento.get("agent_type") or os.environ.get("FORJA_AGENTE") or ""
    return identidade == CONFIG["slug"]


def _cobre(host: str, permitido: str) -> bool:
    """`api.github.com` cai sob `github.com`; `github.com.mau.site` NÃO cai.

    A comparação é por rótulo de domínio, nunca por `endswith` de string —
    `endswith` deixa passar exatamente o sufixo forjado que o atacante escolhe.
    """
    host, permitido = host.lower().strip("."), permitido.lower().strip(".")
    return host == permitido or host.endswith("." + permitido)


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except Exception:
        _negar(
            "o evento do hook não pôde ser lido",
            "isto é falha fechada de propósito — um guarda que não entende o pedido nega",
        )
        return 0

    if not _sou_eu(evento):
        return 0

    ferramenta = evento.get("tool_name", "")
    entrada = evento.get("tool_input", {}) or {}

    if ferramenta in CONFIG["rede"]:
        permitidos = CONFIG["dominios_permitidos"]
        if not permitidos or permitidos == ["nenhum"]:
            _negar(
                f"`{CONFIG['slug']}` não tem domínio permitido nenhum; a saída de rede é barrada.",
                'declare `dominios_permitidos` na spec e recompile com `python -m forja`',
            )
        alvo = entrada.get("url") or ""
        hosts = [urlparse(alvo).hostname or ""] if alvo else list(entrada.get("allowed_domains") or [])
        if not hosts or not any(h for h in hosts):
            _negar(
                f"não deu para extrair domínio de `{ferramenta}`.",
                "chamada de rede sem alvo legível é negada — o guarda não adivinha destino",
            )
        for h in hosts:
            if not any(_cobre(h, d) for d in permitidos):
                _negar(
                    f"`{h}` está fora de `dominios_permitidos` de `{CONFIG['slug']}`: {permitidos}",
                    "acrescente o domínio na spec e recompile, ou use outra fonte",
                )

    if ferramenta in CONFIG["escrita"]:
        cercas = CONFIG["saida_cercada"]
        if not cercas:
            _negar(
                f"`{CONFIG['slug']}` não declara `saida_cercada`; toda escrita é barrada.",
                "declare `saida_cercada` na spec e recompile",
            )
        alvo = entrada.get("file_path") or entrada.get("notebook_path") or ""
        if not alvo:
            _negar(
                f"`{ferramenta}` sem caminho legível.",
                "escrita sem destino legível é negada — o guarda não adivinha caminho",
            )
        try:
            real = Path(alvo).resolve()
            permitido = any(
                real == Path(c).resolve() or Path(c).resolve() in real.parents for c in cercas
            )
        except OSError:
            permitido = False
        if not permitido:
            _negar(
                f"`{alvo}` está fora de `saida_cercada` de `{CONFIG['slug']}`: {cercas}",
                "escreva sob um dos caminhos declarados, ou mude a spec e recompile",
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''' % {"slug": spec.slug, "config": config}
    return f"hooks/cerca_{sub}.py", corpo


def golden(spec: Spec) -> tuple[str, str]:
    """O golden set — a única superfície que pergunta se a RESPOSTA está certa."""
    L = [
        f"# Golden set — `{spec.slug}`",
        "",
        "> Cada resposta esperada aqui foi escrita **à mão, lendo o disco**. Se ela sair de",
        "> uma chamada ao próprio agente, o caso é check espelho: os dois lados vêm da mesma",
        "> fonte, o par passa verde e **trava** o defeito em vez de achá-lo.",
        "",
        f"**{len(spec.golden)} caso(s).** Cobertura não é gateada de propósito: gate de",
        "cobertura empurra para caso fraco, e caso fraco é pior que caso ausente.",
        "",
    ]
    for i, caso in enumerate(spec.golden, start=1):
        L += [
            f"## G{i:02d}",
            "",
            f"**Pergunta:** {caso.pergunta}",
            "",
            f"**Resposta esperada:** {caso.esperado}",
            "",
            f"**Derivado de:** `{caso.derivado_de}` — fora da saída do agente.",
            "",
        ]
    return f"golden/{spec.slug}.md", "\n".join(L)


def lacunas(spec: Spec) -> tuple[str, str]:
    """O que o agente não mede — ausência com dono, não silêncio."""
    return "LACUNAS.md", (
        f"# O que `{spec.slug}` NÃO mede\n\n"
        "> Ausência não deixa rastro. Uma pergunta que o agente não responde não produz\n"
        "> objeto nenhum para alguém inspecionar — ela só produz uma resposta plausível.\n"
        "> Por isso ela é escrita aqui, e por isso a forja se recusa a compilar sem esta lista.\n\n"
        f"{_lista_md(spec.lacunas)}\n\n"
        "## Como fechar uma destas\n\n"
        "Não apague a linha. Escreva ao lado dela **quem** passou a medir e **onde** —\n"
        "um check, outro agente, um humano com nome. Lacuna que some sem dono volta calada.\n"
    )


def receita(spec: Spec, emitidos: list[str], hoje: date | None = None) -> tuple[str, str]:
    """A receita da corrida — de que spec saiu o quê, e quando.

    ⚠️ A data é a da SPEC, não a de hoje. Carimbar hoje faria o artefato mudar
    sozinho à meia-noite e o `--conferir` acusaria "desatualizado" sem ninguém
    ter tocado em nada — um alarme que só sabe disparar por passagem do tempo é
    ruído, e ruído treina quem o lê a ignorá-lo.
    """
    hoje = hoje or _data_da_spec(spec)
    L = [
        f"# Receita — `{spec.slug}`",
        "",
        f"<!-- aferido: forja.artefatos={len(emitidos)} natureza=contagem "
        f"em={hoje.isoformat()} vence=nunca fonte={spec.origem} -->",
        "",
        f"- **Spec de origem:** `{spec.origem}`",
        f"- **Emitido em:** {hoje.isoformat()}",
        f"- **Ferramentas concedidas:** {', '.join(spec.ferramentas) or '_(nenhuma)_'}",
        f"- **Vacina de vírus de ideia:** presente em todo artefato de prompt — `{vacina.FONTE}`",
        "",
        "## Artefatos emitidos",
        "",
        *(f"- `{caminho}`" for caminho in emitidos),
        "",
        "## O que esta receita NÃO prova",
        "",
        "- **Que o agente é bom.** A forja verifica que a fronteira existe, é executável e",
        "  falha fechada. Se o agente responde bem é o golden set que diz, e ele foi",
        "  escrito por quem escreveu a spec.",
        "- **Que a lista de lacunas está completa.** Ela está declarada, não medida.",
        "- **Que o hook está instalado.** Emitir o guarda e registrá-lo no harness são duas",
        "  coisas, e a segunda é sua — está escrito em `RECEITA.md` para não sumir.",
        "",
    ]
    if spec.desconhecidas:
        L += [
            "## ⚠️ Ferramentas que o guarda não classifica",
            "",
            *(f"- `{f}`" for f in spec.desconhecidas),
            "",
            "Elas foram concedidas e **não são cercadas** — o guarda não sabe se são de rede,",
            "de escrita ou de leitura. Isto está impresso em vez de calado.",
            "",
        ]
    return "RECEITA.md", "\n".join(L)


TODOS = (claude_code, agents_md, system_prompt, hook, golden, lacunas)
