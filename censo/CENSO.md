# O Censo do ecossistema de agentes de IA

> **Este arquivo é gerado.** Não o edite à mão — edite `censo/ecossistema.json` e rode
> `python censo/gerar.py`. O verificador reprova se os dois saírem de sincronia.

<!-- measured: censo.gerado_em_dia=1 natureza=relacao em=2026-08-16 vence=nunca fonte=censo/gerar.py -->

Uma lista `awesome-*` não reprova quando envelhece. Este censo reprova.

**15 projetos.** Cada entrada foi lida **na página do repositório**, nunca no
post que o citou. O que não foi verificado está escrito como não verificado — nunca
preenchido por plausibilidade, e nunca convertido em zero.

---

## O achado: cinco nomes não identificam um projeto

Estes nomes identificam um **cacho de projetos independentes** — mesmo nome, mesmo
problema, sem se citarem:

| Nome | Projetos independentes | Existe canônico? |
|---|---:|---|
| `AgentGuard` | **6** | ⛔ **não** |
| `reverse-skill` | **6** | ⛔ **não** |
| `PicoAgents` | **4** | sim |
| `deja-vu` | **2** | sim |
| `repowise` | **2** | sim |

Quem ouve *"instala o AgentGuard"* não tem como saber qual dos seis. **Nenhum dos seis
lista os outros cinco.** Isso não é *"existem muitos projetos"* — é o mesmo projeto
feito seis vezes no escuro.

> **Denominador, e ele importa:** isto é o que **uma busca por nome, num dia** devolveu.
> Não é censo do GitHub. **É piso, não teto** — o número real é maior, nunca menor.

---

## Quem já ocupa cada estágio

Ordenado pelo ciclo de vida de um agente, não pelo alfabeto — porque o que interessa
é **onde já tem dono grande** e onde não tem.

| Estágio | O que é | Quem ocupa |
|---|---|---|
| **Entender o repositório** | o agente lê a base de código antes de agir | repowise · Corbell |
| **Ter capacidade** | de onde vem a habilidade que o agente ainda não tem | AgentSkillOS · reverse-skill |
| **Ter memória** | o que sobrevive ao contexto apagado entre sessões | deja-vu |
| **Saber o que é o quê** | entidades, relações e de onde veio cada fato | Semantica · PANO |
| **Rodar o laço** | quem executa o agente, com sandbox e subagente | DeerFlow · deepagents · PicoAgents |
| **Bloquear em runtime** | o guarda que decide o que o agente não faz | AgentGuard |
| **Provar que passou** | a evidência que o humano lê no lugar do diff | old-coder |
| **Atacar** | quem tenta quebrar o agente de propósito | DeepTeam |
| **Aprender com a falha** | o que converte falha em conserto | Harness-R1 |
| **A ameaça medida** | pesquisa, não ferramenta | Mind Viruses |

---

## Os projetos, com licença lida na fonte

A coluna que decide se você pode usar é a **terceira**, não a segunda. Uma licença que
não é OSI não vira open source por o projeto se chamar de aberto.

| Projeto | Onde | Licença | Veredito | Nomes no cacho |
|---|---|---|---|---:|
| **AgentGuard** | — | varia por projeto | ◻️ não verificado | **6** |
| **AgentSkillOS** | [ynulihao/AgentSkillOS](https://github.com/ynulihao/AgentSkillOS) | MIT | ✅ OSI | 1 |
| **Corbell** | [Corbell-AI/Corbell](https://github.com/Corbell-AI/Corbell) | Apache-2.0 | ◻️ não verificado | 1 |
| **deepagents** | [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | MIT | ◻️ não verificado | 1 |
| **DeepTeam** | [confident-ai/deepteam](https://github.com/confident-ai/deepteam) | Apache-2.0 | ✅ OSI | 1 |
| **DeerFlow** | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | MIT | ✅ OSI | 1 |
| **deja-vu** | [vshulcz/deja-vu](https://github.com/vshulcz/deja-vu) | MIT | ✅ OSI | **2** |
| **Harness-R1** | [DeepExperience/Harness-R1](https://github.com/DeepExperience/Harness-R1) | Apache-2.0 | ✅ OSI | 1 |
| **Mind Viruses** | `arXiv:2608.10218` | paper | ⛔ não é open source | 1 |
| **old-coder** | [AmazingAng/old-coder](https://github.com/AmazingAng/old-coder) | MIT | ✅ OSI | 1 |
| **PANO** | [ALW1EZ/PANO](https://github.com/ALW1EZ/PANO) | CC BY-NC | ⛔ não é open source | 1 |
| **PicoAgents** | [victordibia/designing-multiagent-systems](https://github.com/victordibia/designing-multiagent-systems) | nao verificado | ◻️ não verificado | **4** |
| **repowise** | [repowise-dev/repowise](https://github.com/repowise-dev/repowise) | AGPL-3.0 | ⚠️ OSI, copyleft forte | **2** |
| **reverse-skill** | — | varia por projeto | ◻️ não verificado | **6** |
| **Semantica** | [semantica-agi/semantica](https://github.com/semantica-agi/semantica) | MIT | ✅ OSI | 1 |

**As três portas de uma licença não-OSI**, porque tratá-las como uma só é o erro comum:

| O que fazer | Permitido? |
|---|---|
| **Rodar** a ferramenta | ✅ sim — é o que a licença concede |
| **Ler a arquitetura como especificação** e reimplementar | ✅ sim — API e modelo não são a expressão protegida |
| **Copiar o código para dentro** do seu projeto | ⛔ não — a restrição atravessa para todos os seus usuários |

---

## Ficha de cada um

### Entender o repositório

#### Corbell

- **Repositório:** https://github.com/Corbell-AI/Corbell
- **Licença:** Apache-2.0 — ◻️ não verificado
- **Faz:** Grafo de codigo multi-repo -> geracao e revisao de spec. Expoe grafo, embeddings e ferramentas de spec por MCP.
- **Depende de:** nao verificado
- **Lido em:** 2026-08-16

#### repowise

- **Repositório:** https://github.com/repowise-dev/repowise
- **Licença:** AGPL-3.0 — ⚠️ OSI, copyleft forte
- **Faz:** Repo -> grafo consultavel por 10 ferramentas MCP. AST de 19 linguagens + historico git, comunidades de Leiden, PageRank. O PR bot faz zero chamada de LLM e e' deterministico: o mesmo diff da' sempre a mesma revisao.
- **Depende de:** pip install; offline com Ollama; licenca comercial paga disponivel
- **Peso:** sem LLM no caminho
- **Colide com:** `RepoWise/backend`
- **Lido em:** 2026-08-16

### Ter capacidade

#### AgentSkillOS

- **Repositório:** https://github.com/ynulihao/AgentSkillOS
- **Paper:** `arXiv:2603.02176`
- **Licença:** MIT — ✅ OSI
- **Faz:** Indice de 90.000+ skills (a pagina hoje ja fala em 200.000+) com retrieval hibrido LLM + arvore de capacidade, e composicao em DAG. O repo afirma que embedding puro perde skills que parecem nao-relacionadas no espaco vetorial e sao cruciais.
- **Depende de:** Claude Code instalado + chave de API; SEM MCP
- **Peso:** ⚠️ **custa dinheiro** (chave de API ou serviço pago)
- **Sobre a contagem de colisão:** AgentSkillOS/SkillAnything e' da mesma organizacao, e agentskills/agentskills e' a ESPECIFICACAO mantida pela Anthropic. Nome parecido, projeto diferente — nao e' colisao e nao entra na contagem.
- **Lido em:** 2026-08-16

#### reverse-skill

- **Repositório canônico:** ⛔ **não existe** — ver a seção de colisão
- **Licença:** varia por projeto — ◻️ não verificado
- **Faz:** Skill de engenharia reversa / pentest para Claude Code. NAO EXISTE REPOSITORIO CANONICO: seis autores distintos publicaram sob nomes quase iguais.
- **Depende de:** varia por projeto
- **Peso:** sem embedding
- **Colide com:** `zhaoxuya520/reverse-skill` · `P4nda0s/reverse-skills` · `meirm/reverse-engineering-skill` · `incogbyte/iOS-reverse-engineering-claude-skill` · `SimoneAvogadro/android-reverse-engineering-skill` · `vgrichina/re-skill`
- **Lido em:** 2026-08-16

### Ter memória

#### deja-vu

- **Repositório:** https://github.com/vshulcz/deja-vu
- **Licença:** MIT — ✅ OSI
- **Faz:** Indexa as sessoes que agentes de codigo ja escreveram no disco, de 17 harnesses, e as devolve por MCP, CLI e hooks PreTool.
- **Depende de:** nenhuma; binario Go unico
- **Peso:** sem LLM no caminho · sem embedding
- **Alegação do autor** (não medida por este censo): 84,9% hit@1 no LongMemEval-S; ~1,5 ms mediano sobre 3,5 GB
- **Colide com:** `acoyfellow/deja`
- **Lido em:** 2026-08-16

### Saber o que é o quê

#### PANO

- **Repositório:** https://github.com/ALW1EZ/PANO
- **Licença:** CC BY-NC — ⛔ não é open source
- **Faz:** OSINT como grafo: entities (email, username, website, image, location, event, text) ligadas por transforms (Discovery, Correlation, Analysis, OSINT, Enrichment). Entities e transforms sao explicitamente plugaveis: classe base + arquivo na pasta.
- **Depende de:** Python 3.11 + PySide6/Qt; Windows e Linux
- **Peso:** sem embedding
- **Consequência da licença:** Rodar: permitido. Ler o catalogo entity/transform como especificacao e reimplementar: permitido. Copiar o codigo para dentro de um projeto open source: NAO — a restricao NC atravessa para todos os usuarios abaixo e tira o projeto do open source.
- **Ressalva operacional:** O transform de e-mail exige login GHunt contra conta Google alvo. Isso TOCA ALVO e exige autorizacao de engajamento, independente de licenca.
- **Lido em:** 2026-08-16

#### Semantica

- **Repositório:** https://github.com/semantica-agi/semantica
- **Licença:** MIT — ✅ OSI
- **Faz:** Grafo com W3C PROV-O em cada fato, deteccao de conflito antes do merge, snapshot temporal e raciocinio deterministico (SPARQL/Datalog/Rete). Servidor MCP proprio. Anuncia-se como 'The Open Source Palantir for AI Agents'.
- **Depende de:** triple store (Oxigraph/Jena) ou LPG (Neo4j) E vector store
- **Peso:** sem LLM no caminho
- **Responde:** de onde veio o fato, e o que sabiamos naquela data
- ****Não** responde:** se o que esta escrito continua sendo verdade hoje
- **Lido em:** 2026-08-16

### Rodar o laço

#### deepagents

- **Repositório:** https://github.com/langchain-ai/deepagents
- **Licença:** MIT — ◻️ não verificado
- **Faz:** Quatro middlewares sobre LangGraph: filesystem virtual com allow/deny, SKILL.md/AGENTS.md sob demanda, tool `task` para subagente efemero, `interrupt_on` para human-in-the-loop.
- **Depende de:** runtime LangGraph
- **Peso:** sem embedding
- **Lido em:** 2026-08-16

#### DeerFlow

- **Repositório:** https://github.com/bytedance/deer-flow
- **Licença:** MIT — ✅ OSI
- **Faz:** SuperAgent harness da ByteDance, 2.0 reescrito do zero. Sandbox local/Docker/k8s/E2B, memoria longa, skills por SKILL.md, subagentes com contexto escopado, gateway de IM.
- **Depende de:** Python 3.12 + Node 22; 8-16 GB RAM minimo; exige chave de LLM
- **Peso:** ⚠️ **custa dinheiro** (chave de API ou serviço pago)
- **Lido em:** 2026-08-16

#### PicoAgents

- **Repositório:** https://github.com/victordibia/designing-multiagent-systems
- **Licença:** nao verificado — ◻️ não verificado
- **Faz:** Framework multiagente construido do zero para ENSINAR — cada componente, do loop de raciocinio a' orquestracao, escrito para ser lido. 50+ exemplos por capitulo de livro.
- **Depende de:** nao verificado
- **Peso:** sem embedding
- **Colide com:** `borhen68/picoagents` · `dperezcabrera/pico-agent` · `kir-gadjello/picoagent-rnd`
- **Lido em:** 2026-08-16

### Bloquear em runtime

#### AgentGuard

- **Repositório canônico:** ⛔ **não existe** — ver a seção de colisão
- **Licença:** varia por projeto — ◻️ não verificado
- **Faz:** Guardrail de runtime para agente. NAO EXISTE REPOSITORIO CANONICO: o nome identifica seis projetos independentes que resolvem o mesmo problema sem se citarem.
- **Depende de:** varia por projeto
- **Colide com:** `GoPlusSecurity/agentguard` · `hidearmoon/agentguard` · `WhitzardAgent/AgentGuard` · `filipw/AgentGuard` · `JeongJaeSoon/agent-guard` · `bmdhodl/agent47`
- **Lido em:** 2026-08-16

### Provar que passou

#### old-coder

- **Repositório:** https://github.com/AmazingAng/old-coder
- **Licença:** MIT — ✅ OSI
- **Faz:** Skill, nao runtime. SPEC -> RED -> GREEN -> REFACTOR -> GAUNTLET -> EVIDENCE. O humano aprova o plano de teste antes do codigo existir e le um relatorio de evidencia depois, no lugar do diff.
- **Depende de:** o harness de codigo do usuario
- **Peso:** sem embedding
- **Nota:** O v6 atribuiu este repo a Andre Lindenberg. Andre Lindenberg postou a peca no LinkedIn; a autoria e' de AmazingAng.
- **Lido em:** 2026-08-16

### Atacar

#### DeepTeam

- **Repositório:** https://github.com/confident-ai/deepteam
- **Licença:** Apache-2.0 — ✅ OSI
- **Faz:** Red team de LLM e de agente. 50+ vulnerabilidades e 20+ vetores, com familia `Agentic`: Goal Theft, Recursive Hijacking, Excessive Agency. Alinhado a OWASP LLM Top 10 e NIST AI RMF. O alvo e' um callback string->string.
- **Depende de:** OPENAI_API_KEY por padrao; modelo local possivel via DeepEval
- **Peso:** sem embedding · ⚠️ **custa dinheiro** (chave de API ou serviço pago)
- **Sobre a contagem de colisão:** Voltaram Genez-io/genezio-deepteam e fengjian686/deepteam. NAO entram na contagem de colisao: nao foi verificado se sao forks, e fork nao e' projeto independente. Sub-contar de proposito.
- **Lido em:** 2026-08-16

### Aprender com a falha

#### Harness-R1

- **Repositório:** https://github.com/DeepExperience/Harness-R1
- **Paper:** `arXiv:2608.02276`
- **Licença:** Apache-2.0 — ✅ OSI
- **Faz:** Um engenheiro de harness de 9B (Qwen3.5-9B) treinado por RL converte lotes de falha do agente-alvo em patches executaveis validados. Checkpoints prontos no Hugging Face permitem usar sem treinar.
- **Depende de:** 8x NVIDIA H800 para treinar; checkpoint pronto para usar
- **Peso:** sem embedding
- **Alegação do autor** (não medida por este censo): 44,3% -> 53,6% (+9,3 p.p.); +5,0 p.p. com fine-tune do alvo
- **Ressalva do próprio paper:** um engenheiro so' e' significativo contra o alvo para o qual foi treinado
- **Lido em:** 2026-08-16

### A ameaça medida

#### Mind Viruses

- **Repositório canônico:** ⛔ **não existe** — ver a seção de colisão
- **Paper:** `arXiv:2608.10218`
- **Licença:** paper — ⛔ não é open source
- **Faz:** NAO E' FERRAMENTA. Pesquisa da Anthropic (Papadopoulos, Shah, Zimmerman, Lindsey; 2026-08-10) mostrando que uma ideia implantada em um agente se propaga para os outros. Dois cenarios medidos: um time pequeno de agentes num projeto de codigo compartilhado, e uma cadeia de agentes com contexto apagado entre sessoes.
- **Depende de:** nenhuma — e' um paper
- **Peso:** sem embedding
- **Achado principal:** Um aviso curto no system prompt do agente confere imunidade quase total. Payload nocivo se propaga menos que benigno, mas ainda funciona as vezes.
- **Limite desta leitura:** So' o abstract foi lido. Canal exato de propagacao e persistencia medida estao no corpo do paper e NAO foram abertos. A frase exata do aviso nao esta no abstract.
- **Lido em:** 2026-08-16

---

## O denominador desta leitura

Toda superfície que conta declara **de quantos** contou. Sem isso, um filtro que pula
em silêncio produz resposta plausível e vazia.

| | |
|---|---:|
| Nomes buscados | 15 |
| Com repositório canônico identificado e lido | 12 |
| **Sem** repositório canônico — e essa ausência **é** o achado | 2 |
| São paper, não repositório | 1 |
| **Clonados, instalados ou executados** | **0** |

⚠️ Nenhum repositorio foi clonado, instalado ou executado. Numero de desempenho no campo `alegacao_do_autor` NAO foi medido por este censo.

**O que este censo NÃO mede, declarado:**

- **Se o projeto funciona.** Nada aqui foi executado. Desempenho é alegação do autor.
- **Se ele ainda existe hoje.** É para isso que serve o `vence=` de cada selo — nenhuma
  sonda offline alcança a verdade do mundo lá fora, e confundir as duas coisas seria
  dizer que um JSON coerente é um fato verdadeiro.
- **Quantos projetos existem de verdade.** A contagem de colisão é piso de uma busca.
- **Se a licença mudou depois da data de leitura.** O campo `lido_em` de cada ficha é
  a data em que a página foi aberta, não a data de hoje.

---

## Como contribuir com uma entrada

1. Abra a **página do repositório** — não o post, não a lista, não o print. A memória
   desta casa registra o custo de atribuir pela embalagem: um projeto deste censo
   estava creditado a quem postou no LinkedIn, não a quem escreveu o código.
2. Preencha `censo/ecossistema.json`. **`nao_verificado` é um valor legítimo** e nunca
   vira zero.
3. Rode `python censo/gerar.py` e `python -m loadline .`. Se algum dos dois reprovar, a
   entrada ainda não está pronta.

