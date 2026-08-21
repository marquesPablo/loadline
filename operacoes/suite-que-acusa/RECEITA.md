# Operação 9 · `suite-que-acusa`

> A sua suíte está verde. **Se alguém apagasse o mecanismo que ela protege, ela ficaria vermelha?**
> Para uma boa parte dos testes que existem por aí, a resposta é não. Eles percorrem o caminho
> feliz, confirmam que ele funciona, e passariam idênticos com o mecanismo removido.
> **O custo disso não é zero.** É dar a alguém a sensação de estar coberto — e ninguém vai procurar
> o que já parece protegido.

## O teste que passa igual sem o mecanismo

```python
def test_validacao():
    assert validar("entrada-valida@exemplo.com") is True
```

Troque o corpo inteiro de `validar` por `return True`. **O teste continua verde.**

Ele não prova que a validação valida. Prova que ela não estoura. E a diferença aparece no dia em que
alguém simplifica a função durante um refactor, o teste passa, e a validação some da produção sem
que nenhuma luz acenda.

O conserto é o **controle negativo** — o teste reintroduz o defeito que ele existe para pegar:

```python
def test_validacao():
    assert validar("entrada-valida@exemplo.com") is True

    # O controle negativo: sem ele, o teste acima passa com `return True`.
    assert validar("nao-e-email") is False
```

Duas linhas. E agora o teste morre junto com o mecanismo, que é a única coisa que um teste tem de
fazer.

## A terceira lista

Toda suíte publica duas listas: **o que passou** e **o que falhou**. Quase nenhuma publica a
terceira — **o que ela nunca olhou.**

Sem a terceira, um verde diz apenas *"o que foi olhado passou"*, que é bem menos do que ele parece
dizer. Com ela, o verde passa a ter tamanho: *"olhamos estas 40 coisas, estas 12 estão fora do nosso
alcance, e sabemos quais são."*

Por isso `suite.lacunas_declaradas` **estoura** quando o arquivo não existe, em vez de devolver
zero. Zero lacunas declaradas afirma que a suíte não tem ponto cego — a afirmação mais forte
possível, e a menos provável.

## O que esta operação instala

Seis sondas sobre a sua pasta de testes:
<!-- aferido: operacao.suite.sondas=6 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/suite-que-acusa/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `suite.arquivos` · `suite.checks` | o tamanho da suíte, contado pela árvore sintática | contagem |
| **`suite.sem_assercao`** | **funções de teste que não podem falhar** | **relação** |
| **`suite.sem_controle_negativo`** | **testes que passariam sem o mecanismo (heurística)** | **relação** |
| **`suite.pulados`** | **testes marcados `skip`/`xfail`** | **relação** |
| `suite.lacunas_declaradas` | itens da terceira lista | contagem |

**`suite.checks` é contado pela árvore sintática, não por expressão regular.** Um `def` dentro de
uma string, num comentário ou aninhado noutra função seria contado por regex — e o denominador da
suíte inteira sairia errado, que é a pior classe de erro numa ferramenta que existe para cobrar
denominador.

## ⚠️ Uma das seis é veredito, a outra é lista de leitura

Esta distinção é a coisa mais importante desta receita.

**`suite.sem_assercao` é veredito.** Uma função de teste sem `assert`, sem `assert*` e sem `raise`
**não pode falhar**. Não é opinião, é uma propriedade do código. Ela roda, devolve verde, entra na
contagem de cobertura e não verifica nada. O número certo dela é zero.

**`suite.sem_controle_negativo` é HEURÍSTICA, e ela erra nos dois sentidos.** Ela procura
construções que indicam expectativa de falha (`raises`, `xfail`, `deve_falhar`, a palavra
*reintroduz*…). Um teste que reintroduz o defeito de um jeito que ela não reconhece **é acusado à
toa**. Um `pytest.raises` decorativo **passa por ela**.

**Use-a para produzir a lista de quais testes abrir, nunca para reprovar sozinha no CI.** E se ela
acusar um teste que está certo, o conserto é acrescentar a construção ao vocabulário
`_SU_CONTROLE_NEGATIVO` — **não reescrever o teste para agradar a régua.** Uma régua que faz o
código mudar de forma para caber nela parou de medir o código e passou a medir a si mesma.

## O ajuste

**Dois campos**, no topo do `sondas.py`:

```python
PASTA_DE_TESTES = "tests"
ARQUIVO_DE_LACUNAS = "LACUNAS.md"
```

E, se o seu dialeto de teste não usa `test_` no nome, `_SU_NOME_DE_TESTE`.

## Como rodar

```console
$ cp operacoes/suite-que-acusa/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ PYTHONPATH=/caminho/para/aferido python -m aferido .
```

```console
REPROVA   README.md:31  suite.sem_assercao: escrito=0 medido=4
          → natureza=relacao — PARE e investigue.
SEM PROVA README.md:32  suite.lacunas_declaradas
          → `LACUNAS.md` não existe. É a terceira lista: o que a sua suíte NÃO mede.
```

**Quatro funções de teste que não podem falhar**, e nenhuma terceira lista. Os dois são achados, e o
segundo é o que faz o verde dos outros valer alguma coisa.

## O que esta operação NÃO faz

1. **Não roda a suíte.** Ela lê o código-fonte dos testes. Um teste que passa por acidente e um que
   passa por mérito são idênticos para ela.

2. **Não mede cobertura de linha.** É outra pergunta, já tem ferramenta, e **cobertura alta com
   controle negativo zero é exatamente o estado que esta operação existe para achar** — a suíte
   percorre tudo e não verifica nada.

3. **Não sabe o que ninguém testou.** O que não virou teste é invisível para ela — a mesma lacuna
   que a sua suíte tem, e é para isso que serve a terceira lista, escrita à mão.

4. **Não julga se o mecanismo testado deveria existir.** Ela pergunta se o teste morre junto com
   ele. Se a regra imposta é a certa continua sendo julgamento de quem escreveu.
