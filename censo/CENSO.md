# O Censo do ecossistema de agentes de IA

> **Este arquivo é gerado.** Não o edite à mão — edite `censo/ecossistema.json` e rode
> `python censo/gerar.py`. O verificador reprova se os dois saírem de sincronia.

<!-- measured: censo.gerado_em_dia=1 nature=relation on=2026-08-26 expires=never source=censo/gerar.py -->

Uma lista `awesome-*` não reprova quando envelhece. Este censo reprova.

**25 projetos.** Cada entrada foi lida **na página do repositório**, nunca no
post que o citou. O que não foi verificado está escrito como não verificado — nunca
preenchido por plausibilidade, e nunca convertido em zero.

---

## O achado: 9 nomes não identificam um projeto

Estes nomes identificam um **cacho de projetos independentes** — mesmo nome, mesmo
problema, sem se citarem:

| Nome | Projetos independentes | Existe canônico? |
|---|---:|---|
| `AgentGuard` | **6** | ⛔ **não** |
| `Awesome A2A` | **6** | ⛔ **não** |
| `reverse-skill` | **6** | ⛔ **não** |
| `PicoAgents` | **4** | sim |
| `SILENTCHAIN AI` | **3** | sim |
| `agent-audit` | **3** | sim |
| `MateClaw` | **2** | sim |
| `deja-vu` | **2** | sim |
| `repowise` | **2** | sim |

Quem ouve *"instala o `AgentGuard`"* não tem como saber qual dos 6. **Nenhum lista os outros.** Isso não é "existem muitos projetos" — é o mesmo projeto
feito 6 vezes no escuro, no pior caso desta leitura.

> **Denominador, e ele importa:** isto é o que **uma busca por nome, num dia** devolveu.
> Não é censo do GitHub. **É piso, não teto** — o número real é maior, nunca menor.

---

## Quem já ocupa cada estágio

Ordenado pelo ciclo de vida de um agente, não pelo alfabeto — porque o que interessa
é **onde já tem dono grande** e onde não tem.

| Estágio | O que é | Quem ocupa |
|---|---|---|
| **Entender o repositório** | o agente lê a base de código antes de agir | repowise · Corbell |
| **Ter capacidade** | de onde vem a habilidade que o agente ainda não tem | AgentSkillOS · reverse-skill · awesome-agent-skills |
| **Ter memória** | o que sobrevive ao contexto apagado entre sessões | deja-vu · mem9 |
| **Saber o que é o quê** | entidades, relações e de onde veio cada fato | Semantica · PANO |
| **Rodar o laço** | quem executa o agente, com sandbox e subagente | DeerFlow · deepagents · PicoAgents · MateClaw |
| **Bloquear em runtime** | o guarda que decide o que o agente não faz | AgentGuard · SkillSpector · agent-audit |
| **Provar que passou** | a evidência que o humano lê no lugar do diff | old-coder · PandaProbe · agent-pd |
| **Atacar** | quem tenta quebrar o agente de propósito | DeepTeam · SILENTCHAIN AI |
| **Aprender com a falha** | o que converte falha em conserto | Harness-R1 |
| **A ameaça medida** | pesquisa, não ferramenta | Mind Viruses |

---

## Os projetos, com licença lida na fonte

A coluna que decide se você pode usar é a **terceira**, não a segunda. Uma licença que
não é OSI não vira open source por o projeto se chamar de aberto.

| Projeto | Onde | Licença | Veredito | Nomes no cacho |
|---|---|---|---|---:|
| **agent-audit** | [scadastrangelove/agent-audit](https://github.com/scadastrangelove/agent-audit) | nao verificado | ◻️ não verificado | **3** |
| **agent-pd** | [varmabudharaju/agent-pd](https://github.com/varmabudharaju/agent-pd) | Apache-2.0 | ✅ OSI | 1 |
| **AgentGuard** | — | varia por projeto | ◻️ não verificado | **6** |
| **AgentSkillOS** | [ynulihao/AgentSkillOS](https://github.com/ynulihao/AgentSkillOS) | MIT | ✅ OSI | 1 |
| **Awesome A2A** | — | varia por projeto | ◻️ não verificado | **6** |
| **awesome-agent-skills** | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | MIT | ✅ OSI | 1 |
| **Corbell** | [Corbell-AI/Corbell](https://github.com/Corbell-AI/Corbell) | Apache-2.0 | ◻️ não verificado | 1 |
| **deepagents** | [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | MIT | ◻️ não verificado | 1 |
| **DeepSearcher** | [zilliztech/deep-searcher](https://github.com/zilliztech/deep-searcher) | Apache-2.0 | ✅ OSI | 1 |
| **DeepTeam** | [confident-ai/deepteam](https://github.com/confident-ai/deepteam) | Apache-2.0 | ✅ OSI | 1 |
| **DeerFlow** | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | MIT | ✅ OSI | 1 |
| **deja-vu** | [vshulcz/deja-vu](https://github.com/vshulcz/deja-vu) | MIT | ✅ OSI | **2** |
| **Harness-R1** | [DeepExperience/Harness-R1](https://github.com/DeepExperience/Harness-R1) | Apache-2.0 | ✅ OSI | 1 |
| **MateClaw** | [matevip/mateclaw](https://github.com/matevip/mateclaw) | Apache-2.0 | ✅ OSI | **2** |
| **mem9** | [mem9-ai/mem9](https://github.com/mem9-ai/mem9) | Apache-2.0 | ✅ OSI | 1 |
| **Mind Viruses** | `arXiv:2608.10218` | paper | ⛔ não é open source | 1 |
| **old-coder** | [AmazingAng/old-coder](https://github.com/AmazingAng/old-coder) | MIT | ✅ OSI | 1 |
| **PandaProbe** | [chirpz-ai/pandaprobe](https://github.com/chirpz-ai/pandaprobe) | Apache-2.0 | ✅ OSI | 1 |
| **PANO** | [ALW1EZ/PANO](https://github.com/ALW1EZ/PANO) | CC BY-NC | ⛔ não é open source | 1 |
| **PicoAgents** | [victordibia/designing-multiagent-systems](https://github.com/victordibia/designing-multiagent-systems) | nao verificado | ◻️ não verificado | **4** |
| **repowise** | [repowise-dev/repowise](https://github.com/repowise-dev/repowise) | AGPL-3.0 | ⚠️ OSI, copyleft forte | **2** |
| **reverse-skill** | — | varia por projeto | ◻️ não verificado | **6** |
| **Semantica** | [semantica-agi/semantica](https://github.com/semantica-agi/semantica) | MIT | ✅ OSI | 1 |
| **SILENTCHAIN AI** | [silentchainai/SILENTCHAIN](https://github.com/silentchainai/SILENTCHAIN) | proprietaria, source-visible | ⛔ não é open source | **3** |
| **SkillSpector** | [NVIDIA/skillspector](https://github.com/NVIDIA/skillspector) | Apache-2.0 | ✅ OSI | 1 |

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

#### awesome-agent-skills

- **Repositório:** https://github.com/VoltAgent/awesome-agent-skills
- **Licença:** MIT — ✅ OSI
- **Faz:** Indice curado de 1497+ Agent Skills oficiais (Anthropic, Google Labs, Vercel, Stripe, Cloudflare, Netlify, Trail of Bits, Sentry, Expo, Hugging Face, Figma) mais skills da comunidade, compativel com Claude Code, Codex, Antigravity, Gemini CLI, Cursor, GitHub Copilot, OpenCode, Windsurf.
- **Depende de:** nenhuma - e' uma lista curada, sem servico proprio
- **Peso:** sem LLM no caminho · sem embedding
- **Lido em:** 2026-08-25

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

#### mem9

- **Repositório:** https://github.com/mem9-ai/mem9
- **Licença:** Apache-2.0 — ✅ OSI
- **Faz:** Memoria persistente e compartilhada entre agentes, sessoes e maquinas (OpenClaw, Claude Code, OpenCode, Codex, Dify, Hermes Agent), com hybrid recall (semantica + palavra-chave) e dashboard visual. Ao contrario do deja-vu (mesmo estagio), usa LLM e embedding no caminho: smart-ingest extrai fato com LLM (default gpt-4o-mini) e o recall hibrido depende de embedding.
- **Depende de:** servidor Go + TiDB (ou PostgreSQL); hosted API disponivel; smart-ingest exige LLM compativel com a API da OpenAI
- **Peso:** ⚠️ **custa dinheiro** (chave de API ou serviço pago)
- **Lido em:** 2026-08-25

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

#### MateClaw

- **Repositório:** https://github.com/matevip/mateclaw
- **Licença:** Apache-2.0 — ✅ OSI
- **Faz:** Harness de orquestracao multi-agente (ReAct + Plan-and-Execute sobre StateGraph) empacotado num JAR Spring Boot so, com skills, memoria, MCP e suporte multi-canal. Multi-vendor failover entre LLM (DashScope, OpenAI, Anthropic, Gemini, DeepSeek, Ollama).
- **Depende de:** Java 21 + Spring Boot 3.5; PostgreSQL 16 ou MySQL 8 em producao; Ollama permite rodar sem chave paga
- **Peso:** ⚠️ **custa dinheiro** (chave de API ou serviço pago)
- **Colide com:** `mateaix/mateclaw`
- **Lido em:** 2026-08-25

#### PicoAgents

- **Repositório:** https://github.com/victordibia/designing-multiagent-systems
- **Licença:** nao verificado — ◻️ não verificado
- **Faz:** Framework multiagente construido do zero para ENSINAR — cada componente, do loop de raciocinio a' orquestracao, escrito para ser lido. 50+ exemplos por capitulo de livro.
- **Depende de:** nao verificado
- **Peso:** sem embedding
- **Colide com:** `borhen68/picoagents` · `dperezcabrera/pico-agent` · `kir-gadjello/picoagent-rnd`
- **Lido em:** 2026-08-16

### Bloquear em runtime

#### agent-audit

- **Repositório:** https://github.com/scadastrangelove/agent-audit
- **Licença:** nao verificado — ◻️ não verificado
- **Faz:** Auditor forense estatico e read-only ('no active defense — read-only analysis with consent prompts a cada passo') para agent homes locais (Claude Code, Codex CLI, OpenClaw) e para repositorios com superficie de instrucao (SKILL.md, manifests MCP, plugins). Roda detectores importados (entre eles Cisco PromptGuard, Gitleaks, NOVA, regras YARA da Cisco para MCP) mais logica nativa — 296 regras ao todo, segundo a descricao do proprio repositorio. Produz achados deduplicados, severidade normalizada e patch sugerido; nunca aplica automaticamente. Foco e' seguranca (injecao, exfiltracao, credencial, escalada de privilegio) — nao declara deteccao de sobreposicao/conflito ENTRE dois agentes, que e' o territorio do V6 do loadline. Mesma familia do SkillSpector (mesmo estagio): decide o que e' seguro confiar, nao e' guarda de runtime.
- **Depende de:** Python; `--verify` opcional chama LLM externo para re-checar achado; `yara-python` opcional para as 10 regras YARA da Cisco
- **Sobre a contagem de colisão:** Tres projetos independentes publicaram sob o nome EXATO `agent-audit`, sem se citarem — mesmo padrao do AgentGuard/reverse-skill desta lista. `scadastrangelove/agent-audit` e' o mais documentado dos tres (README completo, 296 regras citadas por nome); os outros dois nao foram lidos em profundidade nesta rodada — so' confirmados como existentes.
- **Colide com:** `piiiico/agent-audit` · `HeadyZhang/agent-audit`
- **Lido em:** 2026-08-26

#### AgentGuard

- **Repositório canônico:** ⛔ **não existe** — ver a seção de colisão
- **Licença:** varia por projeto — ◻️ não verificado
- **Faz:** Guardrail de runtime para agente. NAO EXISTE REPOSITORIO CANONICO: o nome identifica seis projetos independentes que resolvem o mesmo problema sem se citarem.
- **Depende de:** varia por projeto
- **Colide com:** `GoPlusSecurity/agentguard` · `hidearmoon/agentguard` · `WhitzardAgent/AgentGuard` · `filipw/AgentGuard` · `JeongJaeSoon/agent-guard` · `bmdhodl/agent47`
- **Lido em:** 2026-08-16

#### SkillSpector

- **Repositório:** https://github.com/NVIDIA/skillspector
- **Licença:** Apache-2.0 — ✅ OSI
- **Faz:** Scanner de seguranca para SKILL.md antes de instalar — 70 padroes de vulnerabilidade em 17 categorias (prompt injection, exfiltracao de dado, MCP tool poisoning, escalada de privilegio, entre outras). Nao e' guarda de RUNTIME como o resto desta categoria: decide o que INSTALA, nao o que o agente ja instalado pode fazer.
- **Depende de:** Python 3.12+; --no-llm roda so a analise estatica; o segundo estagio (avaliacao semantica, OPCIONAL) aceita OpenAI/Anthropic/AWS Bedrock/NVIDIA/agente CLI local
- **Lido em:** 2026-08-25

### Provar que passou

#### agent-pd

- **Repositório:** https://github.com/varmabudharaju/agent-pd
- **Licença:** Apache-2.0 — ✅ OSI
- **Faz:** Log de auditoria tamper-evident (hash-chain) para Claude Code: hook que audita o agente principal E cada subagente, correlacionando eventos entre sessoes concorrentes e workflows dinamicos. Seis detectores deterministicos (bypass de permissao, acesso a credencial fora de escopo, self-permissioning, ferramenta nao permitida, redundante, trabalho fora de tarefa) com evidencia citada. 'Catch-and-report — it never blocks': e' flight recorder, nunca firewall.
- **Depende de:** Python 3.11+, PyYAML; feature opcional `pd judge` usa Claude Code CLI (assinatura ja paga) ou API Anthropic metered
- **Peso:** sem embedding
- **Sobre a contagem de colisão:** Cobre parte do territorio do V6 do loadline (redundante/self-permissioning tangenciam deteccao de confusao entre agentes) mas em RUNTIME, nao em arquivo parado — o loadline nao roda o agente (LACUNAS.md #12), o agent-pd so' audita agente rodando. Nao declara comparacao de DESCRICAO entre dois agentes (o que o V6 mede).
- **Lido em:** 2026-08-26

#### old-coder

- **Repositório:** https://github.com/AmazingAng/old-coder
- **Licença:** MIT — ✅ OSI
- **Faz:** Skill, nao runtime. SPEC -> RED -> GREEN -> REFACTOR -> GAUNTLET -> EVIDENCE. O humano aprova o plano de teste antes do codigo existir e le um relatorio de evidencia depois, no lugar do diff.
- **Depende de:** o harness de codigo do usuario
- **Peso:** sem embedding
- **Nota:** O v6 atribuiu este repo a Andre Lindenberg. Andre Lindenberg postou a peca no LinkedIn; a autoria e' de AmazingAng.
- **Lido em:** 2026-08-16

#### PandaProbe

- **Repositório:** https://github.com/chirpz-ai/pandaprobe
- **Licença:** Apache-2.0 — ✅ OSI
- **Faz:** Observabilidade de agente: trace, eval e metricas (LangGraph, CrewAI, Claude Agent SDK), self-host ou cloud gerenciado. Ao contrario do old-coder (mesmo estagio), a evidencia aqui e' TRACING AO VIVO durante a execucao, nao um relatorio pos-hoc que substitui o diff.
- **Depende de:** FastAPI + Next.js + PostgreSQL 16 + Redis 7 + Celery; self-host gratuito, cloud com tier gratuito; 'LLM-as-a-judge' (avaliacao automatizada via LiteLLM) e' feature OPCIONAL que exige chave de LLM
- **Peso:** sem LLM no caminho · sem embedding
- **Lido em:** 2026-08-25

### Atacar

#### DeepTeam

- **Repositório:** https://github.com/confident-ai/deepteam
- **Licença:** Apache-2.0 — ✅ OSI
- **Faz:** Red team de LLM e de agente. 50+ vulnerabilidades e 20+ vetores, com familia `Agentic`: Goal Theft, Recursive Hijacking, Excessive Agency. Alinhado a OWASP LLM Top 10 e NIST AI RMF. O alvo e' um callback string->string.
- **Depende de:** OPENAI_API_KEY por padrao; modelo local possivel via DeepEval
- **Peso:** sem embedding · ⚠️ **custa dinheiro** (chave de API ou serviço pago)
- **Sobre a contagem de colisão:** Voltaram Genez-io/genezio-deepteam e fengjian686/deepteam. NAO entram na contagem de colisao: nao foi verificado se sao forks, e fork nao e' projeto independente. Sub-contar de proposito.
- **Lido em:** 2026-08-16

#### SILENTCHAIN AI

- **Repositório:** https://github.com/silentchainai/SILENTCHAIN
- **Licença:** proprietaria, source-visible — ⛔ não é open source
- **Faz:** Extensao de Burp Suite que roda analise passiva de trafego HTTP com IA procurando OWASP Top 10 e configuracao insegura, durante um pentest. Fonte visivel no GitHub, mas a licenca PROIBE redistribuicao sem permissao — exceto para a PortSwigger (BApp Store). Pelo menos dois outros repositorios redistribuem o mesmo codigo sob outro nome de organizacao, aparentemente violando essa mesma licenca.
- **Depende de:** Burp Suite Community/Professional 2025.2+, Java 21, um provedor de IA (Burp AI padrao sem configuracao, ou Ollama local, OpenAI, Claude, Gemini, Azure)
- **Colide com:** `IOCsec/silentchain` · `itsmadaraflow/silentchain`
- **Lido em:** 2026-08-25

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
| Nomes buscados | 25 |
| Com repositório canônico identificado e lido | 21 |
| **Sem** repositório canônico — e essa ausência **é** o achado | 3 |
| São paper, não repositório | 1 |
| **Clonados, instalados ou executados** | **0** |
| Têm repositório (ou cacho), mas nenhum dos dez estágios cobre o que fazem | 2 |

⚠️ Nenhum repositorio foi clonado, instalado ou executado. Numero de desempenho no campo `alegacao_do_autor` NAO foi medido por este censo. `sem_estagio_classificado` conta projetos com `estagio: null` — existem, tem repositorio (ou cacho sem canonico), mas nenhum dos dez estagios do ciclo de vida cobre o que fazem; aparecem na tabela de licenca, nao na secao 'Quem ja ocupa cada estagio'.

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

