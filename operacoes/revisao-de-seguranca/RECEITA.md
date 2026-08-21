# Operação 8 · `revisao-de-seguranca`

> O scanner devolveu 400 achados. **Quantos deles alguém consegue conferir sem gastar vinte
> minutos?**
> Se a resposta for *"depende do achado"*, o relatório inteiro vai ser ignorado — não por
> negligência, por aritmética: 400 × 20 minutos é mais tempo do que qualquer equipe tem, e o
> arquivo vira um anexo que ninguém abre.

## A dor

Um achado de segurança que ninguém consegue conferir **não é um achado: é uma suspeita cara.**

O que falta quase sempre é a mesma coisa, e é pouca:

- **onde** — `caminho/arquivo.py:142`, não *"na camada de autenticação"*;
- **sob qual classificação, com a versão do catálogo** — `CWE-89` sem versão é um endereço sem data;
- **como conferir** — o passo que confirma **ou derruba**. Um achado que não pode ser derrubado
  também não pode ser confirmado: só pode ser acreditado, e isso não pertence a um relatório
  técnico;
- **o veredito** — porque um achado sem ressalva é lido como confirmado por quem tem pressa, e é
  assim que um falso positivo chega ao cliente.

## Por que três agentes, e não um

Esta operação instala **três** specs, e a divisão não é organizacional:

```
revisor-de-seguranca  →  classificador-de-achado  →  redator-de-relatorio
       ACHA                    dá ENDEREÇO                 ESCREVE
   (nunca conserta)         (nunca aproxima)         (nunca envia)
```

Um agente que acha, classifica e redige num passo só produz um texto em que **ninguém consegue
separar o que foi VISTO do que foi INFERIDO.** As três frases saem com a mesma voz e a mesma
confiança, e o leitor perde a única informação que decide o que fazer com cada uma.

Separados, cada passo tem um veredito próprio, e um erro no primeiro não ganha a assinatura dos
outros dois. É também o que impede o defeito mais comum de esteira: o redator "encontrar" um achado
novo enquanto escreve — um achado que nunca passou por veredito e entra no relatório com o peso dos
que passaram.

**E só um dos três tem `Write`.** O redator escreve em `relatorios/` e a cerca emitida pela forja
**nega** qualquer outro caminho — não como pedido de boa-fé dentro do prompt, mas como um processo
que roda antes da ferramenta e responde `deny`.

## O que esta operação instala

Oito sondas sobre a sua pasta de achados:
<!-- aferido: operacao.revisao.sondas=8 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/revisao-de-seguranca/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `seguranca.achados` · `seguranca.confirmados` | o tamanho do lote e quantos passaram | contagem |
| **`seguranca.sem_framework`** | **achados sem identificador — só adjetivo** | **relação** |
| **`seguranca.sem_versao_de_framework`** | **cita o catálogo e não diz qual versão** | **relação** |
| **`seguranca.sem_caminho_linha`** | **sem endereço: quem lê tem de procurar** | **relação** |
| **`seguranca.sem_passo_de_verificacao`** | **não dá como derrubar o achado** | **relação** |
| **`seguranca.sem_veredito`** | **será lido como confirmado por quem tem pressa** | **relação** |
| **`seguranca.acionaveis`** | **os cinco requisitos ao mesmo tempo** | **relação** |

**`seguranca.acionaveis` é o único número daqui que alguém de fora entende**, e é o que vai no
resumo. Ele **não é a soma** das outras: um achado que falha em dois requisitos é contado uma vez
aqui e duas lá. As outras seis são o diagnóstico de **qual** conserto falta.

⚠️ **Estas sondas não procuram vulnerabilidade.** Elas medem se os achados que você já tem são
acionáveis. Quem procura é o primeiro agente da esteira, e nenhuma sonda offline substitui a leitura
do código.

## O ajuste

**Um campo**, no topo do `sondas.py`:

```python
PASTA_DE_ACHADOS = "achados"   # um arquivo .md por achado
```

## Como rodar

```console
$ cp operacoes/revisao-de-seguranca/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ PYTHONPATH=/caminho/para/aferido python -m aferido .
```

```console
REPROVA   achados/README.md:5  seguranca.acionaveis: escrito=400 medido=63
          → natureza=relacao — PARE e investigue.
```

**Esse é o relatório de verdade.** Não são 400 achados: são 63 que alguém consegue conferir e 337
que vão ser ignorados. Saber a diferença muda o que a equipe faz na segunda-feira.

## A terceira lista

Todo relatório publica o que passou e o que falhou. **Quase nenhum publica o que nunca foi olhado**
— e é essa terceira lista que decide se as outras duas significam alguma coisa.

Por isso o redator escreve a seção *"o que esta revisão NÃO olhou"* **mesmo quando o cliente não
pede**. Um relatório sem ela é lido como cobertura total, e alguém toma decisão de risco com base
numa cobertura que ninguém prometeu.

## Zero achados NÃO é «está limpo»

Se a pasta existir e estiver vazia, a sonda **estoura** com o erro escrito, em vez de devolver zero.

*"Não olhei"* e *"olhei e não há"* dizem coisas opostas, e confundi-las é a forma mais barata de
inventar um atestado de segurança. Um `0` num relatório, sem denominador ao lado, é lido como a
segunda quando quase sempre é a primeira.

## O que esta operação NÃO faz

1. **Não toca em alvo.** Os três agentes leem código parado. Nenhum tem `Bash`, nenhum tem rede.
   Recon contra alvo é outra família inteira, exige autorização de engajamento com validade, e não
   está nesta pasta.

2. **Não mede exploitabilidade nem impacto de negócio.** O que é catastrófico num sistema é
   irrelevante noutro, e nenhum dos três conhece o seu contexto.

3. **Não diz que o código está seguro.** A ausência de achado nunca foi prova de ausência de
   vulnerabilidade — e o falso negativo é o erro mais caro desta operação, justamente porque não
   aparece em lugar nenhum.

4. **Não envia nada.** O redator escreve em `relatorios/` e para. Sair da máquina é decisão humana,
   e nunca a última linha de um agente.
