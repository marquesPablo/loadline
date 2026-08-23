# Um roster de exemplo, e ele é ruim de propósito

Quatro agentes escritos à mão, do jeito que quase todo mundo escreve o primeiro: uma descrição
boa, um prompt razoável, e nenhuma declaração que um runtime consiga ler.

```console
$ python -m forja exemplos/roster-de-exemplo
```

**Os quatro aparecem no relatório, e não aparecem igual** — que é o ponto. O `tradutor.md` é o
mais bem escrito dos quatro e sai com dois achados; o `revisor-de-pr.md` sai com sete. Se a
vistoria acusasse os quatro do mesmo jeito, ela não estaria medindo nada.

| Arquivo | O que está errado nele | Achados |
|---|---|---:|
| `revisor-de-pr.md` | sem `tools:` (herda tudo), sem anti-descrição, sem gatilho, e confunde-se com o auditor | 7 |
| `auditor-de-seguranca.md` | pede rede sem dizer com quem fala, sem gatilho, e confunde-se com o revisor | 6 |
| `redator-de-changelog.md` | pede escrita e `Bash` sem dizer onde escreve; não diz o que nunca faz | 4 |
| `tradutor.md` | diz `Escreva só em docs/en/` **na prosa** — e prosa nenhum runtime lê; e nada confere a resposta dele | 2 |

O caso do `tradutor` é o mais instrutivo dos quatro: ele **de fato** declara onde escreve, em
português claro, no corpo do prompt. E é acusado mesmo assim, de propósito. A frase governa quem
lê o arquivo; ela não governa o processo que executa a ferramenta.

Os dois primeiros são o caso que só existe a partir do segundo agente: as descrições disputam o
mesmo despacho, e **nenhum dos dois nomeia o outro**. O orquestrador vai chutar, e vai chutar de
um jeito diferente a cada dia.

Depois de olhar o relatório, experimente o segundo passo — ele escreve, e não sobrescreve nada
do que está aqui:

```console
$ python -m forja exemplos/roster-de-exemplo --adotar
```
