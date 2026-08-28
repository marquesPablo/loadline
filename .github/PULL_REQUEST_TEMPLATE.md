<!-- loadline-ignore-file: a PR template, not a claim about the repository. -->

**What this changes, and why**

The "why" over the "what" — the diff already shows the what.

**Checklist**

- [ ] `python autoteste.py` is green, before and after
- [ ] `python -m loadline .` did not start failing (exit 1). Exit 0 or 2 is fine
- [ ] Any new behavior comes with a negative control — a check that reintroduces the defect it
      catches, and fails if the mechanism is removed
- [ ] Any asserted number in `README.md`, `CONTINUAR`-style docs, or a `LACUNAS.md` carries a seal,
      or is written without the digit
- [ ] No name that only makes sense to someone who already knows this project crossed into a file
      that ships

**If this is an operation** (`comunidade/` or `operacoes/`)

- [ ] The probe reads a source *independent* of the written number (`origem=` declared)
- [ ] `nature` is set on every metric (`count` vs `relation`)
- [ ] A missing source makes the probe blow up, never return `0`
- [ ] Helper function names use a prefix that does not collide with the other operations
- [ ] `python -m forja <path>/agente.toml` compiles with no refusal
