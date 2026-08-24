"""A colheita — vira o que funcionou numa `SKILL.md` nova, e recusa duplicar.

    $ python -m vitrine --colher nome-da-skill --diz "uma frase do que ela faz"
    $ python -m vitrine --colher nome-da-skill --diz "..." --pasta .claude/skills

natureza: seguranca — a colheita é uma recusa antes de ser uma escrita: slug
fora da gramática, slug já ocupado e descrição que colide com uma skill que
já existe NUNCA viram arquivo. Uma ferramenta que "faz o melhor esforço" e
escreve mesmo assim produz a skill nº2 brigando pelo mesmo despacho — o
mesmo defeito que a regra `S11` audita DEPOIS do fato. Aqui ele é pego ANTES.

## As quatro recusas

    H1  slug fora da gramática do formato Agent Skills (mesma régua do S2)
    H2  já existe uma pasta com este slug no destino — nunca sobrescreve
    H3  a descrição colide com uma skill que já existe ali (mesma régua do S11)
    H4  nenhuma descrição foi passada — nada para checar colisão nenhuma

## Isto não é "Skill Forge" com um modelo escrevendo por trás

Não tem LLM aqui, e não vai ter — mesmo invariante do resto do projeto (README:
"um verificador que depende de um modelo não é um verificador"). O que ela
escreve é a metade que NÃO precisa de modelo: um `SKILL.md` que já nasce
compilando limpo nas regras estruturais (`S1`, `S2`, `S6`…), com um `?`
exatamente nos dois campos que só quem viveu o trabalho sabe preencher — e a
certeza, checada ANTES de escrever, de que ninguém no destino já ocupa esse
despacho. Ver `LACUNAS.md` §10 para o que ela NÃO cobre.
"""

from __future__ import annotations

from pathlib import Path

from .regras import LIMIAR_CONFUSAO, NOME_VALIDO, Skill, _confusao, _um_nomeia_o_outro, ler_pasta

FALTA = "?"

#: A `description` final carrega o texto real de `--diz` — nunca vira `{falta}`
#: sozinha. Duas razões, as duas medidas escrevendo este módulo:
#:   1. Se ela virasse `{falta}`, a colheita SEGUINTE, comparando contra esta
#:      skill no disco, não teria palavra nenhuma para cruzar — a checagem de
#:      colisão (H3) ficaria cega para toda skill ainda não preenchida.
#:   2. As DUAS cláusulas que faltam (gatilho positivo e negativo) ficam como
#:      `{falta}` dentro da MESMA description, mas sem a palavra "quando"/
#:      "when" ao lado — escrevê-la aqui faria as regras S3/S4 lerem o rótulo
#:      da lacuna como se fosse o gatilho, e passarem verde num campo vazio.
MODELO = '''---
name: {slug}
description: {descricao} — gatilho positivo: {falta}; gatilho negativo: {falta}
---

# {slug}

{falta}

<!-- A colheita deixou três buracos de pé, de propósito — ela não tem
modelo, e não escreve nenhum deles por você:
  1. gatilho positivo, acima — quando usar, régua S3: escreva a cláusula
     condicional ("...quando o PR mexe em autenticação", por exemplo).
  2. gatilho negativo, acima — quando NÃO usar, régua S4: nomeie a skill
     mais parecida, se houver, pelo slug dela.
  3. o corpo, aqui embaixo — o passo a passo que funcionou de verdade.
Rode `python -m vitrine {pasta}` depois de preencher: os três buracos viram
⛔ até virarem texto de verdade, e o resto das regras (S1, S2, S6…) já nasceu
limpo. -->
'''


class Recusa(ValueError):
    """A colheita se recusou a escrever. Sempre com o código da regra e o conserto."""

    def __init__(self, regra: str, motivo: str, conserto: str) -> None:
        self.regra, self.motivo, self.conserto = regra, motivo, conserto
        super().__init__(f"{regra}: {motivo}\n      conserto: {conserto}")


def colher(slug: str, descricao: str, pasta: Path) -> Path:
    """Escreve `<pasta>/<slug>/SKILL.md`, ou recusa. Nunca os dois pela metade.

    `descricao` é usada SÓ para checar colisão com quem já existe em `pasta` —
    ela não é copiada verbatim para o arquivo: o `description` final nasce
    como `?`, porque a frase que passa na checagem de colisão pode não ser a
    frase que passa em `S3`/`S4` (gatilho positivo e negativo), e confundir
    as duas é exatamente a família de defeito que este projeto inteiro existe
    para cobrar.
    """
    if not (NOME_VALIDO.match(slug) and len(slug) <= 64):
        raise Recusa(
            "H1",
            f"`{slug}` não é um slug válido",
            "1 a 64 caracteres, só minúsculas, dígitos e hífen simples — mesma "
            "gramática que a regra S2 audita depois do fato",
        )
    if not descricao.strip():
        raise Recusa(
            "H4",
            "nenhuma `--diz` foi passada",
            "descreva em uma frase o que a skill faz — é essa frase que a "
            "colheita usa para checar se já existe uma irmã ocupando o mesmo "
            "despacho, antes de escrever um byte",
        )

    pasta = Path(pasta)
    destino = pasta / slug
    if (destino / "SKILL.md").exists():
        raise Recusa(
            "H2",
            f"já existe `{destino / 'SKILL.md'}`",
            "a colheita nunca sobrescreve — edite a existente à mão, ou "
            "escolha outro slug",
        )

    existentes = ler_pasta(pasta, com_git=False) if pasta.is_dir() else []
    proposta = Skill(caminho=destino / "SKILL.md", pasta=destino, nome=slug, descricao=descricao)
    colisoes = [
        (s.slug, round(_confusao(proposta, s) * 100))
        for s in existentes
        if _confusao(proposta, s) >= LIMIAR_CONFUSAO and not _um_nomeia_o_outro(proposta, s)
    ]
    if colisoes:
        pares = ", ".join(f"`{slug_}` ({pct}%)" for slug_, pct in colisoes)
        raise Recusa(
            "H3",
            f"a descrição colide com {pares} — mesma régua do S11",
            "estenda a skill existente em vez de criar uma rival, ou nomeie-a "
            'por extenso na sua `--diz` ("...different from <slug-irmã>...") '
            "para que a régua leia o gatilho negativo como intencional",
        )

    destino.mkdir(parents=True, exist_ok=True)
    (destino / "SKILL.md").write_text(
        MODELO.format(slug=slug, falta=FALTA, pasta=pasta, descricao=descricao.strip()),
        encoding="utf-8",
    )
    return destino / "SKILL.md"
