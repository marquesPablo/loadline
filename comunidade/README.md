# Contribuindo com uma operação

> **Este repositório ainda é privado.** Esta pasta documenta o mecanismo de contribuição para
> quando ele for público — hoje ela não recebe PR de ninguém de fora, porque não há de onde vir.
> Ela existe agora, e não só no dia da publicação, para que a régua já esteja escrita quando a
> primeira pessoa de fora perguntar "posso mandar a minha?".

## O que entra aqui, e o que não entra

**Não é** um lugar para conectores de API, integrações ou exemplos de uso. **É** um lugar para
**sondas de domínio** — a mesma anatomia fixa de `operacoes/`, aplicada a uma dor que você tem e a
prateleira de hoje não cobre.

A régua de admissão é a mesma do produto inteiro (`ADR-109` do hub que mantém este repositório):
**o que a pessoa GANHA ao rodar isto?** Uma sonda que só confirma o que você já desconfiava
("meu README está velho") é higiene. Uma sonda que entrega uma capacidade nova é o que esta
prateleira busca. As duas são bem-vindas — a régua está em `operacoes/README.md`, seção
"Escrevendo a sua".

## Por que isso não é "PR aceito automaticamente se passar o CI verde"

`operacoes/README.md` já diz: **"a prateleira cresce por decisão, não por acúmulo."** A prateleira
nasceu com dez candidatas e o board cortou para sete, porque as que saíram ou eram puro alarme ou
já eram feitas por outra peça. Aceitar contribuição por volume repetiria exatamente esse erro, só
que sem um board para cortar depois.

**Por isso todo PR nesta pasta é revisado por decisão humana antes do merge — nunca por CI
sozinho.** O CI (item 5 do checklist abaixo) é o piso, não o teto: ele reprova o que está
mecanicamente errado; ele não decide se a operação merece existir.

## O checklist de uma contribuição

Copie `_modelo/` para uma pasta nova com o nome da sua operação (`comunidade/nome-da-sua-operacao/`)
e preencha os cinco arquivos. Antes de abrir o PR, confira os cinco pontos que todo revisor vai
conferir primeiro — estão nomeados em `operacoes/README.md` §"Escrevendo a sua":

1. **A sonda não pode ler a fonte que produziu o número escrito.** Se os dois lados saem do mesmo
   lugar, o par passa verde travando o defeito em vez de achá-lo. Declare `origem=` no seu selo
   para isso ser conferível de fora — é a mesma regra que toda sonda desta prateleira já segue.
2. **`natureza` é obrigatória em cada métrica**, e muda o que fazer com o vermelho: `contagem`
   anda quando alguém escreve (resele e siga); `relacao` só anda se o medidor ou o repositório
   quebrou (pare e investigue).
3. **Estourar é melhor que devolver zero.** Se sua sonda não achou a pasta que devia medir, ela
   levanta erro — nunca devolve `0`. *"Não olhei"* e *"olhei e não há"* são coisas opostas, e
   confundir as duas é o defeito que este projeto inteiro existe para proibir.
4. **Nenhum nome de função auxiliar pode colidir com os das outras sete operações.** Prefixe com
   algo específico da sua (as existentes usam `_instr_`, `_repo_`, `_cer_`, `_dec_`, `_su_`,
   `_hand_`, `_vit_` — escolha um prefixo livre).
5. **`agente.toml` precisa compilar na `forja`, sem recusa.** Rode `python -m forja
   comunidade/<sua-operacao>/agente.toml` antes de abrir o PR — as oito recusas da forja falham
   fechadas, e vêm com o conserto escrito.

## O que acontece depois do PR

Alguém do board lê a `RECEITA.md` (a dor é real? o exemplo executado é verdadeiro?) e roda a sonda
contra um repositório de teste. **Aceitar, pedir ajuste, ou recusar com o motivo escrito** — nunca
silêncio. Uma operação aceita entra em `operacoes/`, nunca fica presa em `comunidade/`: esta pasta
é a sala de espera, não o destino final.

## Ligações

- [`operacoes/README.md`](../operacoes/README.md) — a anatomia fixa e a régua completa de "o que
  faz uma boa [operação]"
- [`LACUNAS.md`](../LACUNAS.md) — o que este projeto inteiro nunca mede, para sua sonda não prometer
  o que a prateleira já declarou fora de escopo
