# Operação 7 · `sala-de-decisao`

> **O que está parado agora esperando uma decisão sua?**
> Se responder isso exige abrir o Slack, três threads e a memória de duas pessoas, então nada está
> esperando: as coisas estão **esquecidas**, e o custo aparece na semana em que uma delas passa a
> ser urgente.

## A dor

Toda equipe tem um registro de decisões que morreu na terceira semana. E quase sempre morreu pelo
mesmo motivo: ele registrava o que **já** tinha sido decidido — que é a parte que ninguém precisa,
porque quem decidiu lembra.

A parte cara é a outra: **o que ainda não foi decidido, e está parado.**

Um item parado não fica pior de repente. Ele fica pior um dia por vez, e é exatamente por isso que
ninguém repara. Não há evento, não há notificação, não há diff. No dia 40 alguém diz *"pensei que
você ia decidir isso"*, e as duas pessoas estão convencidas de que a bola era da outra.

E há um segundo defeito, mais silencioso: **a revogação declarada de um lado só.** A decisão nova
diz `revoga: ADR-031`. A `ADR-031` não diz nada. Quem abre a antiga — que é o caminho normal, porque
é ela que está citada nos lugares antigos — lê uma regra revogada como se ela valesse. Os dois
arquivos estão certos, cada um por si. **O defeito mora entre eles.**

## O que esta operação instala

Oito sondas sobre uma pasta de arquivos markdown:
<!-- aferido: operacao.sala.sondas=8 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/sala-de-decisao/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `decisao.total` · `decisao.aceitas` · `decisao.revogadas` | o tamanho e o estado do acervo | contagem |
| **`decisao.sem_status`** | **decisões que não dizem se estão em vigor** | **relação** |
| **`decisao.revogacao_de_um_lado_so`** | **a nova revoga a antiga, e a antiga não sabe** | **relação** |
| **`decisao.sem_alternativa`** | **decisões que não dizem o que foi recusado** | **relação** |
| `decisao.gates_abertos` | quantos itens esperam uma pessoa | contagem |
| **`decisao.gate_mais_velho_dias`** | **há quantos dias o mais antigo espera** | contagem |

**`decisao.gate_mais_velho_dias` é a única métrica desta prateleira inteira que piora quando você
não faz nada.** Ela sobe sozinha, todo dia, até alguém decidir. É de propósito: um número que só
melhora com ação é a única forma honesta de medir o que a inércia custa.

## As duas convenções, e por que elas moram no NOME do arquivo

**Um gate é um arquivo que espera decisão de uma pessoa.** Ele é reconhecido por duas coisas:

```
decisoes/2026-03-04-gate-trocar-o-provedor-de-email.md
          └── a data          └── a palavra `gate`
```

1. **A palavra `gate` no nome.** Sem ela o arquivo é uma decisão comum, e some no meio das outras.
2. **A data no nome.** É de onde sai a idade.

Isto parece detalhe de estilo e não é. **O nome do arquivo é a única parte que aparece em `ls`, no
explorador, no diff do PR e na busca — sem ninguém abrir nada.** Um campo `criada_em:` dentro do
frontmatter é invisível em todos esses lugares. Um item que espera decisão e que ninguém vê não está
esperando: está esquecido.

E o gate fecha com um **título** markdown contendo `DECIDIDO`:

```markdown
## DECIDIDO — 2026-03-19

Ficamos com o provedor atual por mais um ano. Motivo: a migração custaria duas semanas de
uma pessoa e o ganho medido foi de 4% na entrega.
```

**Título, não negrito.** `**DECIDIDO**` no meio de um parágrafo fecha o gate e some do histórico —
e uma busca por títulos é como se lê um registro destes seis meses depois.

## O ajuste

**Um campo**, no topo do `sondas.py`:

```python
PASTA_DE_DECISOES = "decisoes"
```

Não há formato obrigatório para o corpo. As sondas leem `status:` no frontmatter, a palavra
`revoga:`/`emenda:`, e procuram uma seção de alternativas. Se o seu formato usa outras palavras,
ajuste os quatro `re.compile` do topo — eles estão em um bloco só, nomeados.

## Como rodar

```console
$ cp operacoes/sala-de-decisao/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ PYTHONPATH=/caminho/para/aferido python -m aferido .
```

```console
REPROVA   decisoes/README.md:8  decisao.revogacao_de_um_lado_so: escrito=0 medido=3
          → natureza=relacao — PARE e investigue.
REPROVA   decisoes/README.md:9  decisao.gate_mais_velho_dias: escrito=12 medido=47
          → natureza=contagem — resele; e leia o número antes.
```

**O segundo é o que dói.** Ele não é um erro de anotação: é 47 dias de um item esperando você, e o
selo escrito há um mês é a prova de que ninguém olhou desde então.

## O que esta operação NÃO faz

1. **Não decide, e nunca vai decidir.** O agente expõe as decisões que se contradizem e para.
   Escolher exigiria saber qual foi mais pensada, qual o time ainda sustenta e o que mudou no mundo
   — nenhuma das três está no texto. **Decidir é o único trabalho que este registro existe para não
   automatizar.**

2. **Não vê o que não virou arquivo.** O que foi combinado numa reunião e não foi escrito é
   invisível para todas as oito sondas. Essa é a maior lacuna daqui, e nenhuma ferramenta a fecha —
   ela se fecha com o hábito de escrever.

3. **Não mede se a decisão está sendo CUMPRIDA.** Uma decisão pode estar aceita, datada, íntegra,
   com alternativas — e ninguém a seguir. As sondas leem o registro, não o comportamento.

4. **Não julga se a decisão foi boa.** Ela mede se está registrada, datada, com alternativa e com
   contra-ponteiro. Qualidade de julgamento não é recomputável por função nenhuma, e um selo verde
   sobre isso seria um palpite com marca de medida.
