# Operação 4 · `dependencia-com-veredito`

> Alguém rodou `npm i` numa sexta-feira. A dependência entrou, o `package.json` mudou, o PR foi
> aprovado. **A licença dela ninguém leu** — e a tabela de licenças do repositório, escrita com
> carinho há dois anos, continua completa, correta e desatualizada.

## A dor

Toda empresa que publica software tem uma planilha, um `NOTICE`, um `licencas.md` ou um slide onde
está escrito o que cada dependência obriga. **Nenhum desses arquivos reprova quando uma dependência
nova entra sem passar por ele.** O manifesto é escrito pela máquina toda vez que alguém instala; a
tabela é escrita por um humano que foi ler. As duas divergem por construção.

E a divergência tem consequência real: `CC BY-NC` e `AGPL-3.0` são as duas licenças que mais
aparecem descritas como *"open source"* por quem só leu o README. Uma não é open source; a outra é, e
mesmo assim alcança quem usa em rede.

## O que esta operação instala

Oito sondas que medem a **distância entre o manifesto e a tabela** — nunca a licença em si:
<!-- aferido: operacao.dependencia.sondas=8 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/dependencia-com-veredito/sondas.py -->

| Métrica | O que recomputa | Natureza |
|---|---|---|
| `deps.declaradas` | dependências distintas nos manifestos | contagem |
| **`deps.sem_veredito`** | **estão no manifesto e não estão na tabela** — ninguém olhou | **relação** |
| **`deps.veredito_orfao`** | **estão na tabela e saíram do manifesto** — julgamento envelhecido | **relação** |
| `deps.osi` · `deps.copyleft_forte` · `deps.nao_osi` · `deps.proprietarias` | por veredito, só as que ainda estão no manifesto | contagem |
| `deps.nao_verificado` | alguém olhou e **não conseguiu decidir** | contagem |

A última linha é a que quase todo mundo erra. **`nao_verificado` e `sem_veredito` não são a mesma
coisa**, e somá-las apaga a única informação que importa: se alguém olhou. Uma é um humano que foi
lá, tentou e não decidiu — isso é dado. A outra é ninguém ter ido.

## O ajuste

**Um campo.** No topo do `sondas.py`:

```python
TABELA_DE_VEREDITOS = "licencas.md"
```

Aponte para onde a sua tabela mora. Qualquer arquivo de texto serve. A única convenção é: **o nome
da dependência vai entre crases**, e a linha contém um dos sete vereditos do vocabulário fechado.

```markdown
| Dependência | Licença | Veredito |
|---|---|---|
| `react` | MIT | osi |
| `some-agpl-lib` | AGPL-3.0 | osi_copyleft_forte |
| `pacote-obscuro` | ? | nao_verificado |
```

**Não tem tabela?** Crie o arquivo vazio. A sonda passa a dizer quantas dependências ninguém olhou —
que é a primeira coisa útil que ela tem a dizer. Arquivo ausente **estoura** e vira `SEM_PROVA`, de
propósito: *não dá para conferir* nunca deve virar *zero*.

## O que você vê

```console
deps.declaradas          = 5
deps.sem_veredito        = 1
deps.veredito_orfao      = 1
deps.osi                 = 3
deps.copyleft_forte      = 1
deps.nao_verificado      = 0
```

> *Execução sobre o repositório sintético de teste desta operação, em 2026-08-21. Exemplo
> executado, não asserção sobre o repositório de quem lê.*

Cinco dependências, quatro com veredito, **uma que entrou e ninguém olhou**, e **um veredito sobre
um pacote que já saiu**. As duas últimas são as que a tabela sozinha nunca ia contar.

## Como rodar

```console
$ cp operacoes/dependencia-com-veredito/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo
$ python -m aferido .
```

E cole na sua tabela de licenças:

```markdown
Toda dependência deste manifesto tem veredito de licença escrito, e nenhum veredito sobrevive à
dependência que ele julgava.
<!-- aferido: deps.sem_veredito=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=manifesto -->
<!-- aferido: deps.veredito_orfao=0 natureza=relacao em=AAAA-MM-DD vence=30d fonte=manifesto -->
```

## Os dois agentes, e por que são dois

| Agente | Pergunta | Rede |
|---|---|---|
| `curador-de-dependencia` (`agente.toml` daqui) | **quais das minhas ninguém olhou?** | não |
| `revisor-de-licenca` (`forja/exemplos/`) | **esta aqui pode entrar?** | sim, com cerca declarada |

O primeiro acha o buraco sem sair da máquina. O segundo fecha um buraco por vez, e para isso precisa
abrir a página do repositório — por isso ele declara `dominios_permitidos`, e por isso a forja o
recusaria se não declarasse.

```console
$ python -m forja operacoes/dependencia-com-veredito/agente.toml
$ python -m forja forja/exemplos/revisor-de-licenca.toml
```

## As quatro coisas que esta operação não faz

1. **Nada aqui LÊ licença.** A verdade sobre a licença de um pacote está na página dele, e nenhuma
   sonda offline a alcança. A tabela é o que um humano escreveu depois de ir olhar; o `vence=` é o
   que obriga alguém a ir olhar de novo.
2. **Ela não vê dependência transitiva.** Um MIT que puxa um AGPL continua puxando um AGPL, e o
   manifesto não conta isso. Esta operação mede o que está declarado, e diz que é isso que ela mede.
3. **Ela não julga se o SEU projeto é comercial** — que é a pergunta que decide o caso `NC`, e ela é
   sua.
4. **Ela não separa as três portas.** Rodar a ferramenta, ler a arquitetura dela como especificação
   e copiar o código para dentro são permissões diferentes, e um veredito só não distingue as três.
   Quem precisa dessa distinção usa o `revisor-de-licenca`, que a faz explicitamente.
