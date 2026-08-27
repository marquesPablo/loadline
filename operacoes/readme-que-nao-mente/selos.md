# Os selos desta operação

Não copie esta lista à mão. **Rode `python -m loadline . --selar`** — ele escreve o selo de cada
afirmação do seu texto, no lugar certo, com o valor de hoje, e nunca sobrescreve selo existente.

Este arquivo existe para a decisão que vem DEPOIS: qual marca cada selo deveria ter.

## O fluxo, em três passos

```console
$ python -m loadline .          # 1. o que ninguém confere aqui
$ python -m loadline . --selar  # 2. escreve tudo como `arbitrated:`
$ python -m loadline . --sondas # 3. quais métricas têm sonda pronta
```

Depois do passo 3, para cada selo cujo nome de métrica apareça na lista de sondas: troque
`arbitrated:` por `measured:`, acrescente `natureza=` e `fonte=`, e apague o `por=`.

```diff
- <!-- arbitrated: testes=84 by=? on=2026-08-21 expires=90d -->
+ <!-- measured: repo.testes=84 nature=count on=2026-08-21 expires=90d source=codigo -->
```

⚠️ **O nome da métrica que o `--selar` escreve é um chute.** Ele sai da palavra logo depois do
número na frase — *"84 testes"* vira `testes=84`. Renomeie para `repo.testes`, que é o nome que a
sonda cobre. A ferramenta diz isso na saída de toda rodada que escreve; não é uma pegadinha, é uma
sugestão declarada como sugestão.

## Os treze com sonda pronta

```markdown
<!-- measured: repo.arquivos=N nature=count on=AAAA-MM-DD expires=90d source=disco -->
<!-- measured: repo.fontes=N nature=count on=AAAA-MM-DD expires=90d source=disco -->
<!-- measured: repo.linhas=N nature=count on=AAAA-MM-DD expires=90d source=codigo -->
<!-- measured: repo.linguagens=N nature=count on=AAAA-MM-DD expires=90d source=extensoes -->
<!-- measured: repo.testes=N nature=count on=AAAA-MM-DD expires=90d source=codigo -->
<!-- measured: repo.arquivos_de_teste=N nature=count on=AAAA-MM-DD expires=90d source=disco -->
<!-- measured: repo.dependencias=N nature=count on=AAAA-MM-DD expires=60d source=manifesto -->
<!-- measured: repo.dependencias_dev=N nature=count on=AAAA-MM-DD expires=60d source=manifesto -->
<!-- measured: repo.workflows=N nature=count on=AAAA-MM-DD expires=90d source=.github/workflows -->
<!-- measured: repo.pendencias=N nature=count on=AAAA-MM-DD expires=90d source=codigo -->
<!-- measured: repo.maior_arquivo=N nature=count on=AAAA-MM-DD expires=90d source=codigo -->
<!-- measured: repo.contribuidores=N nature=count on=AAAA-MM-DD expires=90d source=git -->
<!-- measured: repo.commits=N nature=count on=AAAA-MM-DD expires=90d source=git -->
```

Todas são de **contagem**: elas andam quando alguém escreve código. Divergiu, resele e siga — é o
comportamento normal, não defeito. Se você quiser que uma delas *não* ande — um teto de
`repo.maior_arquivo`, por exemplo —, isso não é uma medida, é uma **escolha**, e a marca é outra:

```markdown
Nenhum arquivo deste repositório passa de 400 linhas.
<!-- arbitrated: repo.teto_de_arquivo=400 by="time de plataforma" on=AAAA-MM-DD expires=180d
     breaks="o primeiro arquivo que só fique legível acima disso" -->
```

## O que NÃO selar

**Nada gerado.** Se o número está num arquivo produzido por um script a partir de outra fonte, selar
o valor é check espelho: os dois lados saem do mesmo lugar e o par passa verde **travando** o
defeito. Para artefato derivado, use **um** selo de `natureza=relacao` que responda *"isto ainda
corresponde à fonte?"* — ele não anda quando alguém acrescenta um item, só anda se alguém editou o
publicado à mão ou mexeu na fonte sem regerar.

**Nada sobre o mundo lá fora.** *"O mais rápido do mercado"*, *"usado por 200 empresas"*, *"o padrão
da indústria"*. Nenhuma sonda offline alcança isso. Ou a frase ganha denominador e data e vira um
`frozen:` honesto, ou ela sai.

```markdown
Em 2026-08-20, entre os três vizinhos que encontramos, era o único com prazo na asserção.
<!-- frozen: comparação feita em 2026-08-20 lendo página pública dos três; alegação daquela
     data, não asserção viva sobre a de hoje -->
```
