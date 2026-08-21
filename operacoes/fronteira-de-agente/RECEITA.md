# Operação 3 · `fronteira-de-agente`

> Você escreveu doze subagentes. Cinco podem buscar na web, quatro podem escrever no disco.
> **Quantos declaram para onde podem falar e onde podem escrever?**
> Se a resposta for *"está no prompt"*, a resposta é zero: prompt é pedido de boa-fé ao modelo,
> não fronteira. Fronteira é um processo que roda antes da ferramenta e responde `deny`.

## A dor

Um subagente é o único artefato de software que a gente cria sem declarar permissão. Você não subiria
um serviço com credencial de administrador "porque o README pede cuidado" — e é exatamente isso que
um agente com `WebFetch` e sem cerca é.

O pior é que **ninguém sabe quantos são**. O arquivo do agente diz o que ele pode usar; o arquivo de
configuração diz o que está cercado; **os dois nunca são lidos juntos**. Esta operação lê.

## O que esta operação instala

Doze sondas que cruzam `.claude/agents/*.md` com `.claude/settings.json`:
<!-- aferido: operacao.fronteira.sondas=12 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/fronteira-de-agente/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `agentes.total` · `agentes.com_ferramentas` | quantos existem, quantos declaram `tools:` | contagem |
| `agentes.com_rede` · `agentes.com_escrita` · `agentes.com_execucao` | quantos pedem cada classe de poder | contagem |
| `agentes.hooks` | quantos `PreToolUse` estão registrados de verdade | contagem |
| **`agentes.rede_sem_cerca`** | **pedem rede e nenhum hook os cobre** | **relação** |
| **`agentes.escrita_sem_cerca`** | **pedem escrita e nenhum hook os cobre** | **relação** |
| **`agentes.execucao_sem_cerca`** | **pedem shell e nenhum hook os cobre** | **relação** |
| **`agentes.sem_anti_descricao`** | **a descrição não diz em que caso NÃO usá-los** | **relação** |
| `agentes.ferramentas_desconhecidas` | nomes fora do vocabulário fechado | relação |
| **`agentes.reprovariam_na_forja`** | **quantos falhariam R1, R2 ou R3 se fossem compilados** | **relação** |

A última é a que dói. A forja recusa compilar uma spec que peça rede sem declarar domínio, ou
escrita sem declarar caminho, ou que não diga quando *não* ser usada. Esta sonda aplica as mesmas
três regras aos agentes que você já escreveu **à mão**, e devolve quantos não passariam.

## O ajuste

**Um campo.** No topo do `sondas.py`:

```python
PASTAS_DE_AGENTE = (
    ".claude/agents",   # Claude Code
    ".config/agents",
    "agents",
)
```

Acrescente o caminho do seu harness se ele não estiver aí. Pasta ausente não é erro — a lista é lida
inteira e o que não existe é ignorado.

## O que você vê

Num repositório sem cerca nenhuma:

```console
agentes.total                      = 2
agentes.com_rede                   = 1
agentes.hooks                      = 0
agentes.rede_sem_cerca             = 1
agentes.escrita_sem_cerca          = 1
agentes.sem_anti_descricao         = 1
agentes.reprovariam_na_forja       = 1
```

Num repositório que já cercou:

```console
agentes.total                      = 24
agentes.com_rede                   = 2
agentes.com_escrita                = 14
agentes.hooks                      = 4
agentes.rede_sem_cerca             = 0
agentes.escrita_sem_cerca          = 0
agentes.reprovariam_na_forja       = 0
agentes.ferramentas_desconhecidas  = 7
```

> *As duas saídas foram executadas em 2026-08-21 — a primeira sobre um repositório sintético, a
> segunda sobre um repositório real. São exemplos daquela execução, não asserção sobre o seu.*

Repare no `ferramentas_desconhecidas = 7` do segundo. Não é defeito: são ferramentas MCP, que o
vocabulário fechado não conhece. É **exibido** justamente porque tratar nome desconhecido como
inofensivo é como uma cerca deixa de cercar sem ninguém ver.

## Como rodar

```console
$ cp operacoes/fronteira-de-agente/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ python -m aferido .
```

E cole no seu `README.md` ou `AGENTS.md`:

```markdown
## Fronteira dos agentes

Nenhum subagente deste repositório usa rede ou escrita sem um hook que o cerque.
<!-- aferido: agentes.rede_sem_cerca=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=.claude/settings.json -->
<!-- aferido: agentes.escrita_sem_cerca=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=.claude/settings.json -->
<!-- aferido: agentes.reprovariam_na_forja=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=.claude/agents -->
```

Se algum não for zero hoje, **sele o número de hoje mesmo assim**, com `vence=30d`. Um número
incômodo selado com prazo é uma dívida com data; um número incômodo não escrito é uma dívida que
ninguém vai lembrar.

## O agente

`agente.toml` compila o `auditor-de-fronteira`, que faz o que a sonda não faz: abre cada agente
reprovado, diz **qual** das três regras ele falha, e escreve a linha de conserto — o
`dominios_permitidos`, o `saida_cercada` ou o `nunca_usar` que está faltando.

```console
$ python -m forja operacoes/fronteira-de-agente/agente.toml
```

## As quatro coisas que esta operação não faz

1. **Ela mede fronteira DECLARADA, não segurança.** Um hook registrado pode estar quebrado, ou
   liberar tudo. A sonda vê que ele existe; se ele nega de verdade é outra pergunta — e a resposta é
   rodar o hook contra um evento de teste, que é o que o autoteste da forja faz com os hooks que ela
   emite.
2. **Ela não vê `R4` a `R8`.** Lacunas declaradas, golden set, autorização de engajamento e slug
   inválido não são detectáveis num `.md` já compilado — eles moram na spec, não no artefato. Quem
   quer as oito recusas compila pela forja em vez de auditar depois.
3. **`tools: *` conta como "não declara".** Um agente que herda tudo não tem fronteira própria, e
   somá-lo às classes de poder daria um número que parece cercado e não é.
4. **Ela não sabe de hook fora do `settings.json`.** Um harness que registre barreira noutro lugar
   passa como se não tivesse nenhuma. Se for o seu caso, a saída é escrever a sonda — são dez linhas,
   e o `_front_matchers_de_hook` mostra o formato.
