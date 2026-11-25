# Grounds

Reads what a company has already filed about itself, decides whether there is a
finance-operations problem worth naming, and refuses to say anything it cannot
cite and show the arithmetic for.

## Why the refusing is the product

Zamp can diagnose roughly 30 accounts a month because a forward-deployed
engineer does each one by hand. The bottleneck is not writing outreach. It is
knowing which 40 companies out of a thousand have a problem you can name with
evidence.

Every tool in this space optimizes for coverage: give it any company and it
produces a confident paragraph. That is why nothing lands. This one is built to
read a thousand and refuse most of them, so the ones it does not refuse are
worth an hour of someone's time.

On the four fixtures shipped here it refuses three.

## The three rules it is built on

**1. Nothing enters without a citation.** A `Signal` cannot be constructed
without a `Source` naming the document, the year and the exact place inside it.
A `Source` without a locator raises. This is enforced in `__post_init__`, not by
convention, because the reliability claim is the whole product.

**2. No model decides anything.** A hypothesis is a deterministic function over
filed signals. It fires with a computed magnitude and written-out arithmetic, or
it does not fire. The language model writes the opening paragraph at the very
end, and `check_no_new_numbers` re-reads its output and discards the draft if it
contains a figure that was not in the input.

**3. Everything is divided by revenue.** The materiality floor is named
`QUICKLIME_FLOOR` after interview 02, where a quicklime processor was asked
about weighbridge variance. Differences large enough to reach him happened two
or three times a year at 400 to 500 kg, which at Rs 8,250 a tonne is about
Rs 10,000 against roughly Rs 20 crore of revenue. He said it did not matter and
he was right, and the only way to establish that was to extract a frequency and
a unit price and multiply them. An engine that surfaces a finding like that has
not found a problem, it has spent the one piece of attention it was given.

Every hypothesis also has to state `kills_if`: the answer that would disprove
it. A claim with no disconfirming answer is not a hypothesis, it is a sales
line.

## Run it

```bash
pip install -r requirements.txt
```

Screen a directory, one row per company, verdict first:

```bash
python -m grounds.cli screen data/companies
```

Full brief for one company:

```bash
python -m grounds.cli brief data/companies/kaveri-cements.yaml
```

The brief that matters is the refusal:

```bash
python -m grounds.cli brief data/companies/nilgiri-textiles.yaml
```

Tests:

```bash
python tests/test_judgment.py
```

Several of the eleven tests pin a refusal, because refusing is the behavior most
likely to erode as hypotheses get added.

## No API key required

Nothing above calls a model. Provenance, hypotheses, arithmetic, materiality,
ranking and all three verdicts are deterministic, so the engine runs offline with
`pyyaml` as its only dependency.

The model writes the opening paragraph, and even that path runs without a key:

```bash
python -m grounds.cli brief data/companies/kaveri-cements.yaml --prose
```

With `ANTHROPIC_API_KEY` set this calls the model. Without one it replays a
recorded take from `data/replay/`. Both go through the same verification.

The more interesting thing to look at is the guard catching a bad draft:

```bash
python -m grounds.cli brief data/companies/kaveri-cements.yaml --prose --take rejected
```

That take invents a total and a share of revenue. The brief reports exactly what
was caught, drops the draft, and falls back to the deterministic opening:

```
> Draft discarded by the number guard: introduced numbers not present in the
> evidence: 126.00, 3.2. Using the deterministic opening instead.
```

The takes in `data/replay/kaveri-cements.json` were written by hand against the
composer's own system prompt, because no key was available when this was built.
The file says so. They are stand-ins, not transcripts, and `--prose-mode live`
plus a key replaces them with the real thing.

## The three verdicts

| Verdict | Meaning |
|---|---|
| `actionable` | one finding clears the 0.5% lead floor on better-than-weak evidence |
| `thin` | something fired, nothing worth opening a conversation with |
| `abstain` | nothing survived the materiality floor, or the filings were too thin to size anything |

No revenue figure means `abstain` before any hypothesis runs. Without a
denominator nothing can be tested for materiality, and sizing a problem without
one is the error this engine exists to avoid.

## What it reads

Indian statutory filings, because they carry a signal US disclosure does not:
whether a large company pays its small suppliers late is a filed, audited number
here, not an inference.

| ID | Hypothesis | Source | Confidence ceiling |
|---|---|---|---|
| `H04` | Undisputed statutory dues outstanding over six months | CARO 2020 clause vii(a), auditor reported | high |
| `H01` | Statutory interest on late payment to micro and small suppliers | MSMED Act s.22 disclosure in the annual accounts | high |
| `H03` | Interest running on disputed statutory dues | contingent liabilities note | medium |
| `H02` | Payables cycle out of line with the sector | balance sheet plus a sector comparator | medium |
| `H05` | Open headcount in reconciliation and payables | job postings | low, can never lead |

`H05` exists to be weak. A brief resting only on it has to come out `thin`, or
an engine with nothing good to say starts promoting its worst signal.

Statutory rates live in `grounds/hypotheses/rates.py` with the provision each one
comes from, so a reader argues with the law rather than with us. `RBI_BANK_RATE`
is assumed and flagged: verify it against the current notification before any
live use, because every MSMED interest figure scales with it.

## What is not real yet

The four company files in `data/companies` are **synthetic fixtures**. They carry
`capture: synthetic`, every brief prints that in its footer, and the cited
documents do not exist. They exercise the engine across all three verdicts; they
are not evidence about anyone.

`data/companies/_template.yaml` is the shape for a real capture. Next step is
three real ones, captured by hand from published annual reports, with
`capture: hand_seeded`.

## Where the reasoning came from

`../research/` holds five recorded interviews with four businesses, the question
guides, and the decision history including every idea that was killed and why.
Two of the four subjects had nothing worth solving, which is the most useful
result in the set: one denied a Rs 64,000 loss about a minute after describing
it, and one correctly dismissed a problem worth about Rs 10,000 a year. Neither
self-report answered the question. That is the empirical case for diagnosing a
business from what it has filed rather than from what it says.
