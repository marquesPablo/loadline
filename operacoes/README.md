# Operações prontas

> Uma **operação** não é um exemplo. É um trabalho inteiro, pré-montado: as sondas que recomputam,
> os selos que vencem, o agente com gate que mantém tudo, e o job de CI que reprova quando envelhece.
>
> Você ajusta o que a `RECEITA.md` mandar ajustar — nunca mais que três campos — e roda.

O núcleo do `aferido` responde *"isto que está escrito continua sendo verdade hoje?"*. Sozinho, ele
é um motor sem carga: chega num repositório novo, não conhece nenhuma métrica dele, e a primeira
coisa que pede é trabalho — **escreva sua sonda**.

Esta pasta é a carga. Cada operação traz sondas que funcionam em qualquer repositório, sem
configuração, e um par escrito×medido que já vale alguma coisa na primeira execução.

---

## As quatro, e a dor que cada uma resolve

| # | Operação | A dor | O que passa a vencer | Ajuste |
|---|---|---|---|---:|
| 1 | [`instrucao-que-nao-mente`](instrucao-que-nao-mente/) | seu `AGENTS.md` manda rodar um comando que não existe mais, e manda editar uma pasta que foi deletada | `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `GEMINI.md` | **0 campos** |
| 2 | [`readme-que-nao-mente`](readme-que-nao-mente/) | o README afirma números que ninguém recomputa desde que foram escritos | `README.md` e qualquer `.md` do repositório | **0 campos** |
| 3 | [`fronteira-de-agente`](fronteira-de-agente/) | você tem subagentes escritos à mão, e nenhum declara onde pode escrever nem para onde pode falar | `.claude/agents/*.md` e `.claude/settings.json` | **1 campo** |
| 4 | [`dependencia-com-veredito`](dependencia-com-veredito/) | entrou dependência nova e ninguém olhou a licença dela; a tabela de licenças ficou para trás | o manifesto × a sua tabela de vereditos | **1 campo** |

São 4 operações prontas nesta prateleira, e toda expansão dela entra pela mesma anatomia: uma
pasta, um par escrito × medido, e a primeira execução sem pedir configuração.
<!-- aferido: operacoes.total=4 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/ -->

Toda operação tem os mesmos cinco arquivos, sempre com o mesmo nome. Se você aprendeu uma,
aprendeu todas.
<!-- aferido: operacoes.arquivos_por_operacao=5 natureza=relacao em=2026-08-21 vence=nunca fonte=operacoes/ -->

| Arquivo | O que é |
|---|---|
| `RECEITA.md` | a dor, o que ajustar (numerado), como rodar, e o que você vê na tela |
| `sondas.py` | as sondas prontas — **copie para a raiz do seu repositório** |
| `agente.toml` | a spec da forja; compila para os 7 artefatos, incluindo o hook que nega |
| `selos.md` | os selos que esta operação instala, com a natureza e o prazo de cada um |
| `ci.yml` | o job que faz isso reprovar no CI, para copiar em `.github/workflows/` |

---

## Os 60 segundos

```console
$ git clone <este repo> && cd aferido

$ cp operacoes/instrucao-que-nao-mente/sondas.py /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo

$ python -m aferido .
```

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
elas, e importar duas vezes o mesmo módulo da stdlib é legal em Python:

```console
$ cat operacoes/instrucao-que-nao-mente/sondas.py \
      operacoes/readme-que-nao-mente/sondas.py > /caminho/do/seu/repo/sondas.py
```

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
- **O `agente.toml` compila ou é recusado.** A forja tem oito recusas e todas falham fechadas. Se a
  sua spec pede rede sem declarar domínio, ou escrita sem declarar caminho, ela não sai — e a recusa
  vem com o conserto escrito.

> *As operações desta prateleira nasceram em 2026-08-21, e até essa data nenhuma tinha sido
> executada por outra pessoa. Isso é denominador declarado, não modéstia.*
