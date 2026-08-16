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

As quatro primeiras existem, maduras, com dono grande. A quinta não tinha ninguém.

---

## Os cinco vereditos

| | Significa | O que fazer |
|---|---|---|
| `VALE` | escrito == medido, dentro do prazo | nada |
| `DERIVOU` | escrito != medido | **depende da natureza — ver abaixo** |
| `VENCIDO` | passou do `vence`, mesmo batendo | reconferir e resselar |
| `SEM_PROVA` | não há sonda para a métrica | escrever a sonda, ou tirar o número |
| `CONGELADO` | histórico declarado, com motivo | nada; não se recomputa |

<!-- aferido: nucleo.vereditos=5 natureza=relacao em=2026-08-16 vence=nunca fonte=aferido/__main__.py -->

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

Não há passo dois. **Zero dependências** — só a stdlib do Python.

<!-- aferido: nucleo.dependencias=0 natureza=relacao em=2026-08-16 vence=nunca fonte=requisitos.txt -->
<!-- aferido: nucleo.modulos=6 natureza=contagem em=2026-08-16 vence=nunca fonte=aferido/ -->

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

Doze dos quinze têm repositório canônico identificado e lido. Dois não têm canônico nenhum — e essa
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

## Licença

MIT. De propósito, e a escolha é derivada: se o critério é que **tanto o bilionário quanto a tia da
limpeza** possam ler, entender e aplicar, então uma licença que exclui um dos dois já falhou no
critério. `NC` exclui o bilionário. Copyleft forte exclui quem não pode abrir. **MIT não exclui
ninguém.**
