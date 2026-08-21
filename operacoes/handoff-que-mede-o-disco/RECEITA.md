# Operação 10 · `handoff-que-mede-o-disco`

> Você fecha a sessão e escreve — ou pede ao modelo que escreva — um arquivo de retomada:
> *"onde paramos, o que falta, o que roda"*.
> Duas semanas depois alguém abre esse arquivo e segue o que está nele.
> **Quantas das afirmações dele ainda são verdade?**
> Ninguém sabe, porque nada as reconfere. E o documento não parece velho: parece específico.

## A dor

Um arquivo de retomada é uma **afirmação escrita sobre o disco** — e é a espécie mais frágil que
existe, porque o disco muda todo dia e o documento não.

Ele diz que o repositório está limpo, e há doze arquivos sujos. Ele manda rodar um script que foi
renomeado. Ele cita uma pasta que virou outra. Nenhuma dessas linhas fica *visivelmente* errada: elas
ficam **específicas e falsas**, que é pior. Quem lê vai até lá, não encontra, e conclui *"devo estar
no lugar errado"* em vez de *"o documento está velho"*.

E a saída usual piora o problema: pedir ao assistente que **se lembre** da sessão passada. Memória é
exatamente o lado que decai. O disco é o lado que não.

## O que esta operação instala

Oito sondas sobre o seu arquivo de retomada, todas lendo o **git** e o **sistema de arquivos** —
nunca o documento que faz a afirmação:
<!-- aferido: operacao.handoff.sondas=8 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/handoff-que-mede-o-disco/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| **`handoff.commits_desde`** | **commits que entraram depois do último toque no documento** | contagem |
| `handoff.caminhos_citados` · `handoff.comandos_citados` | o tamanho do que ele afirma | contagem |
| **`handoff.caminhos_mortos`** | **caminhos citados que não existem** | **relação** |
| **`handoff.comandos_sem_alvo`** | **comandos cujo script, alvo de `make` ou script de pacote sumiu** | **relação** |
| **`handoff.deriva_de_git`** | **ele diz «está limpo» e o `git status` discorda** | **relação** |
| `handoff.linhas` | o inchaço — a segunda forma de um handoff morrer | contagem |
| `handoff.sessoes_desde` | sessões que rodaram sem ninguém atualizar o documento | contagem |

**`handoff.commits_desde` é o número que abre a conversa.** Um documento com quarenta commits em
cima não está errado — está **desatualizado**, que é diferente e é pior, porque continua parecendo o
estado atual.

## ⚠️ Esta operação NUNCA executa o que o documento manda

O arquivo de retomada é **texto**. Ele pode ter sido escrito por qualquer pessoa, colado de qualquer
lugar, ou editado por um agente. Uma sonda que rodasse os comandos citados nele seria **execução
arbitrária a partir de documento** — injeção com convite escrito.

O que ela faz é conferir se o **alvo existe**: o arquivo do script, a regra no `Makefile`, a chave em
`scripts` do `package.json`. Um comando cujo alvo sumiu é o defeito que interessa, e descobri-lo não
exige rodá-lo.

**A consequência honesta:** `handoff.comandos_sem_alvo=0` significa *"os alvos estão lá"*, **nunca**
*"as verificações passam"*. São coisas diferentes, e a segunda esta operação não mede.

## O ajuste

**Um campo**, no topo do `sondas.py` — o nome do seu arquivo de retomada:

```python
NOMES_DE_HANDOFF = ("CONTINUAR.md", "HANDOFF.md", "RETOMAR.md", "CONTEXT.md", "STATE.md")
```

O primeiro que existir ganha. Se o seu tem outro nome, ponha-o na frente. Se nenhum existir, a sonda
**estoura** com o erro escrito — porque *"não achei o seu handoff"* e *"o seu handoff está
impecável"* são leituras opostas.

## Como rodar

```console
$ cp operacoes/handoff-que-mede-o-disco/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ PYTHONPATH=/caminho/para/aferido python -m aferido .
```

Rodado contra um arquivo de retomada real de 667 linhas, num repositório vivo:

```console
REPROVA   CONTINUAR.md:228  handoff.caminhos_mortos: escrito=0 medido=11
          → natureza=relacao — PARE e investigue.
REPROVA   CONTINUAR.md:228  handoff.deriva_de_git: escrito=0 medido=1
          → o documento diz que está commitado; o git discorda.
```

<!-- congelado: exemplo.caminhos=44 exemplo.mortos=11 exemplo.comandos=3 exemplo.sem_alvo=0 exemplo.deriva=1 motivo="medição de 2026-08-21 num arquivo de retomada de OUTRO repositório; é o exemplo impresso acima, não o estado deste projeto, e recomputá-lo aqui mediria a coisa errada" -->

## Os caminhos "mortos" que não foram deletados

**Tudo é resolvido a partir da raiz do repositório, e isso é decisão.** Um caminho citado como
`00-mapa/vazios.md`, que só existe sob `cerebro/00-mapa/vazios.md`, conta como morto aqui — porque
conta como morto para quem copiar a linha e colar no terminal.

Dos 11 achados na medição acima, **nenhum era arquivo deletado**: todos eram caminhos escritos a
partir de uma raiz implícita que o documento não declarava. O conserto é escrever o caminho inteiro,
e é o mesmo conserto que serve ao leitor.

## Do alarme ao trabalho

`handoff.commits_desde=40` diz que o documento ficou para trás. **Reescrevê-lo a partir do disco** é
o trabalho, e é o que o agente desta operação faz:

```console
$ python -m forja operacoes/handoff-que-mede-o-disco/agente.toml
  ✓ build/escriba-de-retomada/.claude/agents/escriba-de-retomada.md
  ✓ build/escriba-de-retomada/hooks/cerca_escriba_de_retomada.py
  …
```

A regra dele é uma só e é dura: **ou a afirmação sai recomputada, ou sai marcada como não
verificada.** Ele não copia do documento anterior — é assim que um número velho sobrevive a dez
reescritas, ficando mais confiável a cada cópia justamente por ter sido copiado.

## O que esta operação NÃO faz

1. **Não executa nada.** Ver a seção acima. `comandos_sem_alvo=0` diz que os alvos existem, nunca
   que as verificações passam.

2. **Não lê a conversa.** Ela lê o disco. O que foi decidido e não virou arquivo é invisível — e
   essa é a maior lacuna daqui, porque é a mesma lacuna que o arquivo de retomada tem.

3. **`commits_desde` e `sessoes_desde` só valem na sua árvore de trabalho.** O `git` não preserva
   `mtime`: num clone limpo todo arquivo nasce com o mesmo instante e as duas estouram para o total.
   **Um número grande delas logo depois de um clone não é achado**, e o agente diz isso em vez de
   escrevê-lo.

4. **Não julga o que está em voo.** Uma pendência de três semanas e uma de ontem saem lado a lado.
   Priorizar continua sendo de quem lê.

5. **Não sabe a intenção de um commit.** Uma passada de formatação conta igual a uma mudança de
   arquitetura. O número é um **piso**: ele diz no mínimo quanta coisa aconteceu, nunca o quanto
   importou.
