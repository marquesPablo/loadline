# Operação 5 · `fabrica-de-agentes`

> Você tem nove subagentes. **De quantos deles existe uma fonte?**
> Não o arquivo que o harness lê — a fonte: o documento de onde aquele arquivo foi gerado, que
> alguém revisou, e que pode ser recompilado amanhã com uma regra nova.
> Se a resposta for *"o arquivo é a fonte"*, então toda regra que você aprender daqui para a frente
> vai ter de ser aplicada nove vezes, à mão, para sempre.

## A dor

Um agente escrito à mão é o único artefato de software que a gente aceita sem build. Ninguém aceita
um binário sem código-fonte; todo mundo aceita um `.md` de agente sem spec.

O custo aparece na terceira regra. Você descobre que agente sem anti-descrição faz o orquestrador
despachar por tema — e agora tem de editar nove arquivos. Descobre que agente com escrita precisa
declarar caminho — mais nove. Cada regra nova é um mutirão, e o mutirão nunca é completo: **sempre
sobra um arquivo que ninguém tocou, e ele é indistinguível dos outros oito.**

Com fonte, regra nova é uma linha no compilador e um `for` na pasta.

E há um defeito pior, que só existe depois que você adota spec: **a spec editada e o artefato não
recompilado.** Os dois arquivos estão certos, cada um por si. O que roda não é o que está escrito, e
nenhuma revisão de código pega isso — a divergência não mora em nenhum dos dois, mora na distância
entre as datas deles.

## O que esta operação instala

Oito sondas que cruzam as suas specs com os seus artefatos:
<!-- measured: operacao.fabrica.sondas=8 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/fabrica-de-agentes/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `fabrica.artefatos` · `fabrica.specs` | quantos agentes existem, quantas specs existem | contagem |
| **`fabrica.escritos_a_mao`** | **artefato sem spec — agente sem fonte** | **relação** |
| **`fabrica.specs_nao_compiladas`** | **spec sem artefato — está escrito e não roda** | **relação** |
| **`fabrica.artefato_desatualizado`** | **a spec é mais nova que o artefato: o que roda não é o que está escrito** | **relação** |
| **`fabrica.specs_recusadas`** | **specs que a forja recusa — as oito regras rodadas de verdade** | **relação** |
| **`fabrica.artefatos_sem_anti_descricao`** | **a descrição não diz em que caso NÃO usar** | **relação** |
| `fabrica.slugs_invalidos` | slugs que viram nome de arquivo quebrado em algum harness | relação |

**Seis das oito são de relação, e isso é a operação.** Nenhuma delas deveria andar quando você
escreve um agente novo — se andou, alguma coisa ficou pela metade. `contagem` você resela e segue;
`relacao` manda parar.

⚠️ **`fabrica.specs_recusadas` chama a forja de verdade**, ela não reimplementa as oito regras.
Reimplementar seria escrever um segundo juiz que envelhece separado do primeiro — e os dois
discordariam sem ninguém saber qual está certo.

## O ajuste

**Zero campos, se os seus agentes moram em `.claude/agents/`.** Se não, duas tuplas no topo do
`sondas.py`:

```python
PASTAS_DE_SPEC = ("agentes", "specs", "forja/exemplos")
PASTAS_DE_ARTEFATO = (".claude/agents", ".config/agents", ".agents")
```

Se você ainda não tem nenhuma spec, **não crie a pasta** — deixe como está. A primeira rodada vai
dizer que todos os seus agentes são escritos à mão, e esse é o número que abre a conversa.

## Como rodar

```console
$ cp operacoes/fabrica-de-agentes/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ PYTHONPATH=/caminho/para/loadline python -m loadline . --selar
```

O que você vê, num repositório que nunca teve spec:

```console
⚠️  NINGUÉM CONSEGUE CONFERIR ISTO — são suspeitas, não defeitos.
      SEM PROVA  README.md:14  "Temos 9 subagentes especializados."  → ninguém confere 9
------------------------------------------------------------------------
escrevi 1 selo(s), todos como `arbitrated:` — ninguém mediu nada ainda.
```

E depois de trocar `arbitrated:` por `measured:` nas métricas que esta operação sabe recomputar:

```console
$ PYTHONPATH=/caminho/para/loadline python -m loadline .
REPROVA   README.md:14  fabrica.escritos_a_mao: escrito=0 medido=9
          → natureza=relacao — PARE e investigue. Nenhum dos 9 agentes tem fonte.
```

**O `escrito=0` não é um erro de digitação seu.** É o estado normal de quem nunca separou os dois:
o número nunca tinha sido nomeado, então zero era o palpite honesto. A operação existe para o
palpite virar medida.

## Do alarme ao trabalho

`fabrica.escritos_a_mao=9` diz que há nove. **Quais**, e que spec cada um teria, é trabalho — e é
o que o agente desta operação faz:

```console
$ python -m forja operacoes/fabrica-de-agentes/agente.toml
  ✓ build/arquiteto-de-agente/.claude/agents/arquiteto-de-agente.md
  ✓ build/arquiteto-de-agente/hooks/cerca_arquiteto_de_agente.py
  …
```

Ele lê a prosa — a descrição de um trabalho, ou um agente que você já escreveu — e devolve a spec
que a forja aceita, com as oito recusas antecipadas. **Ele não inventa os campos que faltam.** Se a
descrição não diz em que caso o agente é a escolha errada, ele devolve a pergunta, porque
anti-descrição inventada é pior que nenhuma: parece cobertura.

## O que esta operação NÃO faz

1. **Não roda nenhum agente.** Uma spec impecável compila um agente inútil sem reclamar. O que se
   mede aqui é **procedência** — de onde veio o que está rodando —, nunca qualidade.

2. **Não julga se o trabalho precisava de um agente.** Muitos não precisavam: precisavam de uma
   função de dez linhas. Nenhuma sonda daqui vai dizer isso, e o agente também não.

3. **`fabrica.artefato_desatualizado` só vale na sua árvore de trabalho.** O `git` não preserva
   `mtime`: num clone limpo todo arquivo nasce com a mesma data, e a sonda devolve zero por
   construção. **Um zero dela no CI não é prova de nada** — e está escrito assim no próprio
   `sondas.py`, para ninguém descobrir usando.

4. **Não migra nada.** Ela mostra o tamanho do buraco; atravessá-lo é trabalho de quem é dono do
   repositório, e a ordem em que os nove viram spec é decisão, não cálculo.
