# Os selos desta operação

## Os quatro que mandam parar

Cole **no README do seu vault** — o arquivo que descreve o que o corpus é e o que o servidor serve.

```markdown
Este servidor expõe quatro ferramentas somente-leitura sobre as minhas notas, sem nenhuma
dependência de terceiros, e o grafo não tem aresta para o vazio.
<!-- measured: cerebro.ferramentas=4 nature=relation on=AAAA-MM-DD expires=never source=servidor.py -->
<!-- measured: cerebro.dependencias=0 nature=relation on=AAAA-MM-DD expires=never source=servidor.py -->
<!-- measured: cerebro.links_quebrados=0 nature=relation on=AAAA-MM-DD expires=30d source=corpus -->
<!-- measured: cerebro.orfas=0 nature=relation on=AAAA-MM-DD expires=90d source=corpus -->
```

**`cerebro.dependencias=0` é o selo mais valioso desta operação**, e o menos óbvio. *"Zero
dependências"* é a frase que faz alguém rodar isto numa máquina que não administra — e ela morre no
dia em que alguém acrescenta um `import` por conveniência. O diff mostra uma linha; nenhuma revisão
de código repara. A sonda lê o código e conta.

**`cerebro.ferramentas` com `vence=nunca`, de propósito.** Ela não envelhece com o tempo: ela anda
quando alguém mexe no servidor, e é exatamente aí que ela tem de reprovar. Pôr prazo nela faria a
mesma métrica reprovar por duas razões diferentes, e o vermelho deixaria de dizer qual.

## As duas contagens do corpus

```markdown
<!-- measured: cerebro.notas=N nature=count on=AAAA-MM-DD expires=90d source=corpus -->
<!-- measured: cerebro.pastas=N nature=count on=AAAA-MM-DD expires=90d source=corpus -->
```

Estas andam toda vez que você escreve. Divergiram, resele e siga — é o caso em que o vermelho
significa *"você trabalhou"*.

## ⚠️ O erro que esta operação convida você a cometer

**Nunca escreva `[[wiki-link]]` dentro do comentário de um selo, nem numa nota que exista para
MEDIR o grafo.**

Nomear uma nota órfã lhe dá uma aresta de entrada. Se o arquivo onde você registra as órfãs as cita
por wiki-link, ele **fecha o buraco que está medindo** — e `cerebro.orfas` cai para zero por causa
do próprio registro. O número fica verde e a medição morreu.

Vale para o selo também: o parser de link não distingue o comentário HTML do texto. Se precisar
nomear uma nota dentro de um selo ou de um registro de órfãs, escreva o nome **por extenso, sem os
colchetes duplos**.

## O prazo é escolha, e ela tem dono

```markdown
O grafo de notas é reconferido a cada 30 dias.
<!-- arbitrated: cerebro.prazo=30 by="quem adotou a operação" on=AAAA-MM-DD expires=180d
     breaks="um vault que só recebe notas novas, ou um em que várias pessoas renomeiam arquivo" -->
```

Trinta dias para link quebrado e noventa para órfã não é simetria esquecida: **link quebrado nasce
de um rename e conserta-se em segundos**; **órfã é julgamento** — muitas notas legitimamente não
são citadas por ninguém ainda, e cobrar isso a cada mês treina você a criar link de fachada.

## O que NÃO selar aqui

**Nada sobre o CONTEÚDO estar certo.** As sondas contam arquivo, link e import. Uma nota inteira
errada passa por todas elas. Um selo verde aqui diz que o corpus está bem ligado, jamais que ele
está correto.

**Nada sobre desempenho ou tamanho de contexto.** *"O servidor responde em 40 ms"* depende da
máquina de quem rodou, e um número desses selado no seu README vira uma promessa que você faz com o
computador de outra pessoa.

**Nada sobre segurança do conteúdo.** A cerca do servidor é de **caminho**: ele recusa ler fora da
raiz. Ele não julga o que está escrito dentro das notas que serve, e um selo verde não é atestado
de que o seu corpus não contém ordem dirigida a agente.
