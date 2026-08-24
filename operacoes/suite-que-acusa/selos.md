# Os selos desta operação

## O selo que vale por si

Cole **no README do seu repositório**, na seção que fala dos testes — é lá que a promessa é feita.

```markdown
A suíte tem N checks, e nenhum deles é uma função que não pode falhar.
<!-- measured: suite.checks=N natureza=contagem em=AAAA-MM-DD vence=nunca fonte=tests/ -->
<!-- measured: suite.sem_assercao=0 natureza=relacao em=AAAA-MM-DD vence=nunca fonte=tests/ -->
```

**`suite.sem_assercao=0` é o único selo desta operação que é veredito**, e por isso é o único que
merece reprovar o CI sozinho. Uma função de teste sem asserção não pode falhar — é propriedade do
código, não opinião.

`vence=nunca` nos dois, de propósito: eles não envelhecem com o tempo, só andam quando alguém mexe
na suíte. Pôr prazo faria a mesma métrica reprovar por duas razões diferentes, e o vermelho
deixaria de dizer qual.

## A terceira lista

```markdown
Esta suíte declara N coisas que ela NÃO mede.
<!-- measured: suite.lacunas_declaradas=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=LACUNAS.md -->
```

**`vence=90d` aqui, e o prazo é o mecanismo.** Uma lista de lacunas envelhece de um jeito
particular: as lacunas **fecham** sem ninguém apagar a linha. O check que faltava foi escrito há dois
meses e a lista continua declarando o buraco. Um limite declarado que já não existe é tão enganoso
quanto um que não foi declarado — e o prazo é o que obriga alguém a reler.

## ⚠️ O selo heurístico, e como escrevê-lo sem mentir

```markdown
A régua aponta N testes sem controle negativo aparente. É uma lista de leitura, não um veredito:
a detecção erra nos dois sentidos e está declarada como heurística.
<!-- arbitrated: suite.sem_controle_negativo=N por="quem cuida da suíte" em=AAAA-MM-DD vence=60d
     derruba="qualquer teste desta lista que, ao ser aberto, revele controle negativo que a régua não reconheceu" -->
```

**`arbitrated:`, e não `measured:`.** A marca importa: `measured:` diz *isto foi medido*, e esta
métrica é uma aproximação declarada. `arbitrated:` diz *alguém escolheu tratar isto assim, e aqui
está quem*.

E `derruba=` é a parte mais valiosa — ela escreve, antes de acontecer, o que faria o número deixar
de valer. **Não ponha esta métrica no CI como reprovação.** Uma régua heurística que reprova treina
o time a escrever teste para agradar a régua, e aí ela para de medir o código.

## Os dois de higiene

```markdown
<!-- measured: suite.arquivos=N natureza=contagem em=AAAA-MM-DD vence=nunca fonte=tests/ -->
<!-- measured: suite.pulados=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=tests/ -->
```

**`suite.pulados` com prazo curto.** Um teste pulado é um teste que não existe, com aparência de
existir: ele conta na lista, aparece no relatório, e a única coisa que ele mede é há quanto tempo
alguém desistiu dele. Trinta dias é o que impede um `skip` temporário de virar permanente sem
ninguém decidir isso.

## O prazo é escolha, e ela tem dono

```markdown
A régua da suíte é reconferida a cada 60 dias.
<!-- arbitrated: suite.prazo=60 por="quem cuida da suíte" em=AAAA-MM-DD vence=180d
     derruba="um projeto que reescreve a suíte a cada release, ou um cuja suíte não muda há um ano" -->
```

## O que NÃO selar aqui

**Nada que afirme que a suíte é COMPLETA.** *"Cobrimos todos os casos"* é a afirmação que a terceira
lista existe para tornar impossível. O que não virou teste é invisível para todas as seis sondas.

**Nada sobre cobertura de linha.** Outra pergunta, outra ferramenta — e **cobertura alta com
controle negativo zero é o estado exato que esta operação existe para achar**. Selar cobertura ao
lado destas métricas convida a ler uma como confirmação da outra, quando elas frequentemente se
contradizem.

**Nada que afirme que os testes PEGARIAM um bug real.** `sem_controle_negativo=0` diz que a régua
reconheceu uma construção de expectativa de falha em cada teste. Não diz que o defeito reintroduzido
era o certo, nem que ele é o que vai acontecer na produção.
