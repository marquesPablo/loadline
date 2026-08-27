# Os selos desta operação

Cole no fim do seu `README.md` (ou `CLAUDE.md`/`AGENTS.md`). Troque `AAAA-MM-DD` pela data de hoje.

## O mínimo (o que vale por si)

```markdown
## O que as skills deste repositório prometem

Toda skill sob `.claude/skills/` passa na vitrine — nome batendo com a pasta,
gatilho de uso e gatilho negativo declarados.
<!-- measured: vitrine.reprovas=0 nature=relation on=AAAA-MM-DD expires=30d source=vitrine -->
```

**Por que `relacao` e não `contagem`.** Uma grandeza de contagem anda quando alguém escreve — subiu,
resele e siga. Esta só anda se uma skill ficou invisível: nome divergente, gramática quebrada, ou
sem cláusula de gatilho. Divergir aqui manda **parar e consertar a skill**, nunca resselar o número
para cima — marcar isto como `contagem` treinaria o time a resselar o defeito em vez de corrigi-lo.

**Por que `vence=30d`.** Skill nasce e morre com o repositório — trinta dias é a escolha padrão desta
operação, não uma medida, e por isso é um `arbitrated:`, com dono:

```markdown
O prazo de reconferência das skills é 30 dias.
<!-- arbitrated: vitrine.prazo=30 by="quem adotou a operação" on=AAAA-MM-DD expires=180d
     breaks="um repositório em que skills novas apareçam toda semana, ou nenhuma em meses" -->
```

## O completo (as duas)

```markdown
<!-- measured: vitrine.skills=N nature=count on=AAAA-MM-DD expires=90d source=.claude/skills -->
<!-- measured: vitrine.reprovas=0 nature=relation on=AAAA-MM-DD expires=30d source=vitrine -->
```

Não sabe qual `N` escrever? Não escreva. Rode `python -m loadline . --selar` e a ferramenta escreve
os dois, como `arbitrated:`, com o valor de hoje. Troque `arbitrated:` por `measured:` — a troca é o que
transforma um número escolhido num número recomputado.

## O que NÃO selar aqui

**Nada sobre se a skill FUNCIONA.** A `vitrine` julga se a skill é **encontrável** — vitrine correta,
gatilho declarado. Se ela resolve o problema depois de encontrada é outro trabalho, que exige rodar
a skill contra tarefa real, e não tem sonda aqui. Ver `vitrine/LACUNAS.md`.

**E nada sobre o CORPO do `SKILL.md`** além da contagem de linhas. Instrução contraditória, comando
que não existe mais, ordem plantada por outro agente — nada disso é examinado por esta operação.
