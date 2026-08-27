"""Autoteste — cada check reintroduz o defeito que ele existe para pegar.

loadline-ignore-file: este arquivo escreve selos de mentira de propósito.
Julgá-los seria afirmar coisas que ninguém quis afirmar.

Rode: `python autoteste.py`

Um check que só confirma o caminho feliz não prova nada: ele passa igual se o
mecanismo for removido. Aqui cada letra **quebra alguma coisa** e exige que o
motor reprove. Se um destes ficar verde depois de você tirar o mecanismo, o
check é decorativo e deve ser jogado fora.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

from forja.__main__ import main as forja_main

from loadline import (
    ARBITRATED,
    FROZEN,
    DRIFTED,
    PROSE_DRIFT,
    UNPROVEN,
    MATCHES,
    EXPIRED,
    SeloMalformado,
    julgar,
    ler_linha,
    registro,
    selar,
    sonda,
    varrer,
)

try:  # os checks imprimem na decoração, antes de qualquer main()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError, OSError):
    pass





HOJE = date(2026, 8, 16)
_falhas: list[str] = []
_passes = 0

#: Checks que EXISTEM e NÃO rodam nesta corrida, com o motivo de cada um.
#: Está vazio hoje, e é declarado mesmo assim: o denominador de uma suíte é
#: `executados + fora`, e uma suíte que só imprime quantos passaram esconde
#: exatamente o check que alguém desligou. Fora do denominador é fora à vista.
FORA: list[tuple[str, str]] = []


def check(letra: str, o_que: str):
    def decorar(funcao):
        global _passes
        try:
            funcao()
        except AssertionError as exc:
            _falhas.append(f"{letra} — {o_que}\n     {exc}")
            print(f"  ✗ {letra}  {o_que}\n      {exc}")
        except Exception as exc:  # noqa: BLE001
            _falhas.append(f"{letra} — {o_que}\n     estourou: {type(exc).__name__}: {exc}")
            print(f"  ✗ {letra}  {o_que}\n      estourou: {type(exc).__name__}: {exc}")
        else:
            _passes += 1
            print(f"  ✓ {letra}  {o_que}")
        return funcao

    return decorar


def _selo(texto: str):
    return ler_linha(texto, arquivo="teste", linha=1)


# ---------------------------------------------------------------- gramática

@check("A", "selo com métrica e SEM `natureza` é RECUSADO, não aceito calado")
def _a():
    try:
        _selo("<!-- measured: x.y=3 on=2026-08-16 -->")
    except SeloMalformado as exc:
        assert "nature" in str(exc), f"recusou pelo motivo errado: {exc}"
        return
    raise AssertionError(
        "aceitou selo sem natureza — aí todo vermelho vira ruído e a resposta a "
        "todo vermelho vira 'resela', escondendo o único bug que isto pega"
    )


@check("B", "`natureza` fora do vocabulário fechado é RECUSADA")
def _b():
    try:
        _selo("<!-- measured: x.y=3 nature=talvez on=2026-08-16 -->")
    except SeloMalformado:
        return
    raise AssertionError("aceitou `natureza=talvez`; o vocabulário não é fechado de verdade")


@check("C", "`frozen:` sem `motivo` é RECUSADO")
def _c():
    try:
        _selo('<!-- frozen: x.y=3 on=2020-01-01 -->')
    except SeloMalformado as exc:
        assert "reason" in str(exc), f"recusou pelo motivo errado: {exc}"
        return
    raise AssertionError("congelar sem dizer por quê é o mesmo que apagar a medida")


@check("D", "`vence` malformado vira UNPROVEN, nunca MATCHES")
def _d():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 3)
    achados = julgar(_selo("<!-- measured: x.y=3 nature=count on=2026-08-16 expires=semana -->"), HOJE)
    assert achados[0].veredito == UNPROVEN, f"esperava UNPROVEN, veio {achados[0].veredito}"


# ------------------------------------------------------- os dois vermelhos

@check("E", "divergência de CONTAGEM manda RESSELAR")
def _e():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 9)
    a = julgar(_selo("<!-- measured: x.y=3 nature=count on=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == DRIFTED, f"esperava DRIFTED, veio {a.veredito}"
    assert not a.e_defeito, "contagem divergindo NÃO é defeito"
    assert "re-seal" in a.acao.lower(), f"ação errada: {a.acao}"


@check("F", "divergência de RELAÇÃO é DEFEITO e manda PARAR — não resselar")
def _f():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 9)
    a = julgar(_selo("<!-- measured: x.y=3 nature=relation on=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == DRIFTED, f"esperava DRIFTED, veio {a.veredito}"
    assert a.e_defeito, (
        "relação divergindo passou como resselável — é aqui que se esconde o bug "
        "que o mecanismo inteiro existe para achar"
    )
    assert "STOP" in a.acao, f"ação errada: {a.acao}"


# ------------------------------------------------------------- vencimento

@check("G", "valor CERTO + prazo vencido = EXPIRED (o motivo de este projeto existir)")
def _g():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 3)
    a = julgar(
        _selo("<!-- measured: x.y=3 nature=count on=2026-01-01 expires=30d -->"), HOJE
    )[0]
    assert a.veredito == EXPIRED, (
        f"esperava EXPIRED, veio {a.veredito} — um número que ninguém reconfere há meses "
        "é um número que ainda não errou, não um número verificado"
    )
    assert a.escrito == a.medido == "3", "o valor batia; o que venceu foi a conferência"


@check("H", "`vence=nunca` não vence, mesmo antigo")
def _h():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 3)
    a = julgar(_selo("<!-- measured: x.y=3 nature=relation on=2001-01-01 expires=never -->"), HOJE)[0]
    assert a.veredito == MATCHES, f"esperava MATCHES, veio {a.veredito}"


# --------------------------------------------------- não medido ≠ zero

@check("I", "métrica sem sonda vira UNPROVEN, NUNCA MATCHES")
def _i():
    registro.limpar()
    a = julgar(_selo("<!-- measured: nao.existe=3 nature=count on=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == UNPROVEN, f"esperava UNPROVEN, veio {a.veredito}"
    assert not a.verde, "não medido virou verde — é o defeito de contar ausência como zero"


@check("J", "sonda que ESTOURA vira UNPROVEN, e nunca passa como verde")
def _j():
    registro.limpar()

    def quebrada():
        raise RuntimeError("o disco sumiu")

    sonda("x.y", origem="teste")(quebrada)
    a = julgar(_selo("<!-- measured: x.y=3 nature=count on=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == UNPROVEN, f"esperava UNPROVEN, veio {a.veredito}"
    assert "o disco sumiu" in a.detalhe, f"engoliu o erro: {a.detalhe}"


@check("K", "TypeError de DENTRO da sonda não é confundido com aridade errada")
def _k():
    registro.limpar()

    def erra_por_dentro():
        return 1 + "dois"  # noqa: RUF005

    sonda("x.y", origem="teste")(erra_por_dentro)
    a = julgar(_selo("<!-- measured: x.y=3 nature=count on=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == UNPROVEN, f"esperava UNPROVEN, veio {a.veredito}"
    assert "TypeError" in a.detalhe, (
        f"o TypeError da sonda foi engolido pelo despacho de aridade: {a.detalhe}"
    )


# --------------------------------------------------------------- espécime

@check("L", "região de espécime NÃO é julgada — nem a que documenta selo malformado")
def _l():
    registro.limpar()
    with tempfile.TemporaryDirectory() as tmp:
        alvo = Path(tmp) / "doc.md"
        alvo.write_text(
            "# doc\n\n```\n<!-- measured: inventado=99 nature=count on=2026-08-16 -->\n```\n",
            encoding="utf-8",
        )
        r = varrer(alvo, hoje=HOJE)
    assert not r.achados, f"julgou exemplo dentro de cerca: {[str(a) for a in r.achados]}"
    assert not r.malformados, f"reprovou um espécime: {r.malformados}"


@check("M", "fora da cerca, o MESMO selo É julgado — a cerca não é buraco geral")
def _m():
    registro.limpar()
    with tempfile.TemporaryDirectory() as tmp:
        alvo = Path(tmp) / "doc.md"
        alvo.write_text(
            "# doc\n\n<!-- measured: inventado=99 nature=count on=2026-08-16 -->\n",
            encoding="utf-8",
        )
        r = varrer(alvo, hoje=HOJE)
    assert len(r.achados) == 1, f"esperava 1 achado, veio {len(r.achados)}"
    assert r.achados[0].veredito == UNPROVEN


# ----------------------------------------------------------- anti-espelho

@check("N", "toda sonda registrada DECLARA de onde tira o valor")
def _n():
    registro.limpar()
    import sondas  # noqa: F401  — registra as sondas de verdade do projeto

    declaradas = registro.explicar()
    assert declaradas, "nenhuma sonda registrada"
    mudas = [p for p, origem in declaradas if not origem.strip()]
    assert not mudas, (
        f"sondas sem origem declarada: {mudas} — sem isso não dá para auditar se a sonda "
        "lê a MESMA fonte que produziu o número escrito, que é check espelho e não verifica nada"
    )


@check("O", "congelado não é recomputado, e carrega o motivo até o relatório")
def _o():
    registro.limpar()
    a = julgar(_selo('<!-- frozen: x.y=3 on=2020-01-01 reason="launch history" -->'), HOJE)[0]
    assert a.veredito == FROZEN, f"esperava FROZEN, veio {a.veredito}"
    assert a.verde, "congelado com motivo é verde"
    assert "launch history" in a.acao


@check("P", "o relatório declara o DENOMINADOR: arquivo sem selo nenhum é contado")
def _p():
    registro.limpar()
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "vazio.md").write_text("nada aqui\n", encoding="utf-8")
        (Path(tmp) / "outro.md").write_text("também nada\n", encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)
    assert len(r.arquivos_sem_selo) == 2, (
        f"esperava 2 arquivos sem selo, veio {len(r.arquivos_sem_selo)} — sem denominador, "
        "'0 problemas' e 'ninguém mediu' viram a mesma frase"
    )


@check("Q", "resselar reescreve o selo INTEIRO, nunca só metade dele")
def _q():
    from loadline import escrever

    velho = _selo("<!-- measured: x.y=3 nature=count on=2026-01-01 expires=30d -->")
    novo = escrever(velho, **{"x.y": 9, "on": "2026-08-16"})
    assert "x.y=9" in novo, novo
    assert "on=2026-08-16" in novo, novo
    assert "x.y=3" not in novo and "2026-01-01" not in novo, f"sobrou metade do selo velho: {novo}"
    assert "nature=count" in novo and "expires=30d" in novo, f"perdeu campo no resselo: {novo}"


# ------------------------------------------------------------------- forja --
#
# Daqui para baixo o alvo é a forja. A regra é a mesma: cada check REMOVE um
# campo obrigatório e exige que o compilador RECUSE. Um compilador de agente que
# emite mesmo assim entrega o agente sem gate que ele existia para impedir.

import json
import subprocess
import tomllib

from forja import Recusa, ler
from forja import alvos as _alvos
from forja import conselho as _conselho
from forja import vacina as _vacina
from forja.__main__ import compilar

EXEMPLO = Path(__file__).parent / "forja" / "exemplos" / "revisor-de-licenca.toml"


def _spec_de(mudar) -> Path:
    """Escreve uma variante da spec de exemplo num temporário e devolve o caminho.

    Partir do exemplo REAL, e não de um dicionário mínimo, é de propósito: um
    check que monta a spec do zero prova que o campo é exigido numa spec
    inventada, e não que ele é exigido na spec que as pessoas de fato escrevem.
    """
    dados = tomllib.loads(EXEMPLO.read_text(encoding="utf-8"))
    mudar(dados)
    tmp = Path(tempfile.mkdtemp()) / "variante.toml"
    tmp.write_text(_toml(dados), encoding="utf-8")
    return tmp


def _toml(d: dict) -> str:
    """Serializador TOML mínimo — a stdlib só sabe LER, e zero dependências vale aqui também."""

    def valor(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, list):
            return "[" + ", ".join(valor(x) for x in v) + "]"
        return json.dumps(str(v), ensure_ascii=False)

    linhas = []
    for secao in ("agente", "fronteira", "censo"):
        if secao not in d:
            continue
        linhas.append(f"[{secao}]")
        for k, v in d[secao].items():
            if k != "golden":
                linhas.append(f"{k} = {valor(v)}")
        linhas.append("")
    prova = d.get("prova", {})
    linhas.append("[prova]")
    linhas.append(f"lacunas = {valor(prova.get('lacunas', []))}")
    linhas.append("")
    for caso in prova.get("golden", []):
        linhas.append("[[prova.golden]]")
        for k, v in caso.items():
            linhas.append(f"{k} = {valor(v)}")
        linhas.append("")
    return "\n".join(linhas)


def _recusa(mudar, regra: str) -> None:
    caminho = _spec_de(mudar)
    try:
        ler(caminho)
    except Recusa as exc:
        assert exc.regra == regra, f"recusou por {exc.regra}, esperava {regra}: {exc}"
        assert exc.conserto.strip(), f"{regra} recusou sem dizer o conserto"
        return
    raise AssertionError(
        f"{regra}: a forja COMPILOU uma spec que deveria recusar — falha aberta é "
        "exatamente o defeito que a forja existe para impedir"
    )


@check("R", "ferramenta de REDE sem `dominios_permitidos` é RECUSADA (R1)")
def _r():
    _recusa(lambda d: d["fronteira"].pop("dominios_permitidos"), "R1")
    # e a lista VAZIA tem de valer o mesmo que a ausência — senão é porta dos fundos
    _recusa(lambda d: d["fronteira"].__setitem__("dominios_permitidos", []), "R1")


@check("S", "ferramenta de ESCRITA sem `saida_cercada` é RECUSADA (R2)")
def _s():
    def pedir_escrita(d):
        d["fronteira"]["ferramentas"] = ["Read", "Write"]
        d["fronteira"].pop("dominios_permitidos", None)

    _recusa(pedir_escrita, "R2")


@check("T", "spec sem `nunca_usar` é RECUSADA — sem anti-descrição o orquestrador chuta (R3)")
def _t():
    _recusa(lambda d: d["agente"].__setitem__("nunca_usar", []), "R3")


@check("U", "spec sem `lacunas` é RECUSADA — agente sem limite declarado é lido como sem limite (R4)")
def _u():
    _recusa(lambda d: d["prova"].__setitem__("lacunas", []), "R4")


@check("V", "spec com ZERO caso de golden set é RECUSADA (R5)")
def _v():
    _recusa(lambda d: d["prova"].__setitem__("golden", []), "R5")


@check("X", "golden derivado de DENTRO da saída do agente é RECUSADO — é check espelho (R6)")
def _x():
    def espelhar(d):
        d["fronteira"]["ferramentas"] = ["Read", "Write"]
        d["fronteira"]["saida_cercada"] = ["relatorios/"]
        d["fronteira"].pop("dominios_permitidos", None)
        d["prova"]["golden"] = [
            {
                "pergunta": "quantas licenças OSI?",
                "esperado": "sete",
                "derivado_de": "relatorios/ultima-rodada.md",
            }
        ]

    _recusa(espelhar, "R6")
    # e `derivado_de` vazio cai na MESMA regra: sem fonte, não há verificação
    _recusa(
        lambda d: d["prova"].__setitem__(
            "golden", [{"pergunta": "p", "esperado": "e", "derivado_de": ""}]
        ),
        "R6",
    )


@check("Y", "`toca_alvo` sem autorização de engajamento é RECUSADO (R7)")
def _y():
    _recusa(lambda d: d["fronteira"].__setitem__("toca_alvo", True), "R7")


@check("Z", "a vacina de vírus de ideia está em TODO artefato de prompt, e o detector a perde se ela sair")
def _z():
    spec = ler(EXEMPLO)
    artefatos = compilar(spec)
    de_prompt = [c for c in artefatos if c.endswith((".system.md", "AGENTS.md")) or "agents/" in c]
    assert len(de_prompt) == 3, f"esperava 3 artefatos de prompt, achei {de_prompt}"
    for caminho in de_prompt:
        assert _vacina.esta_vacinado(artefatos[caminho]), f"{caminho} saiu SEM vacina"
    # controle negativo: sem a MARCA, o detector tem de dizer que não está vacinado
    sem_marca = artefatos[de_prompt[0]].replace(_vacina.MARCA, "outra-coisa-qualquer")
    assert not _vacina.esta_vacinado(sem_marca), (
        "o detector achou vacina onde a marca não está — ele estaria medindo prosa, e "
        "tradução ou reformatação o derrubaria sem ninguém ver"
    )


def _rodar_hook(hook: Path, evento: dict, slug: str) -> dict | None:
    saida = subprocess.run(
        [sys.executable, str(hook)],
        input=json.dumps(evento),
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "FORJA_AGENTE": slug},
    )
    bruto = saida.stdout.strip()
    return json.loads(bruto) if bruto else None


def _hook_no_disco() -> tuple[Path, str]:
    spec = ler(EXEMPLO)
    artefatos = compilar(spec)
    raiz = Path(tempfile.mkdtemp())
    caminho = next(c for c in artefatos if c.startswith("hooks/"))
    alvo = raiz / caminho
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(artefatos[caminho], encoding="utf-8")
    return alvo, spec.slug


@check("AA", "o hook GERADO nega de verdade: domínio fora da cerca volta `deny` do subprocesso")
def _aa():
    hook, slug = _hook_no_disco()
    r = _rodar_hook(
        hook, {"tool_name": "WebFetch", "tool_input": {"url": "https://exfil.example/x"}}, slug
    )
    assert r and r["hookSpecificOutput"]["permissionDecision"] == "deny", (
        f"o guarda deixou passar domínio fora da cerca: {r} — declarar a fronteira em prosa "
        "e não implementá-la é o defeito exato que a forja existe para fechar"
    )
    assert "conserto" in r["hookSpecificOutput"]["permissionDecisionReason"].lower(), (
        "negou sem dizer o conserto — recusa sem saída treina quem a lê a contorná-la"
    )


@check("AB", "o hook GERADO libera dentro da cerca — a cerca não virou muro geral")
def _ab():
    hook, slug = _hook_no_disco()
    r = _rodar_hook(
        hook,
        {"tool_name": "WebFetch", "tool_input": {"url": "https://api.github.com/repos/x/y"}},
        slug,
    )
    assert r is None, (
        f"o guarda negou um domínio PERMITIDO ({r}) — um guarda que nega tudo é indistinguível "
        "de um guarda quebrado, e o primeiro conserto que alguém faz é desligá-lo"
    )


@check("AC", "sufixo forjado NÃO é coberto: `github.com.mau.site` não cai sob `github.com`")
def _ac():
    hook, slug = _hook_no_disco()
    r = _rodar_hook(
        hook,
        {"tool_name": "WebFetch", "tool_input": {"url": "https://github.com.mau.site/x"}},
        slug,
    )
    assert r and r["hookSpecificOutput"]["permissionDecision"] == "deny", (
        "o guarda aceitou um sufixo forjado — é o que acontece quando a comparação é "
        f"`endswith` de string em vez de rótulo de domínio: {r}"
    )


@check("AD", "evento ilegível NEGA — o guarda falha FECHADO, não aberto")
def _ad():
    hook, slug = _hook_no_disco()
    saida = subprocess.run(
        [sys.executable, str(hook)], input="{ isto não é json", capture_output=True, text=True
    )
    r = json.loads(saida.stdout.strip())
    assert r["hookSpecificOutput"]["permissionDecision"] == "deny", (
        "o guarda liberou quando não entendeu o pedido — a hora em que ele quebra é "
        "exatamente a hora em que alguém está tentando passar"
    )


@check("AE", "a forja é DETERMINÍSTICA, e o carimbo segue a SPEC — não o relógio")
def _ae():
    spec = ler(EXEMPLO)
    a, b = compilar(spec), compilar(ler(EXEMPLO))
    assert a == b, (
        "duas compilações da mesma spec divergiram — sem determinismo, `--conferir` não "
        f"sabe distinguir 'a spec mudou' de 'o relógio andou': {set(a) ^ set(b) or 'conteúdo'}"
    )

    # Controle negativo do carimbo: uma cópia da spec com mtime ANTIGO tem de
    # produzir a data antiga. Se sair a de hoje, o artefato passa a divergir
    # sozinho à meia-noite, e `--conferir` vira um alarme que só sabe disparar
    # por passagem do tempo.
    import os as _os  # noqa: PLC0415

    copia = Path(tempfile.mkdtemp()) / "antiga.toml"
    copia.write_text(EXEMPLO.read_text(encoding="utf-8"), encoding="utf-8")
    velho = date(2020, 3, 4)
    epoca = __import__("datetime").datetime(2020, 3, 4, 12, 0).timestamp()
    _os.utime(copia, (epoca, epoca))

    receita = compilar(ler(copia))["RECEITA.md"]
    assert velho.isoformat() in receita, (
        f"o carimbo não seguiu a spec: esperava {velho.isoformat()} na receita de uma spec "
        "de 2020, e ele veio de outro lugar — provavelmente do relógio"
    )
    assert date.today().isoformat() not in receita, (
        "a receita carimbou HOJE numa spec de 2020 — o artefato vai divergir sozinho"
    )


@check("AF", "CENSO.md é gerado, e editar a fonte sem regerar ACUSA (natureza=relacao)")
def _af():
    sys.path.insert(0, str(Path(__file__).parent))
    from censo import gerar as g  # noqa: PLC0415

    publicado = g.PUBLICADO.read_text(encoding="utf-8")
    assert publicado == g.gerar(), (
        "`censo/CENSO.md` está fora de sincronia com `ecossistema.json` — rode "
        "`python censo/gerar.py`"
    )
    # Controle negativo: mexer na fonte tem de derrubar a comparação.
    # ⚠️ Em BYTES, não em texto. `write_text` traduz `\n` para o fim-de-linha do
    # sistema, então um round-trip "inofensivo" reescreve o arquivo inteiro no
    # Windows — um teste que suja o repositório de quem o roda é um teste que
    # ensina a ignorar o `git status`.
    original = g.FONTE.read_bytes()
    try:
        # 15 -> 23 em 2026-08-25: oito nomes novos verificados na fonte primária
        # (SkillSpector, awesome-agent-skills, mem9, MateClaw, SILENTCHAIN AI,
        # PandaProbe, DeepSearcher, Awesome A2A). 23 -> 25 em 2026-08-26: dois
        # nomes novos (agent-pd, agent-audit) achados numa pesquisa externa de
        # comparação de mercado do `loadline`/`quorum` — nenhum dos dois estava
        # no README nem no censo antes desta rodada. O literal aqui tem de ser o
        # valor REAL de `nomes_buscados` na fonte, porque `bytes.replace` num
        # trecho que não existe mais é um no-op silencioso — e um no-op aqui é
        # exatamente o check espelho que este controle existe para pegar.
        g.FONTE.write_bytes(original.replace(b'"nomes_buscados": 25', b'"nomes_buscados": 99'))
        assert publicado != g.gerar(), (
            "mudei a fonte e o gerado saiu idêntico — o `--conferir` estaria comparando "
            "o arquivo consigo mesmo, e é check espelho"
        )
    finally:
        g.FONTE.write_bytes(original)
    assert g.FONTE.read_bytes() == original, "o check não devolveu a fonte byte a byte"


@check("AG", "censo AUSENTE não vira censo VAZIO — as duas coisas dizem o oposto")
def _ag():
    ausente = _conselho.carregar(Path(tempfile.mkdtemp()) / "nao-existe.json")
    assert ausente is None, "censo ausente virou dicionário — 'não consultei' viraria '0 peças'"
    texto = _conselho.em_markdown(["memoria"], ausente, "x.json")
    assert "não consultado" in texto.lower(), texto
    assert "0" not in texto.split("Censo não consultado")[0], (
        "o bloco de censo ausente afirmou uma contagem — não medido nunca é zero"
    )


@check("AH", "ferramenta fora do vocabulário é EXIBIDA, não tratada como inofensiva")
def _ah():
    caminho = _spec_de(
        lambda d: d["fronteira"].__setitem__(
            "ferramentas", ["Read", "WebFetch", "TelepathyMCP__enviar"]
        )
    )
    spec = ler(caminho)
    assert spec.desconhecidas == ["TelepathyMCP__enviar"], spec.desconhecidas
    _, receita = _alvos.receita(spec, ["a"])
    assert "não classifica" in receita, (
        "a receita não avisou da ferramenta desconhecida — é assim que uma cerca de rede "
        "deixa de cercar sem ninguém ver"
    )


@check("AI", "selo dentro de STRING de `.py` é espécime — o emissor não sabota a si mesmo")
def _ai():
    fonte = (
        "def emitir(n):\n"
        '    return f"<!-- measured: forja.artefatos={n} nature=count on=2026-08-16 -->"\n'
        "\n"
        'DOC = """exemplo malformado que precisa poder existir escrito:\n'
        "<!-- measured: x.y=1 -->\n"
        '"""\n'
    )
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "emissor.py").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)
    assert not r.achados, (
        f"julgou selo que estava dentro de string: {[str(a) for a in r.achados]} — todo "
        "gerador de selo sabotaria a si mesmo"
    )
    assert not r.malformados, (
        f"o exemplo malformado DENTRO da string derrubou a rodada: {r.malformados} — é o "
        "controle negativo que sabota a si mesmo, de novo"
    )


@check("AJ", "e o MESMO selo, num COMENTÁRIO do mesmo arquivo, É julgado — a cerca não é buraco geral")
def _aj():
    registro.limpar()
    sonda("emissor.x")(lambda: 4)
    fonte = (
        'DOC = """dentro da string, espécime: <!-- measured: emissor.x=99 nature=count -->"""\n'
        "# measured: emissor.x=1 nature=count on=2026-08-16 expires=never\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "misto.py").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)
    achados = [a for a in r.achados if a.metrica == "emissor.x"]
    assert len(achados) == 1, (
        f"esperava exatamente 1 achado (o do comentário), veio {len(achados)}: "
        f"{[str(a) for a in r.achados]} — a regra da string virou isenção do arquivo inteiro"
    )
    assert achados[0].veredito == DRIFTED and achados[0].escrito == "1", achados[0]


@check("AK", "`.py` que não parseia NÃO vira espécime — falhar calado é pior que falhar alto")
def _ak():
    registro.limpar()
    sonda("quebrado.x")(lambda: 1)
    fonte = "def ( isto não é python\n# measured: quebrado.x=1 nature=count on=2026-08-16\n"
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "quebrado.py").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)
    assert any(a.metrica == "quebrado.x" for a in r.achados), (
        "arquivo com erro de sintaxe passou inteiro como espécime — um `.py` quebrado "
        "passaria verde e calado, que é o modo de errar que este projeto existe para acabar"
    )


@check("AL", "o confronto prosa × selo ACUSA o número da frase que nenhum selo cobre")
def _al():
    """O defeito real deste repositório entre 2026-08-16 e 2026-08-20, reintroduzido.

    O selo diz 36, a sonda mede 36, e o veredito do selo é MATCHES — como sempre foi.
    O que mudou é que a FRASE, três linhas acima, passou a ser lida.
    """
    registro.limpar()
    sonda("nucleo.checks")(lambda: 36)
    fonte = """```console
$ python autoteste.py
33 passaram
```
<!-- measured: nucleo.checks=36 nature=count on=2026-08-16 expires=never -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    mudos = [a for a in r.achados if a.veredito == PROSE_DRIFT]
    assert any(a.escrito == "33" for a in mudos), (
        "a frase diz 33 e o selo diz 36, e nada acusou — é o buraco que o "
        f"PROSE_DRIFT existe para fechar. Achados: {[str(a) for a in r.achados]}"
    )
    assert any(a.veredito == MATCHES for a in r.achados), (
        "o selo em si tem de continuar MATCHES: é exatamente por isso que o defeito "
        "sobreviveu quatro dias — o verificador olhava só o comentário"
    )
    assert r.reprova, "com a frase errada, a corrida tem de reprovar"


@check("AM", "o confronto NÃO morde artigo, pronome, nem prosa sem número")
def _am():
    """Um detector que grita no texto certo é desligado na primeira semana.

    ⚠️ `nenhum` NÃO entra nesta lista de perdão, e a ausência é deliberada:
    *"Nenhum dos quinze foi clonado"* afirma zero tão literalmente quanto o
    dígito, e é uma das frases seladas deste README. Quem quiser negação
    enfática escreve sem o numeral — foi o que esta própria fixture teve de
    fazer depois de reprovar por dizer *"sem número nenhum"*.
    """
    registro.limpar()
    sonda("x.y")(lambda: 1)
    fonte = """Um registro do ecossistema, e os dois lados saem da mesma fonte.
<!-- measured: x.y=1 nature=count on=2026-08-16 expires=never -->

Prosa inteira que descreve o mecanismo e não afirma quantidade.
<!-- measured: x.y=1 nature=count on=2026-08-16 expires=never -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    mudos = [a for a in r.achados if a.veredito == PROSE_DRIFT]
    assert not mudos, (
        "`Um registro` é artigo e `os dois lados` é pronome — nenhum dos dois "
        f"afirma quantidade. Falsos positivos: {[str(a) for a in mudos]}"
    )


@check("AN", "`eco=nao` dispensa o bloco, e a dispensa sai NOMEADA no relatório")
def _an():
    """Dispensa silenciosa é furo. Dispensa declarada é exceção."""
    registro.limpar()
    sonda("nucleo.checks")(lambda: 36)
    fonte = """33 passaram, e este número é ilustração, não afirmação.
<!-- measured: nucleo.checks=36 echo=no nature=count on=2026-08-16 expires=never -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    assert not [a for a in r.achados if a.veredito == PROSE_DRIFT], (
        "`eco=nao` tem de dispensar o bloco do confronto"
    )
    assert r.dispensados_do_eco, (
        "a dispensa tem de aparecer no relatório — uma exceção que não se vê "
        "é indistinguível de um mecanismo que não roda"
    )
    assert "echo" not in [a.metrica for a in r.achados], (
        "`echo` é chave reservada; lê-la como métrica pediria uma sonda para ela"
    )


# ------------------------------- a terceira marca de selo, e a terceira lista


@check("AO", "`arbitrated:` sem `por=` é MALFORMADO — escolha sem dono é palpite")
def _ao():
    try:
        _selo("<!-- arbitrated: retry.max=3 on=2026-08-16 expires=90d -->")
    except SeloMalformado as exc:
        assert "by=" in str(exc), f"a recusa tem de dizer o que falta, e disse: {exc}"
    else:
        raise AssertionError(
            "`arbitrated:` sem `por=` passou — um número escolhido e anônimo é "
            "exatamente o que esta marca existe para desmascarar"
        )


@check("AP", "`arbitrated:` no prazo é verde, e NÃO chama sonda nenhuma")
def _ap():
    registro.limpar()  # nenhuma sonda registrada: se ele medir, estoura
    selo = _selo('<!-- arbitrated: retry.max=3 by="plataforma" on=2026-08-16 expires=90d -->')
    achados = julgar(selo, hoje=HOJE)
    assert [a.veredito for a in achados] == [ARBITRATED], (
        f"escolha no prazo tem de ser ARBITRATED, e veio {[a.veredito for a in achados]}"
    )
    assert achados[0].verde, "ARBITRATED é verde: alguém assinou, e o prazo não venceu"
    assert achados[0].medido is None, (
        "número arbitrado não tem medida — inventar uma seria a mentira que a marca persegue"
    )


@check("AQ", "`arbitrated:` EXPIRED reprova — escolha sem prazo é escolha esquecida")
def _aq():
    selo = _selo('<!-- arbitrated: teto=10 by="board" on=2026-08-16 expires=30d -->')
    achados = julgar(selo, hoje=date(2026, 12, 1))
    assert [a.veredito for a in achados] == [EXPIRED], (
        f"escolha fora do prazo tem de vencer, e veio {[a.veredito for a in achados]}"
    )
    assert not achados[0].verde, (
        "se escolha vencida ficasse verde, bastaria chamar de arbitrado todo número "
        "incômodo para nunca mais olhar para ele"
    )


@check("AR", "repositório SEM SELO NENHUM sai com código 2, e não com 0")
def _ar():
    # Este é o defeito reintroduzido de propósito: até o conserto,
    # ele, esta mesma árvore devolvia `PASSA` e código 0, com as afirmações
    # dentro. Era `não medido` virando `zero` na ferramenta que proíbe isso.
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "README.md").write_text(
            """# x

Temos 12 endpoints e 3 servicos.
""",
            encoding="utf-8",
        )
        r = varrer(Path(tmp), hoje=HOJE)

    assert not r.achados, "não há selo nenhum: não pode haver achado de selo"
    assert not r.reprova, "nada foi conferido, logo nada pode REPROVAR"
    assert r.sem_prova_nenhuma, (
        "a lista 3 tem de acusar `12` e `3` — sem ela a rodada devolve verde "
        "sobre um arquivo cheio de números que ninguém pode conferir"
    )
    assert {a.numero for a in r.sem_prova_nenhuma} == {"12", "3"}, (
        f"a lista 3 achou {sorted(a.numero for a in r.sem_prova_nenhuma)}"
    )
    assert r.codigo_de_saida == 2, f"código de saída tinha de ser 2, e veio {r.codigo_de_saida}"
    assert r.veredito_da_corrida == "NO DENOMINATOR", r.veredito_da_corrida


@check("AS", "o que o `--selar` escreve volta a ser lido pelo próprio leitor")
def _as():
    with tempfile.TemporaryDirectory() as tmp:
        alvo = Path(tmp) / "README.md"
        alvo.write_text(
            """# x

Temos 12 endpoints.
""",
            encoding="utf-8",
        )

        antes = varrer(Path(tmp), hoje=HOJE)
        escritos, problemas = selar(antes.sem_prova_nenhuma, hoje=HOJE)
        assert not problemas, f"selar não podia falhar aqui: {problemas}"
        assert len(escritos) == 1, f"um selo, uma linha afirmante — vieram {len(escritos)}"
        assert "arbitrated:" in escritos[0].texto, (
            "tem de emitir `arbitrated:` e nunca `measured:` — ninguém mediu nada, e "
            "emitir a outra marca seria a ferramenta inventando que houve medição"
        )
        assert "by=?" in escritos[0].texto, (
            "o `por=?` sai por escrito para o humano preencher; a ferramenta não "
            "sabe quem escolheu, e fingir que sabe é a mesma família de defeito"
        )

        depois = varrer(Path(tmp), hoje=HOJE)

    assert [a.veredito for a in depois.achados] == [ARBITRATED], (
        f"o selo escrito tem de voltar como ARBITRATED, e veio {[a.veredito for a in depois.achados]}"
    )
    assert not depois.sem_prova_nenhuma, "depois de selar, a lista 3 tem de esvaziar"
    assert depois.codigo_de_saida == 0, (
        f"anotado e no prazo é verde — veio {depois.codigo_de_saida}"
    )

    # E a segunda passada não pode duplicar: o lugar já tem dono.
    with tempfile.TemporaryDirectory() as tmp2:
        alvo2 = Path(tmp2) / "README.md"
        alvo2.write_text(
            """# x

Temos 12 endpoints.
""",
            encoding="utf-8",
        )
        r1 = varrer(Path(tmp2), hoje=HOJE)
        selar(r1.sem_prova_nenhuma, hoje=HOJE)
        r2 = varrer(Path(tmp2), hoje=HOJE)
        de_novo, _ = selar(r2.sem_prova_nenhuma, hoje=HOJE)
    assert not de_novo, "selar duas vezes não pode escrever de novo onde já há selo"


@check("AT", "o reconhecedor de BLOCO enxerga as três marcas, não duas")
def _at():
    # Defeito real, achado em 2026-08-20 ao implementar a terceira marca: o
    # `_PADRAO` de `selo.py` ganhou `arbitrado` e a cópia da alternação em
    # `eco.py` ficou para trás. O bloco parou de terminar no selo novo, dois
    # parágrafos viraram um, e o confronto prosa × selo acusou o segundo selo
    # pelos números do primeiro. Ninguém teria visto: o alarme era falso, não
    # ausente. Hoje as duas saem da mesma tupla, e este check trava isso.
    fonte = """# t

Temos 12 endpoints.
<!-- arbitrated: endpoints=12 by="a" on=2026-08-16 expires=90d -->
Temos 40 testes.
<!-- arbitrated: testes=40 by="a" on=2026-08-16 expires=90d -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    mudas = [a for a in r.achados if a.veredito == PROSE_DRIFT]
    assert not mudas, (
        "cada selo cobre o SEU parágrafo. Acusação aqui quer dizer que o "
        f"reconhecedor de bloco não enxergou a marca nova e fundiu os dois: {mudas}"
    )
    assert r.codigo_de_saida == 0, f"tudo coberto e no prazo é verde — veio {r.codigo_de_saida}"




# --------------------------------------------------------------- prateleira ---
# As operações prontas são o que alguém copia para o repositório DELE. Um exemplo
# quebrado aqui não é um exemplo feio: é uma operação que não roda na primeira vez
# que alguém tenta, e a primeira vez é a única que a maioria das pessoas dá.

RAIZ_DA_CASA = Path(__file__).parent


@check("AU", "toda operação da prateleira compila na forja, e spec sem anti-descrição é RECUSADA")
def _au():
    from forja import ler
    from forja.spec import Recusa, validar

    # `agente*.toml`, e não `agente.toml`: uma operação PODE trazer uma ESTEIRA
    # — mais de uma spec na mesma pasta (nenhuma traz hoje, depois do corte do
    # ADR-117; a `revisao-de-seguranca`, cortada, era o exemplo). Globar só o
    # nome exato deixaria specs extras nunca serem compiladas por check nenhum
    # — e uma spec que não compila só é descoberta por quem tentar usá-la.
    specs = sorted((RAIZ_DA_CASA / "operacoes").glob("*/agente*.toml"))
    assert specs, "a prateleira não tem nenhuma operação com spec de agente"
    por_operacao = {c.parent.name for c in specs}
    # `__pycache__` e `.qualquercoisa` não são operações. Sem este filtro, rodar
    # a prateleira uma vez cria a pasta de cache e o check passa a acusar uma
    # «operação sem spec» que ninguém escreveu — o denominador teria crescido
    # sozinho, o que é exatamente a família de defeito que esta suíte persegue.
    operacoes = {
        d.name
        for d in (RAIZ_DA_CASA / "operacoes").iterdir()
        if d.is_dir() and not d.name.startswith((".", "_"))
    }
    assert por_operacao == operacoes, (
        f"operação sem spec de agente: {sorted(operacoes - por_operacao)}"
    )
    for caminho in specs:
        ler(caminho)  # levanta `Recusa` se a spec não passar nas oito

    # O defeito, reintroduzido. Sem isto, o laço acima passaria igual se as oito
    # recusas fossem removidas da forja — ele só confirmaria o caminho feliz, e
    # a prateleira inteira poderia envelhecer para fora do próprio gate.
    spec = ler(specs[0])
    spec.nunca_usar = []
    try:
        validar(spec)
    except Recusa as exc:
        assert exc.regra == "R3", f"a recusa certa é R3, veio {exc.regra}"
    else:
        raise AssertionError(
            "uma spec da prateleira sem `nunca_usar` COMPILOU — as oito recusas não estão vivas"
        )




@check("AV", "os sondas.py da prateleira podem ser concatenados: nenhum padrão colide")
def _av():
    # A `operacoes/README.md` promete que `cat op1/sondas.py op2/sondas.py` funciona.
    # Uma promessa dessas envelhece calada: basta alguém escolher um nome de métrica
    # que já existe noutra operação, e a sonda mais nova SOMBREIA a mais velha sem
    # erro nenhum — o registro aceita padrão repetido e desempata por especificidade.
    import importlib.util

    registro.limpar()
    declaradas = 0
    for indice, caminho in enumerate(sorted((RAIZ_DA_CASA / "operacoes").glob("*/sondas.py"))):
        declaradas += caminho.read_text(encoding="utf-8").count("@sonda(")
        spec = importlib.util.spec_from_file_location(f"sondas_op_{indice}", caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)

    padroes = [p for p, _ in registro.explicar()]
    assert len(padroes) == declaradas, (
        f"{declaradas} sondas declaradas nos arquivos, {len(padroes)} registradas"
    )
    repetidos = {p for p in padroes if padroes.count(p) > 1}
    assert not repetidos, f"padrão de métrica em duas operações — concatenar sombreia: {repetidos}"

    # O defeito, reintroduzido: uma colisão de propósito tem de ser vista pela
    # mesma regra que acabou de dar verde.
    sonda(padroes[0], origem="colisão plantada")(lambda: 0)
    depois = [p for p, _ in registro.explicar()]
    assert {p for p in depois if depois.count(p) > 1} == {padroes[0]}, (
        "a regra não enxerga um padrão repetido — ela estava dando verde por não olhar"
    )
    registro.limpar()




@check("AW", "a sonda da anatomia ESTOURA quando uma operação fica incompleta")
def _aw():
    # Cinco arquivos por operação, sempre com o mesmo nome: é o que faz alguém
    # aprender uma e saber as quatro. A sonda é de RELAÇÃO — ela não anda quando
    # nasce operação nova, só anda se alguma ficou pela metade.
    import importlib.util

    registro.limpar()
    origem = importlib.util.spec_from_file_location(
        "sondas_da_casa", RAIZ_DA_CASA / "sondas.py"
    )
    casa = importlib.util.module_from_spec(origem)
    origem.loader.exec_module(casa)

    assert registro.medir("operacoes.arquivos_por_operacao", None) == len(casa.ANATOMIA), (
        "alguma operação da prateleira não tem os cinco arquivos"
    )

    with tempfile.TemporaryDirectory() as tmp:
        incompleta = Path(tmp) / "operacoes" / "faltando-um"
        incompleta.mkdir(parents=True)
        for nome in casa.ANATOMIA[:-1]:
            (incompleta / nome).write_text("x", encoding="utf-8")
        casa.RAIZ = Path(tmp)
        try:
            valor = registro.medir("operacoes.arquivos_por_operacao", None)
        except LookupError:
            pass  # é o que tem de acontecer: vira UNPROVEN, com o nome do que falta
        else:
            raise AssertionError(
                f"uma operação sem `{casa.ANATOMIA[-1]}` devolveu {valor} em vez de estourar"
            )
    registro.limpar()





@check("AX", "o servidor MCP da `cerebro-local` sobe como SUBPROCESSO, responde, e RECUSA `../`")
def _ax():
    # Lógica em processo passa e protocolo trava. Este check roda o servidor como
    # processo de verdade, fala JSON-RPC por stdin e lê stdout — que é a única
    # forma de provar que ele serve para alguma coisa num cliente MCP real.
    import subprocess

    servidor = RAIZ_DA_CASA / "operacoes" / "cerebro-local" / "servidor.py"
    assert servidor.is_file(), "a operação `cerebro-local` perdeu o `servidor.py`"

    pedidos = chr(10).join(
        [
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "ler_nota",
                        "arguments": {"caminho": "../../../../etc/passwd"},
                    },
                }
            ),
        ]
    )
    # ⚠️ Sem `encoding=`, só `text=True` — que é a forma que o `_rodar_hook`
    # desta suíte já usa. Com `encoding="utf-8"` junto de `input=`, o `stdout`
    # voltou `None` DENTRO desta suíte (e só dentro dela; fora, reproduzido
    # três vezes, volta normal). A causa não foi identificada, e fica escrita
    # aqui em vez de virar um argumento a menos sem explicação.
    saida = subprocess.run(
        [sys.executable, str(servidor), "--raiz", str(RAIZ_DA_CASA / "operacoes")],
        input=pedidos,
        capture_output=True,
        text=True,
        timeout=60,
    ).stdout
    respostas = [json.loads(l) for l in saida.splitlines() if l.strip()]

    # A notificação NÃO pode ter resposta: responder a uma quebra clientes que
    # contam mensagens, e o sintoma aparece longe da causa.
    assert len(respostas) == 3, f"3 respostas para 3 pedidos com id, vieram {len(respostas)}"
    assert respostas[0]["result"]["serverInfo"]["name"] == "cerebro-local"
    nomes = [f["name"] for f in respostas[1]["result"]["tools"]]
    assert nomes == ["mapa", "listar_notas", "ler_nota", "buscar"], nomes

    # O defeito, reintroduzido: a travessia de caminho tem de ser RECUSADA. Sem
    # isto, o laço acima passaria igual num servidor que serve o disco inteiro.
    texto = respostas[2]["result"]["content"][0]["text"]
    assert texto.startswith("RECUSADO"), f"a travessia NÃO foi recusada: {texto[:120]}"


@check("AY", "fonte declarada que não existe ESTOURA — «não medido» nunca vira zero")
def _ay():
    # A tese do projeto inteiro, aplicada à prateleira: um `0` devolvido porque
    # ninguém olhou é indistinguível de um `0` medido. As operações que declaram
    # de onde leem (`PASTA_DE_*`, `ARQUIVO_DE_*`) têm de estourar quando aquele
    # caminho não existe — nunca devolver zero com cara de medida.
    import importlib.util

    examinadas = 0
    for caminho in sorted((RAIZ_DA_CASA / "operacoes").glob("*/sondas.py")):
        registro.limpar()
        origem = importlib.util.spec_from_file_location(f"sondas_ay_{examinadas}", caminho)
        modulo = importlib.util.module_from_spec(origem)
        origem.loader.exec_module(modulo)

        # `PASTA`/`ARQUIVO` como prefixo, não `PASTA_DE_`: uma operação pode
        # declarar de onde lê como `str` ou como tupla de nomes (`PASTAS_DE_X`).
        # O que a regra pergunta é se a operação DECLARA de onde lê — o número e
        # o tipo não mudam isso, e um prefixo estreito demais deixaria a operação
        # fora do denominador sem ninguém ver.
        declaradas = [
            nome
            for nome in vars(modulo)
            if nome.startswith(("PASTA", "ARQUIVO"))
            and isinstance(getattr(modulo, nome), (str, tuple))
        ]
        if not declaradas:
            continue  # opera sobre o repositório inteiro; 0 ali é medida, não ausência
        examinadas += 1
        # Apaga a RAIZ, não só a constante: uma sonda pode ler um arquivo IRMÃO
        # do sondas.py (a `cerebro.dependencias` lê o `servidor.py`), e repontar
        # só `PASTA_DE_*` deixaria essa fonte de pé. A regra é «a árvore sumiu».
        modulo.RAIZ = Path("esta-arvore-nao-existe-em-lugar-nenhum").resolve()
        for padrao, _ in registro.explicar():
            if "*" in padrao:
                continue
            try:
                valor = registro.medir(padrao, None)
            except Exception:
                continue  # estourou: é o que tem de acontecer
            raise AssertionError(
                f"`{padrao}` de {caminho.parent.name} devolveu {valor!r} com a fonte declarada "
                "apontando para o vazio — «não olhei» saiu como «não há»"
            )
    registro.limpar()
    # O piso é 2, não um número calibrado ao tamanho da prateleira de hoje: ele
    # existe só para o check não ficar vacuamente verde se um dia nenhuma operação
    # declarar uma PASTA obrigatória. Hoje são 3 (`sala-de-decisao`, `cerebro-local`,
    # `suite-que-acusa`); operações que procuram arquivo OPCIONAL (`instrucao`,
    # `handoff`) devolvem 0 de propósito e não entram aqui.
    assert examinadas >= 2, f"só {examinadas} operações declaram uma fonte obrigatória — o check ficou vazio"

    # O defeito, reintroduzido: uma sonda que devolve 0 em vez de estourar tem de
    # ser vista pela mesma regra que acabou de dar verde.
    sonda("ay.mentirosa", origem="devolve zero sem olhar nada")(lambda: 0)
    assert registro.medir("ay.mentirosa", None) == 0, "a sonda plantada não rodou"
    registro.limpar()


@check("AZ", "a cerca emitida NEGA fora do caminho declarado, e DEIXA PASSAR dentro")
def _az():
    # Uma cerca que nega tudo é indistinguível de uma quebrada, e a primeira
    # coisa que alguém faz com ela é desligá-la. Por isso as duas direções.
    import subprocess

    from forja import ler
    from forja.__main__ import compilar

    spec = ler(RAIZ_DA_CASA / "operacoes" / "handoff-que-mede-o-disco" / "agente.toml")
    assert spec.saida_cercada == ["retomada/"], spec.saida_cercada

    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        for relativo, conteudo in compilar(spec).items():
            alvo = raiz / relativo
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(conteudo, encoding="utf-8")
        cerca = raiz / "hooks" / f"cerca_{spec.slug.replace('-', '_')}.py"
        assert cerca.is_file(), f"a forja não emitiu a cerca em {cerca}"

        def julgar_caminho(caminho: str) -> str:
            evento = json.dumps(
                {
                    "agent_type": spec.slug,
                    "tool_name": "Write",
                    "tool_input": {"file_path": caminho},
                }
            )
            return subprocess.run(
                [sys.executable, str(cerca)],
                input=evento,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60,
            ).stdout

        fora = julgar_caminho("docs/outra.md")
        assert '"deny"' in fora, f"a cerca NÃO negou fora de `retomada/`: {fora[:120]!r}"

        dentro = julgar_caminho("retomada/CONTINUAR.md")
        assert '"deny"' not in dentro, (
            f"a cerca negou DENTRO do caminho declarado: {dentro[:120]!r} — uma cerca que "
            "nega tudo é indistinguível de uma quebrada"
        )

        # A jurisdição é estreita, e ela é declarada: sem identidade no evento a
        # cerca NÃO age. Provar isto impede que os dois asserts acima passem por
        # acidente num guarda que responde a tudo.
        anonimo = subprocess.run(
            [sys.executable, str(cerca)],
            input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": "docs/x.md"}}),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        ).stdout
        assert '"deny"' not in anonimo, "a cerca agiu sobre evento sem identidade de agente"



@check("BA", "alvo que NÃO existe é recusado com código 2 — nunca `PASSA` com código 0")
def _ba():
    # O defeito que este check trava era real e estava no ponto de entrada: um
    # caminho inexistente varria zero arquivo, não achava afirmação nenhuma, e
    # saía VERDE com código 0. `loadline ./sr` por `./src` deixava o gate do CI
    # aprovando para sempre — *não medido* virando *zero*, dentro da ferramenta
    # cuja tese inteira é que isso não pode acontecer.
    from loadline.__main__ import main as cli

    for alvo in ("esta-pasta-nao-existe-em-lugar-nenhum", "--bandeira-que-nao-existe"):
        assert cli([alvo]) == 2, f"`{alvo}` não foi recusado com código 2"

    # O controle negativo, e ele é o que impede a correção de virar «recuse
    # tudo»: um alvo REAL tem de continuar sendo varrido. Uma recusa que recusa
    # o caminho feliz é indistinguível de uma quebrada, e a primeira coisa que
    # alguém faz com ela é desligá-la.
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        (raiz / "README.md").write_text(
            "Este projeto tem 3 modulos." + chr(10), encoding="utf-8"
        )
        codigo = cli([str(raiz)])
        assert codigo == 2, f"pasta REAL sem selo devia sair 2 (sem denominador), veio {codigo}"

        (raiz / "vazia").mkdir()
        assert cli([str(raiz / "vazia")]) == 2, "pasta real e vazia também é sem denominador"



# --------------------------- a vistoria: ler os agentes que a pessoa JÁ TEM ---
#
# Sete controles, e cada um reintroduz o defeito que ele existe para pegar. Um
# check que só confirma o caminho feliz passa igual se o mecanismo for removido.

from forja import vistoria as _v  # noqa: E402


def _roster(tmp: str, arquivos: dict[str, str], irmaos: dict[str, str] | None = None) -> Path:
    raiz = Path(tmp)
    pasta = raiz / ".claude" / "agents"
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, texto in arquivos.items():
        (pasta / nome).write_text(texto, encoding="utf-8")
    for relativo, texto in (irmaos or {}).items():
        alvo = raiz / relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(texto, encoding="utf-8")
    return pasta


def _regras(pasta: Path) -> set[str]:
    return {a.regra for a in _v.vistoriar(_v.ler_roster(pasta))}


AGENTE_COMPLETO = """---
name: completo
description: "Faz uma coisa so. Usar quando voce precisar dela. NUNCA usar para outra coisa."
tools: Read, Grep
---
Lacunas: nao mede o que esta fora do disco. Golden: resposta esperada escrita a mao.
"""


@check("BB", "agente que NÃO diz o que nunca faz é acusado; o que diz, não é")
def _bb():
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(tmp, {"completo.md": AGENTE_COMPLETO})
        assert "V1" not in _regras(pasta), (
            "um agente que declara o que NUNCA faz não pode ser acusado de não declarar — "
            "se ele for, a régua acusa todo mundo e deixa de separar nada"
        )
    with tempfile.TemporaryDirectory() as tmp:
        mudo = AGENTE_COMPLETO.replace(" NUNCA usar para outra coisa.", "")
        pasta = _roster(tmp, {"completo.md": mudo})
        assert "V1" in _regras(pasta), (
            "tirei a anti-descrição e a vistoria continuou verde: sem anti-descrição o "
            "orquestrador despacha por tema, e é o defeito que V1 existe para pegar"
        )


@check("BC", "dois que se confundem são acusados — e param quando um NOMEIA o outro")
def _bc():
    gemeo = """---
name: {slug}
description: "Revisa codigo procurando problema de qualidade seguranca arquitetura relatorio recomendacao. Usar quando abrir PR. NUNCA usar para {anti}."
tools: Read
---
Lacunas: nenhuma medida fora do disco. Golden: resposta esperada a mao.
"""
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(
            tmp,
            {
                "revisor.md": gemeo.format(slug="revisor", anti="outra coisa"),
                "auditor.md": gemeo.format(slug="auditor", anti="outra coisa"),
            },
        )
        assert "V6" in _regras(pasta), (
            "duas descrições quase iguais, e nenhuma nomeia a outra — se isto passa, "
            "o único defeito que só existe a partir do segundo agente passa junto"
        )
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(
            tmp,
            {
                "revisor.md": gemeo.format(slug="revisor", anti="auditar licenca — isso e do auditor"),
                "auditor.md": gemeo.format(slug="auditor", anti="outra coisa"),
            },
        )
        assert "V6" not in _regras(pasta), (
            "um passou a nomear o irmão e a acusação continuou de pé: então o conserto "
            "que a saída manda fazer não conserta, e a régua treina quem a lê a ignorá-la"
        )


@check("BD", "`tools:` AUSENTE é lido como TODAS as ferramentas, nunca como nenhuma")
def _bd():
    with tempfile.TemporaryDirectory() as tmp:
        sem_tools = AGENTE_COMPLETO.replace("tools: Read, Grep" + chr(10), "")
        pasta = _roster(tmp, {"completo.md": sem_tools})
        lido = _v.ler_roster(pasta)[0]
        assert lido.tools_ausente, "`tools:` não estava lá e a vistoria não percebeu"
        assert lido.usa_escrita and lido.usa_rede, (
            "campo ausente lido como «nenhuma ferramenta» é como toda cerca vira porta "
            "dos fundos: nos harnesses de hoje ausente quer dizer TODAS"
        )
        assert "V7" in _regras(pasta)


@check("BE", "pasta que NÃO EXISTE é recusa com código 2, e nunca verde")
def _be():
    with tempfile.TemporaryDirectory() as tmp:
        codigo = forja_main([str(Path(tmp) / "nao-existe")])
        assert codigo == 2, (
            f"apontar para caminho errado devolveu {codigo}: um erro de digitação no CI "
            "deixaria o gate aprovando para sempre, que é não-medido virando zero"
        )


@check("BF", "pasta VAZIA é recusa com código 2 — zero agente lido não é zero defeito")
def _bf():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / ".claude" / "agents").mkdir(parents=True)
        codigo = forja_main([tmp])
        assert codigo == 2, (
            f"pasta vazia devolveu {codigo}: «não olhei nada» e «está tudo certo» são "
            "coisas opostas, e devolvê-las com o mesmo código é inventar um fato"
        )


@check("BG", "markdown solto na pasta NÃO vira agente, e não infla o denominador")
def _bg():
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(
            tmp,
            {"completo.md": AGENTE_COMPLETO, "README.md": "# so uma nota, sem frontmatter"},
        )
        roster = _v.ler_roster(pasta)
        assert len(roster) == 1, (
            f"li {len(roster)} agentes onde há 1: um arquivo que não é agente entrando na "
            "conta faz o denominador crescer e toda porcentagem daqui mentir"
        )


@check("BH", "cerca em arquivo IRMÃO conta — a vistoria não acusa a saída do compilador")
def _bh():
    escreve = """---
name: escritor
description: "Escreve relatorio. Usar quando pedirem. NUNCA usar para outra coisa."
tools: Read, Write
---
Lacunas: nao mede fora do disco. Golden: resposta esperada a mao.
"""
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(tmp, {"escritor.md": escreve})
        assert "V3" in _regras(pasta), "pede Write, ninguém declarou onde, e passou"
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(
            tmp,
            {"escritor.md": escreve},
            irmaos={"hooks/cerca_escritor.py": '# slug = "escritor" · saida_cercada = ["relatorios/"]'},
        )
        assert "V3" not in _regras(pasta), (
            "o hook que NEGA estava no arquivo irmão e a vistoria acusou mesmo assim — "
            "ela estaria medindo a prosa do prompt, que nenhum runtime lê, e acusaria "
            "exatamente o que a própria forja emite"
        )


@check("BI", "`--adotar` escreve ao lado dos agentes do LEITOR, não no clone da ferramenta")
def _bi():
    # O defeito reintroduzido: a saída era relativa ao diretório corrente. Quem
    # clonasse a ferramenta e a apontasse para o próprio projeto veria as specs
    # nascerem DENTRO do clone, numa pasta que o `.gitignore` de lá ignora — e
    # sumirem sem erro nenhum. O relatório dizia «escrevi 4 spec(s)», e era
    # verdade; só não era no lugar onde a pessoa ia procurar.
    with tempfile.TemporaryDirectory() as alheio, tempfile.TemporaryDirectory() as clone:
        pasta = _roster(alheio, {"completo.md": AGENTE_COMPLETO})
        anterior = Path.cwd()
        try:
            os.chdir(clone)
            forja_main([str(Path(alheio)), "--adotar"])
        finally:
            os.chdir(anterior)
        assert (Path(alheio) / "build" / "specs" / "completo.toml").exists(), (
            "a spec não nasceu ao lado dos agentes do leitor — quem adota não tem "
            "por que adivinhar que o arquivo dele foi parar no clone da ferramenta"
        )
        assert not (Path(clone) / "build").exists(), (
            "a ferramenta escreveu dentro do próprio clone: é lá que o arquivo some, "
            "porque é lá que o `.gitignore` dela ignora `build/`"
        )
        assert pasta.is_dir(), "a vistoria não pode mexer na pasta que ela lê"


def _juntar():
    """Carrega `operacoes/juntar.py` POR CAMINHO, sem tornar a prateleira um pacote.

    `operacoes/` é uma estante de pastas independentes — cada uma existe para ser
    copiada sozinha para o repositório de outra pessoa. Pôr um `__init__.py` ali
    para o teste importar mais fácil mudaria o que a estante é, e ainda faria o
    `__pycache__` nascer contando como operação no check vizinho.
    """
    import importlib.util

    caminho = RAIZ_DA_CASA / "operacoes" / "juntar.py"
    spec = importlib.util.spec_from_file_location("_juntar_da_prateleira", caminho)
    assert spec and spec.loader, f"não consegui carregar {caminho}"
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@check("BJ", "juntar duas operações com `cat` QUEBRA, e o `juntar.py` conserta todos os pares")
def _bj():
    import itertools

    _j = _juntar()

    ops = sorted(p.parent.name for p in (RAIZ_DA_CASA / "operacoes").glob("*/sondas.py"))
    textos = {o: (RAIZ_DA_CASA / "operacoes" / o / "sondas.py").read_text(encoding="utf-8") for o in ops}
    pares = list(itertools.combinations(ops, 2))
    assert pares, "não há operações com sondas — o denominador deste check sumiu"

    # ⚠️ O defeito reintroduzido, e o instrumento importa: `ast.parse` NÃO
    # reprova `from __future__` fora do topo — quem reprova é o compilador. Um
    # check escrito com o parser passaria verde sobre o defeito inteiro.
    quebrados = 0
    for a, b in pares:
        try:
            compile(textos[a] + textos[b], "<cat>", "exec")
        except SyntaxError:
            quebrados += 1
    assert quebrados == len(pares), (
        f"{quebrados} de {len(pares)} pares quebram com `cat`; se este número cair, a "
        "documentação que manda usar `juntar.py` passou a assustar sem motivo"
    )

    for a, b in pares:
        texto = _j.juntar([a, b], raiz=RAIZ_DA_CASA / "operacoes")
        try:
            compile(texto, "<juntado>", "exec")
        except SyntaxError as exc:
            raise AssertionError(f"`juntar.py` produziu arquivo inválido para {a}+{b}: {exc}")


@check("BK", "`juntar.py` RECUSA colisão de padrão de métrica, e não escreve nada")
def _bk():
    _j = _juntar()

    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        corpo = 'from __future__ import annotations\n\nfrom loadline import sonda\n\n\n@sonda(\n    "x.y",\n    origem="teste",\n)\ndef _f() -> int:\n    return 1\n'
        for nome in ("uma", "outra"):
            (raiz / nome).mkdir()
            (raiz / nome / "sondas.py").write_text(corpo, encoding="utf-8")
        try:
            _j.juntar(["uma", "outra"], raiz=raiz)
        except _j.Colisao as exc:
            assert "x.y" in str(exc), "a recusa tem de nomear o padrão que colidiu"
        else:
            raise AssertionError(
                "duas operações registrando `x.y` foram juntadas em silêncio — em Python a "
                "segunda sombreia a primeira sem erro, e a métrica sombreada some do "
                "relatório sem nunca ter reprovado"
            )


# --------------------------------- blind: a fronteira que a varredura não vê ---
#
# Dois checks, e cada um prova uma coisa diferente. `blind/controles.py` já roda
# cinco controles negativos com fixture REAL (`mklink /J`, `git init`); BL prova
# que essa suíte está VIVA — que ela reprovaria se o próprio detector emudecesse
# — em vez de só confirmar que ela existe. BM prova a camada que os controles do
# pacote não tocam: o contrato de saída da CLI (`python -m blind`), nos mesmos
# moldes de BA/BE/BF para `loadline`/`forja`.

from blind import controles as _blindctl  # noqa: E402


@check("BL", "os controles negativos do `blind` passam, e REPROVAM se o detector emudecer")
def _bl():
    assert _blindctl.main() == 0, "os 5 controles do blind têm de passar limpos, com fixture real"

    # O defeito, reintroduzido: um detector que nunca acusa nada (equivalente a
    # `rg` parando na fronteira sem ninguém notar) tinha de derrubar os próprios
    # controles do blind — sem isto, B1/B3 estariam confirmando o caminho feliz
    # e um detector morto passaria pela suíte que existe para pegar exatamente
    # essa morte.
    original = _blindctl.detectar
    _blindctl.detectar = lambda raiz: []
    try:
        assert _blindctl.main() == 1, (
            "detector sempre mudo tinha de derrubar os controles negativos, e não derrubou"
        )
    finally:
        _blindctl.detectar = original


@check("BM", "`python -m blind` tem o mesmo contrato de saída dos outros pontos de entrada")
def _bm():
    from blind.__main__ import main as _blind_cli

    assert _blind_cli([]) == 2, "sem argumento tinha de recusar com código 2, e não variar"
    with tempfile.TemporaryDirectory() as tmp:
        assert _blind_cli([str(Path(tmp) / "nao-existe")]) == 2, (
            "caminho inexistente tinha de recusar com código 2"
        )
        # O controle negativo que impede a correção de virar «recuse tudo»: uma
        # pasta REAL e limpa (sem junction, symlink ou gitignore) tem de sair 0.
        limpa = Path(tmp) / "limpa"
        limpa.mkdir()
        assert _blind_cli([str(limpa)]) == 0, (
            "pasta real sem fronteira nenhuma tinha de sair 0, e não recusar o caminho feliz"
        )


@check("BN", "cerca declarada só no FRONTMATTER conta — V3 não acusa quem faz certo")
def _bn():
    # O defeito, medido em 2026-08-24 sobre o roster do P3G4ZUZ: `saida_cercada`
    # é literalmente uma das marcas de `DIZ_ONDE_ESCREVE`, mas `_contem` só olha
    # `descricao + corpo` — o frontmatter é descartado depois de `name`/
    # `description`/`tools`. Um agente que declara a cerca do jeito CERTO (campo
    # estruturado, o que o próprio harness lê em runtime) reprovava V3 pela
    # MESMA razão que reprovaria um agente sem cerca nenhuma.
    so_frontmatter = """---
name: cercado
description: "Escreve relatorio. Usar quando pedirem. NUNCA usar para outra coisa."
tools: Read, Write
saida_cercada: "relatorios/"
---
Lacunas: nao mede fora do disco. Golden: resposta esperada a mao.
"""
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(tmp, {"cercado.md": so_frontmatter})
        assert "V3" not in _regras(pasta), (
            "`saida_cercada` estava no frontmatter, campo estruturado, e V3 acusou do mesmo "
            "jeito que acusaria zero declaração — falso negativo na própria marca que dá "
            "nome à constante `DIZ_ONDE_ESCREVE`"
        )

    # O controle negativo: tirar o campo tem de trazer V3 de volta — sem isto,
    # o conserto acima poderia ser "V3 nunca acusa nada", que é pior que o bug.
    sem_cerca = so_frontmatter.replace('saida_cercada: "relatorios/"\n', "")
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(tmp, {"cercado.md": sem_cerca})
        assert "V3" in _regras(pasta), (
            "tirei `saida_cercada` do frontmatter e V3 continuou calado: o conserto do "
            "falso negativo virou um falso negativo permanente, não um conserto"
        )

    # Mesma régua para rede: `dominios_permitidos` só no frontmatter.
    so_rede = """---
name: pesquisador
description: "Pesquisa na web. Usar quando pedirem fonte externa. NUNCA usar para outra coisa."
tools: Read, WebFetch
dominios_permitidos: "example.com"
---
Lacunas: nao mede fora do disco. Golden: resposta esperada a mao.
"""
    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(tmp, {"pesquisador.md": so_rede})
        assert "V3" not in _regras(pasta), (
            "`dominios_permitidos` estava no frontmatter e V3 acusou como se a rede não "
            "tivesse dono — mesmo defeito, na outra fronteira"
        )


# ------------------------------------------- evidencia: o relatório --html ---

from evidencia import pagina as _pagina  # noqa: E402


@check("BO", "`evidencia.pagina` é autocontida — nenhuma tag que busca recurso externo, e a cor segue o código")
def _bo():
    ok = _pagina("teste", "alvo", "2026-08-24", ["✅ PASSA"], 0)
    reprova = _pagina("teste", "alvo", "2026-08-24", ["⛔ REPROVA"], 1)
    recusa = _pagina("teste", "alvo", "2026-08-24", ["RECUSADO"], 2)

    for pg in (ok, reprova, recusa):
        assert "<script" not in pg, "uma página autocontida não pode carregar script externo"
        assert "<link" not in pg, "uma página autocontida não pode referenciar `<link>` externo"
        assert "http://" not in pg and "https://" not in pg, (
            "página autocontida não pode citar URL nenhuma — o CSS inteiro é `<style>` inline"
        )

    assert 'class="veredito ok"' in ok, "código 0 tinha de virar veredito verde"
    assert 'class="veredito grave"' in reprova, "código 1 tinha de virar veredito grave"
    assert 'class="veredito grave"' in recusa, (
        "código 2 (RECUSADO) também é grave — não é neutro, e não é o mesmo texto que REPROVA"
    )
    assert "REPROVA" in reprova and "RECUSADO" in recusa and "PASSA" in ok

    # O controle negativo: se a classificação de linha (`_classe`) parasse de
    # reconhecer ⛔/⚠️/✅, toda linha cairia no CSS neutro e o relatório deixaria
    # de colorir o que importa — sem isso o teste acima passaria mesmo com o
    # detector morto, porque ele só olha o veredito do cabeçalho, não as linhas.
    corpo_colorido = _pagina("teste", "alvo", "2026-08-24", ["⛔ grave", "⚠️ aviso", "✅ ok", "neutro"], 0)
    assert 'class="grave"' in corpo_colorido and 'class="aviso"' in corpo_colorido and 'class="ok"' in corpo_colorido


@check("BP", "`python -m forja . --html ARQUIVO` escreve, e o arquivo carrega o MESMO achado do terminal")
def _bp():
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        _roster(tmp, {"completo.md": AGENTE_COMPLETO})
        alvo_html = raiz / "relatorio.html"
        assert not alvo_html.exists()
        codigo = forja_main([str(raiz), "--html", str(alvo_html)])
        assert codigo == 0, "o roster de fixture (AGENTE_COMPLETO) não tem achado — tinha de passar"
        assert alvo_html.is_file(), "`--html` foi pedido e o arquivo não foi escrito"
        conteudo = alvo_html.read_text(encoding="utf-8")
        assert "PASSA" in conteudo and 'class="veredito ok"' in conteudo


# ------------------------------------------------------- forja: --baseline ---

from forja import baseline as _baseline  # noqa: E402

AGENTE_SEM_REDE = """---
name: leitor
description: "Le arquivo. Usar quando precisar ler algo do disco. NUNCA usar para escrever nada."
tools: Read
---
Lacunas: nao mede fora do disco. Golden: resposta esperada escrita a mao.
"""

AGENTE_COM_REDE_SEM_DONO = """---
name: buscador
description: "Busca na web. Usar quando precisar de fonte externa. NUNCA usar para ler arquivo local."
tools: Read, WebFetch
---
Lacunas: nao mede fora do disco. Golden: resposta esperada escrita a mao.
"""


@check("BQ", "`--baseline` sem arquivo gravado RECUSA (exit 2), e nunca finge que nada mudou")
def _bq():
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        _roster(tmp, {"leitor.md": AGENTE_SEM_REDE})
        assert not (raiz / _baseline.ARQUIVO_PADRAO).exists()
        codigo = forja_main([str(raiz), "--baseline"])
        assert codigo == 2, "sem baseline gravado, `--baseline` tinha de recusar — nunca comparar com o vazio"


@check("BR", "`--baseline --gravar` escreve, e a rodada seguinte só acusa o que É NOVO")
def _br():
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        pasta = _roster(tmp, {"leitor.md": AGENTE_SEM_REDE})
        arquivo = raiz / _baseline.ARQUIVO_PADRAO

        assert forja_main([str(raiz), "--baseline", "--gravar"]) == 0
        assert arquivo.is_file(), "`--gravar` tinha de escrever o baseline"

        # Nada mudou: a rodada seguinte tem de passar limpa.
        assert forja_main([str(raiz), "--baseline"]) == 0, "nada mudou desde o baseline — tinha de passar"

        # Introduz uma regressão real: o agente ganha ferramenta de rede sem dono.
        (pasta / "leitor.md").write_text(AGENTE_COM_REDE_SEM_DONO, encoding="utf-8")
        assert forja_main([str(raiz), "--baseline"]) == 1, (
            "um achado NOVO surgiu desde o baseline — `--baseline` tinha de reprovar"
        )

        # O controle negativo: sem o mecanismo de diff, rodar a vistoria pura
        # (sem `--baseline`) já reprovaria de qualquer forma — o que prova que
        # `--baseline` está de fato comparando contra o arquivo, e não só
        # repetindo o exit code da vistoria, é o caso abaixo: gravando o novo
        # estado como baseline, a MESMA árvore volta a passar.
        assert forja_main([str(raiz), "--baseline", "--gravar"]) == 0
        assert forja_main([str(raiz), "--baseline"]) == 0, (
            "depois de regravar o baseline sobre o estado novo, nada mais é NOVO"
        )


@check("BS", "baseline corrompido (JSON inválido) é lido como AUSENTE, não como estourar")
def _bs():
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        raiz.mkdir(exist_ok=True)
        (raiz / _baseline.ARQUIVO_PADRAO).write_text("{ isto não é json", encoding="utf-8")
        assert _baseline.ler(raiz / _baseline.ARQUIVO_PADRAO) is None, (
            "JSON corrompido tinha de virar `None` (mesma leitura de 'não há baseline'), "
            "nunca uma exceção que derruba a rodada inteira"
        )


# ---------------------------------------------------------- forja: --explain ---

from forja import explicar as _explicar_mod  # noqa: E402


@check("BT", "`--explain` de todo achado real (V1–V7) cita algo lido de README.md e de LACUNAS.md")
def _bt():
    for regra in _explicar_mod.CODIGOS:
        linhas = _explicar_mod.explicar(regra)
        texto = "\n".join(linhas)
        assert "O que ele acha:" in texto, f"{regra}: não achou a linha da tabela do README"
        assert f"citado ao vivo de {_explicar_mod.README.name}" in texto
        assert "⚠️ não consegui ler" not in texto, f"{regra}: README mudou de forma e a citação quebrou"


@check("BU", "`--explain` de código fora do vocabulário fechado é RECUSADO, e lista os sete válidos")
def _bu():
    try:
        _explicar_mod.explicar("V9")
    except _explicar_mod.RegraDesconhecida as exc:
        assert "V1" in str(exc) and "V7" in str(exc), "a recusa tinha de listar o vocabulário fechado"
    else:
        raise AssertionError("`V9` não é um dos sete achados, e foi aceito — vocabulário não é fechado de verdade")

    # Via CLI, o mesmo código de recusa é 2 — nunca uma exceção crua até o usuário.
    assert forja_main(["--explain", "V9"]) == 2


@check("BV", "`--explain` MUDA se a doutrina mudar — não é uma cópia congelada num terceiro lugar")
def _bv():
    original = _explicar_mod.README.read_text(encoding="utf-8")
    try:
        marca = "TEXTO-DE-TESTE-QUE-NAO-EXISTE-NA-DOUTRINA-REAL"
        alterado = original.replace(
            "não diz o que **nunca** faz", f"não diz o que **nunca** faz ({marca})", 1
        )
        assert alterado != original, "a linha de V1 na tabela do README mudou de texto — ajuste o fixture"
        _explicar_mod.README.write_text(alterado, encoding="utf-8")
        texto = "\n".join(_explicar_mod.explicar("V1"))
        assert marca in texto, (
            "editei o README e a explicação de V1 não mudou — `--explain` está copiando a doutrina "
            "para um segundo lugar, em vez de lê-la ao vivo"
        )
    finally:
        _explicar_mod.README.write_text(original, encoding="utf-8")


# --------------------------------------------------- forja: modo comparação ---

from forja import comparar as _comparar_mod  # noqa: E402


@check("BW", "`forja repoA repoB` agrega numa tabela só, e um alvo sem pasta de agentes aparece com erro nomeado")
def _bw():
    with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
        _roster(tmp_a, {"completo.md": AGENTE_COMPLETO})
        raiz_b = Path(tmp_b)  # sem pasta .claude/agents — o segundo alvo é vazio de propósito

        resultados = _comparar_mod.comparar([Path(tmp_a), raiz_b])
        assert len(resultados) == 2, "o denominador da comparação tem de contar TODO alvo pedido"
        a, b = resultados
        assert a.erro is None and a.agentes == 1 and a.ausentes == 0
        assert b.erro is not None, "alvo sem pasta de agentes tinha de sair com erro NOMEADO, não sumir da tabela"

        linhas = _comparar_mod.relatorio(resultados, "2026-08-24")
        texto = "\n".join(linhas)
        assert str(tmp_a) in texto and str(raiz_b) in texto, (
            "os DOIS alvos têm de aparecer na tabela — o modo antigo (silenciosamente só o "
            "primeiro) é exatamente o defeito que este modo substitui"
        )
        assert "total" in texto

        codigo = forja_main([tmp_a, str(raiz_b)])
        assert codigo == 2, (
            "`a` passa limpo e `b` nem tem pasta — parte da comparação não foi medida, e isso "
            "nunca pode sair 0 (verde) nem 1 (que diria 'achei declaração ausente', o que não é "
            "o caso aqui): tem de ser 2, a mesma leitura de RECUSA que a vistoria de alvo único já dá"
        )

        # O controle negativo: com um achado REAL num dos alvos válidos, a severidade muda — a
        # declaração ausente pesa mais que o alvo não lido, e o código vira 1, não 2.
        with tempfile.TemporaryDirectory() as tmp_c:
            _roster(tmp_c, {"buscador.md": AGENTE_COM_REDE_SEM_DONO})  # este TEM achado (V3)
            codigo_com_defeito = forja_main([tmp_c, str(raiz_b)])
            assert codigo_com_defeito == 1, (
                "um alvo com declaração ausente de verdade tinha de dominar sobre o alvo não lido"
            )


@check("BX", "um único diretório continua vistoria normal — o modo comparação só liga com DOIS alvos ou mais")
def _bx():
    with tempfile.TemporaryDirectory() as tmp:
        _roster(tmp, {"completo.md": AGENTE_COMPLETO})
        codigo = forja_main([tmp])
        assert codigo == 0, "um alvo só continua sendo vistoria simples, não comparação"


# ------------------------------------------- vendorizar.py: o forja.py sozinho ---

import importlib.util as _ilu  # noqa: E402


def _carregar_vendorizado():
    caminho = RAIZ_DA_CASA / "vendorizado" / "forja.py"
    nome = "_forja_vendorizado_carregado"
    spec = _ilu.spec_from_file_location(nome, caminho)
    assert spec and spec.loader, f"não consegui carregar {caminho}"
    modulo = _ilu.module_from_spec(spec)
    # `dataclass` resolve `cls.__module__` via `sys.modules` para checar
    # anotação — sem registrar aqui, `@dataclass(frozen=True)` do vendorizado
    # (a classe `Caso`) estoura `AttributeError` num módulo que Python nunca
    # viu, mesmo com a execução por si só correta.
    sys.modules[nome] = modulo
    try:
        spec.loader.exec_module(modulo)
    finally:
        del sys.modules[nome]
    return modulo


@check("BY", "`vendorizado/forja.py` no disco bate com o que `vendorizar.py` geraria AGORA")
def _by():
    import vendorizar as _vz

    gerado = _vz.gerar()
    compile(gerado, "<vendorizado>", "exec")  # falha alto se a fonte real quebrar a splice

    assert _vz.SAIDA.is_file(), f"{_vz.SAIDA} não existe — rode `python vendorizar.py` antes de commitar"
    no_disco = _vz.SAIDA.read_text(encoding="utf-8")
    assert no_disco == gerado, (
        f"{_vz.SAIDA} diverge do pacote `forja` de agora — quem editou `forja/spec.py` ou "
        "`forja/vistoria.py` sem regerar o vendorizado deixou um gêmeo desatualizado no disco"
    )

    # O controle negativo: sem hastear o `from __future__` no topo, um arquivo com DOIS
    # future-imports (um deles fora do topo) NÃO compila — prova que a splice de verdade
    # está sendo exercitada, e que só comparar texto não bastaria para provar isso.
    dobrado = "x = 1\nfrom __future__ import annotations\n" + gerado
    try:
        compile(dobrado, "<future-fora-do-topo>", "exec")
    except SyntaxError:
        pass
    else:
        raise AssertionError(
            "`from __future__` fora da primeira linha tinha de estourar `SyntaxError` — se não "
            "estourou, o controle negativo deste check não prova nada"
        )


@check("BZ", "`forja.py` vendorizado RODA sozinho (sem o pacote `forja`) e é BIT A BIT igual ao pacote de verdade")
def _bz():
    modulo = _carregar_vendorizado()

    with tempfile.TemporaryDirectory() as tmp:
        pasta = _roster(tmp, {"completo.md": AGENTE_COMPLETO, "buscador.md": AGENTE_COM_REDE_SEM_DONO})
        hoje = "2026-08-24"

        # De dentro do módulo carregado a partir do ARQUIVO vendorizado — nenhuma
        # importação do pacote `forja` acontece para produzir este resultado.
        roster_v = modulo.ler_roster(pasta)
        achados_v = modulo.vistoriar(roster_v)
        relatorio_v = modulo.relatorio(roster_v, achados_v, pasta, hoje)

        # Do pacote de verdade, sobre o MESMO roster no disco:
        roster_r = _v.ler_roster(pasta)
        achados_r = _v.vistoriar(roster_r)
        relatorio_r = _v.relatorio(roster_r, achados_r, pasta, hoje)

        assert relatorio_v == relatorio_r, (
            "a mesma pasta produziu relatório DIFERENTE no vendorizado e no pacote — a splice "
            "divergiu da lógica real, e é exatamente o gêmeo que apodrece que este check existe "
            "para pegar"
        )

    texto_no_disco = (RAIZ_DA_CASA / "vendorizado" / "forja.py").read_text(encoding="utf-8")
    assert "from .spec import" not in texto_no_disco and "from .vistoria import" not in texto_no_disco, (
        "sobrou um import relativo ao pacote — o arquivo não é standalone de verdade"
    )


# ------------------------------------------------ action.yml: o gate em Python ---


def _gate():
    caminho = RAIZ_DA_CASA / "acao" / "gate.py"
    spec = _ilu.spec_from_file_location("_acao_gate_carregado", caminho)
    assert spec and spec.loader, f"não consegui carregar {caminho}"
    modulo = _ilu.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@check("CA", "`falhar-em=nenhuma` nunca quebra o job, mesmo com as três ferramentas acusando algo")
def _ca():
    gate = _gate()
    assert gate.decidir("nenhuma", {"forja": 1, "placar": 1, "loadline": 2}) == 0, (
        "o default `nenhuma` existe para a Action ser diagnóstico puro na primeira rodada — "
        "reprovar aqui quebraria o build de todo mundo que só instalou a Action para OLHAR"
    )


@check("CB", "`falhar-em` reprova só pela(s) ferramenta(s) NOMEADA(S) — as outras acusarem não pesa")
def _cb():
    gate = _gate()
    codigos = {"forja": 1, "placar": 0, "loadline": 0}
    assert gate.decidir("forja", codigos) == 1, "forja acusou (código 1) e foi citada em `falhar-em` — tinha de reprovar"
    assert gate.decidir("placar", codigos) == 0, "placar passou limpo — `falhar-em=placar` não pode reprovar por causa da forja"
    assert gate.decidir("placar,loadline", codigos) == 0, "nem placar nem loadline acusaram — a combinação tinha de passar"
    assert gate.decidir("forja,placar", codigos) == 1, "forja está na combinação e acusou — tinha de reprovar"

    # O controle negativo: código 2 (RECUSA/sem denominador) TAMBÉM conta como "acusou algo" —
    # sem isto, uma ferramenta que nem conseguiu ler o alvo passaria o gate calada.
    assert gate.decidir("loadline", {"forja": 0, "placar": 0, "loadline": 2}) == 1, (
        "código 2 (recusa) é diferente de 0 — tinha de reprovar o gate igual a um 1"
    )


@check("CC", "`falhar-em` com ferramenta fora do vocabulário fechado RECUSA — nunca ignora em silêncio")
def _cc():
    gate = _gate()
    try:
        gate.decidir("vitrine", {"forja": 0, "placar": 0, "loadline": 0})
    except gate.FerramentaDesconhecida as exc:
        assert "vitrine" in str(exc) and "forja" in str(exc), "a recusa tinha de nomear o que não reconheceu e o vocabulário válido"
    else:
        raise AssertionError("`vitrine` não é uma das três ferramentas do gate, e foi aceita em silêncio")

    # Via CLI (a superfície que o YAML de fato chama): mesma recusa, código 2.
    assert gate.main(["vitrine", "0", "0", "0"]) == 2


@check("CD", "a CLI do gate propaga o código de saída de `decidir`, e recusa entrada não-numérica")
def _cd():
    gate = _gate()
    assert gate.main(["nenhuma", "1", "1", "1"]) == 0
    assert gate.main(["forja", "1", "0", "0"]) == 1
    assert gate.main(["forja", "abacate", "0", "0"]) == 2, (
        "código de saída não-numérico (o YAML passaria isto se um step nem rodasse) tinha de "
        "recusar com 2, nunca estourar até derrubar o job com um traceback cru"
    )


@check("CE", "o confronto NÃO morde identificador de versão de DUAS partes (`Apache-2.0`, `Python 3.14`)")
def _ce():
    """Achado em 2026-08-25, escrevendo uma ficha do censo: a regra `RUIDO` de

    versão em `loadline/eco.py` exigia 3+ segmentos (`\\d+\\.\\d+(?:\\.\\d+)+`),
    então `v2.1.196` era descartado corretamente mas `Apache-2.0`/`Python 3.14`
    — DUAS partes, o formato mais comum de licença SPDX — atravessavam como se
    o `2`/`3` fossem número afirmado de verdade. Mesma família do `AM`: um
    detector que confunde ruído com afirmação é tão caro quanto um que não
    confronta nada, e este especificamente ficou invisível até um selo real
    cair no mesmo bloco de uma licença.
    """
    registro.limpar()
    sonda("licenca.padroes")(lambda: 70)
    fonte = """O projeto usa Apache-2.0, testado em Python 3.14, e o script antigo era v1.2.
<!-- measured: licenca.padroes=70 nature=count on=2026-08-25 expires=never -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    mudos = [a for a in r.achados if a.veredito == PROSE_DRIFT]
    assert not mudos, (
        "`Apache-2.0`, `Python 3.14` e `v1.2` são identificador de versão, não "
        f"afirmação de quantidade. Falsos positivos: {[str(a) for a in mudos]}"
    )


def main() -> int:
    print("autoteste do loadline — cada check reintroduz o defeito que ele pega\n")
    ordem = sorted(
        (nome for nome in globals() if nome.startswith("_") and len(nome) == 2),
        key=lambda n: n[1],
    )
    del ordem  # os checks já rodaram na importação, por decoração

    executados = _passes + len(_falhas)
    print()
    print(
        f"{executados + len(FORA)} checks declarados · {executados} executados"
        f" · {len(FORA)} fora do denominador"
    )
    for letra, motivo in FORA:
        print(f"  fora: {letra} — {motivo}")
    print(f"{_passes} passaram · {len(_falhas)} reprovaram")
    if _falhas:
        print("\nREPROVOU:")
        for f in _falhas:
            print(f"  {f}")
        return 1
    print("\nPASSOU")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
