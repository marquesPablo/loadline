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
