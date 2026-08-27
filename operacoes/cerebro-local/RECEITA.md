# Operation 6 · `cerebro-local`

> Your notes are on the disk. Your assistant does not reach them.
> Today you do one of two things: **paste a fragment into the chat** — and it answers about the
> fragment, without knowing what was around it — or **send everything to a service**, and your
> material starts living on someone else's infrastructure.
> There is a third: a local, read-only process that serves your notes as tools.
> **No API key, no cloud, no embedding, no vector store.**

## The pain

An assistant with no access to your material is a very articulate stranger. It will never say *"you
already decided this in March, and wrote the reason"* — it will say what is usually true, with a
confidence your material does not support.

And the two usual ways out cost dearly:

- **Pasting into the chat** is reintroducing the context every session, choosing by hand what is
  relevant before knowing what the question will need. You end up being the index.
- **Uploading everything** solves access and creates three problems: the material leaves your
  machine, the index falls behind silently, and you start paying per token to re-read what is
  already yours.

What is missing is small: **a process that speaks the protocol your client already speaks, and
reads the disk.**

## What this operation installs

An MCP server in **one file**, `servidor.py`, with four tools and **zero dependencies** — just the
Python stdlib.

| Tool | Answers |
|---|---|
| `map` | the root, how many notes are served, and how they are spread — **call first** |
| `list_notes` | what exists in a folder, with size |
| `read_note` | the full text of a note |
| `search` | `path:line` of a literal term, **crossing a junction and a symlink** |

```console
$ cp -r operacoes/cerebro-local  /path/to/your/repo/cerebro
$ cd /path/to/your/repo
$ python cerebro/servidor.py --root ~/notes --test
```

`--test` does not speak MCP: it calls the four tools and prints, so you can see it works before
registering it in any client. **Including the refusal:**

```console
=== the refusal, proven ===
REFUSED, as it must: `../../../etc/passwd` resolves outside the declared root.
This server reads under `/home/you/notes` and nothing else.
```

To use it for real, register it in your client (the example is the Claude Code format, in
`.mcp.json`; other clients use the same command/args/env trio):

```json
{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": ["cerebro/servidor.py", "--root", "/path/to/your/notes"]
    }
  }
}
```

There is no second step. There is no account to create.

## The trap that costs dearly, and it gives no error

**`rg`, `grep -r` and `find` do not cross a Windows junction or a directory symlink.** They do not
warn, do not error, do not return a non-zero code: **they return fewer files, with the same look of
a complete answer.**

In a knowledge vault that is the rule, not the exception — linked folders are how most people gather
material from several places into one. The search answers about half the corpus and nobody can tell.

`os.walk(followlinks=True)` crosses. That is why this server's `search` is `os.walk` and not a
`subprocess` calling `grep` — and it is why the agent's anti-description forbids, in writing, using
a command-line search over a linked vault.

**If you rewrite the search calling `grep`, the number drops and nothing accuses.** It is the most
expensive family of defect there is: the one that returns a plausible answer.

## The eight probes

<!-- measured: operacao.cerebro.sondas=8 nature=count on=2026-08-21 expires=never source=operacoes/cerebro-local/sondas.py -->

| Metric | What it recomputes | Nature |
|---|---|---|
| `cerebro.notas` · `cerebro.pastas` | the real size of the served corpus | count |
| **`cerebro.ferramentas`** | **entries in `FERRAMENTAS` in the code — not what the README promises** | **relation** |
| **`cerebro.dependencias`** | **third-party imports in the server: it must be zero, and the probe proves it** | **relation** |
| **`cerebro.orfas`** | **notes that no other note cites — only the author reaches them** | **relation** |
| **`cerebro.links_quebrados`** | **distinct `[[link]]` targets that do not exist** | **relation** |
| `cerebro.sem_titulo` | notes with no markdown title on the first line | count |
| `cerebro.maior_nota` | bytes of the largest file | count |

**`cerebro.dependencias` is the most important of the eight, and the least obvious.** *"Zero
dependencies"* is the sentence that makes someone run this on a machine they do not administer. It
dies the day someone adds an `import` for convenience — and no code review catches it, because the
diff shows one line. The probe reads `servidor.py` and counts.

## The adjustment

**One field**, at the top of `sondas.py`:

```python
PASTA_DE_NOTAS = "."   # "." = the whole repository
```

And, if your notes use another extension, `_CER_EXTENSOES` — which has to match `EXTENSOES` in
`servidor.py`. If they diverge, the probe counts one corpus and the server serves another, and the
green seal would be measuring the wrong thing.

## What this operation does NOT do

1. **It does not write, and that is structural.** There is no write tool in the server. It is not a
   promise in the prompt — it is the absence of the code. An agent cannot misuse a tool that does
   not exist.

2. **It does not resolve a contradiction between your notes.** The agent shows the two citations and
   stops. Choosing would need knowing which is more recent, which was more thought through, or which
   you still hold — and none of the three is in the text. An agent that chooses erases the finding:
   that there is a pending decision.

3. **It does not know whether what you wrote is true.** It reads. A wrong note is cited with the
   same confidence as a right one, and no offline probe reaches the world out there. That is what
   the seals' `expires=` is for.

4. **It does not index, on purpose.** No vector store, no BM25, no embedding. An index falls behind,
   and the lag is silent: it answers with yesterday's corpus and today's confidence. At a few
   megabytes, `os.walk` + literal search is instant — and always right about the disk of now.

5. **It does not protect against what is INSIDE your notes.** If a note of yours contains an order
   aimed at an agent — because you pasted external material — this server delivers it like it
   delivers any other text. Its fence is a **path** fence, not a content one.
