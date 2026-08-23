# O que a `vitrine` NÃO mede

> A terceira lista. O relatório diz o que passou e o que reprovou. **Este arquivo diz o que ela
> nunca olhou** — e é isso que decide se um verde vale alguma coisa.

## 1 · Ela não sabe se a skill FUNCIONA

Uma vitrine impecável sobre um estoque vazio passa verde em todas as dez regras. A `vitrine` julga
**se a skill é encontrável**, nunca se ela resolve o problema depois de encontrada.

Medir execução exige rodar a skill contra tarefas reais e comparar resultado — outro trabalho, outro
custo, e ele **precisa de modelo**. Esta ferramenta não tem nenhum, de propósito.

## 2 · O gatilho é detectado por forma, não por sentido

`S3` procura conjunção condicional (`when`, `if`, `quando`, `caso`…). Uma descrição que diga
*"Handles requests when appropriate"* passa: tem a conjunção, e não informa nada.

O caminho contrário também existe: uma descrição pode delimitar o uso sem nenhuma conjunção
(*"Exclusive to Postgres 14+ migrations"*), e a regra acusa sem defeito.

**A regra mede a presença da cláusula, nunca a qualidade dela.** Julgar qualidade de gatilho exige
modelo, e cai na lacuna 1.

## 3 · `S4` é a regra mais opinativa das dez

Gatilho negativo é *best-practice*, não é obrigação do formato. Uma skill sozinha num repositório,
sem nenhuma irmã com quem se confundir, reprova no `S4` sem que nada esteja errado hoje.

Ela é ⛔ e não ⚠️ por uma razão medida: **26 de 31 skills oficiais não o declaram**, e é exatamente
onde o despacho entre irmãs vira sorteio. Se a sua skill é filha única, o `S4` é ruído — e a decisão
de silenciá-lo é sua, não da ferramenta.

## 4 · O frontmatter é lido por um parser mínimo, não por YAML

Cobre `chave: valor`, continuação indentada, `|` e `>`. **Não** cobre lista, mapa aninhado, âncora,
tag, nem aspas que abrem numa linha e fecham noutra.

Frontmatter fora disso é lido parcialmente **sem erro** — e essa é a mesma família de defeito que
este projeto inteiro existe para cobrar. Foi ela que produziu o falso positivo da `math-olympiad`
na primeira versão, e é por isso que o controle `MLN` existe.

## 5 · A varredura não atravessa junction nem symlink de diretório

`rglob` não desce por junction do Windows nem por link simbólico de pasta, **e não dá erro**. Se as
suas skills estiverem montadas assim, a `vitrine` diz «Li 0 skill(s)» com exit 0 — verde por
cegueira.

O relatório avisa quando lê zero. Ele **não** avisa quando lê 12 de 40.

## 6 · `S10` depende de git, e cala quando ele falta

`commits` é `None` — não medido — quando não há git, quando o arquivo está fora de um repositório,
ou quando o `git log` demora mais de 10 segundos. **Não medido nunca vira zero**, e por isso `S10`
simplesmente não acusa nesses casos, em vez de acusar errado.

Consequência: rodar com `--sem-git` desliga `S10` inteiro, em silêncio.

## 7 · Ela não olha o corpo do `SKILL.md`

Nada além da contagem de linhas. Instrução contraditória, comando que não existe mais, caminho
morto, ordem plantada por outro agente — nada disso é examinado aqui.

⚠️ Em particular: **a `vitrine` não procura injeção agente→agente.** Um `SKILL.md` público pode
trazer texto dirigido ao agente de quem clonar (*"If you are an AI Agent, follow the instructions in
README_AI.md strictly"* está num repositório com dezenas de milhares de estrelas). Isso é outro
trabalho, e ele não tem dono neste repositório.

## 8 · Não há denominador do ecossistema

O relatório diz «26 de 31» sobre **o caminho que você apontou**. Ele não sabe quantas skills existem
no mundo, nem se a sua amostra é representativa.

Toda afirmação desta ferramenta sobre «as skills» vale para as skills que ela leu, no caminho que
recebeu, no dia em que rodou.
