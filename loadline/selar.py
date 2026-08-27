"""`--selar` — a anotação vira SAÍDA da primeira rodada, não pedágio dela.

loadline-ignore-file: este arquivo ENSINA a sintaxe que emite, e os selos
escritos aqui são espécimes, não afirmações. Sem esta linha o módulo lê o
próprio gerador como se ele declarasse fatos.

natureza: correcao — este módulo escreve, e por isso ele é o único do projeto
que precisa falhar de forma conservadora: arquivo que não deu para ler ou
escrever vira linha no relatório e a rodada segue, nunca uma exceção no meio de
um lote que deixa metade dos arquivos alterados e metade não.

## Por que isto existe

Sem `--selar`, o custo do produto é todo antecipado: o usuário precisa escrever
o selo À MÃO **e** uma sonda para cada métrica, e o retorno só chega em 90 dias,
quando o primeiro `vence=` dispara. É a forma de adoção que perde.

Com ele, o usuário roda uma vez, vê a lista do que ninguém consegue conferir, e
sai da primeira sessão com o arquivo anotado. O que era pedágio virou produto.

## Quatro regras, e cada uma tem um motivo

1. **Só escreve com a bandeira.** Sem `--selar` o projeto inteiro é
   somente-leitura, e é assim que ele é apresentado.
2. **Emite `arbitrated:` e nunca `measured:`.** Ninguém mediu nada. Emitir
   `measured:` seria a ferramenta inventando que houve medição — a mentira exata
   que ela existe para perseguir.
3. **`by=?` sai por escrito.** A ferramenta não sabe quem escolheu o número, e
   fingir que sabe é a mesma família de defeito. O `?` parseia (o arquivo
   continua válido) e o relatório cobra o preenchimento em toda rodada
   seguinte — falha visível em vez de silenciosa.
4. **Nunca sobrescreve e nunca escreve em espécime.** Se a linha seguinte já tem
   selo, o lugar já tem dono e este módulo não encosta.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .eco import Afirmacao
from .selo import _PADRAO  # o mesmo reconhecedor que lê — nunca uma segunda regra

#: Prazo padrão do selo emitido. É, ele próprio, um número ARBITRADO — e o
#: projeto seria incoerente se fingisse o contrário. Ver `LACUNAS.md`.
VENCE_PADRAO = "90d"


@dataclass(frozen=True)
class Escrito:
    arquivo: str
    linha: int
    texto: str


def _ja_tem_selo(linhas: list[str], indice: int) -> bool:
    """A linha logo abaixo já carrega selo? Então o lugar tem dono."""
    seguinte = indice + 1
    return seguinte < len(linhas) and bool(_PADRAO.search(linhas[seguinte]))


def _nomes_unicos(afirmacoes: list[Afirmacao]) -> dict[int, list[tuple[str, str]]]:
    """Agrupa por linha e desempata nomes repetidos dentro do mesmo arquivo.

    Duas frases que dizem `endpoints` produziriam duas métricas de mesmo nome, e
    o selo do segundo silenciaria o do primeiro. Sufixar é feio e é honesto; o
    humano renomeia os dois quando for preencher o `by=`.
    """
    usados: dict[str, int] = {}
    por_linha: dict[int, list[tuple[str, str]]] = {}
    for af in sorted(afirmacoes, key=lambda a: (a.linha, a.numero)):
        base = af.nome
        usados[base] = usados.get(base, 0) + 1
        nome = base if usados[base] == 1 else f"{base}_{usados[base]}"
        por_linha.setdefault(af.linha, []).append((nome, af.numero))
    return por_linha


def selar_arquivo(
    caminho: Path, afirmacoes: list[Afirmacao], hoje: date, vence: str = VENCE_PADRAO
) -> list[Escrito]:
    """Insere um selo `arbitrated:` depois de cada linha que afirma sem prova.

    Insere de baixo para cima: escrever de cima para baixo desloca todos os
    números de linha seguintes, e o segundo selo cairia no lugar errado — em
    silêncio, que é o modo caro de errar aqui.
    """
    texto = caminho.read_text(encoding="utf-8")
    linhas = texto.splitlines()
    quebra_final = texto.endswith("\n")

    escritos: list[Escrito] = []
    for numero_da_linha, pares in sorted(_nomes_unicos(afirmacoes).items(), reverse=True):
        indice = numero_da_linha - 1
        if indice < 0 or indice >= len(linhas) or _ja_tem_selo(linhas, indice):
            continue
        original = linhas[indice]
        recuo = original[: len(original) - len(original.lstrip())]
        metricas = " ".join(f"{nome}={valor}" for nome, valor in pares)
        selo = (
            f"{recuo}<!-- arbitrated: {metricas} by=? "
            f"on={hoje.isoformat()} expires={vence} -->"
        )
        linhas.insert(indice + 1, selo)
        escritos.append(Escrito(str(caminho), numero_da_linha, selo.strip()))

    if escritos:
        caminho.write_text("\n".join(linhas) + ("\n" if quebra_final else ""), encoding="utf-8")
    return list(reversed(escritos))


def selar(afirmacoes: list[Afirmacao], hoje: date | None = None) -> tuple[list[Escrito], list[str]]:
    """Escreve os selos de toda a lista 3. Devolve `(escritos, problemas)`."""
    hoje = hoje or date.today()
    por_arquivo: dict[str, list[Afirmacao]] = {}
    for af in afirmacoes:
        por_arquivo.setdefault(af.arquivo, []).append(af)

    escritos: list[Escrito] = []
    problemas: list[str] = []
    for arquivo, lote in sorted(por_arquivo.items()):
        try:
            escritos.extend(selar_arquivo(Path(arquivo), lote, hoje))
        except (OSError, UnicodeDecodeError, UnicodeEncodeError) as exc:
            problemas.append(f"{arquivo}: não deu para selar — {exc}")
    return escritos, problemas
