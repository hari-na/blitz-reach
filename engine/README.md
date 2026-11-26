# Grounds

Reads what a company has already filed about itself, decides whether there is a
finance-operations problem worth naming, and refuses to say anything it cannot
cite and show the arithmetic for.

## Why the refusing is the product

This is not a lead generator. Zamp does not need more companies: its pipeline is
already longer than the people available to work it, and it is hiring to catch
up. Every company in that pipeline is there because somebody did outbound and
somebody else picked up the phone, which qualified them on reachability and on
nothing else.

So the question worth answering is not "who could we approach". It is **"we have
N people this month, which N companies?"**

```bash
python -m grounds.cli screen data/companies --capacity 3
```

```
3 slots this month, 7 companies screened.

## Work these, in this order
1. Kaveri Cements Ltd - interest on late payment to micro and small
   suppliers, Rs 47.50 cr a year, 1.131% of revenue, high confidence

## 2 slots unfilled
There is no 2nd company here worth an approach, and filling the slot anyway
is how a pipeline fills with companies nobody can name a reason for. The
constraint is not people. It is evidence.
```

Leaving slots empty is the whole point. A prioritiser that always returns N
companies is a lead generator wearing a different label, and it rebuilds the
problem it was meant to fix.

Every tool in this space optimizes for coverage: give it any company and it
produces a confident paragraph. That is why nothing lands. This one is built to
read a thousand and refuse most of them, so the ones it does not refuse are
worth an hour of someone's time.

On the seven companies shipped here it refuses six, including all three real ones.

## What it says about three real companies

Captured by hand from FY2025-26 annual reports downloaded from BSE, every figure
cited to a page.

| Company | Verdict | Why |
|---|---|---|
| The India Cements Limited | **abstain** | Rs 34.29 cr of GST interest exposure, 0.765% of revenue, real and material. And Crisil tagged the company Issuer Not Cooperating and withdrew its ratings, so the finding is left on the table |
| LMW Limited | **abstain** | every interest line in its MSMED note is nil. Audited proof it pays small suppliers on time |
| Seshasayee Paper and Boards | **abstain** | nil MSMED interest, and the capture was never finished. The brief says which figures are missing |

All three refused, for three different documented reasons. That is the result
worth showing: anything can be built to find a problem everywhere it looks.

### A second source that only subtracts

Credit rating rationales were added as an independent signal family. Read in
full, Crisil's March 2026 rationale for Ramco Cements (AA+/Stable, 29,859
characters) mentions creditors, trade payables and the working capital cycle
**nowhere**, and nor does its March 2023 rationale for India Cements. Analysts
write about payables only once payables are the problem, so a rating document
cannot be where you discover one.

What it reliably carries is whether the company can act on a finding at all. So
`grounds/qualifiers.py` never produces a finding, only a veto, and the brief
prints what was found beside the reason for not calling.

**Reading real filings corrected two real errors**, which is the entire reason
to do it rather than reason from fixtures.

H01 used to size late payment off the principal balance in the MSMED note. That
balance is a closing figure including invoices not yet due, so it only proves the
company buys from small suppliers. LMW has Rs 75.52 crore of it and nil interest
on every line, meaning it pays on time, and the old version would have walked
into Coimbatore announcing a problem the company's own auditors say it does not
have. Interest is the real signal: under s.16 it exists only where payment went
past the appointed day.

H03 used to size off total disputed statutory dues. India Cements' annexure
totals Rs 930.26 crore, mostly excise and sales tax running from 1995-96, sitting
at the Supreme Court and CESTAT, plus Rs 438.62 crore of electricity, stamp duty
and mining cases. Thirty years of tax law under appeal is not a reconciliation
failure. It now takes the GST slice only, because GST is self-assessed and a
demand under it starts as a disagreement between a filed return and the ledger,
and the brief prints what was excluded so a reader can argue with the choice.

India Cements also pays real MSMED penal interest, Rs 1.41 crore of it during the
year, and the materiality floor still throws it out at 0.059% of revenue. Both
halves work: finding it, then declining to lead with it.

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

Fifteen tests, and most of them pin a refusal, because refusing is the behavior
most likely to erode as hypotheses get added. Four pin judgments the real filings
taught: that nil filed interest means silence, that disputed dues are sized on
the GST slice and not the grand total, that real penal interest can still be
immaterial, and that a half-finished capture has to admit it.

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

## What ten reports say about these assumptions

Surveyed with `python -I tools/survey.py data/filings` over ten FY2025-26
reports. Full write-up in `../research/03-filing-survey.md`.

| | |
|---|---|
| MSMED note located by one regex | **9 of 9** readable |
| Interest line parsed | **9 of 9** |
| Interest is nil, so H01 stays silent | **5 of 9** |
| Scale declared on the note's own page | **6 of 9** |
| CARO six-month clause says none, so H04 cannot fire | **7 of 8** |
| Reports unreadable at all | **1 of 10** |

Four things came out of that, and two of them changed the code.

**The wording is boilerplate, so extraction is automatable.** One regex worked
every time. That is the finding the whole approach depends on.

**Units are the real hazard.** India Cements prints its MSMED note in lakhs while
the first scale declared in the document says crore, and the rupee sign extracts
as a different character per report depending on the embedded font: a backtick
in India Cements, `C` and `D` in LMW. A money figure now records `as_filed` and
`filed_unit`, the figure as printed and the scale beside it, and the loader
multiplies them out and **refuses the capture if it disagrees with the value**.
All eighteen figures in the three real captures reconcile, and a test reproduces
the India Cements trap and asserts it cannot be built.

**One report in ten cannot be read.** Dalmia Bharat publishes a PDF Portfolio,
a container holding the real document as an attachment, which every extractor
sees as one page saying "open this in Acrobat." The survey reports it as a
failure rather than skipping it.

**The hypothesis ranking was backwards.** H04 was designed as the strongest
signal because the auditor reports it directly, and in practice 7 of 8 auditors
say there is nothing to report, so it almost never fires. It still earns its
place: a filed zero is what makes an abstain mean "read and clean" instead of
"nobody looked." But H03, disputed GST demands, is the hypothesis that actually
finds anybody, and H01 is selective. Of ten large listed companies, **none**
would be approached on late payment to small suppliers alone.

## Three kinds of output, not one

A finding carries a money figure and can lead a brief. A veto carries none and
only stops one. A **context** carries none either, never moves a verdict, and
says what shape the company is.

Contexts exist because the two indicators that survived testing against ten
reports, the share of purchases from small suppliers and the number of entities
consolidated, do not convert honestly into rupees. Exposure is not a loss.
Forty subsidiaries is not a cost until you invent a cost per subsidiary, and
inventing numbers is the thing the composer's number guard exists to stop.

| | Reads | Says |
|---|---|---|
| `C01` Exposure to small suppliers | BRSR Principle 8, with the prior year | What share of purchases is in MSMED scope, and which way it is moving |
| `C02` Close complexity | The stated subsidiary, joint venture and associate counts | How many entities roll up into one month-end close |

C01 earns its place by saying when a silence means nothing. Seshasayee Paper
sources **59%** of its inputs from small suppliers, up from 51%, and reports nil
MSMED interest on every line. That nil is real discipline. The identical nil at
a company sourcing 2.69% would be an artifact, and the brief says so instead of
letting a reader treat them as cleared.

India Cements went from **1.12% to 17%** in one year. Either its supply base
changed or its definition did, and both are worth asking about.

Every figure is printed beside last year's in an annual report, so trends cost
nothing extra. The prior year is scale-checked exactly like the current one.

## What it reads

Indian statutory filings, because they carry a signal US disclosure does not:
whether a large company pays its small suppliers late is a filed, audited number
here, not an inference.

| ID | Hypothesis | Source | Confidence ceiling |
|---|---|---|---|
| `H04` | Undisputed statutory dues outstanding over six months | CARO 2020 clause vii(a), auditor reported | high |
| `H01` | Interest on late payment to micro and small suppliers | MSMED Act s.22 disclosure, the interest lines, not the balance | high |
| `H03` | Interest exposure on disputed GST demands | CARO clause vii(b) annexure, GST rows only | medium |
| `H02` | Payables cycle out of line with the sector | balance sheet plus a sector comparator | medium |
| `H05` | Open headcount in reconciliation and payables | job postings | low, can never lead |

`H05` exists to be weak. A brief resting only on it has to come out `thin`, or
an engine with nothing good to say starts promoting its worst signal.

Statutory rates live in `grounds/hypotheses/rates.py` with the provision each one
comes from, so a reader argues with the law rather than with us. `RBI_BANK_RATE`
is assumed and flagged: verify it against the current notification before any
live use, because every MSMED interest figure scales with it.

## Real captures and fixtures

Three company files are real, marked `capture: hand_seeded`, read by hand from
the PDFs in `data/filings`. Find the figures in a 300-page report with:

```bash
python -I tools/peek.py data/filings/india-cements-fy2026.pdf
```

Four files are **synthetic fixtures** carrying `capture: synthetic`. Every brief
prints that in its footer and the documents they cite do not exist. They stay
because they exercise paths the real captures do not, such as a company with no
revenue figure at all, and a company where the only surviving finding rests on
the deliberately weak signal.

`data/companies/_template.yaml` is the shape for a new capture. A leading
underscore keeps it out of `screen`.

## Not tested is not the same as clear

An abstain has two very different causes and the brief never blurs them. A
hypothesis that ran on complete filings and found nothing appears under **Tested
and clear**. One that never ran appears under **Not tested**, with the exact
signals it was missing. LMW abstains with two hypotheses clear; Seshasayee
abstains with four never tested, and its brief says so rather than passing an
unfinished capture off as a clean company.

## Where the reasoning came from

`../research/` holds five recorded interviews with four businesses, the question
guides, and the decision history including every idea that was killed and why.
Two of the four subjects had nothing worth solving, which is the most useful
result in the set: one denied a Rs 64,000 loss about a minute after describing
it, and one correctly dismissed a problem worth about Rs 10,000 a year. Neither
self-report answered the question. That is the empirical case for diagnosing a
business from what it has filed rather than from what it says.
