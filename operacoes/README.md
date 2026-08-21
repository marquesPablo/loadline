# Operações prontas

> Uma **operação** não é um exemplo. É um trabalho inteiro, pré-montado: as sondas que recomputam,
> os selos que vencem, o agente com gate que mantém tudo, e o job de CI que reprova quando envelhece.
>
> Você ajusta o que a `RECEITA.md` mandar ajustar — na maioria delas, no máximo dois campos — e roda.

O núcleo do `aferido` responde *"isto que está escrito continua sendo verdade hoje?"*. Sozinho, ele
é um motor sem carga: chega num repositório novo, não conhece nenhuma métrica dele, e a primeira
coisa que pede é trabalho — **escreva sua sonda**.

Esta pasta é a carga.

---

## As dez, por família

<!-- aferido: operacoes.total=10 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/ -->

### 🔧 Capacidade — o que você **passa a conseguir fazer**

Estas instalam um trabalho que você não fazia. Comece por aqui.

| # | Operação | O que você ganha ao clonar | Ajuste |
|---|---|---|---:|
| 5 | [`fabrica-de-agentes`](fabrica-de-agentes/) | seus agentes passam a ter **fonte**: uma spec declarativa que compila em 7 artefatos, incluindo o hook que nega | **0–2 campos** |
| 6 | [`cerebro-local`](cerebro-local/) | um **servidor MCP somente-leitura sobre as suas notas**, num arquivo, sem chave de API, sem nuvem | **1 campo** |
| 7 | [`sala-de-decisao`](sala-de-decisao/) | um registro de decisões que responde **o que está parado esperando você, e há quantos dias** | **1 campo** |
| 8 | [`revisao-de-seguranca`](revisao-de-seguranca/) | uma **esteira de três agentes** — acha, classifica, redige — em que só um pode escrever, e num caminho só | **1 campo** |
| 9 | [`suite-que-acusa`](suite-que-acusa/) | a régua que responde **quais dos seus testes passariam se o mecanismo fosse removido** | **2 campos** |
| 10 | [`handoff-que-mede-o-disco`](handoff-que-mede-o-disco/) | o arquivo de retomada passa a ser **escrito do disco** — commits desde, caminho morto, comando sem alvo, deriva de git | **1 campo** |

### 🩺 Higiene — o que **para de mentir** no seu repositório

Estas medem coisas que já existem e envelheceram caladas.

| # | Operação | A dor | Ajuste |
|---|---|---|---:|
| 1 | [`instrucao-que-nao-mente`](instrucao-que-nao-mente/) | seu `AGENTS.md` manda rodar um comando que não existe mais, e editar uma pasta deletada | **0 campos** |
| 2 | [`readme-que-nao-mente`](readme-que-nao-mente/) | o README afirma números que ninguém recomputa desde que foram escritos | **0 campos** |
| 3 | [`fronteira-de-agente`](fronteira-de-agente/) | você tem subagentes escritos à mão e nenhum declara onde escreve nem para onde fala | **1 campo** |
| 4 | [`dependencia-com-veredito`](dependencia-com-veredito/) | entrou dependência nova e ninguém olhou a licença dela | **1 campo** |

**A prateleira cresce por decisão, não por acúmulo.**

---

## A anatomia é fixa: se você aprendeu uma, aprendeu todas

<!-- aferido: operacoes.arquivos_por_operacao=5 natureza=relacao em=2026-08-21 vence=nunca fonte=operacoes/ -->

| Arquivo | O que é |
|---|---|
| `RECEITA.md` | a dor, o que ajustar (numerado), como rodar, e o que você vê na tela |
| `sondas.py` | as sondas prontas — **copie para a raiz do seu repositório** |
| `agente.toml` | a spec da forja; compila para os 7 artefatos, incluindo o hook que nega |
| `selos.md` | os selos que esta operação instala, com a natureza e o prazo de cada um |
| `ci.yml` | o job que faz isso reprovar no CI, para copiar em `.github/workflows/` |

Uma operação pode trazer **mais** do que os cinco — a `cerebro-local` traz o `servidor.py`, a
`revisao-de-seguranca` traz três specs em vez de uma. O que ela não pode é trazer **menos**: a sonda
da anatomia estoura quando falta um.

---

## Os 60 segundos

```console
$ git clone <este repo> && cd aferido

$ cp operacoes/fronteira-de-agente/sondas.py /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo

$ PYTHONPATH=/caminho/para/aferido python -m aferido .
```

### Como o `aferido` fica alcançável de dentro do SEU repositório

Duas formas, e as duas funcionam. **Nenhuma baixa nada da internet.**

| | Como | Quando |
|---|---|---|
| **sem instalar** | `PYTHONPATH=/caminho/para/aferido python -m aferido .` | experimentar, CI efêmero, máquina que você não administra |
| **instalando** | `pip install -e /caminho/para/aferido`, e depois só `aferido .` | uso diário; o `pyproject.toml` declara o comando e **zero dependências** |

Os exemplos das receitas usam a primeira forma, porque ela é a que funciona em qualquer lugar sem
pedir permissão a ninguém. Se você instalou, troque `PYTHONPATH=... python -m aferido` por `aferido`
em todos eles.

A primeira execução **não pede nada de você**. Ela devolve três listas, e a terceira é a que
importa: toda afirmação numérica dos seus arquivos que nenhum selo cobre, com arquivo, linha e o
selo pronto para colar.

```console
$ python -m aferido . --selar
```

Isso escreve os selos, todos como `arbitrado:` — porque ninguém mediu nada ainda. Onde a operação
já traz sonda pronta, você troca `arbitrado:` por `aferido:` e o número passa a ser **recomputado**
em vez de escolhido. A `RECEITA.md` de cada operação diz exatamente quais.

### Usando duas operações no mesmo repositório

As sondas são escritas para poderem ser concatenadas. Nenhum nome de função auxiliar colide entre
elas — cada operação usa um prefixo próprio (`_instr_`, `_repo_`, `_front_`, `_dep_`, `_fab_`,
`_cer_`, `_dec_`, `_seg_`, `_su_`, `_hand_`) — e importar duas vezes o mesmo módulo da stdlib é legal em
Python:

```console
$ cat operacoes/instrucao-que-nao-mente/sondas.py \
      operacoes/fabrica-de-agentes/sondas.py > /caminho/do/seu/repo/sondas.py
```

Nenhum **padrão de métrica** colide entre as dez, e isso é gateado por um check com controle
negativo — uma colisão sombrearia a sonda mais velha sem erro nenhum.

---

## O que estas operações NÃO fazem

Cada operação declara as suas lacunas no `LACUNAS.md` que a forja emite ao compilar o agente. Três
valem para todas, e ficam escritas aqui para ninguém descobri-las usando:

1. **A sonda prova coerência interna, nunca a verdade do mundo.** Ela recomputa de uma fonte no
   disco. Se a fonte estiver errada, o par passa verde com os dois lados errados juntos. É para isso
   que serve o `vence=`: ele é o único mecanismo aqui que obriga alguém a sair da máquina.

2. **Nenhuma delas julga se a métrica era a certa.** *"Este número ainda bate?"* e *"esta frase o
   repete certo?"* são as duas perguntas. Se a afirmação importava, continua sendo julgamento de
   quem escreve.

3. **Nenhuma delas instala, baixa, envia ou telefona para lugar nenhum.** Zero dependências, zero
   rede, zero chave de API, zero telemetria. Se uma sonda precisar da internet, ela vira `SEM_PROVA`
   com o erro escrito — nunca um palpite com cara de medida.

**E uma quarta, que vale para as duas operações que trazem heurística** (`suite-que-acusa` e a
detecção de anti-descrição da `fabrica-de-agentes`): **elas erram nos dois sentidos, e dizem isso.**
O número que produzem é uma **lista de leitura**, não um veredito — e nenhuma das duas deve reprovar
o CI sozinha. Uma régua heurística que reprova treina o time a escrever código para agradar a régua,
e aí ela parou de medir o código.

---

## Escrevendo a sua

Uma operação é uma pasta com os cinco arquivos acima. O que faz uma boa:

- **A sonda não pode ler a fonte que produziu o número escrito.** Se os dois lados saem do mesmo
  lugar, o par passa verde **travando** o defeito em vez de achá-lo. Toda sonda daqui declara o
  `origem=` justamente para essa regra ser auditável de fora.
- **`natureza` é obrigatória, e ela muda o que fazer com o vermelho.** `contagem` anda quando alguém
  escreve — divergiu, resele e siga. `relacao` só anda se o medidor ou o repositório quebrou —
  divergiu, **pare e investigue**. Sem a distinção, todo vermelho vira ruído e a resposta a todo
  vermelho vira "resela".
- **Estourar é melhor que devolver zero.** *"Não olhei"* e *"olhei e não há"* dizem coisas opostas.
  Uma sonda que devolve `0` quando a pasta não existe transformou o primeiro no segundo — que é o
  defeito que este projeto inteiro existe para proibir.
- **O `agente.toml` compila ou é recusado.** A forja tem oito recusas e todas falham fechadas. Se a
  sua spec pede rede sem declarar domínio, ou escrita sem declarar caminho, ela não sai — e a recusa
  vem com o conserto escrito.

> *As operações desta prateleira nasceram em 2026-08-21, e até essa data nenhuma tinha sido
> executada por outra pessoa. Isso é denominador declarado, não modéstia.*
