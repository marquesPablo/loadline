# Os selos desta operação

## Os dois que valem por si

Cole **na sua tabela de licenças**, não no README. O selo tem de morar no arquivo que ele julga: se
ele estiver noutro lugar, quem edita a tabela não vê o que ela prometia.

```markdown
Toda dependência deste manifesto tem veredito de licença escrito, e nenhum veredito sobrevive à
dependência que ele julgava.
<!-- measured: deps.sem_veredito=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=manifesto -->
<!-- measured: deps.veredito_orfao=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=manifesto -->
```

**Os dois de `relacao`, e nas duas direções.** Um deveria ser zero porque ninguém instala sem
revisar; o outro porque ninguém remove sem limpar. Quando qualquer um sai de zero, é defeito de
processo, não contagem que andou — e a ferramenta manda parar e investigar em vez de resselar.

## A distribuição, e o que ela não é

```markdown
<!-- measured: deps.declaradas=N natureza=contagem em=AAAA-MM-DD vence=60d fonte=manifesto -->
<!-- measured: deps.osi=N natureza=contagem em=AAAA-MM-DD vence=60d fonte=licencas.md -->
<!-- measured: deps.copyleft_forte=N natureza=contagem em=AAAA-MM-DD vence=60d fonte=licencas.md -->
<!-- measured: deps.nao_osi=N natureza=contagem em=AAAA-MM-DD vence=60d fonte=licencas.md -->
<!-- measured: deps.proprietarias=N natureza=contagem em=AAAA-MM-DD vence=60d fonte=licencas.md -->
<!-- measured: deps.nao_verificado=N natureza=contagem em=AAAA-MM-DD vence=30d fonte=licencas.md -->
```

⚠️ **Cuidado com estas seis.** Elas são de contagem porque andam quando alguém instala ou julga — e
mesmo assim há uma armadilha: se você escrever a distribuição **dentro da própria tabela**, o número
escrito e o número medido saem quase do mesmo lugar. A sonda se salva porque cruza a tabela com o
**manifesto** — só conta quem ainda está declarado —, mas a margem é estreita.

**A leitura segura:** escreva a distribuição no `README.md` e deixe os dois de `relacao` na tabela.
Aí os dois lados ficam claramente separados: o texto que uma pessoa lê num lugar, o dado noutro.

**`deps.nao_verificado` com `vence=30d` de propósito.** É a única contagem daqui com prazo curto:
*"alguém olhou e não decidiu"* é um estado legítimo, e é um estado que não deve durar um trimestre.

## O prazo é escolha, e ela tem dono

```markdown
Uma dependência é reconferida a cada 30 dias.
<!-- arbitrated: deps.prazo=30 por="quem adotou a operação" em=AAAA-MM-DD vence=180d
     derruba="um projeto com dependência estável há anos, ou um que troque de stack a cada trimestre" -->
```

Trinta dias é o padrão desta operação, não uma medida. Um número escolhido sem dono é um palpite com
cara de fato — e é exatamente por isso que a terceira marca existe.

## O que NÃO selar aqui

**Nada que afirme o que a licença DIZ.** *"Nenhuma dependência nossa é copyleft"* pode ser verdade
sobre a tabela e falsa sobre o mundo: a tabela é o que alguém escreveu depois de ir ler, e um
relicenciamento posterior não avisa ninguém. O selo honesto sobre isso é de idade, não de conteúdo —
e é o `vence=` fazendo o trabalho dele: obrigar alguém a sair da máquina.

**Nada sobre dependência transitiva.** O manifesto não a declara, a sonda não a vê, e um selo sobre
ela seria um número inventado com marca de medido.
