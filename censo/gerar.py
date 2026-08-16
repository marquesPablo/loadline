"""Gera `censo/CENSO.md` — a superfície de leitura do censo — do `ecossistema.json`.

natureza: correcao — este gerador só lê JSON e escreve Markdown. Ele não decide
nada de segurança; erro aqui vira exceção visível, nunca artefato pela metade.

⚠️ **Por que o CENSO.md quase não tem selo, e isso é de propósito.**

Ele é ARTEFATO GERADO. Selar cada número dele seria check espelho (`ADR-012` do
P3G4ZUZ): os dois lados sairiam do mesmo JSON, e o par passaria verde travando o
defeito em vez de achá-lo. A pergunta certa para um artefato derivado não é *"o
número está certo?"* — é **"este artefato ainda corresponde à fonte?"**.

Por isso o CENSO.md carrega **um** selo só, `censo.gerado_em_dia`, de
`natureza=relacao`: ele não anda quando alguém escreve no censo, ele só anda se
alguém editou o publicado à mão ou mexeu na fonte e não regerou. Divergir ali é
defeito, e o veredito manda parar — que é a leitura certa para lista publicada
que saiu de sincronia com o dado.

    python censo/gerar.py            # escreve censo/CENSO.md
    python censo/gerar.py --conferir # não escreve; sai 1 se estiver desatualizado
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "censo" / "ecossistema.json"
PUBLICADO = RAIZ / "censo" / "CENSO.md"

# Ordem de leitura, e ela é um argumento: o ciclo de vida de um agente, do que
# ele entende até quem o ataca. Alfabética esconderia que estágio tem dono e
# qual não tem.
ESTAGIOS = [
    ("entendimento", "Entender o repositório", "o agente lê a base de código antes de agir"),
    ("capacidade", "Ter capacidade", "de onde vem a habilidade que o agente ainda não tem"),
    ("memoria", "Ter memória", "o que sobrevive ao contexto apagado entre sessões"),
    ("ontologia", "Saber o que é o quê", "entidades, relações e de onde veio cada fato"),
    ("runtime", "Rodar o laço", "quem executa o agente, com sandbox e subagente"),
    ("controle", "Bloquear em runtime", "o guarda que decide o que o agente não faz"),
    ("prova", "Provar que passou", "a evidência que o humano lê no lugar do diff"),
    ("adversarial", "Atacar", "quem tenta quebrar o agente de propósito"),
    ("aprendizado", "Aprender com a falha", "o que converte falha em conserto"),
    ("ameaca", "A ameaça medida", "pesquisa, não ferramenta"),
]

ROTULO_LICENCA = {
    "osi": "✅ OSI",
    "osi_copyleft_forte": "⚠️ OSI, copyleft forte",
    "nao_osi": "⛔ não é open source",
    "nao_verificado": "◻️ não verificado",
}


def carregar() -> dict:
    return json.loads(FONTE.read_text(encoding="utf-8"))


def _linha_de_projeto(p: dict) -> str:
    alvo = p.get("repo") or (f"`{p['paper']}`" if p.get("paper") else "—")
    if alvo.startswith("http"):
        alvo = f"[{alvo.split('github.com/')[-1]}]({alvo})"
    colisao = len(p.get("colide_com") or [])
    marca_colisao = f"**{colisao + (1 if p.get('repo') else 0)}**" if colisao else "1"
    return (
        f"| **{p['nome']}** | {alvo} | {p.get('licenca', '—')} "
        f"| {ROTULO_LICENCA.get(p.get('veredito_licenca', ''), '◻️')} | {marca_colisao} |"
    )


def _ficha(p: dict) -> list[str]:
    linhas = [f"#### {p['nome']}", ""]
    if p.get("repo"):
        linhas.append(f"- **Repositório:** {p['repo']}")
    else:
        linhas.append("- **Repositório canônico:** ⛔ **não existe** — ver a seção de colisão")
    if p.get("paper"):
        linhas.append(f"- **Paper:** `{p['paper']}`")
    linhas.append(
        f"- **Licença:** {p.get('licenca', '—')} — {ROTULO_LICENCA.get(p.get('veredito_licenca', ''), '◻️')}"
    )
    linhas.append(f"- **Faz:** {p['faz']}")
    linhas.append(f"- **Depende de:** {p.get('dependencias', 'não verificado')}")

    sem = []
    if p.get("sem_llm") is True:
        sem.append("sem LLM no caminho")
    if p.get("sem_embedding") is True:
        sem.append("sem embedding")
    if p.get("custa_dinheiro") is True:
        sem.append("⚠️ **custa dinheiro** (chave de API ou serviço pago)")
    if sem:
        linhas.append(f"- **Peso:** {' · '.join(sem)}")

    if p.get("alegacao_do_autor"):
        linhas.append(
            f"- **Alegação do autor** (não medida por este censo): {p['alegacao_do_autor']}"
        )
    for campo, rotulo in (
        ("responde", "Responde"),
        ("nao_responde", "**Não** responde"),
        ("achado_principal", "Achado principal"),
        ("ressalva_do_proprio_paper", "Ressalva do próprio paper"),
        ("consequencia_da_licenca", "Consequência da licença"),
        ("ressalva_operacional", "Ressalva operacional"),
        ("nota", "Nota"),
        ("nota_de_colisao", "Sobre a contagem de colisão"),
        ("limite_desta_leitura", "Limite desta leitura"),
    ):
        if p.get(campo):
            linhas.append(f"- **{rotulo}:** {p[campo]}")

    if p.get("colide_com"):
        outros = " · ".join(f"`{x}`" for x in p["colide_com"])
        linhas.append(f"- **Colide com:** {outros}")
    linhas.append(f"- **Lido em:** {p.get('lido_em', '—')}")
    linhas.append("")
    return linhas


def gerar(hoje: date | None = None) -> str:
    censo = carregar()
    projetos = censo["projetos"]
    den = censo["denominador"]
    # ⚠️ A data do selo é a leitura MAIS NOVA do censo, nunca `date.today()`.
    # Carimbar hoje faria o arquivo gerado mudar sozinho à meia-noite, e o
    # `--conferir` acusaria "desatualizado" sem ninguém ter tocado em nada —
    # um alarme que só sabe disparar por passagem do tempo é ruído, não medida.
    hoje = hoje or max(
        (date.fromisoformat(p["lido_em"]) for p in projetos if p.get("lido_em")),
        default=date.today(),
    )

    colisoes = sorted(
        (
            (p["nome"], len(p["colide_com"]) + (1 if p.get("repo") else 0))
            for p in projetos
            if p.get("colide_com")
        ),
        key=lambda x: (-x[1], x[0]),
    )

    L: list[str] = []
    A = L.append

    A("# O Censo do ecossistema de agentes de IA")
    A("")
    A("> **Este arquivo é gerado.** Não o edite à mão — edite `censo/ecossistema.json` e rode")
    A("> `python censo/gerar.py`. O verificador reprova se os dois saírem de sincronia.")
    A("")
    A(f"<!-- aferido: censo.gerado_em_dia=1 natureza=relacao em={hoje.isoformat()} vence=nunca fonte=censo/gerar.py -->")
    A("")
    A("Uma lista `awesome-*` não reprova quando envelhece. Este censo reprova.")
    A("")
    A(f"**{len(projetos)} projetos.** Cada entrada foi lida **na página do repositório**, nunca no")
    A("post que o citou. O que não foi verificado está escrito como não verificado — nunca")
    A("preenchido por plausibilidade, e nunca convertido em zero.")
    A("")

    # --- o achado, primeiro: é o motivo de o censo existir --------------------
    A("---")
    A("")
    A("## O achado: cinco nomes não identificam um projeto")
    A("")
    A("Estes nomes identificam um **cacho de projetos independentes** — mesmo nome, mesmo")
    A("problema, sem se citarem:")
    A("")
    A("| Nome | Projetos independentes | Existe canônico? |")
    A("|---|---:|---|")
    for nome, quantos in colisoes:
        canonico = next(p for p in projetos if p["nome"] == nome)
        tem = "sim" if canonico.get("repo") else "⛔ **não**"
        A(f"| `{nome}` | **{quantos}** | {tem} |")
    A("")
    A("Quem ouve *\"instala o AgentGuard\"* não tem como saber qual dos seis. **Nenhum dos seis")
    A("lista os outros cinco.** Isso não é *\"existem muitos projetos\"* — é o mesmo projeto")
    A("feito seis vezes no escuro.")
    A("")
    A("> **Denominador, e ele importa:** isto é o que **uma busca por nome, num dia** devolveu.")
    A("> Não é censo do GitHub. **É piso, não teto** — o número real é maior, nunca menor.")
    A("")

    # --- por estágio ----------------------------------------------------------
    A("---")
    A("")
    A("## Quem já ocupa cada estágio")
    A("")
    A("Ordenado pelo ciclo de vida de um agente, não pelo alfabeto — porque o que interessa")
    A("é **onde já tem dono grande** e onde não tem.")
    A("")
    A("| Estágio | O que é | Quem ocupa |")
    A("|---|---|---|")
    for chave, titulo, oque in ESTAGIOS:
        nomes = [p["nome"] for p in projetos if p.get("estagio") == chave]
        A(f"| **{titulo}** | {oque} | {' · '.join(nomes) if nomes else '—'} |")
    A("")

    # --- tabela geral ---------------------------------------------------------
    A("---")
    A("")
    A("## Os projetos, com licença lida na fonte")
    A("")
    A("A coluna que decide se você pode usar é a **terceira**, não a segunda. Uma licença que")
    A("não é OSI não vira open source por o projeto se chamar de aberto.")
    A("")
    A("| Projeto | Onde | Licença | Veredito | Nomes no cacho |")
    A("|---|---|---|---|---:|")
    for p in sorted(projetos, key=lambda x: x["nome"].lower()):
        A(_linha_de_projeto(p))
    A("")
    A("**As três portas de uma licença não-OSI**, porque tratá-las como uma só é o erro comum:")
    A("")
    A("| O que fazer | Permitido? |")
    A("|---|---|")
    A("| **Rodar** a ferramenta | ✅ sim — é o que a licença concede |")
    A("| **Ler a arquitetura como especificação** e reimplementar | ✅ sim — API e modelo não são a expressão protegida |")
    A("| **Copiar o código para dentro** do seu projeto | ⛔ não — a restrição atravessa para todos os seus usuários |")
    A("")

    # --- fichas ---------------------------------------------------------------
    A("---")
    A("")
    A("## Ficha de cada um")
    A("")
    for chave, titulo, _ in ESTAGIOS:
        do_estagio = [p for p in projetos if p.get("estagio") == chave]
        if not do_estagio:
            continue
        A(f"### {titulo}")
        A("")
        for p in sorted(do_estagio, key=lambda x: x["nome"].lower()):
            L.extend(_ficha(p))

    # --- denominador ----------------------------------------------------------
    A("---")
    A("")
    A("## O denominador desta leitura")
    A("")
    A("Toda superfície que conta declara **de quantos** contou. Sem isso, um filtro que pula")
    A("em silêncio produz resposta plausível e vazia.")
    A("")
    A("| | |")
    A("|---|---:|")
    A(f"| Nomes buscados | {den['nomes_buscados']} |")
    A(f"| Com repositório canônico identificado e lido | {den['com_repo_canonico']} |")
    A(f"| **Sem** repositório canônico — e essa ausência **é** o achado | {den['sem_repo_canonico']} |")
    A(f"| São paper, não repositório | {den['sao_paper_nao_repo']} |")
    A(f"| **Clonados, instalados ou executados** | **{den['clonados_ou_executados']}** |")
    A("")
    A(f"⚠️ {den['aviso']}")
    A("")
    A("**O que este censo NÃO mede, declarado:**")
    A("")
    A("- **Se o projeto funciona.** Nada aqui foi executado. Desempenho é alegação do autor.")
    A("- **Se ele ainda existe hoje.** É para isso que serve o `vence=` de cada selo — nenhuma")
    A("  sonda offline alcança a verdade do mundo lá fora, e confundir as duas coisas seria")
    A("  dizer que um JSON coerente é um fato verdadeiro.")
    A("- **Quantos projetos existem de verdade.** A contagem de colisão é piso de uma busca.")
    A("- **Se a licença mudou depois da data de leitura.** O campo `lido_em` de cada ficha é")
    A("  a data em que a página foi aberta, não a data de hoje.")
    A("")
    A("---")
    A("")
    A("## Como contribuir com uma entrada")
    A("")
    A("1. Abra a **página do repositório** — não o post, não a lista, não o print. A memória")
    A("   desta casa registra o custo de atribuir pela embalagem: um projeto deste censo")
    A("   estava creditado a quem postou no LinkedIn, não a quem escreveu o código.")
    A("2. Preencha `censo/ecossistema.json`. **`nao_verificado` é um valor legítimo** e nunca")
    A("   vira zero.")
    A("3. Rode `python censo/gerar.py` e `python -m aferido .`. Se algum dos dois reprovar, a")
    A("   entrada ainda não está pronta.")
    A("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    novo = gerar()
    if "--conferir" in argv:
        atual = PUBLICADO.read_text(encoding="utf-8") if PUBLICADO.exists() else ""
        if atual == novo:
            print(f"{PUBLICADO.name}: em dia com {FONTE.name}")
            return 0
        print(f"{PUBLICADO.name}: DESATUALIZADO — rode `python censo/gerar.py`")
        return 1
    PUBLICADO.write_text(novo, encoding="utf-8")
    print(f"{PUBLICADO}: {len(novo)} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
