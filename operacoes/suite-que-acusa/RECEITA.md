# Operation 9 · `suite-que-acusa`

> Your suite is green. **If someone deleted the mechanism it protects, would it go red?**
> For a good share of the tests out there, the answer is no. They walk the happy path, confirm it
> works, and would pass identical with the mechanism removed.
> **The cost of that is not zero.** It is giving someone the feeling of being covered — and nobody
> looks for what already seems protected.

## The test that passes the same without the mechanism

```python
def test_validacao():
    assert validar("entrada-valida@exemplo.com") is True
```

Replace the whole body of `validar` with `return True`. **The test stays green.**

It does not prove that the validation validates. It proves that it does not blow up. And the
difference shows up the day someone simplifies the function during a refactor, the test passes, and
the validation disappears from production without a single light coming on.

The fix is the **negative control** — the test reintroduces the defect it exists to catch:

```python
def test_validacao():
    assert validar("entrada-valida@exemplo.com") is True

    # The negative control: without it, the test above passes with `return True`.
    assert validar("nao-e-email") is False
```

Two lines. And now the test dies along with the mechanism, which is the only thing a test has to do.

## The third list

Every suite publishes two lists: **what passed** and **what failed**. Almost none publishes the
third — **what it never looked at.**

Without the third, a green only says *"what was looked at passed"*, which is far less than it seems
to say. With it, the green gets a size: *"we looked at these 40 things, these 12 are outside our
reach, and we know which."*

That is why `suite.lacunas_declaradas` **blows up** when the file does not exist, instead of
returning zero. Zero declared gaps claims the suite has no blind spot — the strongest possible
claim, and the least likely.

## What this operation installs

Six probes over your tests folder:
<!-- measured: operacao.suite.sondas=6 nature=count on=2026-08-21 expires=never source=operacoes/suite-que-acusa/sondas.py -->

| Metric | What it recomputes | Nature |
|---|---|---|
| `suite.arquivos` · `suite.checks` | the size of the suite, counted by the syntax tree | count |
| **`suite.sem_assercao`** | **test functions that cannot fail** | **relation** |
| **`suite.sem_controle_negativo`** | **tests that would pass without the mechanism (heuristic)** | **relation** |
| **`suite.pulados`** | **tests marked `skip`/`xfail`** | **relation** |
| `suite.lacunas_declaradas` | items in the third list | count |

**`suite.checks` is counted by the syntax tree, not by a regular expression.** A `def` inside a
string, in a comment or nested in another function would be counted by regex — and the whole suite's
denominator would come out wrong, which is the worst class of error in a tool that exists to demand
a denominator.

## ⚠️ One of the six is a verdict, the other is a reading list

This distinction is the most important thing in this recipe.

**`suite.sem_assercao` is a verdict.** A test function with no `assert`, no `assert*` and no `raise`
**cannot fail**. It is not opinion, it is a property of the code. It runs, returns green, enters the
coverage count and verifies nothing. Its right number is zero.

**`suite.sem_controle_negativo` is a HEURISTIC, and it gets it wrong both ways.** It looks for
constructs that indicate an expectation of failure (`raises`, `xfail`, `deve_falhar`, the word
*reintroduces*…). A test that reintroduces the defect in a way it does not recognize **is accused
for nothing**. A decorative `pytest.raises` **gets past it**.

**Use it to produce the list of which tests to open, never to fail on its own in CI.** And if it
accuses a test that is right, the fix is to add the construct to the `_SU_CONTROLE_NEGATIVO`
vocabulary — **not to rewrite the test to please the rule.** A rule that makes the code change shape
to fit it has stopped measuring the code and started measuring itself.

## The adjustment

**Two fields**, at the top of `sondas.py`:

```python
PASTA_DE_TESTES = "tests"
ARQUIVO_DE_LACUNAS = "LACUNAS.md"
```

And, if your test dialect does not use `test_` in the name, `_SU_NOME_DE_TESTE`.

## How to run

```console
$ cp operacoes/suite-que-acusa/sondas.py  /path/to/your/repo/sondas.py
$ cd /path/to/your/repo
$ PYTHONPATH=/path/to/loadline python -m loadline .
```

```console
FAIL       README.md:31  suite.sem_assercao: written=0 measured=4
           → nature=relation — STOP and investigate.
UNVERIFIED README.md:32  suite.lacunas_declaradas
           → `LACUNAS.md` does not exist. It is the third list: what your suite does NOT measure.
```

**Four test functions that cannot fail**, and no third list. Both are findings, and the second is
what makes the green of the others worth something.

## What this operation does NOT do

1. **It does not run the suite.** It reads the tests' source code. A test that passes by accident
   and one that passes on merit are identical to it.

2. **It does not measure line coverage.** That is another question, there is already a tool, and
   **high coverage with zero negative control is exactly the state this operation exists to find** —
   the suite walks everything and verifies nothing.

3. **It does not know what nobody tested.** What did not become a test is invisible to it — the same
   gap your suite has, and that is what the third list is for, written by hand.

4. **It does not judge whether the tested mechanism should exist.** It asks whether the test dies
   along with it. Whether the imposed rule is the right one stays a judgment for whoever wrote it.
