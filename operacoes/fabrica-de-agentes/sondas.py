"""Sondas da operação `fabrica-de-agentes`.

natureza: correcao — sonda que estoura vira `UNPROVEN` no relatório, com o erro
por extenso. Ela nunca devolve um palpite.

COPIE ESTE ARQUIVO para a raiz do seu repositório, como `sondas.py`.
Para combinar com outra operação, concatene os arquivos — nenhum nome auxiliar
daqui colide com o das outras (todos começam com `_fab_`).

⚠️ **A regra anti-espelho, e aqui ela é a operação inteira.** Há duas fontes com
donos diferentes: a **spec** (`.toml`, escrita por uma pessoa) e o **artefato**
(`.claude/agents/*.md`, escrito pelo compilador). Um repositório saudável é
aquele em que todo artefato veio de uma spec, e nenhuma spec ficou para trás.

A sonda que mais dói é `fabrica.artefato_desatualizado`: a spec foi editada
DEPOIS do artefato, o que significa que o agente que roda hoje não é o agente
que está escrito. Ninguém percebe isso lendo a spec — ela está certa. O defeito
mora na distância entre os dois `mtime`.

⚠️ **E o limite honesto:** nada aqui roda o agente. Uma spec impecável pode
compilar um agente inútil, e nenhuma sonda offline sabe disso. O que se mede é
procedência: de onde veio o que está rodando.
"""

from __future__ import annotations

import re
from pathlib import Path

from loadline import sonda

RAIZ = Path(__file__).resolve().parent

#: AJUSTE ÚNICO desta operação: onde moram as suas specs declarativas.
#: Se você ainda não tem nenhuma, deixe como está — a sonda vai dizer que
#: 100% dos seus agentes são escritos à mão, que é o achado.
PASTAS_DE_SPEC = ("agentes", "specs", "forja/exemplos")

#: Onde os artefatos compilados (ou escritos à mão) são procurados.
PASTAS_DE_ARTEFATO = (".claude/agents", ".config/agents", ".agents")

_FAB_FRONT = re.compile(r"^---\s*$")
_FAB_SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def _fab_specs() -> dict[str, Path]:
    """slug -> arquivo da spec. O slug sai do CONTEÚDO, nunca do nome do arquivo.

    Ler o slug do nome do arquivo faria a sonda concordar com ela mesma: um
    artefato `revisor.md` casaria com uma spec `revisor.toml` mesmo que a spec
    declarasse outro slug lá dentro, e a divergência que interessa passaria.
    """
    achadas: dict[str, Path] = {}
    for pasta in PASTAS_DE_SPEC:
        base = RAIZ / pasta
        if not base.is_dir():
            continue
        for arquivo in sorted(base.rglob("*.toml")):
            texto = arquivo.read_text(encoding="utf-8", errors="replace")
            achado = re.search(r'^\s*slug\s*=\s*["\']([^"\']+)["\']', texto, re.MULTILINE)
            if achado:
                achadas.setdefault(achado.group(1), arquivo)
    return achadas


def _fab_artefatos() -> dict[str, Path]:
    """slug -> arquivo do artefato. O slug sai do frontmatter `name:`, e o nome
    do arquivo é o desempate — é assim que os harnesses de hoje o resolvem."""
    achados: dict[str, Path] = {}
    for pasta in PASTAS_DE_ARTEFATO:
        base = RAIZ / pasta
        if not base.is_dir():
            continue
        for arquivo in sorted(base.glob("*.md")):
            texto = arquivo.read_text(encoding="utf-8", errors="replace")
            achado = re.search(r"^\s*name\s*:\s*(\S+)", texto, re.MULTILINE)
            slug = achado.group(1).strip("\"'") if achado else arquivo.stem
            achados.setdefault(slug, arquivo)
    return achados


def _fab_ha_estado() -> None:
    """Zero artefato E zero spec não é um repositório saudável: é um repositório
    onde esta operação não tem o que dizer. Devolver 0 seria transformar *não
    medido* em *zero*, que é o defeito que o `loadline` inteiro existe para
    proibir."""
    if not _fab_artefatos() and not _fab_specs():
        raise LookupError(
            "não achei nenhum agente nem nenhuma spec. Procurei artefato em "
            f"{', '.join(PASTAS_DE_ARTEFATO)} e spec em {', '.join(PASTAS_DE_SPEC)}. "
            "Se os seus moram noutro lugar, ajuste as duas tuplas no topo de sondas.py — "
            "sem isso o número seria zero por eu não ter olhado, não por não haver nada"
        )


def _fab_forja():
    """A forja do `loadline`, ou o erro que explica por que ela não veio."""
    try:
        from forja import ler  # noqa: PLC0415
        from forja.spec import Recusa  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - depende do PYTHONPATH de quem adota
        raise LookupError(
            "o pacote `forja` não está no PYTHONPATH — esta sonda precisa dele para saber "
            "quais specs seriam recusadas. Rode com "
            "`PYTHONPATH=/caminho/para/loadline python -m loadline .`, ou `pip install -e`. "
            f"({exc})"
        ) from exc
    return ler, Recusa


# ---------------------------------------------------------------------------
# As sondas
# ---------------------------------------------------------------------------


@sonda("fabrica.artefatos", origem="arquivos .md nas pastas de agente, contados por slug")
def fab_artefatos() -> int:
    _fab_ha_estado()
    return len(_fab_artefatos())


@sonda("fabrica.specs", origem="arquivos .toml que declaram `slug =` nas pastas de spec")
def fab_specs() -> int:
    _fab_ha_estado()
    return len(_fab_specs())


@sonda(
    "fabrica.escritos_a_mao",
    origem="slugs com artefato e SEM spec — cruzamento das duas árvores",
)
def fab_escritos_a_mao() -> int:
    """De RELAÇÃO, e é o número que abre a conversa.

    Um agente sem spec não é um agente pior: é um agente sem fonte. Ninguém
    sabe de que decisão ele saiu, ninguém pode recompilá-lo, e a próxima
    edição dele é feita direto no artefato — que é onde a divergência nasce.
    """
    _fab_ha_estado()
    return len(set(_fab_artefatos()) - set(_fab_specs()))


@sonda(
    "fabrica.specs_nao_compiladas",
    origem="slugs com spec e SEM artefato — a direção contrária",
)
def fab_specs_nao_compiladas() -> int:
    """De RELAÇÃO. A spec existe, foi escrita, foi revisada — e nada roda.

    É o defeito mais silencioso dos dois: quem lê a spec acha que aquilo está
    no ar, e o repositório não tem como desmentir.
    """
    _fab_ha_estado()
    return len(set(_fab_specs()) - set(_fab_artefatos()))


@sonda(
    "fabrica.artefato_desatualizado",
    origem="mtime da spec > mtime do artefato, no sistema de arquivos",
)
def fab_artefato_desatualizado() -> int:
    """De RELAÇÃO, e é a sonda cara desta operação.

    A spec foi editada depois do artefato. Os dois existem, os dois parecem
    certos, e o que roda não é o que está escrito. Nenhuma revisão de código
    pega isso: os dois arquivos estão corretos, cada um por si.

    ⚠️ `mtime` mente depois de um clone — o git não preserva data de modificação,
    e num checkout novo todos os arquivos nascem com o mesmo instante. A leitura
    honesta é: **este número só vale na árvore de trabalho de quem edita.** No
    CI ele tende a zero por construção, e um zero ali não é prova de nada.
    """
    _fab_ha_estado()
    specs, artefatos = _fab_specs(), _fab_artefatos()
    return sum(
        1
        for slug, spec in specs.items()
        if slug in artefatos and spec.stat().st_mtime > artefatos[slug].stat().st_mtime
    )


@sonda(
    "fabrica.specs_recusadas",
    origem="specs que a forja do loadline RECUSA — as oito regras rodadas de verdade",
)
def fab_specs_recusadas() -> int:
    """De RELAÇÃO. Não é estilo: é a spec não compilar.

    A sonda não reimplementa as oito recusas — ela CHAMA a forja. Reimplementar
    seria escrever um segundo juiz que envelhece separado do primeiro, e os dois
    discordariam sem ninguém notar qual está certo.
    """
    _fab_ha_estado()
    ler, Recusa = _fab_forja()
    recusadas = 0
    for arquivo in set(_fab_specs().values()):
        try:
            ler(arquivo)
        except Recusa:
            recusadas += 1
        except Exception as exc:  # TOML quebrado é outra coisa, e não se conta como recusa
            raise LookupError(f"`{arquivo}` não é uma spec legível: {exc}") from exc
    return recusadas


@sonda(
    "fabrica.artefatos_sem_anti_descricao",
    origem="artefatos cuja descrição não diz em que caso NÃO usá-los",
)
def fab_sem_anti_descricao() -> int:
    """De RELAÇÃO, e vale para o artefato escrito à mão tanto quanto para o compilado.

    É a regra R3 da forja aplicada a quem nunca vai escrever uma spec. Sem
    anti-descrição o orquestrador despacha por semelhança de tema — e o agente
    errado responde com a confiança do certo.
    """
    _fab_ha_estado()
    marcas = ("nunca usar", "não usar", "nao usar", "never use", "do not use", "não é para")
    sem = 0
    for arquivo in set(_fab_artefatos().values()):
        texto = arquivo.read_text(encoding="utf-8", errors="replace").lower()
        if not any(marca in texto for marca in marcas):
            sem += 1
    return sem


@sonda(
    "fabrica.slugs_invalidos",
    origem="slugs de artefato fora de [a-z0-9-] — eles viram nome de arquivo em 4 harnesses",
)
def fab_slugs_invalidos() -> int:
    _fab_ha_estado()
    return sum(1 for slug in _fab_artefatos() if not _FAB_SLUG.match(slug))
