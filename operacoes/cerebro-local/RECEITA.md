# Operação 6 · `cerebro-local`

> As suas notas estão no disco. O seu assistente não as alcança.
> Hoje você faz uma de duas coisas: **cola pedaço no chat** — e ele responde sobre o pedaço, sem
> saber o que havia em volta — ou **manda tudo para um serviço**, e o seu material passa a morar
> na infraestrutura de outra pessoa.
> Existe uma terceira: um processo local, somente-leitura, que serve as suas notas como ferramentas.
> **Sem chave de API, sem nuvem, sem embedding, sem banco vetorial.**

## A dor

Um assistente sem acesso ao seu material é um estranho muito articulado. Ele nunca vai dizer *"você
já decidiu isso em março, e escreveu o motivo"* — ele vai dizer o que costuma ser verdade, com uma
confiança que o seu material não sustenta.

E as duas saídas usuais custam caro:

- **Colar no chat** é reintroduzir o contexto a cada sessão, escolhendo à mão o que é relevante
  antes de saber o que a pergunta vai exigir. Você acaba sendo o índice.
- **Subir tudo** resolve o acesso e cria três problemas: o material sai da sua máquina, o índice
  defasa em silêncio, e você passa a pagar por token para reler o que já é seu.

O que falta é pequeno: **um processo que fale o protocolo que o seu cliente já fala, e leia o disco.**

## O que esta operação instala

Um servidor MCP em **um arquivo**, `servidor.py`, com quatro ferramentas e **zero dependências** —
só a stdlib do Python.

| Ferramenta | Responde |
|---|---|
| `mapa` | a raiz, quantas notas são servidas, e como elas se distribuem — **chame primeiro** |
| `listar_notas` | o que existe numa pasta, com tamanho |
| `ler_nota` | o texto integral de uma nota |
| `buscar` | `caminho:linha` de um termo literal, **atravessando junction e symlink** |

```console
$ cp -r operacoes/cerebro-local  /caminho/do/seu/repo/cerebro
$ cd /caminho/do/seu/repo
$ python cerebro/servidor.py --raiz ~/notas --teste
```

`--teste` não fala MCP: ele chama as quatro ferramentas e imprime, para você ver que funciona antes
de registrar em cliente nenhum. **Inclusive a recusa:**

```console
=== a recusa, provada ===
RECUSADO, como tem de ser: `../../../etc/passwd` resolve para fora da raiz declarada.
Este servidor lê debaixo de `/home/voce/notas` e nada mais.
```

Para usar de verdade, registre no seu cliente (o exemplo é o formato do Claude Code, em `.mcp.json`;
outros clientes usam o mesmo trio comando/argumentos/ambiente):

```json
{
  "mcpServers": {
    "notas": {
      "command": "python",
      "args": ["cerebro/servidor.py", "--raiz", "/caminho/das/suas/notas"]
    }
  }
}
```

Não há segundo passo. Não há conta para criar.

## A armadilha que custa caro, e ela não dá erro

**`rg`, `grep -r` e `find` não atravessam junction do Windows nem symlink de diretório.** Não
avisam, não erram, não retornam código diferente de zero: **devolvem menos arquivos, com a mesma
cara de resposta completa.**

Num vault de conhecimento isso é a regra, não a exceção — pastas ligadas são como a maioria das
pessoas junta material de vários lugares num lugar só. A busca responde sobre metade do corpus e
ninguém tem como saber.

`os.walk(followlinks=True)` atravessa. É por isso que a `buscar` deste servidor é `os.walk` e não um
`subprocess` chamando `grep` — e é por isso que a anti-descrição do agente proíbe, por escrito, usar
busca de linha de comando sobre um vault ligado.

**Se você reescrever a busca chamando `grep`, o número cai e nada acusa.** É a família de defeito
mais cara que existe: a que devolve uma resposta plausível.

## As oito sondas

<!-- measured: operacao.cerebro.sondas=8 nature=count on=2026-08-21 expires=never source=operacoes/cerebro-local/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `cerebro.notas` · `cerebro.pastas` | o tamanho real do corpus servido | contagem |
| **`cerebro.ferramentas`** | **entradas de `FERRAMENTAS` no código — não o que o README promete** | **relação** |
| **`cerebro.dependencias`** | **imports de terceiros no servidor: tem de ser zero, e a sonda prova** | **relação** |
| **`cerebro.orfas`** | **notas que nenhuma outra cita — só o autor as alcança** | **relação** |
| **`cerebro.links_quebrados`** | **alvos distintos de `[[link]]` que não existem** | **relação** |
| `cerebro.sem_titulo` | notas sem título markdown na primeira linha | contagem |
| `cerebro.maior_nota` | bytes do maior arquivo | contagem |

**`cerebro.dependencias` é a mais importante das oito, e a menos óbvia.** *"Zero dependências"* é a
frase que faz alguém rodar isto numa máquina que não administra. Ela morre no dia em que alguém
acrescenta um `import` por conveniência — e nenhuma revisão de código repara, porque o diff mostra
uma linha. A sonda lê o `servidor.py` e conta.

## O ajuste

**Um campo**, no topo do `sondas.py`:

```python
PASTA_DE_NOTAS = "."   # "." = o repositório inteiro
```

E, se as suas notas usam outra extensão, `_CER_EXTENSOES` — que precisa bater com `EXTENSOES` do
`servidor.py`. Se divergirem, a sonda conta um corpus e o servidor serve outro, e o selo verde
estaria medindo a coisa errada.

## O que esta operação NÃO faz

1. **Não escreve, e isso é estrutural.** Não há ferramenta de escrita no servidor. Não é uma
   promessa no prompt — é a ausência do código. Um agente não pode usar mal uma ferramenta que não
   existe.

2. **Não resolve contradição entre as suas notas.** O agente exibe as duas citações e para.
   Escolher exigiria saber qual é mais recente, qual foi mais pensada, ou qual você ainda sustenta —
   e nenhuma das três está no texto. Um agente que escolhe apaga o achado: que existe uma decisão
   pendente.

3. **Não sabe se o que você anotou é verdade.** Ele lê. Uma nota errada é citada com a mesma
   confiança de uma certa, e nenhuma sonda offline alcança o mundo lá fora. É para isso que serve o
   `vence=` dos selos.

4. **Não indexa, de propósito.** Sem banco vetorial, sem BM25, sem embedding. Um índice defasa, e a
   defasagem é silenciosa: ele responde com o corpus de ontem e com a confiança de hoje. A alguns
   megabytes, `os.walk` + busca literal é instantâneo — e sempre certo sobre o disco de agora.

5. **Não protege contra o que está DENTRO das suas notas.** Se uma nota sua contém uma ordem
   dirigida a um agente — porque você colou material de fora —, este servidor a entrega como
   entrega qualquer outro texto. A cerca dele é de **caminho**, não de conteúdo.
