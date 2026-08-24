# O que o `placar` NÃO mede

> A mesma terceira lista que o `LACUNAS.md` da raiz, da `vitrine` e do `blind` publicam. Sete portas
> que respondem "existe evidência?" não são sete portas que respondem "isto está bem feito?" — e é
> esta lista que marca a fronteira entre as duas.

## 1 · Toda porta é AUSÊNCIA DE DECLARAÇÃO, nunca julgamento de qualidade

O mesmo contrato da `vistoria` (`forja/vistoria.py`): uma porta acusa quando não encontra evidência
legível por máquina — nunca decide se a evidência encontrada é a certa. Um `PreToolUse` que nega por
um motivo errado passa a `APPROVAL`. Um registro de decisão cheio de datas e vazio de substância passa
a `TRACEABILITY`. **`placar` prova que a peça existe, não que ela funciona.**

## 2 · `OBJECTIVE` e `FAILURE` são busca de palavra, e a lista é ESCOLHIDA

`MARCAS_OBJECTIVE` e `MARCAS_FAILURE` (`placar/portas.py`) são vocabulário coletado, não normativo.
Um agente que declara orçamento com uma palavra fora da lista passa como REPROVA. Achar sinônimo
exigiria um modelo — e um verificador que depende de modelo não é verificador, é segunda opinião.

## 3 · `IDENTITY` é sete padrões REAIS, não um scanner de entropia

Sete formatos de credencial conhecidos (AWS, GitHub, Slack, Anthropic, OpenAI, Google, chave privada
PEM). **Não cobre:** segredo genérico sem prefixo reconhecível, credencial de serviço interno, hash
que parece chave mas não é, nem o inverso — texto de alta entropia que É segredo mas não casa com
nenhum dos sete formatos. Isto é um piso, não um `gitleaks`/`trufflehog` completo, e a lista de
exclusão de placeholder (`_PLACEHOLDER`) pode deixar passar um segredo real cujo nome de variável
contém uma das palavras da lista (`API_KEY_EXAMPLE_PROD = "sk-ant-..."`, por exemplo).

## 4 · `IDENTITY` não olha o HISTÓRICO do git

Um segredo removido do arquivo de hoje e ainda vivo em `git log -p` não é achado. `placar` lê o
disco atual, nunca a árvore de commits — a mesma fronteira que o `blind` já declara para si mesmo.

## 5 · `AUTHORITY` sem roster é mais fraco que `AUTHORITY` com roster

Com `.claude/agents/`, a porta reusa `V3`/`V7` da `vistoria` — por agente, com nome. Sem roster
(harness de um agente só, ou nenhuma pasta de agentes), ela cai para uma pergunta mais grosseira:
*existe algum `PreToolUse` cobrindo escrita e algum cobrindo rede/execução, no harness inteiro?* Ela
não sabe dizer QUAL ferramenta ficou sem cerca — só que existe cobertura ou não.

## 6 · `APPROVAL` lê o SCRIPT, nunca RODA o hook

A porta procura, no texto do arquivo referenciado por `PreToolUse`, os marcadores que o Claude Code
de fato usa para negar (`permissionDecision: deny`, `decision: block`, `sys.exit(2)`). Ela não invoca
o hook com um evento sintético e confere a saída — um script que contém a string `"deny"` dentro de
um comentário, nunca executado, passaria. E um hook escrito em linguagem sem essas três marcas
(Node com `process.exit(1)`, por exemplo, que também bloqueia no Claude Code) pode ficar sem crédito:
`_MARCA_EXIT2` cobre `process.exit(2)`, mas não todo código de saída não-zero que a ferramenta aceita.

## 7 · `TRACEABILITY` não verifica APPEND-ONLY de verdade

A proposta original pede "registro presente, append-only, datado". `placar` confere presença e data.
**Não confere append-only** — isso exigiria varrer `git log` por arquivo procurando remoção ou edição
destrutiva de entrada antiga, e nesta rodada isso não foi construído. Um registro de decisões que é
editado e reescrito por cima passa igual a um que só cresce.

## 8 · `CONTAINMENT` é o mais fraco das sete, e é assim de propósito

A busca por `\bR[0-4]\b` perto de uma palavra de reversibilidade é o padrão MENOS específico do
módulo — ele vai errar para os dois lados. **A régua R0–R4 em si é emprestada** de uma fonte externa
ao ecossistema majoritário; a maioria dos repositórios do mundo não usa NENHUM vocabulário parecido,
mesmo tendo mecanismo de reversibilidade de fato (um `git revert` documentado, um feature flag). Isto
faz `CONTAINMENT` reprovar a maioria absoluta dos repositórios reais hoje — **e essa é a leitura
correta da proposta**: é a porta mais rara de passar, porque é a menos praticada do ecossistema.

Medido nesta rodada: o próprio repositório `loadline` **não tem harness de agente na raiz**
(`python -m placar .` devolve exit 2 — nenhum `CLAUDE.md`/`AGENTS.md`/`.claude/`, porque este
repositório É a ferramenta, não um agente configurado). Contra `exemplos/roster-de-exemplo/` — o
mesmo fixture que o `README.md` da `forja` usa — o placar reprova 6 das 7 portas, e `CONTAINMENT` é
uma delas: nenhum dos quatro agentes de exemplo classifica reversibilidade. `IDENTITY` é a única que
passa limpa. Isto não está publicado no `README.md` — o `README.md` está deliberadamente curto
(`ADR-112`), e uma rodada completa de `placar` não cabe nele sem competir com o exemplo da `forja`,
que é a porta de entrada.

## 9 · Nenhuma porta é dinâmica

`placar` lê arquivo parado. Ele não roda o agente, não observa o hook sendo de fato chamado pelo
harness, e não sabe se o `PreToolUse` está de fato registrado no lugar que o Claude Code lê (um
`settings.json` mal-formado que o parser do harness rejeita silenciosamente passaria aqui, porque
`json.loads` consegue ler o que o Claude Code recusaria). Mesma fronteira que `LACUNAS.md` da raiz já
declara para a `vistoria`, generalizada às sete portas.

## 10 · O teto de 4.000 arquivos por varredura é ESCOLHIDO, não medido

`_arquivos_de_texto` para de ler depois de 4.000 arquivos (2.000 para `TRACEABILITY`) — um monorepo
gigante pode ter segredo ou registro de decisão fora da janela lida. **O corte em si é declarado no
relatório** (ver item "Fechadas" abaixo); o que continua em aberto é só o NÚMERO do teto, que foi
escolhido para não travar, não medido contra um repositório real desse tamanho.

## Fechadas

- **`_arquivos_de_texto` cortava em silêncio ao bater o teto** — fechada na mesma rodada em que
  nasceu, antes do primeiro commit. `IDENTITY`, `TRACEABILITY` (ramo sem pasta de decisão dedicada)
  e `CONTAINMENT` agora recebem `(arquivos, truncado, puladas)` e imprimem o aviso no `resumo` quando
  o corte aconteceu. Era exatamente a armadilha que o comentário do próprio código já citava (`rg`
  sem `-L`) — deixá-la de pé teria sido a ferramenta que prega honestidade sendo desonesta sobre si
  mesma.
- **A varredura de arquivo atravessava junction/symlink sem avisar** — fechada na mesma rodada.
  `os.walk` sem cuidado desce por dentro de reparse point do Windows de qualquer forma (a mesma causa
  1 que o `blind` desta casa mediu). `_arquivos_de_texto` agora PODA junction e symlink de diretório
  antes de descer, e o relatório nomeia quantas fronteiras foram puladas, apontando para
  `python -m blind` como o comando que mostra o que está atrás. Sem isto, rodar `placar` na raiz de
  um repositório com uma junction para conteúdo externo (este próprio ecossistema de `loadline` vive
  ao lado de um cérebro montado por junction) leria — e poderia reportar segredo de — uma árvore que
  o alvo declarado não sabia que alcançava.
