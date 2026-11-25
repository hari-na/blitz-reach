# Survey of ten annual reports: do the engine's assumptions hold?

Date: 2026-11-26. Ten FY2025-26 annual reports downloaded from BSE, 131 MB.
Run it yourself: `python -I tools/survey.py data/filings`

Companies: The India Cements, Ramco Cements, Dalmia Bharat, JSW Steel,
EID Parry, Tamil Nadu Newsprint and Papers, Seshasayee Paper and Boards,
Vardhman Textiles, LMW, Suzlon Energy. Chosen because they are the sectors
interview 04's motor rewinding shop actually sells into: cement, steel, sugar,
paper, textile and wind.

```
report                   pages doc unit  msmed accrued value  unit?  caro
-------------------------------------------------------------------------
dalmia-bharat                1 UNREADABLE: PDF Portfolio, real document is embedded
eid-parry                  384    crore      1         17,12   NONE   amt
india-cements              266    crore      2 123.34,110.81   lakh   nil
jsw-steel                  366    crore      2           6,6  crore   nil
lmw                        152    crore      2       nil,nil   NONE   nil
ramco-cements              352    crore      6       nil,nil  crore   nil
seshasayee-paper           324    crore      4       nil,nil  crore     -
suzlon                     474  million      3     7.48,5.77   NONE   nil
tnpl                       298     lakh      1       nil,nil   lakh   nil
vardhman-textiles          167    crore      2       nil,nil  crore   nil

10 reports surveyed, 9 readable
  MSMED note located:              9/9
  interest line found and parsed:  9/9
  of those, interest is nil:       5/9
  unit declared on the note page:  6/9
  note unit differs from doc unit: 1
  CARO six-month clause found:     8/9
  of those, auditor says none:     7/8
```

---

## 1. The wording is consistent enough to automate. Confirmed.

One regex for `interest accrued and remaining unpaid` found and parsed a value in
**9 of 9** readable reports. The MSMED disclosure is statutory boilerplate under
s.22, so companies reproduce the six prescribed items nearly verbatim. Automated
extraction of this signal is viable, which is the single most important thing the
survey establishes.

## 2. One report in ten needs unwrapping, not OCR. Fixed.

Dalmia Bharat publishes as a **PDF Portfolio**, a container holding the real
document as an embedded attachment. Every text extractor sees one page saying
"open this PDF portfolio in Acrobat." It is not scanned and not corrupt; it is a
format the tooling cannot reach.

OCR is the wrong instinct here and would have been wasted work. Nothing is
scanned; the text is perfectly intact one level down. `tools/unwrap.py` reads the
attachments and writes out the largest PDF, which recovered a 249-page readable
report. The survey is now 10 of 10 on a readable document.

Genuinely scanned reports will turn up eventually and will need OCR. Tesseract is
not installed here, so that is unbuilt and untested rather than assumed to work.

Either way a failure has to be reported as a failure, because a screening run
that silently drops companies is worse than one that stops.

## 3. Units are the dangerous part, and they are often not next to the number.

The scale was declared on the note's own page in only **6 of 9**. Worse, in
**The India Cements Limited the note is in lakhs while the first scale declared
in the document says crore.** Anyone automating this will reach for the
document-level declaration, and that is a hundredfold error.

Two compounding traps found:

- The rupee sign extracts as a different character per report depending on the
  embedded font. Observed: a backtick in India Cements, `C` and `D` in LMW.
  A units regex anchored on a fixed symbol list silently finds nothing.
- Scale varies by company, not just by note: crore, lakh and million all appear
  across the ten.

**What changed because of this.** A captured money figure can now record
`as_filed` and `filed_unit`, the figure as printed and the scale printed beside
it, and the conversion is checked at construction. A mismatch raises
`ScaleError` rather than screening. All eighteen figures across the three real
captures reconcile. A test reproduces the India Cements trap exactly and asserts
it cannot be built.

## 4. Nil is the common case. H01 stays silent for the majority.

**5 of 9** report nil interest on every MSMED line, which is an audited statement
that they pay micro and small suppliers within the appointed day. H01 is
therefore a selective signal, not a general one, and it is right that the engine
says nothing about those five.

This is good for credibility and bad for pipeline volume. H01 alone will not
fill a target list.

## 5. H04 is nearly inert at this tier. This was a surprise.

The CARO clause vii(a) six-month arrears test was designed as the engine's
highest-confidence hypothesis, because the auditor reports it directly. In
practice the clause was found in 8 of 9 reports and the auditor asserts **none**
in 7 of those 8. Only EID Parry showed an amount.

So the hypothesis I ranked strongest almost never fires at the large-listed tier.
It is not useless: a filed zero is what makes an abstain mean "the documents were
read and this is clean" rather than "nobody looked", and that is exactly how the
LMW brief reads. But it will not be the hypothesis that finds anybody.

**The practical ordering is the reverse of the designed one.** H03, disputed GST
demands, is the workhorse: India Cements alone carries Rs 190.48 crore of it.
H01 is selective. H04 is a clearing test.

## 6. Four companies show non-nil interest, and most are still immaterial.

India Cements (123.34 lakhs), JSW Steel (6 crore), Suzlon (7.48), EID Parry (17).
Set against revenue, JSW Steel's Rs 6 crore is about 0.003% and India Cements'
total late-payment cost is 0.059%. Both are below the 0.1% materiality floor.

So the honest base rate so far: of ten large listed companies, **zero** would be
approached on late payment to small suppliers alone. That is a real finding about
the hypothesis, not a bug, and it is worth saying out loud rather than tuning the
floor until something passes.

---

## What this means for the product argument

The survey supports the central claim and narrows it.

Automated extraction of statutory disclosures across thousands of companies is
clearly feasible: the wording is boilerplate and one regex works 9 times in 9.
What is not feasible is doing it carelessly, because the three failure modes
found here, an unreadable container format, a scale declared on a different page,
and a currency glyph that varies by font, all produce silent wrong answers rather
than errors. Every one of them is a reason the engine should refuse rather than
guess, which is the same argument the materiality floor makes.

And the hypothesis portfolio needs rebalancing on evidence rather than on how
compelling each one sounded when written.


---

## 7. A second signal source was added, and it cannot find anything

Added after the first survey, because one document family is one point of view.
The candidate was credit rating rationales: free, public, short, and written by
an analyst rather than by the company about itself.

Two were read in full.

- **Ramco Cements, Crisil, March 2026, AA+/Stable.** 29,859 characters, read end
  to end. Mentions creditors, trade payables, creditor days and the working
  capital cycle **nowhere**. The only working-capital sentence is that bank lines
  are expected to meet incremental requirements.
- **The India Cements, Crisil, March 2023.** Also mentions creditors, payables
  and liquidity nowhere.

So the hypothesis that rating documents would yield payables findings is dead.
Analysts write about payables once payables are already the problem, which means
a rating document cannot be where you discover one.

**What it does carry is whether the company can act at all**, and that turned out
to matter more. The India Cements rationale revised the company to BB/Stable
**Issuer Not Cooperating**, then withdrew its ratings at the company's own
request, after Crisil followed up by letter on 3 January, 3 February, 17 February
and 23 February 2023 and received nothing.

The engine sizes a real Rs 34.29 crore GST interest exposure at that company,
0.765% of revenue, comfortably past the lead floor. And an organisation that
stops answering its own rating agency will not answer an outbound approach about
its accounts payable. The approach is wasted either way.

**So the second vector is a qualifier, not a finder.** `grounds/qualifiers.py`
never creates a finding; it only vetoes one, and the brief prints what was found
next to the reason for leaving it. India Cements flips from actionable to
abstain, which takes the engine to **all three real companies refused**, for
three different documented reasons:

| Company | Refused because |
|---|---|
| LMW | nil MSMED interest on every line. Audited proof it pays on time |
| Seshasayee | nil interest, and the capture was never finished. The brief says which figures are missing |
| India Cements | a real material finding at a company that stopped answering its own rating agency |

That is a better result than one hit. Anyone can build something that finds a
problem everywhere it looks.
