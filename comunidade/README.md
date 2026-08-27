# Contributing an operation

> **This repository is still private.** This folder documents the contribution mechanism for when it
> goes public — today it takes no PR from anyone outside, because there is nowhere for one to come
> from. It exists now, and not only on publication day, so the ruler is already written when the
> first outside person asks "can I send mine?".

## What goes here, and what does not

**It is not** a place for API connectors, integrations or usage examples. **It is** a place for
**domain probes** — the same fixed anatomy as `operacoes/`, applied to a pain you have that today's
shelf does not cover.

The admission ruler is the same as the whole product's: **what does the person GAIN by running
this?** A probe that only confirms what you already suspected ("my README is stale") is hygiene. A
probe that delivers a new capability is what this shelf is after. Both are welcome — the ruler is in
`operacoes/README.md`, section "Writing your own".

## Why this is not "PR merged automatically if CI is green"

`operacoes/README.md` already says: **"the shelf grows by decision, not by accumulation."** The
shelf was born with ten candidates and the board cut it to seven, because the ones that left were
either pure alarm or were already done by another piece. Accepting contributions by volume would
repeat exactly that mistake, only with no board to cut afterward.

**That is why every PR in this folder is reviewed by human decision before the merge — never by CI
alone.** CI (item 5 of the checklist below) is the floor, not the ceiling: it fails what is
mechanically wrong; it does not decide whether the operation deserves to exist.

## A contribution's checklist

Copy `_modelo/` to a new folder named after your operation (`comunidade/your-operation-name/`) and
fill in the five files. Before opening the PR, check the five points every reviewer will check
first — they are named in `operacoes/README.md` §"Writing your own":

1. **The probe must not read the source that produced the written number.** If both sides come from
   the same place, the pair passes green locking the defect in instead of finding it. Declare
   `origem=` on your seal so that is auditable from outside — it is the same rule every probe on
   this shelf already follows.
2. **`nature` is required on every metric**, and it changes what to do with the red: `count` moves
   when someone writes (re-seal and move on); `relation` only moves if the meter or the repository
   broke (stop and investigate).
3. **Blowing up is better than returning zero.** If your probe did not find the folder it was meant
   to measure, it raises an error — it never returns `0`. *"I did not look"* and *"I looked and
   there is nothing"* are opposite things, and confusing the two is the defect this whole project
   exists to forbid.
4. **No helper function name may collide with those of the other seven operations.** Prefix with
   something specific to yours (the existing ones use `_instr_`, `_repo_`, `_cer_`, `_dec_`, `_su_`,
   `_hand_`, `_vit_` — pick a free prefix).
5. **`agente.toml` must compile in the forge, with no refusal.** Run `python -m forja
   comunidade/<your-operation>/agente.toml` before opening the PR — the forge's eight refusals fail
   closed, and come with the fix written out.

## What happens after the PR

Someone on the board reads the `RECEITA.md` (is the pain real? is the run in the example true?) and
runs the probe against a test repository. **Accept, ask for changes, or refuse with the reason
written out** — never silence. An accepted operation moves into `operacoes/`, it never stays stuck
in `comunidade/`: this folder is the waiting room, not the final destination.

## Links

- [`operacoes/README.md`](../operacoes/README.md) — the fixed anatomy and the full ruler for "what
  makes a good [operation]"
- [`LACUNAS.md`](../LACUNAS.md) — what this whole project never measures, so your probe does not
  promise what the shelf has already declared out of scope
