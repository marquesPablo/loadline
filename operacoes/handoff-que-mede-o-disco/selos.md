# Os selos desta operação

## Onde eles moram, e aqui isso é a decisão inteira

Cole **dentro do próprio arquivo de retomada**, no topo. Em nenhuma outra operação da prateleira o
lugar importa tanto: o selo tem de estar no documento que ele julga, porque é esse documento que
alguém vai abrir daqui a três semanas acreditando nele.

Um selo sobre o handoff guardado no README é um aviso pendurado na porta errada.

## Os três que mandam parar

```markdown
Este arquivo foi escrito lendo o disco: nenhum caminho citado está morto, nenhum comando perdeu o
alvo, e o que ele diz sobre o estado do repositório é o que o git diz.
<!-- aferido: handoff.caminhos_mortos=0 natureza=relacao em=AAAA-MM-DD vence=7d fonte=disco -->
<!-- aferido: handoff.comandos_sem_alvo=0 natureza=relacao em=AAAA-MM-DD vence=7d fonte=disco -->
<!-- aferido: handoff.deriva_de_git=0 natureza=relacao em=AAAA-MM-DD vence=7d fonte=git -->
```

**`vence=7d` nos três, e é o prazo mais curto de toda a prateleira** — junto com o da fila de
decisão. Não é rigor: é que o valor deles caduca em dias. Um handoff que estava correto há um mês
não está *quase* correto hoje; ele está falso com aparência de específico, que é o estado mais caro
de todos.

⚠️ **`handoff.deriva_de_git` é 0 ou 1, não uma contagem.** Ela responde *"o documento afirma uma
coisa sobre o estado e o git afirma outra?"*. Se o documento **não afirma nada** sobre o estado, ela
é 0 — silêncio não é asserção, e acusá-lo transformaria a sonda numa cobrança de estilo.

## A idade, que é o número que abre a conversa

```markdown
Escrito depois do commit N. Nada entrou desde então.
<!-- aferido: handoff.commits_desde=0 natureza=contagem em=AAAA-MM-DD vence=7d fonte=git -->
<!-- aferido: handoff.sessoes_desde=0 natureza=contagem em=AAAA-MM-DD vence=7d fonte=harness -->
```

De contagem: elas andam sozinhas, todo dia, e é essa a graça. **Divergiram, resele — mas leia o
número antes.** Se `commits_desde` foi de 0 para 40, o resselo não é a tarefa: a tarefa é reescrever
o documento, e o resselo é a consequência.

⚠️ **As duas só valem na sua árvore de trabalho.** O git não preserva `mtime`; num clone limpo elas
estouram para o total. **Não leia o verde delas no CI como prova** — e se o seu CI rodar esta
operação, leia a advertência que está no `ci.yml`.

## O tamanho, e por que ele é `arbitrado:` e não `aferido:`

```markdown
Este arquivo cabe em 400 linhas. Passou disso, alguma coisa aqui virou histórico e devia sair.
<!-- arbitrado: handoff.teto_de_linhas=400 por="quem cuida do projeto" em=AAAA-MM-DD vence=180d
     derruba="um projeto com muitas frentes paralelas, ou um handoff que passou a ser lido por gente de fora" -->
<!-- aferido: handoff.linhas=N natureza=contagem em=AAAA-MM-DD vence=30d fonte=disco -->
```

**O teto é uma escolha, não uma medida** — por isso a terceira marca. Um handoff morre de duas
formas: envelhecendo e **inchando**. A segunda é mais silenciosa, porque ninguém o rejeita: ele
apenas passa a ocupar o começo de toda sessão sem devolver nada, e cada rodada acrescenta um pouco.

## O que NÃO selar aqui

**Nada que afirme que as verificações PASSAM.** Esta operação não executa nada — ela confere que o
alvo do comando existe. `comandos_sem_alvo=0` e *"a suíte está verde"* são afirmações diferentes, e
selar a segunda com a sonda da primeira é dar marca de medida a uma esperança.

**Nada sobre o que foi decidido na sessão.** As sondas leem o disco. O que foi combinado e não virou
arquivo é invisível para todas as oito, e um selo verde não é atestado de que o contexto está
completo.

**Nada sobre o handoff estar CERTO.** Ele pode ter zero caminho morto, zero deriva, zero commits em
cima — e descrever mal o que importa. As sondas medem se ele corresponde ao disco. Se ele conta a
história certa continua sendo julgamento de quem escreve.
