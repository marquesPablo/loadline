# Os selos desta operação

TODO — cole no arquivo que a sua métrica julga (o selo tem de morar no arquivo que ele mede, nunca
num relatório à parte).

```markdown
TODO — a frase em prosa que a métrica sustenta.
<!-- measured: NOME.exemplo=N natureza=contagem-ou-relacao em=AAAA-MM-DD vence=90d fonte=caminho/relativo/ -->
```

## Sobre `natureza`

- **`contagem`** — anda quando alguém escreve. Divergiu, resele e siga.
- **`relacao`** — só anda se o medidor ou o repositório quebrou. Divergiu, **pare e investigue**.

Se sua métrica é ambígua entre as duas, releia `LACUNAS.md` do repositório — a distinção existe
precisamente para que ninguém precise adivinhar o que um vermelho significa.

## Sobre `vence`

TODO — escolha o prazo e diga por quê, no mesmo espírito de
`operacoes/sala-de-decisao/selos.md` (`vence=7d` porque o valor ali envelhece em dias, não meses).
Um selo sem `vence` nomeado é um número sem prazo de validade.

## O que NÃO selar aqui

TODO — pelo menos uma frase que pareceria natural selar e que a sua sonda NÃO pode sustentar (ex.:
qualidade, intenção, comportamento em produção — coisas que a sonda não lê). Toda operação desta
prateleira nomeia isso; é o que impede um selo verde de virar a ferramenta atestando o próprio
ponto cego.
