# O que este projeto NÃO mede

> **A terceira lista.** Toda ferramenta publica o que passou e o que falhou. Quase nenhuma publica
> **o que ela nunca olhou** — e é essa terceira lista que decide se um verde significa alguma coisa.
>
> Este arquivo é o denominador do projeto inteiro, no mesmo espírito da `LACUNAS.md` que a `forja`
> emite para cada agente que compila. Ele existe para que ninguém precise descobrir um limite
> **usando** a ferramenta e sendo surpreendido por ele.

## 1 · A sonda prova coerência interna, nunca a verdade do mundo

A sonda recomputa o número de uma fonte no disco. Se essa fonte estiver errada, o par passa verde
com os dois lados errados juntos. **Um JSON coerente não é um fato verdadeiro.**

É para isso que serve o `vence=`: ele é o único mecanismo aqui que obriga alguém a sair da máquina.
Nenhum verde deste projeto significa *"isto é verdade lá fora"*.

## 2 · O confronto prosa × selo morde numa direção só

O `PROSA_MUDA` acusa **número na frase que nenhum selo do bloco cobre**. A direção contrária — *a
frase afirma uma GRANDEZA que o selo não nomeia*, sem escrever número — exige um registro fechado de
grandezas e o julgamento do que conta como afirmação. **Não está implementada.**

Consequência prática: *"a suíte está verde"* e *"o repositório está sincronizado"* são asserções, e
passam sem cobrança nenhuma aqui.

## 3 · `um` e `uma` não são lidos como numeral

Em português são artigo indefinido antes de serem número, e *"Um registro do ecossistema"* não
afirma quantidade. Separar os dois usos exige análise sintática que este projeto não faz.

**O custo:** uma frase que afirme de verdade *"um projeto não tem canônico"* passa sem cobrança. A
saída para quem precisa é escrever o dígito.

## 4 · Percentual não é confrontado

Percentual é derivado, e cobrá-lo exigiria conhecer o denominador — que é justamente o que o texto
costuma omitir. Ele é retirado antes do confronto, junto com data, versão e identificador.

## 5 · O confronto só olha prosa, não código

Em `.py`, o que está ao redor de um selo é código, e cobrar eco de número ali acusaria todo literal
vizinho. Selo em comentário de código é julgado pelo valor, nunca pela frase.

## 6 · Nada aqui mede a QUALIDADE do que foi escrito

O projeto responde *"este número ainda bate?"* e *"esta frase o repete certo?"*. Ele não responde se
a métrica era a certa, se a sonda mede o que diz medir, ou se a afirmação importava. Isso é
julgamento, e ele continua sendo de quem escreve.

## 7 · Não há marca para o número que foi ESCOLHIDO, e não medido

Hoje o vocabulário tem duas marcas — `aferido:` (recomputável) e `congelado:` (histórico) — e **as
duas pressupõem que o número um dia foi medido**. Não existe marca para o número que ninguém pode
medir e alguém arbitrou: limiar, teto, prazo, `vence=90d`.

Todo limiar deste arquivo é um número escolhido vestido de número medido, **inclusive os `vence=` do
próprio censo**. É a lacuna mais funda da lista, e é a próxima coisa a nascer.

## 8 · O denominador dos vizinhos é de uma data, não de sempre

A comparação com `drift`, `Provena` e `freshprobe` no `README.md` foi feita em **2026-08-20**, lendo
página pública. Nenhum dos três foi clonado, instalado ou executado. Eles podem ter mudado desde
então, e nada aqui reconfere isso sozinho — é a lacuna nº 1 aplicada a este próprio argumento.
