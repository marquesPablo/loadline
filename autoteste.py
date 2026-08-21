"""Autoteste — cada check reintroduz o defeito que ele existe para pegar.

aferido-ignorar-arquivo: este arquivo escreve selos de mentira de propósito.
Julgá-los seria afirmar coisas que ninguém quis afirmar.

Rode: `python autoteste.py`

Um check que só confirma o caminho feliz não prova nada: ele passa igual se o
mecanismo for removido. Aqui cada letra **quebra alguma coisa** e exige que o
motor reprove. Se um destes ficar verde depois de você tirar o mecanismo, o
check é decorativo e deve ser jogado fora.
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import date
from pathlib import Path

from aferido import (
    ARBITRADO,
    CONGELADO,
    DERIVOU,
    PROSA_MUDA,
    SEM_PROVA,
    VALE,
    VENCIDO,
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
        _selo("<!-- aferido: x.y=3 em=2026-08-16 -->")
    except SeloMalformado as exc:
        assert "natureza" in str(exc), f"recusou pelo motivo errado: {exc}"
        return
    raise AssertionError(
        "aceitou selo sem natureza — aí todo vermelho vira ruído e a resposta a "
        "todo vermelho vira 'resela', escondendo o único bug que isto pega"
    )


@check("B", "`natureza` fora do vocabulário fechado é RECUSADA")
def _b():
    try:
        _selo("<!-- aferido: x.y=3 natureza=talvez em=2026-08-16 -->")
    except SeloMalformado:
        return
    raise AssertionError("aceitou `natureza=talvez`; o vocabulário não é fechado de verdade")


@check("C", "`congelado:` sem `motivo` é RECUSADO")
def _c():
    try:
        _selo('<!-- congelado: x.y=3 em=2020-01-01 -->')
    except SeloMalformado as exc:
        assert "motivo" in str(exc), f"recusou pelo motivo errado: {exc}"
        return
    raise AssertionError("congelar sem dizer por quê é o mesmo que apagar a medida")


@check("D", "`vence` malformado vira SEM_PROVA, nunca VALE")
def _d():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 3)
    achados = julgar(_selo("<!-- aferido: x.y=3 natureza=contagem em=2026-08-16 vence=semana -->"), HOJE)
    assert achados[0].veredito == SEM_PROVA, f"esperava SEM_PROVA, veio {achados[0].veredito}"


# ------------------------------------------------------- os dois vermelhos

@check("E", "divergência de CONTAGEM manda RESSELAR")
def _e():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 9)
    a = julgar(_selo("<!-- aferido: x.y=3 natureza=contagem em=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == DERIVOU, f"esperava DERIVOU, veio {a.veredito}"
    assert not a.e_defeito, "contagem divergindo NÃO é defeito"
    assert "resele" in a.acao.lower(), f"ação errada: {a.acao}"


@check("F", "divergência de RELAÇÃO é DEFEITO e manda PARAR — não resselar")
def _f():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 9)
    a = julgar(_selo("<!-- aferido: x.y=3 natureza=relacao em=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == DERIVOU, f"esperava DERIVOU, veio {a.veredito}"
    assert a.e_defeito, (
        "relação divergindo passou como resselável — é aqui que se esconde o bug "
        "que o mecanismo inteiro existe para achar"
    )
    assert "PARE" in a.acao, f"ação errada: {a.acao}"


# ------------------------------------------------------------- vencimento

@check("G", "valor CERTO + prazo vencido = VENCIDO (o motivo de este projeto existir)")
def _g():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 3)
    a = julgar(
        _selo("<!-- aferido: x.y=3 natureza=contagem em=2026-01-01 vence=30d -->"), HOJE
    )[0]
    assert a.veredito == VENCIDO, (
        f"esperava VENCIDO, veio {a.veredito} — um número que ninguém reconfere há meses "
        "é um número que ainda não errou, não um número verificado"
    )
    assert a.escrito == a.medido == "3", "o valor batia; o que venceu foi a conferência"


@check("H", "`vence=nunca` não vence, mesmo antigo")
def _h():
    registro.limpar()
    sonda("x.y", origem="teste")(lambda: 3)
    a = julgar(_selo("<!-- aferido: x.y=3 natureza=relacao em=2001-01-01 vence=nunca -->"), HOJE)[0]
    assert a.veredito == VALE, f"esperava VALE, veio {a.veredito}"


# --------------------------------------------------- não medido ≠ zero

@check("I", "métrica sem sonda vira SEM_PROVA, NUNCA VALE")
def _i():
    registro.limpar()
    a = julgar(_selo("<!-- aferido: nao.existe=3 natureza=contagem em=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == SEM_PROVA, f"esperava SEM_PROVA, veio {a.veredito}"
    assert not a.verde, "não medido virou verde — é o defeito de contar ausência como zero"


@check("J", "sonda que ESTOURA vira SEM_PROVA, e nunca passa como verde")
def _j():
    registro.limpar()

    def quebrada():
        raise RuntimeError("o disco sumiu")

    sonda("x.y", origem="teste")(quebrada)
    a = julgar(_selo("<!-- aferido: x.y=3 natureza=contagem em=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == SEM_PROVA, f"esperava SEM_PROVA, veio {a.veredito}"
    assert "o disco sumiu" in a.detalhe, f"engoliu o erro: {a.detalhe}"


@check("K", "TypeError de DENTRO da sonda não é confundido com aridade errada")
def _k():
    registro.limpar()

    def erra_por_dentro():
        return 1 + "dois"  # noqa: RUF005

    sonda("x.y", origem="teste")(erra_por_dentro)
    a = julgar(_selo("<!-- aferido: x.y=3 natureza=contagem em=2026-08-16 -->"), HOJE)[0]
    assert a.veredito == SEM_PROVA, f"esperava SEM_PROVA, veio {a.veredito}"
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
            "# doc\n\n```\n<!-- aferido: inventado=99 natureza=contagem em=2026-08-16 -->\n```\n",
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
            "# doc\n\n<!-- aferido: inventado=99 natureza=contagem em=2026-08-16 -->\n",
            encoding="utf-8",
        )
        r = varrer(alvo, hoje=HOJE)
    assert len(r.achados) == 1, f"esperava 1 achado, veio {len(r.achados)}"
    assert r.achados[0].veredito == SEM_PROVA


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
    a = julgar(_selo('<!-- congelado: x.y=3 em=2020-01-01 motivo="histórico do lançamento" -->'), HOJE)[0]
    assert a.veredito == CONGELADO, f"esperava CONGELADO, veio {a.veredito}"
    assert a.verde, "congelado com motivo é verde"
    assert "histórico do lançamento" in a.acao


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
    from aferido import escrever

    velho = _selo("<!-- aferido: x.y=3 natureza=contagem em=2026-01-01 vence=30d -->")
    novo = escrever(velho, **{"x.y": 9, "em": "2026-08-16"})
    assert "x.y=9" in novo, novo
    assert "em=2026-08-16" in novo, novo
    assert "x.y=3" not in novo and "2026-01-01" not in novo, f"sobrou metade do selo velho: {novo}"
    assert "natureza=contagem" in novo and "vence=30d" in novo, f"perdeu campo no resselo: {novo}"


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
        g.FONTE.write_bytes(original.replace(b'"nomes_buscados": 15', b'"nomes_buscados": 99'))
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
        '    return f"<!-- aferido: forja.artefatos={n} natureza=contagem em=2026-08-16 -->"\n'
        "\n"
        'DOC = """exemplo malformado que precisa poder existir escrito:\n'
        "<!-- aferido: x.y=1 -->\n"
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
        'DOC = """dentro da string, espécime: <!-- aferido: emissor.x=99 natureza=contagem -->"""\n'
        "# aferido: emissor.x=1 natureza=contagem em=2026-08-16 vence=nunca\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "misto.py").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)
    achados = [a for a in r.achados if a.metrica == "emissor.x"]
    assert len(achados) == 1, (
        f"esperava exatamente 1 achado (o do comentário), veio {len(achados)}: "
        f"{[str(a) for a in r.achados]} — a regra da string virou isenção do arquivo inteiro"
    )
    assert achados[0].veredito == DERIVOU and achados[0].escrito == "1", achados[0]


@check("AK", "`.py` que não parseia NÃO vira espécime — falhar calado é pior que falhar alto")
def _ak():
    registro.limpar()
    sonda("quebrado.x")(lambda: 1)
    fonte = "def ( isto não é python\n# aferido: quebrado.x=1 natureza=contagem em=2026-08-16\n"
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

    O selo diz 36, a sonda mede 36, e o veredito do selo é VALE — como sempre foi.
    O que mudou é que a FRASE, três linhas acima, passou a ser lida.
    """
    registro.limpar()
    sonda("nucleo.checks")(lambda: 36)
    fonte = """```console
$ python autoteste.py
33 passaram
```
<!-- aferido: nucleo.checks=36 natureza=contagem em=2026-08-16 vence=nunca -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    mudos = [a for a in r.achados if a.veredito == PROSA_MUDA]
    assert any(a.escrito == "33" for a in mudos), (
        "a frase diz 33 e o selo diz 36, e nada acusou — é o buraco que o "
        f"PROSA_MUDA existe para fechar. Achados: {[str(a) for a in r.achados]}"
    )
    assert any(a.veredito == VALE for a in r.achados), (
        "o selo em si tem de continuar VALE: é exatamente por isso que o defeito "
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
<!-- aferido: x.y=1 natureza=contagem em=2026-08-16 vence=nunca -->

Prosa inteira que descreve o mecanismo e não afirma quantidade.
<!-- aferido: x.y=1 natureza=contagem em=2026-08-16 vence=nunca -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    mudos = [a for a in r.achados if a.veredito == PROSA_MUDA]
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
<!-- aferido: nucleo.checks=36 eco=nao natureza=contagem em=2026-08-16 vence=nunca -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    assert not [a for a in r.achados if a.veredito == PROSA_MUDA], (
        "`eco=nao` tem de dispensar o bloco do confronto"
    )
    assert r.dispensados_do_eco, (
        "a dispensa tem de aparecer no relatório — uma exceção que não se vê "
        "é indistinguível de um mecanismo que não roda"
    )
    assert "eco" not in [a.metrica for a in r.achados], (
        "`eco` é chave reservada; lê-la como métrica pediria uma sonda para ela"
    )


# ------------------------------------------- ADR-107: a terceira marca e a lista 3


@check("AO", "`arbitrado:` sem `por=` é MALFORMADO — escolha sem dono é palpite")
def _ao():
    try:
        _selo("<!-- arbitrado: retry.max=3 em=2026-08-16 vence=90d -->")
    except SeloMalformado as exc:
        assert "por=" in str(exc), f"a recusa tem de dizer o que falta, e disse: {exc}"
    else:
        raise AssertionError(
            "`arbitrado:` sem `por=` passou — um número escolhido e anônimo é "
            "exatamente o que esta marca existe para desmascarar"
        )


@check("AP", "`arbitrado:` no prazo é verde, e NÃO chama sonda nenhuma")
def _ap():
    registro.limpar()  # nenhuma sonda registrada: se ele medir, estoura
    selo = _selo('<!-- arbitrado: retry.max=3 por="plataforma" em=2026-08-16 vence=90d -->')
    achados = julgar(selo, hoje=HOJE)
    assert [a.veredito for a in achados] == [ARBITRADO], (
        f"escolha no prazo tem de ser ARBITRADO, e veio {[a.veredito for a in achados]}"
    )
    assert achados[0].verde, "ARBITRADO é verde: alguém assinou, e o prazo não venceu"
    assert achados[0].medido is None, (
        "número arbitrado não tem medida — inventar uma seria a mentira que a marca persegue"
    )


@check("AQ", "`arbitrado:` VENCIDO reprova — escolha sem prazo é escolha esquecida")
def _aq():
    selo = _selo('<!-- arbitrado: teto=10 por="board" em=2026-08-16 vence=30d -->')
    achados = julgar(selo, hoje=date(2026, 12, 1))
    assert [a.veredito for a in achados] == [VENCIDO], (
        f"escolha fora do prazo tem de vencer, e veio {[a.veredito for a in achados]}"
    )
    assert not achados[0].verde, (
        "se escolha vencida ficasse verde, bastaria chamar de arbitrado todo número "
        "incômodo para nunca mais olhar para ele"
    )


@check("AR", "repositório SEM SELO NENHUM sai com código 2, e não com 0")
def _ar():
    # Este é o defeito que o ADR-107 existe para consertar, reintroduzido: até
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
    assert r.veredito_da_corrida == "SEM DENOMINADOR", r.veredito_da_corrida


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
        assert "arbitrado:" in escritos[0].texto, (
            "tem de emitir `arbitrado:` e nunca `aferido:` — ninguém mediu nada, e "
            "emitir a outra marca seria a ferramenta inventando que houve medição"
        )
        assert "por=?" in escritos[0].texto, (
            "o `por=?` sai por escrito para o humano preencher; a ferramenta não "
            "sabe quem escolheu, e fingir que sabe é a mesma família de defeito"
        )

        depois = varrer(Path(tmp), hoje=HOJE)

    assert [a.veredito for a in depois.achados] == [ARBITRADO], (
        f"o selo escrito tem de voltar como ARBITRADO, e veio {[a.veredito for a in depois.achados]}"
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
<!-- arbitrado: endpoints=12 por="a" em=2026-08-16 vence=90d -->
Temos 40 testes.
<!-- arbitrado: testes=40 por="a" em=2026-08-16 vence=90d -->
"""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "leia.md").write_text(fonte, encoding="utf-8")
        r = varrer(Path(tmp), hoje=HOJE)

    mudas = [a for a in r.achados if a.veredito == PROSA_MUDA]
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

    # `agente*.toml`, e não `agente.toml`: uma operação pode trazer uma ESTEIRA
    # (a `revisao-de-seguranca` traz três specs). Globar só o nome exato deixaria
    # duas delas nunca serem compiladas por check nenhum — e uma spec que não
    # compila só é descoberta por quem tentar usá-la.
    specs = sorted((RAIZ_DA_CASA / "operacoes").glob("*/agente*.toml"))
    assert specs, "a prateleira não tem nenhuma operação com spec de agente"
    por_operacao = {c.parent.name for c in specs}
    operacoes = {d.name for d in (RAIZ_DA_CASA / "operacoes").iterdir() if d.is_dir()}
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
            pass  # é o que tem de acontecer: vira SEM_PROVA, com o nome do que falta
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

        # `PASTA`/`ARQUIVO` em vez de `PASTA_DE_`: a `fabrica-de-agentes`
        # declara `PASTAS_DE_SPEC` (plural, e uma tupla). O que a regra pergunta
        # é se a operação DECLARA de onde lê — o número e o tipo não mudam isso,
        # e um prefixo estreito demais deixaria a operação fora do denominador
        # sem ninguém ver.
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
    assert examinadas >= 5, f"só {examinadas} operações declaram a fonte de onde leem"

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

    spec = ler(RAIZ_DA_CASA / "operacoes" / "revisao-de-seguranca" / "agente-redator.toml")
    assert spec.saida_cercada == ["relatorios/"], spec.saida_cercada

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

        fora = julgar_caminho("docs/seguranca.md")
        assert '"deny"' in fora, f"a cerca NÃO negou fora de `relatorios/`: {fora[:120]!r}"

        dentro = julgar_caminho("relatorios/laudo.md")
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
    # saía VERDE com código 0. `aferido ./sr` por `./src` deixava o gate do CI
    # aprovando para sempre — *não medido* virando *zero*, dentro da ferramenta
    # cuja tese inteira é que isso não pode acontecer.
    from aferido.__main__ import main as cli

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



def main() -> int:
    print("autoteste do aferido — cada check reintroduz o defeito que ele pega\n")
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
