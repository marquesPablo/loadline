# Operação · `nome-da-sua-operacao`

> TODO — uma frase que resume a dor, no mesmo tom de "O que está parado agora esperando uma decisão
> sua?" (`sala-de-decisao`) ou "Você tem mais de um agente e ninguém olha o conjunto" (`forja`). Se
> a frase não incomoda ninguém, a operação provavelmente não devia existir.

## A dor

TODO — dois ou três parágrafos. Descreva o problema real, com um exemplo concreto (nome de arquivo,
formato, situação). Não descreva a solução aqui — só a dor.

## O que esta operação instala

TODO — a tabela de sondas, no mesmo formato das outras:

<!-- measured: operacao.NOME.sondas=N natureza=contagem em=AAAA-MM-DD vence=nunca fonte=comunidade/nome-da-sua-operacao/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `NOME.exemplo` | TODO | contagem ou relacao |

## O ajuste

TODO — o campo (ou campos) que quem clona precisa mudar. A régua da casa: no máximo dois campos.

```python
CAMPO_DE_AJUSTE = "TODO"
```

## Como rodar

```console
$ cp comunidade/nome-da-sua-operacao/sondas.py /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ PYTHONPATH=/caminho/para/loadline python -m loadline .
```

TODO — cole a saída real de uma execução, não uma saída inventada. Se a saída for inventada, o
revisor vai pedir a execução de verdade antes de continuar.

## O que esta operação NÃO faz

TODO — pelo menos dois itens. Toda operação desta prateleira declara o limite dela por extenso;
uma operação sem esta seção não passa de revisão. Releia `LACUNAS.md` do repositório antes de
escrever esta seção — três dos limites de lá (a sonda prova coerência interna, nunca a verdade do
mundo; nada aqui julga se a métrica era a certa; nada aqui instala/baixa/envia/telefona) valem para
a sua operação também, e não precisam ser reescritos — só citados.
