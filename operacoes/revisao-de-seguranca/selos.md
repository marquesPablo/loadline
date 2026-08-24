# Os selos desta operação

## O que vai no resumo, e ele é um só

Cole **no `achados/README.md`** — o índice do lote, não o relatório entregue. O relatório vai para
o cliente e não deve carregar a instrumentação interna da sua esteira.

```markdown
Este lote tem N achados, e todos os N são acionáveis: cada um com endereço, classificação com
versão de catálogo, passo de verificação e veredito.
<!-- measured: seguranca.achados=N natureza=contagem em=AAAA-MM-DD vence=30d fonte=achados/ -->
<!-- measured: seguranca.acionaveis=N natureza=relacao em=AAAA-MM-DD vence=30d fonte=achados/ -->
```

**`acionaveis` é de RELAÇÃO e `achados` é de CONTAGEM, e a assimetria é a operação inteira.** O
tamanho do lote anda quando alguém trabalha — divergiu, resele. Quantos são acionáveis **não deve
andar**: se caiu, entrou achado pela metade no lote, e a resposta certa é abrir o arquivo.

## Os cinco do diagnóstico

```markdown
<!-- measured: seguranca.sem_framework=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=achados/ -->
<!-- measured: seguranca.sem_versao_de_framework=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=achados/ -->
<!-- measured: seguranca.sem_caminho_linha=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=achados/ -->
<!-- measured: seguranca.sem_passo_de_verificacao=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=achados/ -->
<!-- measured: seguranca.sem_veredito=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=achados/ -->
```

Os cinco existem para dizer **qual** conserto falta quando `acionaveis` cai. Sem eles você sabe que
há 337 achados ruins e não sabe se falta endereço ou falta veredito — e são trabalhos diferentes,
feitos por pessoas diferentes.

## ⚠️ O selo que você NÃO pode escrever, e é o que todo mundo quer escrever

```markdown
<!-- ISTO ESTÁ ERRADO E NENHUMA SONDA DESTA OPERAÇÃO O SUSTENTA -->
Este repositório não tem vulnerabilidades conhecidas.
<!-- measured: seguranca.vulnerabilidades=0 natureza=relacao em=... -->
```

**Não existe sonda para isso, e a ausência é deliberada.** As sondas contam a qualidade dos achados
que existem. Um lote impecável, com 100% de acionáveis, é compatível com um sistema cheio de
vulnerabilidades que ninguém procurou.

**A ausência de achado nunca foi prova de ausência de vulnerabilidade** — e o falso negativo é o
erro mais caro desta operação justamente porque não aparece em lugar nenhum. Um selo verde afirmando
segurança seria a ferramenta atestando o próprio ponto cego, com marca de medida.

O que você pode selar honestamente é **cobertura declarada**:

```markdown
Esta revisão olhou 42 dos 87 arquivos de origem. Os outros 45 não foram olhados.
<!-- arbitrated: seguranca.arquivos_revisados=42 por="quem conduziu a revisão" em=AAAA-MM-DD vence=30d
     derruba="qualquer commit que mexa num dos 45 que não foram olhados" -->
```

`arbitrated:`, e não `measured:` — o recorte foi **escolhido**, não medido. E `derruba=` é a parte
mais valiosa: ela diz o que faria essa escolha deixar de valer.

## O prazo, e por que 30 dias

```markdown
Um lote de achados é reconferido a cada 30 dias.
<!-- arbitrated: seguranca.prazo=30 por="quem conduz a revisão" em=AAAA-MM-DD vence=180d
     derruba="um repositório congelado, ou um que faz release diário" -->
```

Trinta dias é curto porque **achado envelhece por dois caminhos ao mesmo tempo**: o código muda
debaixo dele, e o catálogo muda por cima dele. Nenhum dos dois dispara evento no seu repositório.

## O que NÃO selar aqui

**Nada sobre severidade agregada.** *"Nenhum achado crítico"* depende do vetor, do contexto de
negócio e de quem calculou. Selar isso é dar aparência de medida a três julgamentos empilhados.

**Nada sobre correção.** *"Todos os achados foram corrigidos"* é sobre o código, e estas sondas
leem a pasta de achados. Um achado marcado como corrigido e não corrigido passa por todas elas.

**Nada no relatório entregue ao cliente.** Os selos são instrumentação da sua esteira. Um cliente
lendo `natureza=relacao` no meio do laudo lê ruído — e o que ele precisa saber sobre limites está na
seção «o que esta revisão não olhou», escrita em português.
