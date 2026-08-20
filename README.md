# aferido

> **Aquilo que não está escrito não existe.**
> E aquilo que está escrito e não é reconferido, **mente**.

Toda documentação envelhece calada. O número que estava certo em janeiro continua na página em
agosto, com a mesma cara de certo, e ninguém tem como saber. Lista `awesome-*`, README, wiki
interna, dossiê de arquitetura: **nenhum deles reprova quando envelhece.**

`aferido` faz uma afirmação escrita dizer **quando ela vence** e **como recomputá-la**.

```markdown
Seis projetos independentes usam o nome AgentGuard.
<!-- aferido: colisao.agentguard=6 natureza=contagem em=2026-08-16 vence=90d -->
```

```console
$ python -m aferido .
VENCIDO   README.md:12  colisao.agentguard: escrito=6 medido=6
          → reconfira e resele — ninguém olha isto há 94 dias (prazo: 90d)
```

**O número está certo e mesmo assim reprova.** É o ponto: um número que ninguém reconfere há três
meses é um número que ainda não errou — não um número verificado.

---

## Por que isto não existe ainda

Fui atrás de dezenas de ferramentas do ecossistema de agentes e passei todas por uma pergunta só:

| Mecanismo | Responde |
|---|---|
| Proveniência (W3C PROV-O) | **de onde** veio o fato |
| Snapshot temporal | **o que** sabíamos naquela data |
| Teste / relatório de evidência | esta corrida **passou** |
| Build determinístico | é **reprodutível** |
| **`aferido`** | **isto que está escrito continua sendo verdade hoje?** |

As quatro primeiras existem, maduras, com dono grande.

**A quinta tem vizinhos, e eles merecem ser nomeados** — conferido em 2026-08-20:

| Vizinho | O que faz | Onde ele para |
|---|---|---|
| [`drift`](https://www.driftdev.sh/) | ancora spec markdown no código com tree-sitter e falha o CI | compara doc × código **agora**; não tem noção de prazo |
| `Provena` | trilha com hash encadeado e **checagem de frescor com limiar de idade** | governa **fonte de contexto** em runtime (RAG, ferramenta, memória, MCP), não asserção escrita em prosa |
| [`freshprobe`](https://github.com/Sudhan30/freshprobe) | sonda endpoint para frescor de cache, latência, TLS | é endpoint, não documento |

**O que continua sem dono é mais estreito do que "a quinta linha", e mais afiado:** ninguém junta as duas metades — **(a)** um prazo de validade na asserção com **(b)** a regra de que a sonda **não pode ler a fonte que produziu o número escrito**. O `drift` não tem (a). O `Provena` tem (a) sobre outro objeto e não tem (b). **A regra anti-espelho é a metade que não existe em lugar nenhum**, e sem ela o par passa verde travando o defeito em vez de achá-lo.

⚠️ Este parágrafo já disse *"a quinta não tinha ninguém"*. Era forte demais, e caiu quando alguém foi conferir. Fica escrito que caiu: um registro que existe para cobrar denominador não pode abrir com um claim sem denominador.

---

## Os seis vereditos

| | Significa | O que fazer |
|---|---|---|
| `VALE` | escrito == medido, dentro do prazo | nada |
| `DERIVOU` | escrito != medido | **depende da natureza — ver abaixo** |
| `VENCIDO` | passou do `vence`, mesmo batendo | reconferir e resselar |
| `SEM_PROVA` | não há sonda para a métrica | escrever a sonda, ou tirar o número |
| `CONGELADO` | histórico declarado, com motivo | nada; não se recomputa |
| **`PROSA_MUDA`** | **a FRASE afirma um número que o selo do bloco não cobre** | **corrigir a frase, ou nomear a grandeza no selo** |

<!-- aferido: nucleo.vereditos=6 natureza=relacao em=2026-08-20 vence=nunca fonte=aferido/__main__.py -->

### `PROSA_MUDA` — o buraco que os outros cinco deixavam

Os cinco primeiros olham o **valor dentro do comentário**. Nenhum olhava a **frase ao lado dele**.
Quem resela mexe no comentário, que é o que reprova, e esquece o texto, que é o que a pessoa lê:

```markdown
33 passaram · 0 reprovaram
<!-- aferido: nucleo.checks=36 natureza=contagem em=2026-08-16 vence=nunca -->
```

O selo diz 36. A sonda mede 36. **`VALE`.** E a linha de cima diz 33, para sempre.

Isto não é hipótese: **é o estado deste repositório entre 2026-08-16 e 2026-08-20**, achado ao
rodar a ferramenta contra ela mesma. O conserto foi o veredito acima, e o número na frase.

A regra morde numa direção só: **número afirmado na prosa que nenhum selo do bloco explica.**
Prosa sem número não é acusada — não há o que contradizer. Artigo e pronome ficam de fora
(*"os dois lados"* retoma, não conta), e data, versão, percentual e identificador com
dois-pontos são endereço, não asserção. Um selo pode declarar `eco=nao` e sair do confronto —
e a dispensa aparece **nomeada** no relatório, que é a diferença entre uma exceção e um furo.

### `DERIVOU` sozinho não diz nada

É o par `(veredito, natureza)` que diz. Por isso `natureza` é **obrigatória** em todo selo com
métrica — sem ela o selo não é lido, ele é recusado:

- **`natureza=contagem`** — a grandeza anda quando alguém escreve. Divergir é normal.
  **Resele e siga.**
- **`natureza=relacao`** — a grandeza só anda se o medidor ou o corpus quebrou. Divergir é
  **defeito**. **Pare e investigue antes de resselar.**

Sem essa distinção, todo vermelho vira ruído, e a resposta certa a todo vermelho vira "resela". Aí o
único bug que o mecanismo existia para pegar passa despercebido, resselado junto com o resto.

---

## A regra que faz o par valer alguma coisa

**A sonda não pode ler a mesma fonte que produziu o número escrito.**

Se os dois lados saem do mesmo lugar, o par passa verde **travando** o defeito em vez de achá-lo.
É check espelho, e ele não verifica nada. Por isso toda sonda declara de onde tira o valor, e a
declaração sai no relatório:

```console
$ python -m aferido . --sondas
sondas carregadas de: sondas.py
  censo.projetos               ← len(projetos) em censo/ecossistema.json
  colisao.*                    ← len(colide_com) + 1 se houver repo canônico, por nome
```

**E há um limite declarado de propósito:** a sonda prova **coerência interna**. Nenhuma sonda
offline alcança a verdade do mundo lá fora. É para isso que serve o `vence=` — ele é o que obriga
alguém a sair da máquina. Confundir os dois seria dizer que um JSON coerente é um fato verdadeiro.

---

## Instalação

```console
$ git clone <este repo> && cd aferido
$ python -m aferido .
```

Não há segundo passo. **Zero dependências** — só a stdlib do Python.

<!-- aferido: nucleo.dependencias=0 natureza=relacao em=2026-08-16 vence=nunca fonte=requisitos.txt -->
<!-- aferido: nucleo.modulos=7 natureza=contagem em=2026-08-20 vence=nunca fonte=aferido/ -->

Sem LLM, sem embedding, sem banco vetorial, sem chave de API, sem serviço. Uma afirmação ou é
recomputável por uma função, ou não é afirmável. Isso não é minimalismo estético: um verificador que
depende de um modelo não é um verificador, é uma segunda opinião.

---

## `censo/` — a primeira aplicação, e a prova de conceito

Um registro do ecossistema de agentes de IA onde **cada entrada vence**. Cada projeto sai com
licença, veredito de compatibilidade OSI, o que ele **faz** (lido na página do repositório, nunca no
post que o citou) e **com quem ele colide**.

<!-- aferido: censo.projetos=15 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->

Quinze projetos catalogados até aqui. E a entrada nº 1 é o motivo de o censo existir:

**Cinco desses nomes não identificam um projeto.** Identificam um cacho de projetos independentes,
mesmo nome, mesmo problema, que não se citam:

| Nome | Projetos independentes |
|---|---:|
| `AgentGuard` | **6** |
| `reverse-skill` | **6** |
| `PicoAgents` | **4** |
| `repowise` | **2** |
| `deja-vu` | **2** |

<!-- aferido: colisao.nomes=5 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->
<!-- aferido: colisao.agentguard=6 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->
<!-- aferido: colisao.reverse-skill=6 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->
<!-- aferido: colisao.picoagents=4 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->
<!-- aferido: colisao.repowise=2 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->
<!-- aferido: colisao.deja-vu=2 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->

Quem ouve *"instala o AgentGuard"* não tem como saber qual dos seis. Nenhum dos seis lista os outros
cinco. **Não falta um sétimo AgentGuard. Falta o registro — e falta ele vencer.**

### O denominador do censo, declarado

Doze dos quinze têm repositório canônico identificado e lido. Dois não têm repositório canônico — e essa
ausência **é** o achado, não uma falha da busca. Um é paper, não repositório.

<!-- aferido: censo.com_repo_canonico=12 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->
<!-- aferido: censo.sem_repo_canonico=2 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->

**Nenhum dos quinze foi clonado, instalado ou executado.** Todo número de desempenho no censo está
no campo `alegacao_do_autor` — ele é alegação, não medição.

<!-- aferido: censo.clonados_ou_executados=0 natureza=relacao em=2026-08-16 vence=nunca fonte=censo/ecossistema.json -->

Sete carregam licença aprovada pela OSI, lida na página do repositório. Dois **não são open source**
apesar de se apresentarem como abertos — e essa distinção é a razão de o campo existir.

<!-- aferido: censo.licenca.osi=7 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->
<!-- aferido: censo.licenca.nao_osi=2 natureza=contagem em=2026-08-16 vence=90d fonte=censo/ecossistema.json -->

> **Sobre `CC BY-NC` e por que ela reprova aqui.** Uma licença não-comercial não é open source: não é
> aprovada pela OSI, não se relicencia, e a restrição atravessa para todos os usuários abaixo. Um
> projeto que a vendorize passa a proibir uso comercial a todo mundo — excluindo a padaria da
> esquina, a cooperativa e a ONG que cobra por serviço. **Rodar** essas ferramentas é livre; **ler a
> arquitetura delas como especificação** é livre; **copiar o código para dentro** é o que
> contamina. O censo separa as três coisas em vez de dar um veredito só.

---

### A lista publicável

`censo/CENSO.md` é a superfície de leitura, **gerada** de `censo/ecossistema.json`:

```console
$ python censo/gerar.py             # escreve censo/CENSO.md
$ python censo/gerar.py --conferir  # não escreve; sai 1 se estiver fora de sincronia
```

**E ela quase não tem selo, de propósito.** Selar cada número de um arquivo gerado seria check
espelho: os dois lados sairiam do mesmo JSON, e o par passaria verde **travando** o defeito em vez
de achá-lo. A pergunta certa para um artefato derivado não é *"o número está certo?"* — é **"isto
ainda corresponde à fonte?"**. Por isso o `CENSO.md` carrega **um** selo só, de `natureza=relacao`:
ele não anda quando alguém acrescenta um projeto, só anda se alguém editou o publicado à mão ou
mexeu na fonte sem regerar. Divergir ali manda **parar**, não resselar.

---

## `forja/` — o compilador de agente, e ele emite gate, não prompt

Uma spec declarativa entra. **Sete artefatos saem** — e três deles não são texto para o modelo ler.

```console
$ python -m forja forja/exemplos/revisor-de-licenca.toml
  ✓ build/revisor-de-licenca/.claude/agents/revisor-de-licenca.md
  ✓ build/revisor-de-licenca/AGENTS.md
  ✓ build/revisor-de-licenca/revisor-de-licenca.system.md
  ✓ build/revisor-de-licenca/hooks/cerca_revisor_de_licenca.py
  ✓ build/revisor-de-licenca/golden/revisor-de-licenca.md
  ✓ build/revisor-de-licenca/LACUNAS.md
  ✓ build/revisor-de-licenca/RECEITA.md
```

<!-- aferido: forja.artefatos=7 natureza=contagem em=2026-08-16 vence=nunca fonte=forja/__main__.py -->
<!-- aferido: forja.modulos=6 natureza=contagem em=2026-08-16 vence=nunca fonte=forja/ -->

| Artefato | Para quem | O que ele é |
|---|---|---|
| `.claude/agents/<slug>.md` | Claude Code | subagente com frontmatter e prompt |
| `AGENTS.md` | qualquer harness | o formato que ninguém é dono |
| `<slug>.system.md` | SDK / harness próprio | system prompt cru |
| **`hooks/cerca_<slug>.py`** | o runtime | **código que nega antes de a ferramenta rodar** |
| **`golden/<slug>.md`** | quem verifica | **a pergunta que confere a RESPOSTA, não o código** |
| **`LACUNAS.md`** | quem lê a resposta | **o que este agente não mede** |
| `RECEITA.md` | auditoria | de que spec saiu o quê, e quando |

**Prompt bonito sem esses três é um agente sem gate com uma descrição melhor.** É por isso que a
forja existe, e é a única diferença que importa entre ela e um gerador de texto.

### Oito recusas, e todas falham fechadas

A forja **não emite** quando não consegue decidir. Ausente e vazio significam a mesma coisa, e as
duas barram — porque tratar ausente como permissivo é como toda cerca vira porta dos fundos.

| | Recusa quando | Por quê |
|---|---|---|
| `R1` | pede rede e não declara `dominios_permitidos` | fronteira escrita em prosa não é fronteira |
| `R2` | pede escrita e não declara `saida_cercada` | *"escrevo num caminho só"* é intenção, não cerca |
| `R3` | `nunca_usar` vazio | sem anti-descrição o orquestrador despacha por tema |
| `R4` | `lacunas` vazio | agente sem limite declarado é lido como sem limite |
| `R5` | golden set vazio | nada pergunta se a **resposta** está certa |
| `R6` | golden derivado de dentro da saída do agente | check espelho: os dois lados, a mesma fonte |
| `R7` | `toca_alvo` sem autorização de engajamento | comando fora do alvo autorizado é incidente |
| `R8` | slug inválido | ele vira nome de arquivo e de pasta em todo artefato emitido |

<!-- aferido: forja.recusas=8 natureza=contagem em=2026-08-16 vence=nunca fonte=forja/spec.py -->

Toda recusa traz o **conserto escrito**. Recusa sem saída treina quem a lê a contorná-la.

### O guarda emitido nega de verdade

Não é um comentário pedindo boa-fé ao modelo. É um `PreToolUse` que roda como processo, lê o evento
no stdin e responde `deny` — e o autoteste o prova **rodando o subprocesso**, não lendo o código:

- domínio fora da cerca → `deny`, com o conserto na razão;
- domínio dentro da cerca → passa (uma cerca que nega tudo é indistinguível de uma quebrada, e a
  primeira coisa que alguém faz com ela é desligá-la);
- `github.com.mau.site` **não** cai sob `github.com` — a comparação é por rótulo de domínio, e não
  por `endswith` de string, que deixa passar exatamente o sufixo que o atacante escolhe;
- evento ilegível → `deny`. **A hora em que o guarda quebra é a hora em que alguém está passando.**

### A vacina de vírus de ideia entra sem perguntar

Todo artefato de prompt sai com um parágrafo curto — o mesmo que `arXiv:2608.10218` (*Mind Viruses:
Self-Propagating Ideas in Multi-Agent LLM Systems*, Anthropic, 2026-08-10) mediu como conferindo
**imunidade quase total** à propagação de ideia entre agentes.

O canal medido pelo paper não é exótico: os vírus *"se espalham escrevendo a si mesmos nos arquivos
de memória e de configuração dos agentes, e instruindo cada novo hospedeiro a copiá-los adiante"*.
Memória, spec, arquivo de boot, roster — **todo projeto de agente sério tem os quatro.**

O texto é o `defensive_v2.md` do repositório do próprio paper (`frotaur/mindvirus-viruschain`, MIT),
citado com fonte. ⚠️ **"Quase total" não é total: é vacina, não muralha** — e o próprio paper avisa
que essas proteções serão testadas conforme os sistemas multiagente crescerem.

### O que a forja consulta antes de aconselhar

Quando a spec declara `precisa = ["memoria"]`, a forja **abre o Censo** e devolve as peças reais,
com licença, veredito de OSI e aviso de colisão — em vez de recomendar de cabeça:

```console
### `controle`
- **AgentGuard** — ⛔ sem canônico
  - ◻️ licença não verificada — confira antes de usar (`varia por projeto`)
  - ⚠️ **`AgentGuard` identifica 6 projetos independentes.** Instalar pelo nome é
    loteria — use a URL, não o nome.
```

É a parte que serve à régua: *a tia da limpeza não precisa do sétimo framework — ela precisa saber
**qual dos seis**, e se o que leram sobre ele ainda vale.* E o bilionário precisa da mesma coisa,
pelo mesmo motivo; só que ele chama de auditoria.

**Censo ausente nunca vira censo vazio.** *"Não consultei"* e *"não existe peça"* dizem coisas
opostas, e confundi-las é a forma mais barata de inventar um fato.

---

## O que este projeto NÃO mede

Oito lacunas declaradas em [`LACUNAS.md`](LACUNAS.md) — de *"a sonda prova coerência interna,
nunca a verdade do mundo"* até *"não há marca para o número que foi **escolhido**, e não medido"*.

<!-- aferido: nucleo.lacunas=8 natureza=contagem em=2026-08-20 vence=nunca fonte=LACUNAS.md -->

Toda ferramenta publica o que passou e o que falhou. Quase nenhuma publica **o que nunca olhou** —
e é essa terceira lista que decide se um verde significa alguma coisa. O número acima é escrito
aqui e recomputado de lá: dois artefatos, que é o que faz o par valer.

---

## Os controles negativos

```console
$ python autoteste.py
39 checks declarados · 39 executados · 0 fora do denominador
PASSOU
```

<!-- aferido: nucleo.checks=39 nucleo.fora=0 natureza=contagem em=2026-08-20 vence=nunca fonte=autoteste.py -->

**Cada check reintroduz o defeito que ele existe para pegar.** Um check que só confirma o caminho
feliz passa igual se o mecanismo for removido — ele não prova nada, e o custo dele é dar a alguém a
sensação de que está coberto.

---

## Licença

MIT. De propósito, e a escolha é derivada: se o critério é que **tanto o bilionário quanto a tia da
limpeza** possam ler, entender e aplicar, então uma licença que exclui um dos dois já falhou no
critério. `NC` exclui o bilionário. Copyleft forte exclui quem não pode abrir. **MIT não exclui
ninguém.**
