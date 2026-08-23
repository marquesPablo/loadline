# Os selos desta operação

Cole no fim do seu `README.md` (ou `CLAUDE.md`/`AGENTS.md`). Troque `AAAA-MM-DD` pela data de hoje.

## O mínimo (o que vale por si)

```markdown
## O que as skills deste repositório prometem

Toda skill sob `.claude/skills/` passa na vitrine — nome batendo com a pasta,
gatilho de uso e gatilho negativo declarados.
<!-- aferido: vitrine.reprovas=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=vitrine -->
```

**Por que `relacao` e não `contagem`.** Uma grandeza de contagem anda quando alguém escreve — subiu,
resele e siga. Esta só anda se uma skill ficou invisível: nome divergente, gramática quebrada, ou
sem cláusula de gatilho. Divergir aqui manda **parar e consertar a skill**, nunca resselar o número
para cima — marcar isto como `contagem` treinaria o time a resselar o defeito em vez de corrigi-lo.

**Por que `vence=30d`.** Skill nasce e morre com o repositório — trinta dias é a escolha padrão desta
operação, não uma medida, e por isso é um `arbitrado:`, com dono:

```markdown
O prazo de reconferência das skills é 30 dias.
<!-- arbitrado: vitrine.prazo=30 por="quem adotou a operação" em=AAAA-MM-DD vence=180d
     derruba="um repositório em que skills novas apareçam toda semana, ou nenhuma em meses" -->
```

## O completo (as duas)

```markdown
<!-- aferido: vitrine.skills=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=.claude/skills -->
<!-- aferido: vitrine.reprovas=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=vitrine -->
```

Não sabe qual `N` escrever? Não escreva. Rode `python -m aferido . --selar` e a ferramenta escreve
os dois, como `arbitrado:`, com o valor de hoje. Troque `arbitrado:` por `aferido:` — a troca é o que
transforma um número escolhido num número recomputado.

## O que NÃO selar aqui

**Nada sobre se a skill FUNCIONA.** A `vitrine` julga se a skill é **encontrável** — vitrine correta,
gatilho declarado. Se ela resolve o problema depois de encontrada é outro trabalho, que exige rodar
a skill contra tarefa real, e não tem sonda aqui. Ver `vitrine/LACUNAS.md`.

**E nada sobre o CORPO do `SKILL.md`** além da contagem de linhas. Instrução contraditória, comando
que não existe mais, ordem plantada por outro agente — nada disso é examinado por esta operação.
