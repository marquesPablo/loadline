# loadline

**Você tem mais de um agente de IA no seu repositório. Ninguém olha o conjunto.**

Existe ferramenta para revisar **um** `AGENTS.md`. Não existe nenhuma que leia a sua pasta
`.claude/agents/` inteira e responda a pergunta que só aparece a partir do terceiro agente:

> *Dois destes disputam o mesmo despacho? Algum alcança o disco todo? O que nenhum deles cobre?*

Um comando, sem configurar nada, sem escrever nada. Clone, e rode contra o roster de exemplo que
vem junto — ou troque o caminho pelo do seu projeto:

```console
$ git clone https://github.com/marquesPablo/loadline && cd loadline
$ python -m forja exemplos/roster-de-exemplo
vistoria · exemplos\roster-de-exemplo\.claude\agents · em 2026-08-22
==========================================================================
Li 4 agente(s).

⛔ A FRONTEIRA ESTÁ SÓ NA PROSA                                     4 de 4
     auditor-de-seguranca.md            pede rede e não declara com quem pode falar
     redator-de-changelog.md            pede escrita e não declara onde pode escrever
     revisor-de-pr.md                   pede escrita e não declara onde pode escrever
     revisor-de-pr.md                   pede rede e não declara com quem pode falar
     tradutor.md                        pede escrita e não declara onde pode escrever
     → "escrevo num caminho só" e "só consulto a documentação" são intenção.
       Nenhum runtime lê prosa: sem declaração, o agente alcança tudo o que o
       harness alcança.

⛔ SE CONFUNDEM ENTRE SI                                         1 par(es)
     auditor-de-seguranca.md × revisor-de-pr.md    67% das palavras em comum
     → descrições disputando o mesmo despacho, e nenhum dos dois nomeia o outro.
       O conserto é nominal: cada um cita o irmão no que NUNCA faz.

--------------------------------------------------------------------------
4 agente(s) · 7 tipo(s) de defeito · 17 de 24 declarações ausentes

REPROVA                                                        (exit 1)
```

No seu projeto, é a mesma linha com outro caminho — ou nenhum caminho, de dentro dele:

```console
$ python -m forja /caminho/do/seu/projeto
```

**Zero dependência.** Só a biblioteca padrão do Python 3.10+. Sem LLM, sem chave de API, sem
serviço. Um verificador que depende de um modelo não é um verificador — é uma segunda opinião.

<!-- measured: nucleo.dependencias=0 natureza=relacao em=2026-08-22 vence=nunca fonte=pyproject.toml -->

---

## Para quem isto é

**É para você se** você tem três ou mais subagentes escritos à mão, já não lembra de cor qual faz
o quê, e nenhum deles tem uma cerca que o runtime realmente leia.

**Não é para você se** você tem um agente só. Com um, você não tem um sistema — tem um arquivo, e
um arquivo você lê.

---

## Os sete achados

Os cinco primeiros são sobre **um** agente. Os dois últimos só existem porque há **mais de um**, e
são a razão de isto existir.

<!-- measured: vistoria.achados=7 natureza=relacao em=2026-08-22 vence=nunca fonte=forja/vistoria.py -->

| | O que ele acha | Por que dói |
|---|---|---|
| `V1` | não diz o que **nunca** faz | o orquestrador despacha por tema, e o tema de dois agentes se parece muito mais do que o trabalho deles |
| `V2` | não diz **quando** usar | agente sem gatilho existe no disco e nunca no despacho |
| `V3` | a fronteira está **só na prosa** | nenhum runtime lê prosa; sem declaração, ele alcança tudo o que o harness alcança |
| `V4` | não diz **o que não cobre** | silêncio é lido como cobertura, e o que faltou vira "não tem" |
| `V5` | nada confere a **resposta** | você testa se ele rodou, nunca se ele acertou |
| `V6` | **dois se confundem** | duas descrições disputando o mesmo despacho, e nenhuma nomeia a outra |
| `V7` | **herda toda ferramenta** | `tools:` ausente não quer dizer nenhuma: nos harnesses de hoje quer dizer TODAS |

Todo achado é a **ausência de uma declaração legível por máquina** — nunca um julgamento sobre a
qualidade do agente. Um agente excelente cuja fronteira está escrita em prosa aparece aqui, e deve
aparecer. Prosa não é cerca; é intenção.

**E a vistoria olha os arquivos irmãos.** Se a cerca está num hook ao lado e não no texto do
prompt, ela conta — senão a ferramenta acusaria exatamente o que ela mesma emite.

---

## Ele não para no alarme

Um relatório dizendo que você está mal não é um trabalho feito. O segundo comando escreve.

```console
$ python -m forja --adotar
escrevi 4 spec(s) em build/specs/ — uma por agente lido:
  ✓ build/specs/revisor-de-pr.toml
  …
```

Cada spec sai **preenchida com o que já estava no seu arquivo**, e com um `?` em cada buraco que
já existia e ninguém tinha onde ver. Você preenche os `?` — e aí:

```console
$ python -m forja build/specs/revisor-de-pr.toml
  ✓ .claude/agents/revisor-de-pr.md      seu subagente, agora com fonte
  ✓ AGENTS.md                            o formato que harness nenhum é dono
  ✓ revisor-de-pr.system.md              system prompt cru, para SDK
  ✓ hooks/cerca_revisor-de-pr.py         ⬅ CÓDIGO QUE NEGA
  ✓ golden/revisor-de-pr.md              ⬅ a pergunta que confere a RESPOSTA
  ✓ LACUNAS.md                           ⬅ o que ele não mede
  ✓ RECEITA.md                           de que spec saiu o quê, e quando
```

**Os três marcados não são texto para o modelo ler.** O hook é um processo `PreToolUse` que lê o
evento e responde `deny` antes de a ferramenta rodar. Prompt bonito sem esses três é um agente sem
gate com uma descrição melhor.

E o ciclo fecha: rode a vistoria no que saiu da forja, e ele passa — `0 de 6 declarações ausentes`.

### A forja se recusa a compilar oito coisas

Ausente e vazio significam a mesma coisa, e as duas barram — porque tratar campo ausente como
permissivo é como toda cerca vira porta dos fundos. **Toda recusa traz o conserto escrito**: uma
recusa que não diz a saída treina quem a lê a contorná-la.

| | Recusa quando | | Recusa quando |
|---|---|---|---|
| `R1` | pede rede sem dizer com quem fala | `R5` | golden set vazio |
| `R2` | pede escrita sem dizer onde escreve | `R6` | golden tirado de dentro da saída do agente |
| `R3` | não diz o que nunca faz | `R7` | toca alvo externo sem autorização |
| `R4` | não diz o que não cobre | `R8` | slug que vira nome de arquivo inválido |

<!-- measured: forja.recusas=8 natureza=contagem em=2026-08-22 vence=nunca fonte=forja/spec.py -->

---

## Instalação

```console
$ git clone https://github.com/marquesPablo/loadline && cd loadline
$ python -m forja /caminho/do/seu/projeto
```

Não há segundo passo.

---

## CI — sem infra própria, sem Docker, só o runner de quem adota

Uma Action composite roda `forja`, `placar` e `loadline` inteiros no seu próprio runner —
nenhuma chamada sai para fora dele.

```yaml
# .github/workflows/loadline.yml
name: loadline
on: [pull_request]
jobs:
  loadline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: marquesPablo/loadline@main
        with:
          html: 'true'          # escreve loadline-{forja,placar,loadline}.html
          falhar-em: 'nenhuma'  # default: diagnóstico, não quebra o build
```

`falhar-em` liga o gate quando você decidir que está pronto — `'forja'`, `'placar,loadline'`, ou
qualquer combinação das três. Com `html: 'true'`, os três relatórios sobem como artefato do job
(`loadline-report`); um link para eles, no seu README, é a evidência real que falta para um badge
não ser só um número que promete sem provar:

```markdown
[📄 relatório loadline](LINK-PARA-O-ARTEFATO-OU-PÁGINA-QUE-VOCÊ-HOSPEDAR)
```

**Por que não um badge pronto de `shields.io`.** Um badge que só afirma "passou", sem link
clicável para a evidência que o gerou, já foi proposto para este projeto e **retirado**: é
gameável do mesmo jeito que qualquer selo verde sem prova atrás. O link acima aponta para o
`--html` de verdade — a mesma rodada que o badge estaria resumindo — porque um verde sem clique
não é diferente de uma afirmação de cabeça.

⚠️ **A Action ainda não está no GitHub Marketplace** (exige repositório público), e este
repositório é privado hoje — o `uses: marquesPablo/loadline@main` acima passa a funcionar de fora
quando os dois mudarem. Escrever e testar a Action local não depende de nenhum dos dois.

---

## O que isto NÃO faz

- **Não julga a qualidade** do seu agente. Ele responde *"esta declaração existe?"*, nunca *"esta
  era a declaração certa?"*. Isso é julgamento, e continua sendo seu.
- **Não lê frontmatter multi-linha.** Ele lê `chave: valor` de uma linha, que é o que os harnesses
  de hoje escrevem.
- **O `V6` compara palavras, não sentido.** Ele acha `revisor` × `auditor`, que repetem as mesmas
  palavras. Ele **não acha** `pesquisador` × `investigador` — mesma vaga, escrita com sinônimos,
  17% de palavras em comum. Achar sinônimo exigiria um modelo, e aí isto deixaria de rodar offline.
  **Ele é um piso, nunca um teto:** silêncio dele não prova que o seu roster não se confunde.
- **O limiar do `V6` foi escolhido** — 30% de palavras em comum — e não medido. O número está no
  código com o motivo ao lado, em vez de enterrado num `if`.
- **Não roda o seu agente.** Nada aqui sabe se ele responde bem; só se existe alguma coisa capaz de
  dizer que ele respondeu mal.

As quinze lacunas declaradas estão em [`LACUNAS.md`](LACUNAS.md).

<!-- measured: nucleo.lacunas=15 natureza=contagem em=2026-08-24 vence=nunca fonte=LACUNAS.md -->

Toda ferramenta publica o que passou e o que falhou; quase nenhuma publica **o que nunca olhou**, e
é essa terceira lista que decide se um verde significa alguma coisa.

---

## Quem já faz parecido

Conferido em 2026-08-20, lendo a página pública de cada um. Nenhum foi clonado ou executado.

| Projeto | O que faz | Onde ele para |
|---|---|---|
| [`agents-lint`](https://github.com/giacomo/agents-lint) | caminho que não existe, script morto, pacote deprecado, seção faltando | um arquivo por vez; não enxerga o roster |
| `AgentLint` | 33 checks em cinco eixos, sobre um `AGENTS.md` | auditoria estrutural e estilística de um arquivo |
| `AgentLinter` | clareza, estrutura, segurança, memória | qualidade do prompt, não fronteira executável |
| [`drift`](https://www.driftdev.sh/) | ancora spec markdown no código e falha o CI | documento × código, e nunca agente × agente |

**Todos lintam um arquivo. Nenhum lê o conjunto, e nenhum emite o gate.** É essa a diferença, e é a
única que importa aqui.

---

## Também mora neste repositório

- [`loadline/`](loadline/) — a mesma régua aplicada ao **texto**: uma afirmação escrita ganha prazo de
  validade e uma sonda que a recomputa, e a sonda **não pode ler a fonte que produziu o número**.
  `python -m loadline .`
- [`operacoes/`](operacoes/) — nove trabalhos prontos que rodam no seu repositório sem configuração.
  <!-- measured: operacoes.total=9 natureza=contagem em=2026-08-24 vence=nunca fonte=operacoes/ -->
- [`censo/`](censo/) — um registro do ecossistema de agentes de IA onde cada entrada **vence**.
- [`blind/`](blind/) — a fronteira que uma varredura ingênua atravessa em silêncio: junction,
  symlink de diretório, e a regra de `.gitignore` que esconde mesmo de quem atravessa a fronteira
  estrutural. `python -m blind .`
- [`placar/`](placar/) — as sete portas de "Would you ship this AI agent?" (OBJECTIVE · IDENTITY ·
  AUTHORITY · FAILURE · APPROVAL · TRACEABILITY · CONTAINMENT), cada uma conferida com evidência de
  disco, nunca opinião. Reprovar IDENTITY, AUTHORITY ou CONTAINMENT é NO-GO. `python -m placar .`
  <!-- measured: placar.portas=7 natureza=contagem em=2026-08-23 vence=nunca fonte=placar/portas.py -->

---

## Os controles negativos

```console
$ python autoteste.py
81 checks declarados · 81 executados · 0 fora do denominador
PASSOU
```

<!-- measured: nucleo.checks=81 nucleo.fora=0 natureza=contagem em=2026-08-24 vence=nunca fonte=autoteste.py -->

**Cada check reintroduz o defeito que ele existe para pegar.** Um check que só confirma o caminho
feliz passa igual se o mecanismo for removido — ele não prova nada, e o custo dele é dar a alguém a
sensação de estar coberto. Foi um deles que descobriu, enquanto este texto era escrito, que apontar
a forja para um caminho inexistente devolvia *"sua spec está errada"* em vez de *"eu não li nada"*.

---

## Licença

MIT. Se o critério é que qualquer pessoa possa ler, entender e aplicar, uma licença que exclui
alguém já falhou no critério.
