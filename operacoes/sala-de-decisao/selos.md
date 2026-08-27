# Os selos desta operação

## Os três que mandam parar

Cole **no índice do seu registro de decisões** — `decisoes/README.md` ou o arquivo que lista o
acervo. O selo tem de morar no arquivo que ele julga.

```markdown
Toda decisão deste acervo declara se está em vigor, diz o que foi recusado, e nenhuma revogação
foi declarada de um lado só.
<!-- measured: decisao.sem_status=0 nature=relation on=AAAA-MM-DD expires=90d source=decisoes/ -->
<!-- measured: decisao.revogacao_de_um_lado_so=0 nature=relation on=AAAA-MM-DD expires=90d source=decisoes/ -->
<!-- measured: decisao.sem_alternativa=0 nature=relation on=AAAA-MM-DD expires=90d source=decisoes/ -->
```

**Os três de `relacao`, e nenhum deles deve andar quando você escreve uma decisão nova.** Se um saiu
de zero, alguma coisa ficou pela metade — e a resposta certa é abrir o arquivo, não resselar.

## A fila, e o único número que piora sozinho

```markdown
Há N itens esperando uma decisão, e o mais antigo espera há D dias.
<!-- measured: decisao.gates_abertos=N nature=count on=AAAA-MM-DD expires=7d source=decisoes/ -->
<!-- measured: decisao.gate_mais_velho_dias=D nature=count on=AAAA-MM-DD expires=7d source=decisoes/ -->
```

⚠️ **`vence=7d` nos dois, e é o prazo mais curto de toda a prateleira.** Não é rigor: é que o valor
deles caduca em dias, não em meses. Um selo que diz *"o mais antigo espera há 3 dias"* escrito há
dois meses não está errado — está **obsoleto**, que é pior, porque ele parece informação.

**`decisao.gate_mais_velho_dias` é a única métrica desta prateleira que sobe quando você não faz
nada.** Ela é de contagem — divergiu, resele —, mas leia o número antes de resselar. Se ele foi de
12 para 47, o resselo não é a tarefa: a tarefa é o item que está lá há 47 dias.

## As três contagens do acervo

```markdown
<!-- measured: decisao.total=N nature=count on=AAAA-MM-DD expires=90d source=decisoes/ -->
<!-- measured: decisao.aceitas=N nature=count on=AAAA-MM-DD expires=90d source=decisoes/ -->
<!-- measured: decisao.revogadas=N nature=count on=AAAA-MM-DD expires=90d source=decisoes/ -->
```

⚠️ **Não escreva as três numa frase que também afirme a soma.** *"São 44 decisões: 41 aceitas e 3
revogadas"* afirma quatro coisas, e o selo cobre três — a quarta (que 41+3 esgota as 44) é uma
afirmação de relação que nenhuma métrica ali nomeia. É para isso que existe o veredito `PROSE_DRIFT`.

Se você quiser mesmo afirmar que esgota, **selar `decisao.sem_status=0` é o que diz isso** — e aí a
frase e o selo passam a falar da mesma coisa.

## O prazo é escolha, e ela tem dono

```markdown
Um item esperando decisão é revisto toda semana.
<!-- arbitrated: decisao.prazo_de_fila=7 by="quem toca a sala de decisão" on=AAAA-MM-DD expires=180d
     breaks="uma equipe que decide em rodadas mensais, ou um item cujo custo de espera é zero" -->
```

Sete dias é o padrão desta operação, não uma medida. Um número escolhido sem dono é um palpite com
cara de fato.

## O que NÃO selar aqui

**Nada que afirme que as decisões estão sendo CUMPRIDAS.** *"Seguimos todas as nossas decisões"* é
sobre comportamento, e as sondas leem arquivo. Uma decisão pode estar aceita, datada, íntegra — e
ninguém a seguir. Selar isso seria dar marca de medida a uma esperança.

**Nada sobre a qualidade da decisão.** Registrada, datada e com alternativa é o que se mede.
*Certa* não é recomputável por função nenhuma.

**Nada sobre o que não virou arquivo.** *"Todas as nossas decisões estão registradas"* é
exatamente o que nenhuma sonda daqui pode confirmar: ela conta o que existe na pasta, e o que foi
combinado numa reunião e nunca escrito é invisível para ela. Um selo verde ali seria a ferramenta
atestando o próprio ponto cego.
