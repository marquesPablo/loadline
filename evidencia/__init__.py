"""evidencia — a report of CLI lines becomes ONE self-contained HTML page.

nature: fix — this module only formats what the tool already decided. Zero
disk reads, zero network: it receives the SAME lines that were already going
to the terminal, and returns a page that opens in any browser — no server, no
CDN, no `<script src=...>` and no external `<link>`.

    from evidencia import pagina
    Path("report.html").write_text(pagina("placar", str(alvo), hoje, linhas, codigo))

The contract: every line of the report already carries its own mark — ⛔ ✅ ⚠️,
or the word PASS/FAIL/REFUSED at the end. This page only READS those marks to
colour; it never re-evaluates anything, and so it cannot diverge from what the
terminal already said.
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
    # Matches both the English verdict words and, during the translation, the
    # Portuguese ones the other CLIs still print. Over-matching a colouriser is
    # harmless; a missed colour is not.
    grave = ("REPROVA", "REPROVOU", "FAIL", "NO-GO", "RECUSADO", "REFUSED", "MALFORMAD", "MALFORMED")
    ok = ("PASSA", "PASSOU", "PASS", "PASSED")
    if "⛔" in linha or any(m in linha for m in grave):
        return "grave"
    if "⚠️" in linha:
        return "aviso"
    if "✅" in linha or any(m in linha for m in ok):
        return "ok"
    return ""


def pagina(comando: str, alvo: str, hoje: str, linhas: list[str], codigo: int) -> str:
    """The SAME lines the terminal already printed, in a self-contained page.

    `codigo` is the tool's exit code (0/1/2, the same contract in `forja`,
    `placar` and `loadline`): 0 becomes PASS, 2 becomes REFUSED (nothing was
    read), anything else becomes FAIL.
    """
    corpo = "\n".join(
        f'<span class="{_classe(linha)}">{_stdlib_html.escape(linha)}</span>' for linha in linhas
    )
    if codigo == 0:
        veredito, cor = "PASS", "ok"
    elif codigo == 2:
        veredito, cor = "REFUSED", "grave"
    else:
        veredito, cor = "FAIL", "grave"
    gerado_em = datetime.now().isoformat(timespec="seconds")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_stdlib_html.escape(comando)} · {_stdlib_html.escape(alvo)}</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <h1>{_stdlib_html.escape(comando)} · {_stdlib_html.escape(alvo)}</h1>
  <p class="meta">on {_stdlib_html.escape(hoje)} · page generated {gerado_em} · exit code {codigo}</p>
  <p class="veredito {cor}">{veredito}</p>
</header>
<pre>{corpo}</pre>
<footer>
  <p>Self-contained page — no server, no network call, no API key. The lines above
     are exactly what the terminal printed; this page only colours them, it never re-evaluates.</p>
</footer>
</body>
</html>
"""
