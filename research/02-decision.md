# Decision: what to build

Consolidated from eight agent passes. 2026-11-16. Supersedes `01-current-candidate.md`.

---

## The pick: Second Opinion — independent review of an AI employee's work

**One sentence.** When a digital employee owns a finance function, its accuracy becomes
self-reported by the same system that produced it, so Zamp should ship what every
profession that trusts expert judgment already has: randomised, independent, severity-graded
re-performance of a sample of completed work, producing a materiality-weighted error rate
per class of judgment that nobody inside the customer's system can compute.

### The four arguments, in the order they should be made

**1. Every control in enterprise finance verifies agreement, not correctness.**
Three-way match confirms three documents agree. Reconciliation confirms two balances
agree. A touchless rate confirms that nothing argued. None of them verify the judgment:
which rate card, which GL account, which tax treatment, which severity. A set of
perfectly agreeing documents can be uniformly, silently wrong. Confirmed externally: a PO
coded to the wrong account at requisition matches cleanly and posts confidently to the
wrong place, and a miscoded line does not move an account large enough to hide it.

**2. The failure mode changes when the worker is an AI, and every existing control was
built for the old one.** Human error is random and idiosyncratic: a clerk miscodes freight
invoices differently each time. Agent error is systematic and correlated: an agent
miscodes *every* freight invoice the same wrong way. Correlated error does not average
out, never presents as an outlier, and is invisible to the entire incumbent stack, because
anomaly detection hunts the tail of a distribution and a uniform bias sits in the mode.
**Anomaly detection finds the tail. Only sampled independent re-performance finds the
bias.**

**3. Replacing the BPO deleted its quality function, and nobody noticed.** This is the
argument that should win the room. AP outsourcing ships with QA as standard practice: a
defined sample of completed work, a measured defect rate, **severity bands agreed in the
contract rather than argued afterwards**, risk-tiered sampling plans, accuracy SLAs around
98%. Zamp sells against BPOs. The BPO could be held to a number; the digital employee
reports its own.

**4. It is the condition on which a customer extends autonomy to the next process.** A
BPO structurally cannot show you its own error rate. A shared-brain vendor can, and can
do it adversarially. Since Zamp prices per process, a credible measured error rate per
class of judgment is what converts one process into three. It also attacks their own
stated problem: it tells you in week two which judgments are safe to automate instead of
in month six.

### Where it came from: the interviews, not a whiteboard

- **Interview 03** contains a formal production QA regime nobody examined for four
  passes: **5 to 10% of his reports are randomly redistributed to other radiologists and
  graded on a miss-severity scale, paid as a separate billing line.** Real-world anchor:
  ACR RADPEER, 18,000+ radiologists, 1,100+ groups, a 1 to 3 scale with sub-classification
  for clinical significance. **Medicine solved this in 2002.** QA is a funded production
  line item there, not overhead.
- **Interview 03** also gives the other half: GMC annual appraisal feeding five-year
  revalidation. A licensed professional must periodically re-demonstrate competence to
  keep working. That is the missing half of "digital employee."
- **Interview 03** on the nature of the disputes: when his count disagreed with the
  client's it was never arithmetic, it was *"perceptions of what particular studies
  are... disagreements with the principles, rather than undercounting."* **Classification
  disputes, not counting disputes.** That is exactly the class of error this detects.
- **Interviews 03 and 04** both stopped measuring because measurement had no resolution
  path, so QA must be re-performance **with a disposition**, never a report.
- **Interview 02b** is the proof of method: the only subject who judged his own exposure
  correctly did so because frequency times unit price got multiplied. Severity grading is
  that multiplication, institutionalised.

### Market position: genuinely unbuilt, and the spec is being written now

Three adjacent categories are funded. This one is not.

| Category | Status | Examples |
|---|---|---|
| **Audit the transaction** | Mature | AppZen ($180M Series D, Sept 2025), Oversight Systems, MindBridge, Pathlock (~$220M), Coupa SpendGuard, plus 50 years of recovery audit. All answer "was this transaction wrong?" |
| **Automate the auditor** | Hot | Petual ($20M, a16z), Midship, Clark, Auditstage; all four Big 4 (KPMG first with AIUC-1 after ISO 42001; EY rolling agentic AI across ~130,000 auditors) |
| **Govern and log the agent** | Became real in 2026 | Drata AI Agent Governance (Aug 2026, tool-call proxy), OneTrust, Vanta, ServiceNow AI Control Tower, Workday Agent System of Record, Baselayer ($35M Series A, "Know Your Agent") |
| **Independently verify the decision was correct** | **Unbuilt** | — |

Baselayer **explicitly disclaims** verifying whether the agent decided correctly. Every
claim of agent-decision auditability comes from the vendor whose agent it is: AppZen's
"audit trail behind every decision," Basware's "explainable by design," Maximor's agents
auditing each other inside Maximor. Nobody independent tests the decision.

**And it is unbuilt for a structural reason, not a demand reason: the incumbents best
placed to build it now ship agents themselves, so auditing the agent means auditing
yourself.** AppZen currently gates its own website behind a Gartner report on governing
agentic AI.

**The standard-setters are ahead of the tooling:**

- **ISACA, 2026**, *"Auditing Agentic AI Workflows: How to Control-Test When the System
  Decides for Itself"*: non-determinism kills transaction sampling as audit evidence;
  prescribes **output-distribution analysis against a documented baseline**; names zero
  tools.
- **Gartner, Aug 2026**, *CFO Guide to Governing Agentic AI*: requires traceability,
  **continuous output checking**, and evaluation gates before outputs reach systems of
  record; judge pilots on governance readiness rather than ROI.
- **IDC, Sept 2026**, *"The audit trail that doesn't exist"*: **more than a third of
  enterprises already run agents in finance and accounting** while most cannot verify
  what those agents do, and 35% cannot shut down a rogue agent.
- **Forrester** (commissioned by Oversight): **60% of 207 finance and audit leaders** say
  volume prevents them from meaningfully auditing total company spend.
- SOX's "test of one" for automated controls rests on determinism. Practitioners have
  noticed it breaks for AI-enabled controls and **no PCAOB, AICPA or COSO guidance exists
  on what replaces it.** The sample-size question is open and unowned. *(State this as a
  live debate, not settled guidance.)*

**Touchless rates are self-graded and definitionally soft.** Medius defines touchless as
"approved without any user intervention whatsoever" at 63.8% average and 94.9%
best-in-class. Coupa's 87.4% first-time match is a top-quartile median, not a population
median. Hackett's 60% is an average across customers of assessed vendors. **There is no
independent published figure for the share of invoices failing three-way match.**

**Agent eval tooling is not this.** LangSmith, Braintrust, Patronus and the judge services
are build-time, test-set, vendor-owned, and graded against a reference answer. Not
production-sampled, not customer-owned, not graded in money. MindBridge's Sept 2026
"Agentic Risk Assessment" is the nearest competitor and bets the opposite way:
full-population anomaly scoring, which by construction cannot see a uniform bias.

### The number to own

**The materiality-weighted rate at which automated judgments are wrong, per class of
judgment, with a confidence interval.** Confirmed unowned by anyone.

### The hinge quote, in Zamp's own words so it cannot be contradicted

Their homepage: they optimise for **"a business outcome and not just the accuracy of a
single response."** They then publish outcome figures with no methodology, no error rate,
no SLA and no independent verification.

### The demo

1. Build a toy AP agent. Process ~500 synthetic invoices. It reports **96% touchless.**
2. Seed a **correlated** defect: every freight invoice from one vendor class gets the
   wrong rate card.
3. Run an anomaly-detection / continuous-monitoring pass over the same population. **It
   returns clean** — the bias is in the mode, not the tail. Show this side by side.
4. Run Second Opinion: stratified random sample weighted by materiality and judgment
   class; **re-perform each decision independently** (different evidence path, different
   prompt, no sight of the first decision); grade disagreements on a 1 to 3 severity scale
   with financial-significance sub-classification.
5. Output: measured error rate per judgment class with a confidence interval, the
   rupee-weighted exposure, and a signed evidence pack.
6. Close on the digital employee's record: role, graded review history, revalidation date.

Both halves are built here, so nothing depends on access to Zamp.

### Risks, stated honestly

1. **Nearest kill-list item is the agent management dashboard.** The defence must be
   structural, not rhetorical: a control room *displays what the agent reports about
   itself*; this *re-performs the work and produces a statistic that exists nowhere in the
   system*, and it is sold to a different buyer. If it still reads as a dashboard, it is
   dead.
2. **Do not overstate the SOX angle.** It is a live practitioner debate, not guidance.
3. **The inversion to lead with:** every vendor works the exception queue. The risk lives
   in the 95% that **never became an exception.**
4. **SAP ships a partial counterexample.** Standard Logistics Invoice Verification
   includes a **stochastic (random) block** — table T169P, fields `XSPST`, `BTSTO`,
   `PRSTO` — which blocks invoices for payment at a configured probability. It is opt-in
   and off by default. **A knowledgeable listener may raise it.** The answer: it samples,
   but it compares to nothing, and it grades nothing.

---

## What died, and why

### Quotation-blindness in three-way match — DEAD, three independent kills

1. **The novelty claim is false and cheaply disproven.** Cognilium published
   *"Three-Way Matching Cannot Catch a Wrongly Priced PO"* in August 2026. Phacet Labs
   sells against it with the bullet "a PO raised at the wrong price, which the invoice
   then matches cleanly." CostCrunch is a whole company built on quote-versus-invoice
   auditing, claiming 4 to 8% average overpayment across $125M+ audited. On a screen that
   tests judgment, being caught not having searched for your own thesis is worse than a
   mediocre idea.
2. **The load-bearing direction has no evidence anywhere.** Every quote from Pearl is
   about *losing* money; he absorbs discounts. The buyer-overpays inversion was invented
   in this session, never said by him, never asked about. Enterprise AP structurally
   suppresses it: invoices above the PO are rejected or routed, and standard tolerances
   (e.g. Oracle Fusion price 8%; USC 20% or $500) absorb exactly the small typos
   described. For the buyer to overpay, the supplier must knowingly pocket a windfall,
   which is a different act.
3. **The money is not there.** Generous sizing at a $20B-revenue industrial: ~$1.25M/year,
   about **1 basis point** of the sub-segment, 0.006% of revenue. Recovery audit already
   recovers 7.8 bps of audited spend across all claim types. Three to four orders of
   magnitude below external audit materiality.

**And the cost-of-control datum that ends it:** one published case tightened price
tolerance from 7%+$60 to 2%+$25, took held lines from 899 to 3,700, and recovered about
$5,300 — roughly $26,000 of marginal handling cost to find $5,300. **The control
environment has already run this calculation and decided that looking costs more than
paying.** That is a considered decision, not an oversight to sell against.

**Two further objections worth remembering as general lessons:**

- **There may be no finding at all.** A quotation is an offer; the PO is a counter-offer;
  the supplier performed and invoiced at the PO price, accepting by performance. There is
  a contract at the PO price. *"We agreed a different number and they performed. What is
  the finding?"*
- **The procurement veto.** A wrong PO price is a defect in a process procurement owns,
  the fix is preventive and cheap (SAP BAdI per KB 3733443, an Oracle profile option, a
  Coupa integration), and you would need procurement's sponsorship to email its own
  suppliers for evidence of its own errors.

### N=1, not N=2 — the overfit charge was correct

Tested condition by condition, Pearl and the radiologist share only two conditions, and
both are the generic conditions of being the small party. They diverge on the two that
matter: whether a supplier-authored price document exists, and **which side is blind.** In
Pearl the buyer is blind and would pay to see. In teleradiology the buyer has perfect
sight and the supplier is blind, and the supplier has no budget. **Opposite commercial
implications.**

Worse, the radiologist's mechanism is the famous one: Evaluated Receipt Settlement /
self-billing, with published standards (VDA 4938 in automotive, supplier guides from
Bosch and ZF, SAP Fieldglass auto-generating invoices from approved timesheets,
recipient-created tax invoice regimes in several VAT jurisdictions). Presenting it as a
discovery is the easiest thing in the world to puncture.

**Stop citing staffing timesheets, marketplace payouts and self-billing as supporting
evidence.** They evidence the other mechanism and it is already productised.

### The supplier-side inbox agent — DEAD (from the earlier pass)

Conexiom has done emailed-PDF-POs into ERP since 2012 with 100,000+ formats and a
certified SAP S/4HANA app. Duvo raised $32M (Balderton, Oct 2026) for agents across ERPs,
portals, spreadsheets and inboxes; Stuut raised $52.5M (Insight, Oct 2026) for agentic
order-to-cash. HighRadius and Esker have sold deduction management for 15+ years.
Microsoft ships an inbox-watching Payables Agent inside Dynamics 365 Business Central.
Extraction is ~$0.30 a run and Docsumo's free tier exceeds Pearl's entire PO volume. The
exact MVP is already a published blog post (Gmail to Tally POs, claimed 98% accuracy).

### Also killed by this round

- **Buyer-side supplier inquiry desk** ("where is my payment"): shipped. Medius Supplier
  Conversations, Auditoria.AI, Payhawk Agent Fetch (publishes 68.6% autonomous
  resolution), GEP, Automation Anywhere.
- **Supplier portal submission:** disconfirmed by interview 04 itself (portals are "quite
  simple," always a named contact), and Tesorio already ships a Coupa and Ariba submission
  agent, with Visa, BILL and Billtrust piloting agents acting inside portals since Oct 2026.
- **ISO 42001 as the assurance answer:** not a competitor, a tailwind. It certifies the
  management system and **disclaims output assurance in writing.** Fewer than 100 orgs
  certified as of Jan 2026.
- **The regulatory-delta employee** (EDF, pollution forms): mandate monitoring is covered
  by Sovos, Avalara and Pagero, and the sharp version ("our agents retrain faster than a
  BPO") is a claim about Zamp's internals.
- **Selling anything to the small business itself:** Zamp's published buyer's guide says
  they are not for small businesses, and both willing subjects sit below the floor of
  every enterprise tool. The gap there is distribution and price, not capability.

---

## Kept as pitch sentences, not products

- **Three-way match never sees the quotation.** Four-way match adds a quality inspection
  report instead (in Oracle EBS, literally two flags on `PO_LINE_LOCATIONS_ALL`). Price
  variance accounting baselines on the PO price or standard cost, never the quote.
  Recovery audit's source documents are invoices, POs, contracts, receipts and time logs.
  **So the pre-PO price decision is the only step in procure-to-pay with no automated
  control at all.** True, citable, and verified across SAP, Oracle, Coupa and Ariba.
- **PPV cannot exist for scope-discovered spend.** A free-text PO or service line has no
  material master, no price control indicator and no standard price; service entry sheets
  post differences to the cost centre, not to a price-difference account. Under Oracle
  average costing there is no PPV at all.
- **Mandating a document does not create reconciliation.** Canada legally provides a
  dispute route for farmers who disagree with an elevator's weight and grade. It is used
  **150 to 250 times a year, nationally.** This is the single best illustration in all the
  research that a channel is not the same as a practice. The same point: EDI 865 already
  lets a supplier formally reject a buyer's PO price, and Pearl simply chooses not to,
  because contesting costs more than the difference.
- **A regulatory change lands as unallocated manual work on whoever cannot refuse it.**
  Interview 03's EDF: six weeks old, the accountant half-handled it, the bank was
  unhelpful, three weeks of cash blocked, and it landed on a doctor. **Now confirmed:**
  from 1 Oct 2026 the EDF covers goods, software *and* other services, and SOFTEX is
  discontinued. Services previously required no declaration at all. Transition treatment
  for September invoices is contested and RBI has not published a rule, so his confusion
  was the market's, not his.
- **Cost is a weak argument against a BPO.** Zamp's best published cost number is only
  30% below BPO. Retraining latency is the strong one, and it is the argument Second
  Opinion makes measurable.

---

## Factual corrections to carry into the pitch

- **Customer metrics.** Instacart: AP approval 2 weeks to 2 days, 80% of manual work
  automated. Mindbody: 95%+ of invoices processed end-to-end. Block: 75% of close
  touchpoints eliminated. Uber Freight: invoice audit 1 day to 1 hour, 30% below BPO.
  Amgen: 85% of purchase requisitions automated, turnaround cut 60%. Wio: chargebacks
  under 10 minutes per case, zero missed network deadlines. **Attribute each to the right
  customer.**
- **Not DoorDash, Uber or Stripe.** Those were in the original brief and are not on the
  site.
- **Two companies are called Zamp.** `zamp.ai` is FKA Varni Labs, Bengaluru, $22M seed
  2022 (Sequoia, Dara Khosrowshahi, Tony Xu). Zamp Inc is a US sales-tax company that
  raised ~$30M from Acrew in April 2026. Never cite the Acrew round.
- **Recovery audit contingency is ~10%, not 20 to 30%.** Three convergent anchors:
  Medicare RACs 9 to 12.5% (average 10.86%), PRGX's implied blended 9.4%, and disclosed
  rate pressure.
- Every market figure in this research is vendor, consultancy or advocacy sourced except
  the Saudi change-order study and CAPS Research. **Attribute, never assert.**

---

## Open items

1. Settle the demo scope and build. Prior estimate for a comparable build was ~30 hours.
2. Decide whether the honest research narrative goes in the pitch: four subjects, two
   misses, one finding, and the hypothesis killed twice by its own evidence. It is the
   strongest available demonstration of judgment, which is half the screen.
3. Write the one-year answer. Current best shape: not more digital employees per customer,
   but a measured error rate per class of judgment that makes outcome-based pricing
   contestable in procurement, and that tells a customer in week two rather than month six
   which judgments are safe to automate next.
