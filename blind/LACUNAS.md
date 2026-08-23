# O que o `blind` NÃO mede

> A mesma terceira lista que o `LACUNAS.md` da raiz e a `vitrine` publicam.
> Quase toda ferramenta diz o que passou e o que falhou; poucas dizem o que
> nunca olharam — e é essa lista que decide se o silêncio do `blind` significa
> alguma coisa.

## 1 · Duas causas nomeadas, e só essas duas

`blind` sabe procurar reparse point (junction/symlink) e regra de `.gitignore`
dentro de repositório git real. Ele **não** procura:

- **Submódulo git** (`.gitmodules`) — nomeado na proposta original, não
  implementado nesta rodada. Um submódulo com `CLAUDE.md` dentro escapa.
- **`.ignore`/`.rgignore`** — o ripgrep respeita os dois além do `.gitignore`,
  mesmo fora de repositório git. Não lidos aqui.
- **`.git/info/exclude`** e gitignore **global** (`core.excludesFile`) — regra
  de exclusão que não mora num `.gitignore` versionado não é vista.
- **Fronteira de monorepo** (workspace do pnpm/Bazel/Nx que aponta para fora
  da árvore) — nomeada na proposta, não medida: não há um formato único para
  detectar por parser.
- **Symlink de ARQUIVO**, só de diretório. Um `CLAUDE.md` que é ele mesmo um
  symlink para outro lugar não é achado.

## 2 · O parser de `.gitignore` é um piso, não a especificação

Cobre nome simples, `/` inicial (ancorado à pasta do próprio `.gitignore`),
`/` final (só diretório) e curinga via `fnmatch`. **Não cobre:** negação
(`!padrao`), `**`, classe de caracteres `[abc]`, nem a precedência entre
`.gitignore` aninhados (um `.gitignore` mais profundo que reverte a regra do
pai). Um padrão usando qualquer um destes pode casar errado — falso positivo
ou falso negativo, sem aviso.

## 3 · A lista de "arquivo de declaração" é ESCOLHIDA, não normativa

`CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `agent.toml`, `settings.json`, mais
qualquer coisa sob uma pasta `.claude/`. É a lista de nomes que os harnesses
de hoje usam — **não** um padrão do formato. Um harness que inventar outro
nome de arquivo de instrução não é reconhecido aqui.

<!-- aferido: blind.declaracao=5 natureza=contagem em=2026-08-23 vence=nunca fonte=blind/limites.py -->

## 4 · `blind` não prova o que a SUA ferramenta faz

Ele inventaria a fronteira e simula as duas causas medidas nesta casa (rg,
Python `os.walk`/`rglob`). Ele **não roda** o seu `grep`, o seu indexador de
IDE, ou o crawler do seu CI contra o alvo — não sabe se ELES especificamente
enxergam a fronteira. Ele responde *"existe aqui uma fronteira que É CONHECIDA
por confundir ferramenta nenhuma-consciente"*, não *"a sua ferramenta X
especificamente falhou agora"*.

## 5 · Ciclo de symlink não foi testado sob estresse

Um symlink que aponta para um ancestral dele mesmo (ciclo) não é impedido
explicitamente — a pilha de varredura do `_reparse_points` não desce POR
DENTRO da fronteira encontrada (ela varre para inventariar, não para
percorrer de novo pela pilha principal), o que evita o caso comum, mas não
foi montado um teste dirigido para o ciclo.

## 6 · Construído e testado só no Windows, nesta sessão

A detecção de junction usa `os.path.isjunction` (Python ≥ 3.12) com fallback
para o reparse tag `0xA0000003`, e os cinco controles negativos
(`blind/controles.py`) rodam `mklink /J`. `os.path.islink` (o ramo de
symlink, para POSIX) é código escrito e não tem controle negativo dirigido
nesta rodada — **nomeado, não verificado**.

## 7 · Não julga se a fronteira devia existir

Uma junction é frequentemente uma decisão legítima — é assim que este próprio
cérebro liga vaults. `blind` nunca diz "remova isto"; ele diz "isto existe, e
aqui está o que uma varredura ingênua não veria atrás dela". A decisão sobre
se a fronteira é apropriada continua sendo de quem lê o relatório.
