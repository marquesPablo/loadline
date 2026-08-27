# The AI agent ecosystem census

> **This file is generated.** Do not edit it by hand — edit `censo/ecossistema.json` and run
> `python censo/gerar.py`. The verifier fails if the two fall out of sync.

<!-- measured: censo.gerado_em_dia=1 nature=relation on=2026-08-26 expires=never source=censo/gerar.py -->

An `awesome-*` list does not fail when it ages. This census fails.

**25 projects.** Every entry was read **on the repository's page**, never in the
post that cited it. What was not verified is written as not verified — never filled in by
plausibility, and never turned into a zero.

---

## The finding: 9 names do not identify a project

These names identify a **cluster of independent projects** — same name, same problem,
not citing each other:

| Name | Independent projects | Is there a canonical one? |
|---|---:|---|
| `AgentGuard` | **6** | ⛔ **no** |
| `Awesome A2A` | **6** | ⛔ **no** |
| `reverse-skill` | **6** | ⛔ **no** |
| `PicoAgents` | **4** | yes |
| `SILENTCHAIN AI` | **3** | yes |
| `agent-audit` | **3** | yes |
| `MateClaw` | **2** | yes |
| `deja-vu` | **2** | yes |
| `repowise` | **2** | yes |

Someone who hears *"install `AgentGuard`"* has no way to know which of the 6. **None of them lists the others.** This is not "there are many projects" — it is the same
project built 6 times in the dark, in the worst case of this reading.

> **Denominator, and it matters:** this is what **a search by name, on one day** returned.
> It is not a census of GitHub. **It is a floor, not a ceiling** — the real number is larger, never smaller.

---

## Who already occupies each stage

Ordered by an agent's life cycle, not by the alphabet — because what matters is **where
there is already a big owner** and where there is not.

| Stage | What it is | Who occupies it |
|---|---|---|
| **Understand the repository** | the agent reads the codebase before acting | repowise · Corbell |
| **Have capability** | where the skill the agent does not yet have comes from | AgentSkillOS · reverse-skill · awesome-agent-skills |
| **Have memory** | what survives the context wiped between sessions | deja-vu · mem9 |
| **Know what is what** | entities, relations and where each fact came from | Semantica · PANO |
| **Run the loop** | what runs the agent, with sandbox and subagents | DeerFlow · deepagents · PicoAgents · MateClaw |
| **Block at runtime** | the guard that decides what the agent does not do | AgentGuard · SkillSpector · agent-audit |
| **Prove it passed** | the evidence the human reads instead of the diff | old-coder · PandaProbe · agent-pd |
| **Attack** | who tries to break the agent on purpose | DeepTeam · SILENTCHAIN AI |
| **Learn from failure** | what turns failure into a fix | Harness-R1 |
| **The measured threat** | research, not a tool | Mind Viruses |

---

## The projects, with the license read at the source

The column that decides whether you can use it is the **third**, not the second. A license
that is not OSI does not become open source because the project calls itself open.

| Project | Where | License | Verdict | Names in the cluster |
|---|---|---|---|---:|
| **agent-audit** | [scadastrangelove/agent-audit](https://github.com/scadastrangelove/agent-audit) | not verified | ◻️ not verified | **3** |
| **agent-pd** | [varmabudharaju/agent-pd](https://github.com/varmabudharaju/agent-pd) | Apache-2.0 | ✅ OSI | 1 |
| **AgentGuard** | — | varies by project | ◻️ not verified | **6** |
| **AgentSkillOS** | [ynulihao/AgentSkillOS](https://github.com/ynulihao/AgentSkillOS) | MIT | ✅ OSI | 1 |
| **Awesome A2A** | — | varies by project | ◻️ not verified | **6** |
| **awesome-agent-skills** | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | MIT | ✅ OSI | 1 |
| **Corbell** | [Corbell-AI/Corbell](https://github.com/Corbell-AI/Corbell) | Apache-2.0 | ◻️ not verified | 1 |
| **deepagents** | [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | MIT | ◻️ not verified | 1 |
| **DeepSearcher** | [zilliztech/deep-searcher](https://github.com/zilliztech/deep-searcher) | Apache-2.0 | ✅ OSI | 1 |
| **DeepTeam** | [confident-ai/deepteam](https://github.com/confident-ai/deepteam) | Apache-2.0 | ✅ OSI | 1 |
| **DeerFlow** | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | MIT | ✅ OSI | 1 |
| **deja-vu** | [vshulcz/deja-vu](https://github.com/vshulcz/deja-vu) | MIT | ✅ OSI | **2** |
| **Harness-R1** | [DeepExperience/Harness-R1](https://github.com/DeepExperience/Harness-R1) | Apache-2.0 | ✅ OSI | 1 |
| **MateClaw** | [matevip/mateclaw](https://github.com/matevip/mateclaw) | Apache-2.0 | ✅ OSI | **2** |
| **mem9** | [mem9-ai/mem9](https://github.com/mem9-ai/mem9) | Apache-2.0 | ✅ OSI | 1 |
| **Mind Viruses** | `arXiv:2608.10218` | paper | ⛔ not open source | 1 |
| **old-coder** | [AmazingAng/old-coder](https://github.com/AmazingAng/old-coder) | MIT | ✅ OSI | 1 |
| **PandaProbe** | [chirpz-ai/pandaprobe](https://github.com/chirpz-ai/pandaprobe) | Apache-2.0 | ✅ OSI | 1 |
| **PANO** | [ALW1EZ/PANO](https://github.com/ALW1EZ/PANO) | CC BY-NC | ⛔ not open source | 1 |
| **PicoAgents** | [victordibia/designing-multiagent-systems](https://github.com/victordibia/designing-multiagent-systems) | not verified | ◻️ not verified | **4** |
| **repowise** | [repowise-dev/repowise](https://github.com/repowise-dev/repowise) | AGPL-3.0 | ⚠️ OSI, strong copyleft | **2** |
| **reverse-skill** | — | varies by project | ◻️ not verified | **6** |
| **Semantica** | [semantica-agi/semantica](https://github.com/semantica-agi/semantica) | MIT | ✅ OSI | 1 |
| **SILENTCHAIN AI** | [silentchainai/SILENTCHAIN](https://github.com/silentchainai/SILENTCHAIN) | proprietary, source-visible | ⛔ not open source | **3** |
| **SkillSpector** | [NVIDIA/skillspector](https://github.com/NVIDIA/skillspector) | Apache-2.0 | ✅ OSI | 1 |

**The three doors of a non-OSI license**, because treating them as one is the common mistake:

| What to do | Allowed? |
|---|---|
| **Run** the tool | ✅ yes — it is what the license grants |
| **Read the architecture as a specification** and reimplement it | ✅ yes — an API and a model are not the protected expression |
| **Copy the code into** your project | ⛔ no — the restriction carries across to all of your users |

---

## Each one's entry

### Understand the repository

#### Corbell

- **Repository:** https://github.com/Corbell-AI/Corbell
- **License:** Apache-2.0 — ◻️ not verified
- **Does:** A multi-repo code graph -> spec generation and review. Exposes the graph, embeddings and spec tools over MCP.
- **Depends on:** not verified
- **Read on:** 2026-08-16

#### repowise

- **Repository:** https://github.com/repowise-dev/repowise
- **License:** AGPL-3.0 — ⚠️ OSI, strong copyleft
- **Does:** Repo -> graph queryable by 10 MCP tools. AST of 19 languages + git history, Leiden communities, PageRank. The PR bot makes zero LLM calls and is deterministic: the same diff always gives the same review.
- **Depends on:** pip install; offline with Ollama; a paid commercial license is available
- **Weight:** no LLM in the path
- **Collides with:** `RepoWise/backend`
- **Read on:** 2026-08-16

### Have capability

#### AgentSkillOS

- **Repository:** https://github.com/ynulihao/AgentSkillOS
- **Paper:** `arXiv:2603.02176`
- **License:** MIT — ✅ OSI
- **Does:** An index of 90,000+ skills (the page now talks about 200,000+) with hybrid retrieval (LLM + capability tree), and composition as a DAG. The repo claims that pure embedding misses skills that look unrelated in vector space and are crucial.
- **Depends on:** Claude Code installed + an API key; NO MCP
- **Weight:** ⚠️ **costs money** (API key or paid service)
- **About the collision count:** AgentSkillOS/SkillAnything is from the same organization, and agentskills/agentskills is the SPECIFICATION maintained by Anthropic. Similar name, different project — it is not a collision and does not enter the count.
- **Read on:** 2026-08-16

#### awesome-agent-skills

- **Repository:** https://github.com/VoltAgent/awesome-agent-skills
- **License:** MIT — ✅ OSI
- **Does:** A curated index of 1497+ official Agent Skills (Anthropic, Google Labs, Vercel, Stripe, Cloudflare, Netlify, Trail of Bits, Sentry, Expo, Hugging Face, Figma) plus community skills, compatible with Claude Code, Codex, Antigravity, Gemini CLI, Cursor, GitHub Copilot, OpenCode, Windsurf.
- **Depends on:** none - it is a curated list, with no service of its own
- **Weight:** no LLM in the path · no embedding
- **Read on:** 2026-08-25

#### reverse-skill

- **Canonical repository:** ⛔ **does not exist** — see the collision section
- **License:** varies by project — ◻️ not verified
- **Does:** A reverse-engineering / pentest skill for Claude Code. THERE IS NO CANONICAL REPOSITORY: six distinct authors published under near-identical names.
- **Depends on:** varies by project
- **Weight:** no embedding
- **Collides with:** `zhaoxuya520/reverse-skill` · `P4nda0s/reverse-skills` · `meirm/reverse-engineering-skill` · `incogbyte/iOS-reverse-engineering-claude-skill` · `SimoneAvogadro/android-reverse-engineering-skill` · `vgrichina/re-skill`
- **Read on:** 2026-08-16

### Have memory

#### deja-vu

- **Repository:** https://github.com/vshulcz/deja-vu
- **License:** MIT — ✅ OSI
- **Does:** Indexes the sessions that code agents have already written to disk, across 17 harnesses, and serves them back over MCP, CLI and PreTool hooks.
- **Depends on:** none; a single Go binary
- **Weight:** no LLM in the path · no embedding
- **Author's claim** (not measured by this census): 84.9% hit@1 on LongMemEval-S; ~1.5 ms median over 3.5 GB
- **Collides with:** `acoyfellow/deja`
- **Read on:** 2026-08-16

#### mem9

- **Repository:** https://github.com/mem9-ai/mem9
- **License:** Apache-2.0 — ✅ OSI
- **Does:** Persistent memory shared across agents, sessions and machines (OpenClaw, Claude Code, OpenCode, Codex, Dify, Hermes Agent), with hybrid recall (semantic + keyword) and a visual dashboard. Unlike deja-vu (same stage), it uses an LLM and embedding in the path: smart-ingest extracts a fact with an LLM (default gpt-4o-mini) and hybrid recall depends on embedding.
- **Depends on:** a Go server + TiDB (or PostgreSQL); a hosted API is available; smart-ingest requires an LLM compatible with the OpenAI API
- **Weight:** ⚠️ **costs money** (API key or paid service)
- **Read on:** 2026-08-25

### Know what is what

#### PANO

- **Repository:** https://github.com/ALW1EZ/PANO
- **License:** CC BY-NC — ⛔ not open source
- **Does:** OSINT as a graph: entities (email, username, website, image, location, event, text) linked by transforms (Discovery, Correlation, Analysis, OSINT, Enrichment). Entities and transforms are explicitly pluggable: a base class + a file in the folder.
- **Depends on:** Python 3.11 + PySide6/Qt; Windows and Linux
- **Weight:** no embedding
- **License consequence:** Running it: allowed. Reading the entity/transform catalog as a specification and reimplementing it: allowed. Copying the code into an open source project: NO — the NC restriction carries across to all downstream users and takes the project out of open source.
- **Operational caveat:** The email transform requires a GHunt login against a target Google account. That TOUCHES A TARGET and requires engagement authorization, regardless of the license.
- **Read on:** 2026-08-16

#### Semantica

- **Repository:** https://github.com/semantica-agi/semantica
- **License:** MIT — ✅ OSI
- **Does:** A graph with W3C PROV-O on every fact, conflict detection before the merge, a temporal snapshot and deterministic reasoning (SPARQL/Datalog/Rete). Its own MCP server. Bills itself as 'The Open Source Palantir for AI Agents'.
- **Depends on:** a triple store (Oxigraph/Jena) or an LPG (Neo4j) AND a vector store
- **Weight:** no LLM in the path
- **Answers:** where the fact came from, and what we knew on that date
- **Does **not** answer:** whether what is written is still true today
- **Read on:** 2026-08-16

### Run the loop

#### deepagents

- **Repository:** https://github.com/langchain-ai/deepagents
- **License:** MIT — ◻️ not verified
- **Does:** Four middlewares on top of LangGraph: a virtual filesystem with allow/deny, SKILL.md/AGENTS.md on demand, a `task` tool for an ephemeral subagent, `interrupt_on` for human-in-the-loop.
- **Depends on:** the LangGraph runtime
- **Weight:** no embedding
- **Read on:** 2026-08-16

#### DeerFlow

- **Repository:** https://github.com/bytedance/deer-flow
- **License:** MIT — ✅ OSI
- **Does:** ByteDance's SuperAgent harness, 2.0 rewritten from scratch. Local/Docker/k8s/E2B sandbox, long memory, skills via SKILL.md, subagents with scoped context, an IM gateway.
- **Depends on:** Python 3.12 + Node 22; 8-16 GB RAM minimum; requires an LLM key
- **Weight:** ⚠️ **costs money** (API key or paid service)
- **Read on:** 2026-08-16

#### MateClaw

- **Repository:** https://github.com/matevip/mateclaw
- **License:** Apache-2.0 — ✅ OSI
- **Does:** A multi-agent orchestration harness (ReAct + Plan-and-Execute over a StateGraph) packaged as a single Spring Boot JAR, with skills, memory, MCP and multi-channel support. Multi-vendor failover across LLMs (DashScope, OpenAI, Anthropic, Gemini, DeepSeek, Ollama).
- **Depends on:** Java 21 + Spring Boot 3.5; PostgreSQL 16 or MySQL 8 in production; Ollama lets it run with no paid key
- **Weight:** ⚠️ **costs money** (API key or paid service)
- **Collides with:** `mateaix/mateclaw`
- **Read on:** 2026-08-25

#### PicoAgents

- **Repository:** https://github.com/victordibia/designing-multiagent-systems
- **License:** not verified — ◻️ not verified
- **Does:** A multi-agent framework built from scratch to TEACH — every component, from the reasoning loop to the orchestration, written to be read. 50+ examples per book chapter.
- **Depends on:** not verified
- **Weight:** no embedding
- **Collides with:** `borhen68/picoagents` · `dperezcabrera/pico-agent` · `kir-gadjello/picoagent-rnd`
- **Read on:** 2026-08-16

### Block at runtime

#### agent-audit

- **Repository:** https://github.com/scadastrangelove/agent-audit
- **License:** not verified — ◻️ not verified
- **Does:** A static, read-only forensic auditor ('no active defense — read-only analysis with consent prompts at every step') for local agent homes (Claude Code, Codex CLI, OpenClaw) and for repositories with an instruction surface (SKILL.md, MCP manifests, plugins). Runs imported detectors (among them Cisco PromptGuard, Gitleaks, NOVA, Cisco's YARA rules for MCP) plus native logic — 296 rules in all, according to the repository's own description. It produces deduplicated findings, normalized severity and a suggested patch; it never applies automatically. The focus is security (injection, exfiltration, credentials, privilege escalation) — it does not declare overlap/conflict detection BETWEEN two agents, which is loadline's V6 territory. Same family as SkillSpector (same stage): it decides what is safe to trust, it is not a runtime guard.
- **Depends on:** Python; the optional `--verify` calls an external LLM to re-check a finding; `yara-python` is optional for Cisco's 10 YARA rules
- **About the collision count:** Three independent projects published under the EXACT name `agent-audit`, without citing each other — the same pattern as AgentGuard/reverse-skill in this list. `scadastrangelove/agent-audit` is the most documented of the three (full README, 296 rules cited by name); the other two were not read in depth this round — only confirmed to exist.
- **Collides with:** `piiiico/agent-audit` · `HeadyZhang/agent-audit`
- **Read on:** 2026-08-26

#### AgentGuard

- **Canonical repository:** ⛔ **does not exist** — see the collision section
- **License:** varies by project — ◻️ not verified
- **Does:** A runtime guardrail for an agent. THERE IS NO CANONICAL REPOSITORY: the name identifies six independent projects that solve the same problem without citing each other.
- **Depends on:** varies by project
- **Collides with:** `GoPlusSecurity/agentguard` · `hidearmoon/agentguard` · `WhitzardAgent/AgentGuard` · `filipw/AgentGuard` · `JeongJaeSoon/agent-guard` · `bmdhodl/agent47`
- **Read on:** 2026-08-16

#### SkillSpector

- **Repository:** https://github.com/NVIDIA/skillspector
- **License:** Apache-2.0 — ✅ OSI
- **Does:** A security scanner for SKILL.md before you install it — 70 vulnerability patterns in 17 categories (prompt injection, data exfiltration, MCP tool poisoning, privilege escalation, among others). It is not a RUNTIME guard like the rest of this category: it decides what gets INSTALLED, not what the already-installed agent can do.
- **Depends on:** Python 3.12+; --no-llm runs only the static analysis; the second stage (semantic evaluation, OPTIONAL) accepts OpenAI/Anthropic/AWS Bedrock/NVIDIA/a local CLI agent
- **Read on:** 2026-08-25

### Prove it passed

#### agent-pd

- **Repository:** https://github.com/varmabudharaju/agent-pd
- **License:** Apache-2.0 — ✅ OSI
- **Does:** A tamper-evident audit log (hash-chain) for Claude Code: a hook that audits the main agent AND every subagent, correlating events across concurrent sessions and dynamic workflows. Six deterministic detectors (permission bypass, out-of-scope credential access, self-permissioning, disallowed tool, redundant work, off-task work) with cited evidence. 'Catch-and-report — it never blocks': it is a flight recorder, never a firewall.
- **Depends on:** Python 3.11+, PyYAML; the optional `pd judge` feature uses the Claude Code CLI (subscription already paid) or the metered Anthropic API
- **Weight:** no embedding
- **About the collision count:** It covers part of loadline's V6 territory (redundant/self-permissioning touch on inter-agent confusion detection) but at RUNTIME, not on a file at rest — loadline does not run the agent (LACUNAS.md #12), agent-pd only audits a running agent. It does not declare DESCRIPTION comparison between two agents (what V6 measures).
- **Read on:** 2026-08-26

#### old-coder

- **Repository:** https://github.com/AmazingAng/old-coder
- **License:** MIT — ✅ OSI
- **Does:** A skill, not a runtime. SPEC -> RED -> GREEN -> REFACTOR -> GAUNTLET -> EVIDENCE. The human approves the test plan before the code exists and reads an evidence report afterward, instead of the diff.
- **Depends on:** the user's code harness
- **Weight:** no embedding
- **Note:** v6 attributed this repo to Andre Lindenberg. Andre Lindenberg posted the piece on LinkedIn; the authorship is AmazingAng's.
- **Read on:** 2026-08-16

#### PandaProbe

- **Repository:** https://github.com/chirpz-ai/pandaprobe
- **License:** Apache-2.0 — ✅ OSI
- **Does:** Agent observability: traces, evals and metrics (LangGraph, CrewAI, Claude Agent SDK), self-hosted or managed cloud. Unlike old-coder (same stage), the evidence here is LIVE TRACING during execution, not a post-hoc report that replaces the diff.
- **Depends on:** FastAPI + Next.js + PostgreSQL 16 + Redis 7 + Celery; free self-host, cloud with a free tier; 'LLM-as-a-judge' (automated evaluation via LiteLLM) is an OPTIONAL feature that requires an LLM key
- **Weight:** no LLM in the path · no embedding
- **Read on:** 2026-08-25

### Attack

#### DeepTeam

- **Repository:** https://github.com/confident-ai/deepteam
- **License:** Apache-2.0 — ✅ OSI
- **Does:** LLM and agent red teaming. 50+ vulnerabilities and 20+ vectors, with an `Agentic` family: Goal Theft, Recursive Hijacking, Excessive Agency. Aligned with the OWASP LLM Top 10 and the NIST AI RMF. The target is a string->string callback.
- **Depends on:** OPENAI_API_KEY by default; a local model is possible via DeepEval
- **Weight:** no embedding · ⚠️ **costs money** (API key or paid service)
- **About the collision count:** Genez-io/genezio-deepteam and fengjian686/deepteam came up. They do NOT enter the collision count: it was not verified whether they are forks, and a fork is not an independent project. Undercounting on purpose.
- **Read on:** 2026-08-16

#### SILENTCHAIN AI

- **Repository:** https://github.com/silentchainai/SILENTCHAIN
- **License:** proprietary, source-visible — ⛔ not open source
- **Does:** A Burp Suite extension that runs passive AI analysis of HTTP traffic looking for the OWASP Top 10 and insecure configuration, during a pentest. Source is visible on GitHub, but the license FORBIDS redistribution without permission — except for PortSwigger (the BApp Store). At least two other repositories redistribute the same code under a different organization name, apparently violating that same license.
- **Depends on:** Burp Suite Community/Professional 2025.2+, Java 21, an AI provider (Burp AI by default with no configuration, or local Ollama, OpenAI, Claude, Gemini, Azure)
- **Collides with:** `IOCsec/silentchain` · `itsmadaraflow/silentchain`
- **Read on:** 2026-08-25

### Learn from failure

#### Harness-R1

- **Repository:** https://github.com/DeepExperience/Harness-R1
- **Paper:** `arXiv:2608.02276`
- **License:** Apache-2.0 — ✅ OSI
- **Does:** A 9B harness engineer (Qwen3.5-9B) trained by RL turns batches of the target agent's failures into validated, executable patches. Ready-made checkpoints on Hugging Face let you use it without training.
- **Depends on:** 8x NVIDIA H800 to train; a ready-to-use checkpoint
- **Weight:** no embedding
- **Author's claim** (not measured by this census): 44.3% -> 53.6% (+9.3 pp); +5.0 pp with a fine-tune of the target
- **The paper's own caveat:** one engineer is only significant against the target it was trained for
- **Read on:** 2026-08-16

### The measured threat

#### Mind Viruses

- **Canonical repository:** ⛔ **does not exist** — see the collision section
- **Paper:** `arXiv:2608.10218`
- **License:** paper — ⛔ not open source
- **Does:** NOT A TOOL. Anthropic research (Papadopoulos, Shah, Zimmerman, Lindsey; 2026-08-10) showing that an idea planted in one agent propagates to the others. Two measured scenarios: a small team of agents on a shared code project, and a chain of agents with the context wiped between sessions.
- **Depends on:** none — it is a paper
- **Weight:** no embedding
- **Main finding:** A short warning in the agent's system prompt confers near-total immunity. A harmful payload propagates less than a benign one, but it still works sometimes.
- **Limit of this reading:** Only the abstract was read. The exact propagation channel and the measured persistence are in the body of the paper and were NOT opened. The exact wording of the warning is not in the abstract.
- **Read on:** 2026-08-16

---

## The denominator of this reading

Every surface that counts declares **how many** it counted from. Without that, a filter that
skips silently produces a plausible, empty answer.

| | |
|---|---:|
| Names searched | 25 |
| With a canonical repository identified and read | 21 |
| **Without** a canonical repository — and that absence **is** the finding | 3 |
| Are a paper, not a repository | 1 |
| **Cloned, installed or run** | **0** |
| Have a repository (or cluster), but none of the ten stages covers what they do | 2 |

⚠️ No repository was cloned, installed or run. Performance numbers in the `alegacao_do_autor` field were NOT measured by this census. `sem_estagio_classificado` counts projects with `estagio: null` — they exist, they have a repository (or a cluster with no canonical one), but none of the ten life-cycle stages covers what they do; they show up in the license table, not in the 'Who already occupies each stage' section.

**What this census does NOT measure, declared:**

- **Whether the project works.** Nothing here was run. Performance is the author's claim.
- **Whether it still exists today.** That is what each seal's `expires=` is for — no offline
  probe reaches the truth of the world out there, and confusing the two would be saying that
  a coherent JSON is a true fact.
- **How many projects really exist.** The collision count is the floor of one search.
- **Whether the license changed after the reading date.** Each entry's `lido_em` field is
  the date the page was opened, not today's date.

---

## How to contribute an entry

1. Open the **repository's page** — not the post, not the list, not the screenshot. This
   house's memory records the cost of attributing by the packaging: one project in this
   census was credited to whoever posted on LinkedIn, not to whoever wrote the code.
2. Fill in `censo/ecossistema.json`. **`nao_verificado` is a legitimate value** and never
   becomes zero.
3. Run `python censo/gerar.py` and `python -m loadline .`. If either one fails, the entry
   is not ready yet.

