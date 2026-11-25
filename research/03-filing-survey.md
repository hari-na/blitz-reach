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

## 2. One report in ten is not readable at all. New.

Dalmia Bharat publishes as a **PDF Portfolio**, a container holding the real
document as an embedded attachment. Every text extractor sees one page saying
"open this PDF portfolio in Acrobat." It is not scanned and not corrupt; it is a
format the tooling cannot reach.

A 10% hard-failure rate has to be reported as a failure, not silently skipped,
or a screening run quietly drops companies and nobody knows which.

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
