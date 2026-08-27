"""Onde uma varredura ingênua para sem avisar, e por qual dos dois motivos.

nature: fix — fronteira que não dá para classificar vira item "não
verificado" no relatório, nunca uma exceção que derruba a rodada inteira.

## As duas causas, medidas, nunca a mesma

**Causa 1 — estrutural.** Um reparse point (junction do Windows, symlink de
diretório em qualquer sistema) não é descido por uma varredura que não pede
isso explicitamente. É o defeito fundador: `rg --files` sem `-L` para na
fronteira, `os.walk(seguir_links=False)` também para — mas junction do
Windows **não é** symlink (`os.path.islink` devolve `False` nas duas; quem
acerta é `os.path.isjunction`, só a partir do Python 3.12, ou o reparse tag
`0xA0000003` lido direto em versões anteriores).

**Causa 2 — política, não estrutura.** Dentro de um repositório git de
verdade, um `.gitignore` que lista a pasta esconde o conteúdo dela de
qualquer ferramenta que respeite ignore files — **mesmo com a flag que
atravessa reparse point ligada**. As duas causas parecem a mesma coisa de
fora ("a ferramenta não viu") e pedem conserto diferente: a primeira pede
apontar para a raiz real; a segunda pede `--no-ignore` ou editar o
`.gitignore`, e apontar para a raiz real NÃO resolve sozinho se o próprio
`.gitignore` da raiz nova também a esconde.

Medido nesta sessão, com fixture sintético e `.git` real:

    rg --files -L <pasta-sem-.git>                    → atravessa o link
    rg --files -L <pasta-com-.git-e-.gitignore>        → NÃO atravessa
    rg --files -L --no-ignore <a mesma, com .gitignore> → atravessa de novo

É a mesma distinção que o `Y12` desta casa mede desde 2026-08-08, generalizada
para qualquer repositório — não só o cérebro que a documenta.
"""

from __future__ import annotations

import fnmatch
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

#: Arquivos cuja ausência do relatório de alguém é o pior caso possível: são
#: os que carregam a instrução ou o gate. Nome exato, não padrão — um agente
#: chamado "AGENTS.MD.bak" não é este arquivo, e fingir que é seria o mesmo
#: excesso que o `V6` da `vitrine` já decidiu não cometer.
ARQUIVOS_DE_DECLARACAO = frozenset({
    "CLAUDE.md", "AGENTS.md", "SKILL.md", "agent.toml", "settings.json",
})

#: Pasta cujo conteúdo inteiro é declaração, mesmo que o nome do arquivo
#: dentro dela não bata com a lista acima — `.claude/agents/*.md`,
#: `.claude/hooks/*.py`, `.claude/skills/**/SKILL.md`.
PASTA_DE_DECLARACAO = ".claude"

_JUNCTION_TAG = 0xA0000003  # IO_REPARSE_TAG_MOUNT_POINT — o mesmo valor que o Y6 desta casa lê.


@dataclass
class Fronteira:
    """Um ponto onde varredura ingênua e varredura completa divergem."""

    tipo: str                                  #: "junction" · "symlink" · "gitignore"
    caminho: str                                #: relativo à raiz avaliada
    alvo: str | None = None                     #: para junction/symlink: o destino
    regra: str | None = None                    #: para gitignore: o padrão que casou
    arquivos_atras: list[str] = field(default_factory=list)  #: declaração escondida, se houver

    @property
    def grave(self) -> bool:
        """Fronteira vira achado GRAVE quando esconde declaração de verdade.

        Uma junction sem nada sensível atrás é fato do disco, não defeito —
        por isso ela aparece no relatório como aviso, nunca como reprovação.
        """
        return bool(self.arquivos_atras)


def _tipo_do_link(caminho: Path) -> str | None:
    """"junction" · "symlink" · `None`. Nunca lança — chamado em toda pasta da árvore."""
    try:
        if os.path.islink(caminho):
            return "symlink"
        if hasattr(os.path, "isjunction"):                 # Python ≥ 3.12
            return "junction" if os.path.isjunction(caminho) else None
        tag = getattr(os.lstat(caminho), "st_reparse_tag", 0)
        return "junction" if tag == _JUNCTION_TAG else None
    except OSError:
        return None


def _e_declaracao(caminho: Path) -> bool:
    if caminho.name in ARQUIVOS_DE_DECLARACAO:
        return True
    return PASTA_DE_DECLARACAO in caminho.parts


def _arquivos_de_declaracao_sob(pasta: Path) -> list[str]:
    """Varredura EXPLÍCITA da fronteira para dentro — só chamada depois de a
    fronteira já ter sido identificada. Não é a varredura ingênua; é a
    ferramenta provando o que a ingênua deixaria de ver.

    Devolve caminho relativo À PRÓPRIA FRONTEIRA, não à raiz avaliada — o
    relatório já nomeia a fronteira uma vez; repetir o prefixo em cada linha
    só teria feito o achado mais difícil de ler.
    """
    achados: list[str] = []
    try:
        for caminho in pasta.rglob("*"):
            if caminho.is_file() and _e_declaracao(caminho):
                achados.append(str(caminho.relative_to(pasta)))
    except OSError:
        pass
    return sorted(achados)


def _reparse_points(raiz: Path) -> list[Fronteira]:
    fronteiras: list[Fronteira] = []
    pilha = [raiz]
    while pilha:
        pasta = pilha.pop()
        try:
            entradas = sorted(pasta.iterdir())
        except OSError:
            continue
        for entrada in entradas:
            if not entrada.is_dir():
                continue
            tipo = _tipo_do_link(entrada)
            if tipo is None:
                pilha.append(entrada)  # pasta comum: desce normalmente
                continue
            try:
                alvo = str(entrada.resolve())
            except OSError:
                alvo = None
            fronteiras.append(Fronteira(
                tipo=tipo,
                caminho=str(entrada.relative_to(raiz)),
                alvo=alvo,
                arquivos_atras=_arquivos_de_declaracao_sob(entrada),
            ))
            # NÃO desce por dentro da fronteira pela pilha principal — ela já
            # foi varrida à parte por `_arquivos_de_declaracao_sob`. Descer
            # aqui também contaria a mesma fronteira em profundidades diferentes.
    return fronteiras


def _raiz_do_git(caminho: Path) -> Path | None:
    """A pasta com `.git`, subindo a árvore — `None` se não houver nenhuma.

    `.gitignore` só é lido por ferramentas cientes de git QUANDO existe um
    repositório de verdade por perto (medido nesta sessão: o mesmo
    `.gitignore`, fora de um `.git`, não tem efeito nenhum sobre o `rg`).
    Sem isto o achado de "gitignore esconde declaração" dispararia até em
    pasta que ferramenta nenhuma trataria como ignorada.
    """
    atual = caminho.resolve()
    for candidata in (atual, *atual.parents):
        if (candidata / ".git").exists():
            return candidata
    return None


def _ler_gitignore(caminho: Path) -> list[str]:
    """Padrões crus de um `.gitignore`. Não é o parser completo do git — não
    cobre negação (`!padrao`) nem `**` — e isso está na `LACUNAS.md`."""
    try:
        linhas = caminho.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    return [ln.strip() for ln in linhas if ln.strip() and not ln.strip().startswith("#")]


def _padrao_bate(padrao: str, relativo_da_regra: str) -> bool:
    """Subconjunto de gitignore: nome simples, `/` inicial (ancorado à pasta
    do próprio `.gitignore`), `/` final (só diretório), curinga via `fnmatch`.
    Documentado como piso em `LACUNAS.md` — não é negação, não é `**`."""
    alvo = padrao.rstrip("/")
    ancorado = alvo.startswith("/")
    alvo = alvo.lstrip("/")
    partes = Path(relativo_da_regra).parts
    if ancorado:
        return bool(partes) and fnmatch.fnmatch(partes[0], alvo)
    return any(fnmatch.fnmatch(parte, alvo) for parte in partes)


def _fronteiras_de_gitignore(raiz: Path) -> list[Fronteira]:
    raiz_git = _raiz_do_git(raiz)
    if raiz_git is None:
        return []

    fronteiras: list[Fronteira] = []
    for gitignore in raiz.rglob(".gitignore"):
        padroes = _ler_gitignore(gitignore)
        pasta_da_regra = gitignore.parent
        if not padroes:
            continue

        # Só a fronteira MAIS RASA que bate — um padrão como "vinculo" casa
        # com "vinculo" e com todo descendente dele (`fnmatch` roda por
        # componente de caminho). Sem este corte, cada nível abaixo da mesma
        # junction virava um achado repetido citando o mesmo arquivo.
        aceitas: list[Path] = []
        for caminho in sorted(pasta_da_regra.rglob("*"), key=lambda p: len(p.parts)):
            if not caminho.is_dir():
                continue
            if any(a in caminho.parents for a in aceitas):
                continue
            relativo = str(caminho.relative_to(pasta_da_regra))
            if any(_padrao_bate(p, relativo) for p in padroes):
                aceitas.append(caminho)

        for caminho in aceitas:
            atras = _arquivos_de_declaracao_sob(caminho)
            if not atras:
                continue
            relativo = str(caminho.relative_to(pasta_da_regra))
            regra = next(p for p in padroes if _padrao_bate(p, relativo))
            fronteiras.append(Fronteira(
                tipo="gitignore",
                caminho=str(caminho.relative_to(raiz)),
                regra=regra,
                arquivos_atras=atras,
            ))
    return fronteiras


def detectar(raiz: str | Path) -> list[Fronteira]:
    """Toda fronteira sob `raiz` — reparse point e regra de `.gitignore` que
    esconde declaração. Não executa nada, não chama modelo, só lê o disco."""
    caminho = Path(raiz).expanduser()
    achadas = _reparse_points(caminho) + _fronteiras_de_gitignore(caminho)
    return sorted(achadas, key=lambda f: (f.tipo, f.caminho))
