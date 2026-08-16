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

import sys
import tempfile
from datetime import date
from pathlib import Path

from aferido import (
    CONGELADO,
    DERIVOU,
    SEM_PROVA,
    VALE,
    VENCIDO,
    SeloMalformado,
    julgar,
    ler_linha,
    registro,
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


def main() -> int:
    print("autoteste do aferido — cada check reintroduz o defeito que ele pega\n")
    ordem = sorted(
        (nome for nome in globals() if nome.startswith("_") and len(nome) == 2),
        key=lambda n: n[1],
    )
    del ordem  # os checks já rodaram na importação, por decoração

    print()
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
