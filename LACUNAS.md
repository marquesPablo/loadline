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

## 7 · O denominador dos vizinhos é de uma data, não de sempre

A comparação com `drift`, `Provena` e `freshprobe` no `README.md` foi feita em **2026-08-20**, lendo
página pública. Nenhum dos três foi clonado, instalado ou executado. Eles podem ter mudado desde
então, e nada aqui reconfere isso sozinho — é a lacuna nº 1 aplicada a este próprio argumento.

## 8 · O nome da métrica que o `--selar` escreve é um CHUTE

Ele sai da palavra logo depois do número na frase — *"12 endpoints"* vira `endpoints=12`. É a mesma
leitura que um humano faz, e erra pelos mesmos motivos: ordem inversa (*"endpoints: 12"*), a palavra
seguinte ser preposição, ou o número não ter substantivo nenhum ao lado. Nesses casos sai
`SUA_METRICA`, e nomes repetidos no mesmo arquivo ganham sufixo.

**Isto é sugestão para renomear, nunca afirmação de que a ferramenta entendeu o que o número
significa** — e a diferença entre as duas está escrita na saída de toda rodada que escreve.

## 9 · A vistoria acusa a AUSÊNCIA da declaração, nunca a qualidade dela

Ela responde *"existe aqui alguma coisa legível por máquina dizendo o que este agente nunca faz?"*.
Ela não responde se a anti-descrição estava certa, se a fronteira declarada era a fronteira boa, ou
se o caso do golden set pergunta o que importa. **Um agente excelente com a fronteira escrita em
prosa aparece na lista, e deve aparecer** — mas a recíproca não vale: declarar não é acertar.

## 10 · Frontmatter multi-linha não é lido

O leitor pega `chave: valor` de uma linha, que é o que os harnesses de hoje escrevem. Uma
`description` quebrada em várias linhas, ou um bloco YAML aninhado, é lido pela metade — e a
metade que faltou vira ausência, que é justamente o erro que este arquivo existe para nomear.

**O custo:** um agente bem declarado em YAML multi-linha pode ser acusado à toa.

## 11 · O limiar do `V6` é ESCOLHIDO, e não medido

Trinta por cento de palavras em comum. Ninguém mediu que 30% é onde dois agentes passam a disputar
o mesmo despacho — o número foi escolhido olhando rosters reais, e está no código com o motivo ao
lado em vez de enterrado numa condição. Ele erra nos dois sentidos, e a saída dele é **lista de
leitura, nunca veredito**: `V6` sozinho não deve reprovar o CI de ninguém.

## 12 · Nada aqui roda o agente

A vistoria lê arquivo parado. Ela não despacha, não observa o orquestrador escolhendo, e não sabe
se o seu agente responde bem. Ela sabe se existe, no repositório, **alguma coisa capaz de dizer que
ele respondeu mal** — que é uma pergunta menor, e é a única que dá para responder offline e sem
modelo.

## 13 · O `V6` compara PALAVRAS, e não sentido

Ele acha `revisor` × `auditor` quando as duas descrições dizem *"procurando problema de qualidade,
segurança e arquitetura"* — palavras iguais, 67% em comum. Ele **não acha**
`pesquisador` × `investigador` quando uma diz *"pesquisa na web e resume o que achou sobre um
tema"* e a outra *"investiga na web e resume o que encontrou sobre um assunto"*. São a mesma vaga,
escritas com sinônimos: 17% de palavras em comum, abaixo do limiar, e passam verdes.

Achar sinônimo exigiria um modelo, e um verificador que depende de um modelo não é um verificador —
é uma segunda opinião, e ela não roda offline nem no CI de quem mais precisa dela.

**O custo, dito por extenso:** o `V6` acha colisão de VOCABULÁRIO. Ele é um piso, nunca um teto —
silêncio dele não é prova de que o seu roster não se confunde. A pergunta que ele não faz, e que
continua sendo sua: *se eu escondesse os nomes, eu saberia qual dos dois despachar?*

## Fechadas

Uma lacuna sai desta lista quando o mecanismo que a fechava passa a existir e a ter controle
negativo. O registro fica, porque a lista encolher em silêncio seria a mesma família de defeito que
este arquivo existe para impedir.

- **`Não há marca para o número que foi ESCOLHIDO, e não medido`** — fechada em 2026-08-20 pela
  marca `arbitrado:`, que exige o dono (`por=`) e vence como qualquer outro selo. Era descrita aqui
  como *"a lacuna mais funda da lista, e a próxima coisa a nascer"*. Controles negativos: três
  checks do autoteste, cada um reintroduzindo o defeito.
