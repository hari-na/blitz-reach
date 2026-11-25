# Current candidate and full kill list

State as of 2026-11-16. Read with `00-synthesis.md` and the interview logs.

---

## The current leading idea: enterprise AP is blind to the quotation

**The mechanism, in one example.**

A cement plant's motor fails and goes to Pearl Engineering (interview 04). Pearl strips
it, inspects it, and quotes Rs 1,96,000. The buyer's purchase department raises a PO for
Rs 1,84,500 — a typo, or a unilateral discount, it does not matter which.

Pearl invoices **Rs 1,84,500**, not its own quoted figure. This is their stated standing
policy: *"Even if the customer has made a small mistake in the PO amount, we raise the
invoice for that PO amount."* Contesting it means driving to the buyer's accounts
department with printed email threads and waiting months.

What now arrives in the buyer's AP: invoice Rs 1,84,500, PO Rs 1,84,500, goods receipt
present. **A perfect three-way match.** Approved untouched. Counted as a clean, touchless
transaction. Pearl absorbed Rs 11,500 and told nobody.

**The inversion, which is the actual insight.** The error has no preferred direction. If
the buyer had typed Rs 2,19,000, Pearl would have invoiced Rs 2,19,000 under the same
policy, and would certainly not have called to complain. Invoice, PO and receipt agree
perfectly again. **The buyer overpaid Rs 23,000 and no control in the building will ever
flag it**, because three-way match compares invoice to PO to receipt and all three agree.

The only document that says Rs 1,96,000 is the quotation, and it lives in the supplier's
sent mail. It was never in the buyer's system.

**The consequence for Zamp.** Their published outcome metrics ("95%+ of invoices
end-to-end", "80% of manual work automated") are measured by the same system that
produced them, inside the buyer, on documents a supplier silently conformed to the
buyer's figure. Automation causes the conformance: pre-automation an AP clerk would phone
the supplier and sort it out; post-automation, exact matching means the supplier's only
survival strategy is pre-emptive conformance.

**Why it is specific rather than generic.** This is about **scope-discovered work** —
repair, overhaul, maintenance, professional services, anything where the price is created
*after* a physical inspection. There is no contract price or price list to validate
against. The number is born in an emailed quotation and can legitimately change mid-job.
Standard four-way match adds an inspection record, not the quote.

**Why it is commercially right for Zamp:** it sells to the buyer (their existing GTM and
the only party with budget), it is revenue-additive rather than cannibalising, and the
customer cannot state the problem because the data defining it is not theirs — which is
the FDE shape.

**The line:** "Your 95% touchless rate is partly a measure of how much your suppliers are
quietly eating. I can show you the number, and nobody inside your AP system can."

**The number to own:** the fraction of clean three-way matches that disagree with the
supplier's quotation. Currently unmeasured by anyone.

---

## Known weaknesses of this candidate

1. **It may be overfitted to one interview.** The mechanism is evidenced by exactly one
   business (Pearl). The radiologist's case is argued to be "the same mechanism at a
   different distance," but that is an interpretation, not a second instance.
2. **It may already be addressed** by the recovery-audit industry, contract-compliance
   tooling, spend analytics, or buyer-side four-way match variants.
3. **Market size is unknown.** Scope-discovered work may be a small share of enterprise
   AP spend.
4. Only lightly validated against how enterprise AP, internal audit and external audit
   actually treat price variance today.

---

## KILL LIST — do not re-propose any of these

Rejected by the applicant:
- **Reusing his existing projects** (`kaasu` finance dashboard, Obsidian tax playbook).
  Judged hobby-grade.
- **A self-explaining exception queue that learns from operator corrections.** Table
  stakes for a company already serving Instacart and Block.
- **Adversarial / AI-generated invoice fraud detection.** The demo requires Zamp's own
  agent, which nobody applying can access, so the central claim is unverifiable and
  collapses if the CEO says "we handle that."
- **An agent management layer / control room** for digital employees. Reads as a dashboard.
- **"This process is redundant, delete it."** Zamp prices per process, so it reduces their
  own revenue.

Killed by market research:
- **An inbox-watching supplier-side document agent** (recognise inbound POs/invoices from
  email, extract, match against the supplier's records, flag missed POs, below-quote POs
  and short payments). Dead because:
  - **Conexiom** has done emailed-PDF-POs into ERP since 2012; 100,000+ formats; certified
    SAP S/4HANA app; validates against ERP master data before posting.
  - **Duvo** raised $32M (Balderton, Oct 2026) for agents across ERPs, supplier portals,
    spreadsheets and inboxes. **Stuut** raised $52.5M (Insight, Oct 2026) for agentic
    order-to-cash.
  - **HighRadius** and **Esker** have sold short-payment and deduction management for 15+
    years; Esker's bots already log into customer portals to retrieve deduction backup.
  - **Microsoft** ships an inbox-watching Payables Agent inside Dynamics 365 Business
    Central. The moat on "watch the inbox, recognise the document" is zero.
  - Extraction is commodity: ~$0.30/run (Nanonets), Docsumo free tier covers 1,000
    pages/month, which exceeds Pearl's entire PO volume.
  - The exact MVP is already a published blog post: Gmail to Tally POs with GPT-4,
    claimed 98% extraction accuracy.
  - **It fails on our own evidence.** Interview 03 has no second document to match
    against (he is locked out and keeps no record of his own output), and interview 04 has
    a standing policy of ignoring the variance, so the alert fires for an event the user
    has already decided to absorb.
- **Supplier portal submission agents.** Interview 04 explicitly disconfirmed this:
  portals are "quite simple," always a named contact. **Tesorio** already ships a Coupa
  and Ariba submission agent, and Visa, BILL and Billtrust began a live pilot in Oct 2026
  for agents acting inside supplier portals.
- **Selling anything to the small business itself.** Zamp's own published buyer's guide
  says they are not for small businesses, and both willing subjects are below the market
  floor of every enterprise tool. The gap there is distribution and price point, not
  capability, which is not a product insight.

Rejected on judgment grounds (keep as a pitch sentence, do not build):
- **The EDF filing agent.** Now **confirmed**: from 1 October 2026 the Export Declaration
  Form covers goods, software and other services, and SOFTEX is discontinued; services
  previously required no declaration at all. Transition treatment for September invoices
  is contested and RBI has not published a rule. Still rejected as the MVP because it
  reads as a narrow Indian compliance utility rather than an enterprise finance product,
  and because a regulation six weeks old with unpublished FAQs is a bad thing to stake a
  demo on. The generalizable half survives as a sentence: a regulatory change lands as
  unallocated manual work on whoever cannot refuse it.

---

## Open structural observations worth reusing (not yet products)

- **Zamp owns the inside of a boundary and is paid by the party inside it.** All six
  published workflows are one machine: a document arrives from outside, is checked against
  internal records and rules, then approved, routed or filed. Both good interviews are the
  outside of that same boundary.
- **The asymmetry worsens as Zamp wins.** An automated buyer demands exact matching, so
  every touchpoint removed on the buyer's side raises the precision demanded of a supplier
  still working by hand.
- **Detection without resolution is net-negative**, which is why both willing subjects
  switched off their own measurement. Pearl invoices the buyer's number and does not look;
  the radiologist audited for a few months and stopped. Anything that only surfaces
  problems gets muted.
- **Neither business owns a system of record for what it is owed.** The authoritative
  record sits in the counterparty's database and arrives as an artifact addressed to a
  human.
- **Counterparty knowledge travels between Zamp's customers; process knowledge does not.**
  The same vendor sends the same documents to two different Zamp customers, so it is the
  one cross-customer asset that is legally clean (the shared party consents directly).
  Candidate metric: pre-warmed coverage, the share of a new customer's invoice spend
  already known on day one.
- **E-invoicing mandates make reading an invoice worth nothing** and standardise none of
  the argument (scope change, cancel-and-reissue, unilateral discounts, short pays).
  Value migrates from capture to contest. India's IRN proves registration, not that
  anything was ordered, received or priced correctly.
- **The non-delegable hour is the escalation, not the data entry.** Both owners named
  standing in front of a counterparty (an accounts department, a bank officer), not
  typing. The transcription is already done by junior staff. The deliverable they need is
  an argument, not a record.
- **Retraining latency as the real moat.** A shared brain absorbs a new regulation in a
  day; a BPO retrains in a quarter. Zamp's best published number is only 30% below BPO on
  cost, so cost is a weak argument. Time-to-compliance after a rule change is one no BPO
  can put in a contract.
