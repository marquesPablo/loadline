# Os selos desta operação

Cole no fim do seu arquivo de instrução. Troque `AAAA-MM-DD` pela data de hoje — a data é o que faz
o `vence=` significar alguma coisa.

## O mínimo (os dois que valem por si)

```markdown
## O que este arquivo promete

Todo comando citado aqui existe, e todo caminho citado aqui existe.
<!-- measured: instrucao.comandos_quebrados=0 nature=relation on=AAAA-MM-DD expires=30d source=package.json -->
<!-- measured: instrucao.caminhos_quebrados=0 nature=relation on=AAAA-MM-DD expires=30d source=disco -->
```

**Por que `relacao` e não `contagem`.** Uma grandeza de contagem anda quando alguém escreve — subiu,
resele e siga. Estas duas só andam se alguma coisa quebrou: um script sumiu, uma pasta foi deletada,
ou a sonda parou de enxergar. Divergir aqui manda **parar e investigar**, e a ferramenta imprime
essas palavras. Marcar isto como `contagem` seria treinar o time a resselar o defeito.

**Por que `vence=30d`.** Um arquivo de instrução muda com o repositório. Trinta dias é a escolha
padrão desta operação, não uma medida — e por isso a linha abaixo é um `arbitrated:`, com dono:

```markdown
O prazo de reconferência do arquivo de instrução é 30 dias.
<!-- arbitrated: instrucao.prazo=30 by="quem adotou a operação" on=AAAA-MM-DD expires=180d
     breaks="um repositório em que a instrução fique meses estável, ou um em que quebre toda semana" -->
```

## O completo (as sete)

```markdown
<!-- measured: instrucao.arquivos=N nature=count on=AAAA-MM-DD expires=90d source=raiz -->
<!-- measured: instrucao.linhas=N nature=count on=AAAA-MM-DD expires=90d source=arquivos-de-instrucao -->
<!-- measured: instrucao.comandos=N nature=count on=AAAA-MM-DD expires=90d source=cercas-de-codigo -->
<!-- measured: instrucao.comandos_quebrados=0 nature=relation on=AAAA-MM-DD expires=30d source=package.json -->
<!-- measured: instrucao.caminhos=N nature=count on=AAAA-MM-DD expires=90d source=crases -->
<!-- measured: instrucao.caminhos_quebrados=0 nature=relation on=AAAA-MM-DD expires=30d source=disco -->
<!-- measured: instrucao.divergencia=N nature=count on=AAAA-MM-DD expires=60d source=titulos -->
```

Não sabe qual `N` escrever? Não escreva. Rode `python -m loadline . --selar` e a ferramenta escreve
todos, como `arbitrated:`, com o valor de hoje. Depois troque `arbitrated:` por `measured:` nestes sete
— eles têm sonda pronta, e a troca é o que transforma um número escolhido num número recomputado.

## O que NÃO selar aqui

**Nada que só o próprio arquivo de instrução saiba.** Se o número escrito e o número medido saem do
mesmo arquivo, o par passa verde **travando** o defeito em vez de achá-lo — é check espelho, e ele
não verifica nada. Todas as sete acima conferem contra uma segunda fonte: `package.json`, o
`Makefile`, ou o sistema de arquivos.

**E nada que dependa da internet.** Nenhuma sonda desta operação sai da máquina. A verdade lá fora é
exatamente o que o `vence=` existe para cobrar de um humano.
