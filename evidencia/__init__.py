"""evidencia — um relatório de linhas de CLI vira UMA página HTML autocontida.

natureza: correcao — este módulo só formata o que a ferramenta já decidiu. Zero
leitura de disco, zero rede: ele recebe as MESMAS linhas que já iam para o
terminal, e devolve uma página que abre em qualquer navegador — sem servidor,
sem CDN, sem `<script src=...>` nem `<link>` externo.

    from evidencia import pagina
    Path("relatorio.html").write_text(pagina("placar", str(alvo), hoje, linhas, codigo))

O contrato: cada linha do relatório já carrega sua própria marca — ⛔ ✅ ⚠️, ou a
palavra PASSA/REPROVA/RECUSADO no fim. Esta página só LÊ essas marcas para
colorir; ela nunca reavalia nada, e por isso não pode divergir do que o
terminal já disse.
"""

from __future__ import annotations

import html as _stdlib_html
from datetime import datetime

__all__ = ["pagina"]

_CSS = """
:root {
  --bg: #f7f7f5; --fg: #1c1c1a; --linha: #e4e2dc; --mono: #ffffff;
  --grave: #b3261e; --grave-bg: #fbeceb; --aviso: #8a5a00; --aviso-bg: #fbf3e1;
  --ok: #1f7a3f; --ok-bg: #eaf6ee; --neutro: #55534c;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #171715; --fg: #e9e8e3; --linha: #33322c; --mono: #100f0d;
    --grave: #ff8078; --grave-bg: #2c1614; --aviso: #e8b23d; --aviso-bg: #2b2210;
    --ok: #6fd48d; --ok-bg: #10261a; --neutro: #a9a79c;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2rem 1.25rem 3rem; background: var(--bg); color: var(--fg);
  font: 15px/1.5 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
}
header { max-width: 62rem; margin: 0 auto 1.25rem; }
h1 { font-size: 1.15rem; margin: 0 0 0.2rem; font-family: ui-monospace, Consolas, monospace; }
.meta { margin: 0; color: var(--neutro); font-size: 0.85rem; }
.veredito {
  display: inline-block; margin-top: 0.6rem; padding: 0.15rem 0.6rem; border-radius: 0.3rem;
  font-weight: 600; font-family: ui-monospace, Consolas, monospace; font-size: 0.85rem;
}
.veredito.ok { color: var(--ok); background: var(--ok-bg); }
.veredito.grave { color: var(--grave); background: var(--grave-bg); }
pre {
  max-width: 62rem; margin: 0 auto; padding: 1rem 1.25rem; overflow-x: auto;
  background: var(--mono); border: 1px solid var(--linha); border-radius: 0.4rem;
  font: 13px/1.55 ui-monospace, Consolas, "Courier New", monospace; white-space: pre;
}
pre span { display: inline; }
pre span.grave { color: var(--grave); }
pre span.aviso { color: var(--aviso); }
pre span.ok { color: var(--ok); }
footer { max-width: 62rem; margin: 1rem auto 0; color: var(--neutro); font-size: 0.8rem; }
"""


def _classe(linha: str) -> str:
    if "⛔" in linha or "REPROVA" in linha or "NO-GO" in linha or "RECUSADO" in linha:
        return "grave"
    if "⚠️" in linha:
        return "aviso"
    if "✅" in linha or "PASSA" in linha:
        return "ok"
    return ""


def pagina(comando: str, alvo: str, hoje: str, linhas: list[str], codigo: int) -> str:
    """As MESMAS linhas que o terminal já imprimiu, numa página autocontida.

    `codigo` é o código de saída da ferramenta (0/1/2, o mesmo contrato em
    `forja`, `placar` e `loadline`): 0 vira PASSA, 2 vira RECUSADO (nada foi
    lido), qualquer outro vira REPROVA.
    """
    corpo = "\n".join(
        f'<span class="{_classe(linha)}">{_stdlib_html.escape(linha)}</span>' for linha in linhas
    )
    if codigo == 0:
        veredito, cor = "PASSA", "ok"
    elif codigo == 2:
        veredito, cor = "RECUSADO", "grave"
    else:
        veredito, cor = "REPROVA", "grave"
    gerado_em = datetime.now().isoformat(timespec="seconds")

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_stdlib_html.escape(comando)} · {_stdlib_html.escape(alvo)}</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <h1>{_stdlib_html.escape(comando)} · {_stdlib_html.escape(alvo)}</h1>
  <p class="meta">em {_stdlib_html.escape(hoje)} · página gerada {gerado_em} · código de saída {codigo}</p>
  <p class="veredito {cor}">{veredito}</p>
</header>
<pre>{corpo}</pre>
<footer>
  <p>Página autocontida — sem servidor, sem chamada de rede, sem chave de API. As linhas acima
     são exatamente as que o terminal imprimiu; esta página só as colore, nunca as reavalia.</p>
</footer>
</body>
</html>
"""
