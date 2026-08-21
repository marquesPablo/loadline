# Os selos desta operação

## Os quatro que valem por si

Cole no `README.md` ou no `AGENTS.md` do repositório onde os agentes moram.

```markdown
## Fronteira dos agentes

Nenhum subagente deste repositório usa rede, escrita ou shell sem um hook registrado que o cerque,
e todos dizem em que caso NÃO devem ser usados.
<!-- aferido: agentes.rede_sem_cerca=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=.claude/settings.json -->
<!-- aferido: agentes.escrita_sem_cerca=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=.claude/settings.json -->
<!-- aferido: agentes.execucao_sem_cerca=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=.claude/settings.json -->
<!-- aferido: agentes.sem_anti_descricao=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=.claude/agents -->
```

**Todos de `relacao`, e o motivo importa.** Estes números deveriam ser sempre zero. Quando um sai de
zero, não é *"a contagem andou porque alguém escreveu"* — é *alguém acrescentou poder sem cerca*. A
ferramenta imprime **PARE. Relação divergindo é defeito — investigue antes de resselar**, e essa
frase é a operação inteira.

Marcar isto como `contagem` treinaria o time a resselar exatamente o defeito que o selo existe para
pegar. É o erro mais fácil de cometer aqui e o mais caro.

## Se hoje não for zero

**Sele o número de hoje mesmo assim.** Um número incômodo selado é uma dívida com data; um número
incômodo não escrito é uma dívida que ninguém vai lembrar.

```markdown
Três subagentes ainda usam rede sem hook que os cerque. É dívida declarada, com prazo.
<!-- aferido: agentes.rede_sem_cerca=3 natureza=relacao em=AAAA-MM-DD vence=30d fonte=.claude/settings.json -->
```

Quando você cercar os três, o número cai para 0, a sonda mede 0, o selo diz 3 → **`DERIVOU`**. E
está certo que reprove: alguém precisa reescrever a frase e o selo juntos. Melhorar também é mudar.

## Os de contexto

```markdown
<!-- aferido: agentes.total=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=.claude/agents -->
<!-- aferido: agentes.com_rede=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=.claude/agents -->
<!-- aferido: agentes.com_escrita=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=.claude/agents -->
<!-- aferido: agentes.com_execucao=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=.claude/agents -->
<!-- aferido: agentes.hooks=N natureza=contagem em=AAAA-MM-DD vence=90d fonte=.claude/settings.json -->
<!-- aferido: agentes.ferramentas_desconhecidas=N natureza=relacao em=AAAA-MM-DD vence=90d fonte=.claude/agents -->
```

`agentes.ferramentas_desconhecidas` é de **relação** e as outras cinco são de **contagem**. Nomes
fora do vocabulário fechado não deveriam aparecer sozinhos: se esse número mudar sem ninguém ter
acrescentado ferramenta, a leitura quebrou.

## A decisão que este selo NÃO toma

**Menor privilégio continua sendo julgamento humano.** Nada aqui diz que um agente pede poder demais
para a tarefa dele — só que o poder que ele pede está, ou não está, cercado. Um agente com `Bash`
irrestrito e um hook que cerca `Bash` sai verde nas duas medidas, e pode continuar sendo uma péssima
ideia.

Se o time quiser um teto, ele é **escolha**, não medida, e a marca é a terceira:

```markdown
Nenhum agente deste repositório recebe ferramenta de execução.
<!-- arbitrado: agentes.teto_de_execucao=0 por="time de plataforma" em=AAAA-MM-DD vence=180d
     derruba="o primeiro trabalho que só se faça rodando comando, com autorização de escopo escrita" -->
```
