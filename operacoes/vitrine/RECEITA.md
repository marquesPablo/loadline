# Operação 11 · `vitrine`

> Um agente decide carregar uma skill lendo **dois campos**: `name` e `description`.
> O corpo do `SKILL.md` só é lido **depois** que a decisão já foi tomada.
> **Ninguém confere esses dois campos, porque nada olha para eles.**

## A dor

Medido nesta máquina, em 2026-08-23, sem tocar em nenhuma linha de código: das **31 skills do
marketplace oficial da Anthropic**, **26 não declaram quando NÃO usar** e **1 declara um `name` que
não bate com o nome da própria pasta** — `writing-rules/SKILL.md` diz `name: writing-hookify-rules`.

Isso não é um erro de sintaxe. É um erro que **não produz erro nenhum**: a skill continua existindo,
continua sendo lida por quem abre o arquivo, e continua **invisível** para o roteador que decide, em
tempo de execução, qual skill carregar. O relato de fora é sempre "a skill não pegou", nunca "o
`name` diverge da pasta" — porque nada nunca disse isso.

## O que esta operação instala

Duas sondas que recomputam a vitrine outra vez a cada rodada — nunca a partir do que já foi escrito:
<!-- measured: operacao.vitrine.sondas=2 natureza=contagem em=2026-08-23 vence=nunca fonte=operacoes/vitrine/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `vitrine.skills` | quantos `SKILL.md` existem sob o caminho declarado | contagem |
| **`vitrine.reprovas`** | **quantas dessas skills têm ⛔ em alguma das onze regras da `vitrine`** (nome divergente da pasta, gramática do nome, sem gatilho de uso, sem gatilho negativo, duas skills se confundindo) | **relação** |

A segunda é o coração. Ela deveria ser sempre `0`; quando sai de zero, isso não é "o número mudou",
é **defeito** — uma skill ficou invisível ou vai ficar, e a ferramenta diz isso com essas palavras.

As onze regras completas, cada uma citando a fonte pública de onde sai, estão em
`vitrine/regras.py`. Rodar o linter isolado, fora deste selo: `python -m vitrine <caminho>`.

**A vitrine também sabe CRIAR uma skill nova**, não só auditar as que já existem —
`python -m vitrine --colher <slug> --diz "o que ela faz"` recusa nascer se colidir com uma skill já
existente (mesma régua `S11`) e escreve um `SKILL.md` que já nasce limpo nas regras estruturais,
com `?` só nos dois campos que ninguém além de quem viveu o trabalho sabe preencher: o gatilho
positivo e o negativo. Sem modelo, sem chave de API — ver `vitrine/colheita.py`.

## O ajuste

**Um campo.** Abra `sondas.py` desta operação e troque `CAMINHO_DE_SKILLS` pelo caminho real da sua
pasta de skills — o padrão aponta para `.claude/skills`, que é onde Claude Code, e a maioria dos
harnesses com suporte a Agent Skills, procuram.

⚠️ **Copie a pasta `vitrine/` inteira**, não só o `sondas.py` desta operação — é a única gaveta da
prateleira, com a `cerebro-local`, que traz mais do que os cinco arquivos padrão.
