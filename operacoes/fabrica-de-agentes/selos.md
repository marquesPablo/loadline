# Os selos desta operação

## Os seis que mandam parar

Cole **no arquivo que descreve os seus agentes** — o `README.md` da pasta de agentes, o `AGENTS.md`,
ou onde quer que esteja escrito quantos você tem. O selo tem de morar no arquivo que ele julga: se
ele estiver noutro lugar, quem edita a lista não vê o que ela prometia.

```markdown
Todo agente deste repositório tem uma spec de onde saiu, toda spec está compilada, e o que roda é
o que está escrito.
<!-- measured: fabrica.escritos_a_mao=0 natureza=relacao em=AAAA-MM-DD vence=60d fonte=.claude/agents/ -->
<!-- measured: fabrica.specs_nao_compiladas=0 natureza=relacao em=AAAA-MM-DD vence=60d fonte=agentes/ -->
<!-- measured: fabrica.artefato_desatualizado=0 natureza=relacao em=AAAA-MM-DD vence=7d fonte=mtime -->
<!-- measured: fabrica.specs_recusadas=0 natureza=relacao em=AAAA-MM-DD vence=60d fonte=forja -->
<!-- measured: fabrica.artefatos_sem_anti_descricao=0 natureza=relacao em=AAAA-MM-DD vence=60d fonte=.claude/agents/ -->
<!-- measured: fabrica.slugs_invalidos=0 natureza=relacao em=AAAA-MM-DD vence=nunca fonte=.claude/agents/ -->
```

**Todos de `relacao`, e nenhum deles deve andar quando você escreve um agente novo.** É isso que
os separa das duas contagens abaixo: se um deles saiu de zero, alguma coisa ficou pela metade, e a
resposta certa é parar — nunca resselar o número para cima.

### O prazo de 7 dias do `artefato_desatualizado`, e por que ele é o mais curto daqui

Uma spec editada e não recompilada é o defeito mais curto de vida útil desta operação: ele nasce no
minuto em que alguém salva a spec e morre no minuto em que alguém roda a forja. Um prazo de 60 dias
ali daria cobertura a um estado que dura horas — e cobertura sobre um estado que já passou é a forma
mais barata de um verde não significar nada.

⚠️ **E ele tem um limite que não dá para selar em volta:** `mtime` não sobrevive a um clone. No CI
esta sonda devolve zero por construção. **Selar isto no `README.md` e ler o verde do CI como prova
é a armadilha desta operação inteira** — o número vale na máquina de quem edita, e é lá que ele
tem de ser lido.

## As duas contagens

```markdown
<!-- measured: fabrica.artefatos=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=.claude/agents/ -->
<!-- measured: fabrica.specs=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=agentes/ -->
```

Estas duas andam quando alguém escreve. Divergiram, resele e siga.

⚠️ **Não escreva as duas na mesma frase que afirma um terceiro número.** *"Temos 9 agentes, todos
compilados de 9 specs"* afirma três coisas e o selo cobre duas — a terceira (*todos*) é uma
afirmação de relação que nenhuma métrica ali nomeia, e o veredito `PROSE_DRIFT` existe exatamente
para isso.

## O prazo é escolha, e ela tem dono

```markdown
A pasta de agentes é reconferida a cada 60 dias.
<!-- arbitrated: fabrica.prazo=60 por="quem adotou a operação" em=AAAA-MM-DD vence=180d
     derruba="um time que cria agente toda semana, ou um repositório cujos agentes não mudam há um ano" -->
```

Sessenta dias é o padrão desta operação, não uma medida. Um número escolhido sem dono é um palpite
com cara de fato — e é para isso que a terceira marca existe.

## O que NÃO selar aqui

**Nada que afirme que um agente FUNCIONA.** As sondas leem procedência: de onde veio o arquivo que
está rodando. Uma spec impecável compila um agente inútil sem reclamar, e um selo verde sobre
qualidade seria um número inventado com marca de medido.

**Nada sobre o poder ser o mínimo necessário.** *"Nenhum agente nosso pede mais do que precisa"* é
julgamento de menor privilégio — ele é humano, muda com a tarefa, e nenhuma sonda offline o alcança.
O que se pode selar é a **cerca declarada**, e isso é a operação `fronteira-de-agente`.

**Nada sobre o conteúdo do prompt.** Injeção, ordem plantada e vírus de ideia são outra família de
defeito, e exigem outro método. Um selo de `fabrica.*` verde não diz nada sobre eles.
