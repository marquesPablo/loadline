# Operação 1 · `instrucao-que-nao-mente`

> O seu `AGENTS.md` manda rodar `npm run test:unit`. Esse script foi renomeado em março.
> O agente lê a instrução, roda o comando, falha, e tenta adivinhar o que você quis dizer.
> **Ninguém foi avisado, porque nada olha para isso.**

## A dor

Mais de 60 mil repositórios adotaram `AGENTS.md`, lido hoje por Claude Code, Codex CLI, Cursor,
Aider, Copilot, Gemini CLI, Zed, Continue e outros. Quem tem dois arquivos — `CLAUDE.md` **e**
`AGENTS.md` — tem o problema em dobro: um é atualizado, o outro fica, e os dois divergem em silêncio.

Um arquivo de instrução é um documento cheio de **afirmações sobre o repositório**: rode este
comando, edite esta pasta, os testes ficam ali. Toda afirmação envelhece. Nenhuma reprova quando
envelhece.

## O que esta operação instala

Sete sondas que conferem as promessas do arquivo de instrução contra o disco — não contra ele mesmo:
<!-- measured: operacao.instrucao.sondas=7 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/instrucao-que-nao-mente/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `instrucao.arquivos` | quantos arquivos de instrução existem | contagem |
| `instrucao.linhas` | o tamanho somado deles | contagem |
| `instrucao.comandos` | comandos distintos citados dentro de cerca de código | contagem |
| **`instrucao.comandos_quebrados`** | **comandos cujo script/alvo não existe** em `package.json`, `Makefile` ou no disco | **relação** |
| `instrucao.caminhos` | caminhos relativos citados entre crases | contagem |
| **`instrucao.caminhos_quebrados`** | **caminhos citados que não existem** | **relação** |
| `instrucao.divergencia` | títulos presentes num arquivo e ausentes no outro | contagem |

As duas em **relação** são o coração. Elas deveriam ser sempre `0`, e quando saem de zero isso não é
"o número mudou" — é **defeito**. A ferramenta diz isso na tela, com essas palavras.

## O ajuste

**Nenhum.** As sondas descobrem os arquivos de instrução sozinhas, pela lista fechada de nomes que
os harnesses de hoje leem. Se o seu tem outro nome, acrescente-o em `NOMES_DE_INSTRUCAO`, no topo do
`sondas.py` — é a única linha desta operação que alguém precisa tocar, e só nesse caso.

## Como rodar

```console
$ cp operacoes/instrucao-que-nao-mente/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ PYTHONPATH=/caminho/para/loadline python -m loadline .
```

> Instalou com `pip install -e /caminho/para/loadline`? Então é só `loadline .`. As duas
> formas estão em [`operacoes/README.md`](../README.md), e nenhuma baixa nada.

A primeira execução não pede nada. Ela devolve o que ninguém consegue conferir no seu repositório.
Depois, cole no fim do seu `AGENTS.md`:

```markdown
## O que este arquivo promete

Todo comando citado aqui existe, e todo caminho citado aqui existe.
<!-- measured: instrucao.comandos_quebrados=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=package.json -->
<!-- measured: instrucao.caminhos_quebrados=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=disco -->
```

Troque `AAAA-MM-DD` por hoje. Pronto — a operação está no ar.

## O que você vê quando alguma coisa quebra

```console
$ PYTHONPATH=/caminho/para/loadline python -m loadline .
loadline · . · em 2026-08-21
========================================================================
DRIFTED   AGENTS.md:19  instrucao.comandos_quebrados: escrito=0 medido=2  → PARE. Relação divergindo é defeito — investigue antes de resselar
DRIFTED   AGENTS.md:20  instrucao.caminhos_quebrados: escrito=0 medido=2  → PARE. Relação divergindo é defeito — investigue antes de resselar

⚠️  NINGUÉM CONSEGUE CONFERIR ISTO — são suspeitas, não defeitos.
      SEM PROVA  AGENTS.md:3  "Este repo tem 3 servicos e 12 endpoints." → ninguém confere 3
      SEM PROVA  AGENTS.md:3  "Este repo tem 3 servicos e 12 endpoints." → ninguém confere 12
------------------------------------------------------------------------
2 métricas em 3 arquivos · 2 arquivos sem selo nenhum · 2 afirmações que ninguém confere
  DRIFTED    2
  ⚠️  2 de RELAÇÃO — isso é defeito, não resselo

REPROVA
```

> *Saída literal desta operação sobre um repositório sintético, executada em 2026-08-21. É um
> exemplo daquela execução, não o estado do seu repositório.*

## O agente

`agente.toml` compila o `guardiao-de-instrucao`, que faz o que a sonda não faz: **abre cada quebra e
diz qual é**. A sonda conta 2; o agente diz *"o `npm run test:unit` não existe mais em
`package.json`, e o `src/legacy/velho.ts` foi deletado"*.

```console
$ python -m forja operacoes/instrucao-que-nao-mente/agente.toml
```

Sete artefatos saem, entre eles um `LACUNAS.md` que declara o que este agente **não** mede — leia-o
antes de confiar num verde.

## O CI

`ci.yml` faz a operação reprovar o build. Copie para `.github/workflows/`. Ele distingue os três
códigos de saída: `0` verde, `1` alguma coisa conferida não bate, `2` você ainda não anotou nada.

## As três coisas que esta operação não faz

1. **Se ninguém CITA um comando, nada aqui descobre que ele existia e sumiu.** A cobertura é do que
   está escrito, e o denominador é o arquivo de instrução — nunca o repositório inteiro.
2. **Comando fora de cerca de código não conta.** `npm test` no meio de uma frase pode ser exemplo,
   contraexemplo ou o que *não* fazer. Dentro da cerca é instrução; fora, é prosa.
3. **A checagem de quebra é conservadora, e erra para o lado de calar.** Sem `package.json` não há
   como decidir sobre `npm run X`, e ela não decide. Uma sonda que grita lobo é uma sonda que alguém
   apaga na segunda semana.
