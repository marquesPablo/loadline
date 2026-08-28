---
name: Bug report
about: A tool gave a wrong answer, crashed, or behaved differently from what the docs say
title: ""
labels: bug
---

**What you ran**

The exact command, and the path you pointed it at.

**What you expected, and what happened**

Paste the output. If a probe returned `UNPROVEN`, include the error line it printed.

**Environment**

- OS and Python version (`python --version`)
- How you installed it: `pip install`, `git clone` + `PYTHONPATH`, the GitHub Action, or `curl -O` the vendored file
- loadline version or commit

**A minimal repository, if you can**

The smallest `.claude/agents/` folder, `AGENTS.md`, or seal that reproduces it. A wrong answer this
tool cannot reproduce is a wrong answer it cannot fix.
