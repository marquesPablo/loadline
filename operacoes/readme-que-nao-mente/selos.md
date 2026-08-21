# Os selos desta operação

Não copie esta lista à mão. **Rode `python -m aferido . --selar`** — ele escreve o selo de cada
afirmação do seu texto, no lugar certo, com o valor de hoje, e nunca sobrescreve selo existente.

Este arquivo existe para a decisão que vem DEPOIS: qual marca cada selo deveria ter.

## O fluxo, em três passos

```console
$ python -m aferido .          # 1. o que ninguém confere aqui
$ python -m aferido . --selar  # 2. escreve tudo como `arbitrado:`
$ python -m aferido . --sondas # 3. quais métricas têm sonda pronta
```

Depois do passo 3, para cada selo cujo nome de métrica apareça na lista de sondas: troque
`arbitrado:` por `aferido:`, acrescente `natureza=` e `fonte=`, e apague o `por=`.

```diff
- <!-- arbitrado: testes=84 por=? em=2026-08-21 vence=90d -->
+ <!-- aferido: repo.testes=84 natureza=contagem em=2026-08-21 vence=90d fonte=codigo -->
```

⚠️ **O nome da métrica que o `--selar` escreve é um chute.** Ele sai da palavra logo depois do
número na frase — *"84 testes"* vira `testes=84`. Renomeie para `repo.testes`, que é o nome que a
sonda cobre. A ferramenta diz isso na saída de toda rodada que escreve; não é uma pegadinha, é uma
sugestão declarada como sugestão.

## Os treze com sonda pronta

```markdown
<!-- aferido: repo.arquivos=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=disco -->
<!-- aferido: repo.fontes=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=disco -->
<!-- aferido: repo.linhas=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=codigo -->
<!-- aferido: repo.linguagens=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=extensoes -->
<!-- aferido: repo.testes=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=codigo -->
<!-- aferido: repo.arquivos_de_teste=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=disco -->
<!-- aferido: repo.dependencias=N natureza=contagem em=AAAA-MM-DD vence=60d fonte=manifesto -->
<!-- aferido: repo.dependencias_dev=N natureza=contagem em=AAAA-MM-DD vence=60d fonte=manifesto -->
<!-- aferido: repo.workflows=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=.github/workflows -->
<!-- aferido: repo.pendencias=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=codigo -->
<!-- aferido: repo.maior_arquivo=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=codigo -->
<!-- aferido: repo.contribuidores=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=git -->
<!-- aferido: repo.commits=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=git -->
```

Todas são de **contagem**: elas andam quando alguém escreve código. Divergiu, resele e siga — é o
comportamento normal, não defeito. Se você quiser que uma delas *não* ande — um teto de
`repo.maior_arquivo`, por exemplo —, isso não é uma medida, é uma **escolha**, e a marca é outra:

```markdown
Nenhum arquivo deste repositório passa de 400 linhas.
<!-- arbitrado: repo.teto_de_arquivo=400 por="time de plataforma" em=AAAA-MM-DD vence=180d
     derruba="o primeiro arquivo que só fique legível acima disso" -->
```

## O que NÃO selar

**Nada gerado.** Se o número está num arquivo produzido por um script a partir de outra fonte, selar
o valor é check espelho: os dois lados saem do mesmo lugar e o par passa verde **travando** o
defeito. Para artefato derivado, use **um** selo de `natureza=relacao` que responda *"isto ainda
corresponde à fonte?"* — ele não anda quando alguém acrescenta um item, só anda se alguém editou o
publicado à mão ou mexeu na fonte sem regerar.

**Nada sobre o mundo lá fora.** *"O mais rápido do mercado"*, *"usado por 200 empresas"*, *"o padrão
da indústria"*. Nenhuma sonda offline alcança isso. Ou a frase ganha denominador e data e vira um
`congelado:` honesto, ou ela sai.

```markdown
Em 2026-08-20, entre os três vizinhos que encontramos, era o único com prazo na asserção.
<!-- congelado: comparação feita em 2026-08-20 lendo página pública dos três; alegação daquela
     data, não asserção viva sobre a de hoje -->
```
