# Operação 2 · `readme-que-nao-mente`

> *"Mais de 200 testes."* Quem contou? Quando? A frase está no `README.md` desde a v0.3.
> Hoje são 84, porque a suíte foi dividida em dois pacotes e metade foi para o outro repositório.
> **O número não errou de repente. Ele nunca mais foi conferido.**

## A dor

Todo README afirma quantidade. Endpoints, testes, dependências, linguagens, contribuidores, tamanho.
Nenhuma dessas frases tem prazo de validade, nenhuma reprova quando envelhece, e a que envelheceu
continua com a mesma cara de certa — que é o que a torna pior que uma frase ausente.

## O que esta operação instala

Treze sondas genéricas. Elas funcionam em qualquer repositório, sem uma linha de configuração, e
nenhuma delas lê `.md` nenhum — todas leem código, manifesto ou `git`.

| Métrica | O que recomputa |
|---|---|
| `repo.arquivos` · `repo.fontes` · `repo.linhas` | tamanho real, fora de `node_modules`, `venv`, `dist`, `build`… |
| `repo.linguagens` | extensões de linguagem distintas |
| `repo.testes` · `repo.arquivos_de_teste` | funções de teste pela convenção de Python, Go, JS/TS, Rust, Java |
| `repo.dependencias` · `repo.dependencias_dev` | de `pyproject.toml`, `package.json`, `requirements.txt`, `go.mod` |
| `repo.workflows` | arquivos em `.github/workflows/` |
| `repo.pendencias` | `TODO` / `FIXME` / `XXX` / `HACK` |
| `repo.maior_arquivo` | linhas do maior arquivo — o número que ninguém quer ver |
| `repo.contribuidores` · `repo.commits` | de `git`, não de arquivo |

<!-- aferido: operacao.readme.sondas=13 natureza=contagem em=2026-08-21 vence=nunca fonte=operacoes/readme-que-nao-mente/sondas.py -->

## O ajuste

**Nenhum.** Se o seu projeto tem uma pasta de build com nome incomum, acrescente-a a `_REPO_IGNORAR`
no topo do `sondas.py`. É a única linha que alguém precisa tocar, e só nesse caso.

## Como rodar — os 60 segundos

```console
$ cp operacoes/readme-que-nao-mente/sondas.py  /caminho/do/seu/repo/sondas.py
$ cd /caminho/do/seu/repo

$ python -m aferido .            # o que ninguém consegue conferir aqui
$ python -m aferido . --selar    # escreve o selo de cada um, para você colar
```

O `--selar` escreve tudo como `arbitrado:` — *este número foi escolhido, não medido* — porque
ninguém mediu nada ainda. **Onde houver sonda com o mesmo nome, troque `arbitrado:` por `aferido:`.**
Essa troca é a operação inteira: o número deixa de ser um palpite anotado e passa a ser recomputado
a cada execução.

Não sabe quais têm sonda? A ferramenta diz:

```console
$ python -m aferido . --sondas
sondas carregadas de: sondas.py
  repo.arquivos                ← arquivos fora das pastas de dependência e de build
  repo.commits                 ← `git rev-list --count HEAD`
  repo.contribuidores          ← autores distintos em `git shortlog -sne --all`
  ...
```

## O que você vê

```console
$ python -m aferido .
DERIVOU   README.md:8   repo.testes: escrito=200 medido=84   → resele: contagem anda quando alguém escreve
VENCIDO   README.md:11  repo.dependencias: escrito=7 medido=7
          → reconfira e resele — ninguém olha isto há 214 dias (prazo: 90d)
```

> *Exemplo escrito à mão para ilustrar os dois vereditos. Não é saída de um repositório real —
> e a diferença entre ilustrar e medir é a razão de este aviso existir.*

Repare no segundo: **o número está certo e mesmo assim reprova.** Um número que ninguém reconfere há
sete meses é um número que ainda não errou — não um número verificado. É esse o ponto do projeto
inteiro, e este é o exemplo mais barato dele.

## O agente

`agente.toml` compila o `auditor-de-afirmacao`, que responde a pergunta que vem depois da terceira
lista: **para cada afirmação que ninguém confere, existe sonda pronta, ou ela precisa virar
`arbitrado:`, ou o número deveria sair do texto?** São três destinos diferentes, e escolher errado é
como um repositório acumula selo decorativo.

```console
$ python -m forja operacoes/readme-que-nao-mente/agente.toml
```

## As três coisas que esta operação não faz

1. **Contagem não é qualidade.** `repo.testes` conta o que *parece* teste pela convenção da
   linguagem. Ela não sabe se o teste testa alguma coisa — e um repositório pode dobrar esse número
   sem ficar mais seguro.
2. **`0` em `repo.dependencias` diz "não declara dependência em manifesto que eu leia"**, não "não
   tem dependência". Quatro ecossistemas são lidos; um quinto passaria como zero. Se o seu for o
   quinto, escreva a sonda — são seis linhas, e o `sondas.py` mostra o formato.
3. **Nenhuma sonda daqui alcança a verdade do mundo.** Elas provam coerência interna. *"Somos o
   verificador mais rápido do mercado"* não é conferível por nada aqui, e a ferramenta diz que não
   é, em vez de deixar passar.
