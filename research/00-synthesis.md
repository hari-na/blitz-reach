# Zamp AI PM application: where everything stands

Updated 2026-11-16. Nothing built, nothing sent.

---

## 1. The application, settled

| | |
|---|---|
| **Send to** | `Palak@zamp.ai` |
| **Subject** | `Product Manager - Hari Narayanan` |
| **Deliverable** | A working MVP plus a ~2 minute **video** pitch |
| **Addressed to** | Amit Jain, Co-Founder and CEO (ex-MD Sequoia, ex-Head of APAC Uber) |
| **Funnel** | All entries → top 50 → live pitch to Amit → **2 hired** |
| **Timeline** | Rolling review, reply within 7 days. No deadline. Both pages live as of 16 Nov |
| **Screen** | Two things only: **Vision** ("where should Zamp's product be in a year?") and **Judgment** ("critical thinking over project execution") |

**The address was not ambiguous.** The assignment site Cloudflare-obfuscates the email;
XOR-decoded it is `Palak@zamp.ai`. The visible text on the Kula posting agrees. Only the
`mailto:` href says `aman.raj`, and it is a stale rich-text artifact where the anchor text
was overwritten and the link target was not. No clarifying email needed.

**The two asks were never in conflict.** "Build an MVP" and "pitch a product you have
built" are the same request. The site also says: "It can be anything - a feature layer on
top of Zamp, **or something you've already shipped on your own.**" So a Zamp feature layer
is one option they offer, not a requirement.

---

## 2. What Zamp actually is

AI workers that own finance back-office jobs end to end and are measured on outcomes, not
copilots. Six published workflows: AP approval, purchase requisition approval, accounting
close, invoice audit, end-to-end invoice processing, chargeback filing.

Real customers and metrics (**not** DoorDash/Uber/Stripe): Instacart (AP approval 2 weeks
→ 2 days, 80% of manual work automated), Amgen, Block (75% of close touchpoints removed),
Uber Freight (invoice audit 1 day → 1 hour, 30% below BPO), Wio (chargebacks), Mindbody
(95%+ invoices end to end).

They sell against outsourcing firms, not against ERPs. All six workflows are the same
machine: **a document arrives from outside, gets checked against internal records and
rules, then something is approved, routed or filed.**

**Their own stated problem**, from their homepage: automating one process takes four to six
months, and the reason given is assembling scattered process knowledge.

**Manifesto vocabulary worth using:** shared brain, infinite replicability, pure alignment,
institutional immortality.

**Traps.** Two companies are called Zamp. `zamp.ai` is FKA **Varni Labs**, Amit Jain,
Bengaluru, $22M seed 2022 (Sequoia, Dara Khosrowshahi, Tony Xu). Zamp Inc is a US
sales-tax company that raised ~$30M from Acrew in April 2026. Search blends them. Also:
no free trial, no pricing page, no docs. `app.zamp.ai` is a provisioned-access login only.
Nobody applying can try the product, so the playing field is level and a pitch claiming
inside knowledge would read as bluffing.

**From Hemant (ex-Zamp), which is unguessable from outside:** the enterprise motion runs on
**FDEs who research a company's problems from the outside**, because the customer almost
never states the problem and the description is useless when they do. The FDE then walks in
with a plan. There is also a self-serve ambition for smaller businesses, **but Zamp's own
published buyer's guide says they are not for small businesses**, so that stays a vision
argument, never a factual claim in the pitch.

---

## 3. Ideas killed, and why

| Idea | Killed because |
|---|---|
| Reuse `kaasu` / `growth` finance work | Hari: hobby projects, not good enough |
| Exception queue that explains itself and learns | Already table stakes for a company serving Instacart and Block |
| Adversarial / AI-generated invoice fraud | Demo requires **their** agent. Unverifiable claim about their internals. If Amit says "we handle that," it collapses in the room |
| Agent management layer ("you hired 40 employees, no org chart") | Softest insight. Reads as a dashboard |
| "This process is redundant, delete it" | Zamp prices per process, so it reduces their revenue. Awkward to pitch |

**Still live:** the FDE diagnostic (turn the FDE's outside-in judgment into product), and
the supplier side of the transaction (see below). The interviews strengthened both.

---

## 4. The four interviews

Method: never ask whether something is a problem, ask **how would you know**; push every
policy answer to a specific recent event; extract frequency and unit price and do the
arithmetic yourself.

### 01 + 01b. Travel DMC / IATA agent (two calls)

**Hypothesis died.** He is a destination management company dealing directly with resorts.
No intermediary, so no deduction mechanism. Refunds arrive in 2 to 3 hours.

One real exposure: Maldives commission is settled **once a year, in February, in cash, in
USD, as a single total with no line items**, across **500+ bookings and 300+ resorts**, at
rates of 5 to 10% that change monthly, against bookings that mutate after sale.
**Never reconciled, never queried, in nine years.** "Do you compare it against your
bookings?" → "No, we don't." → "You just trust them fully?" → "Yes, yes, yes."

But he would never buy a fix. He also gave a **reasoned objection to the whole thesis**:
clients defect to him *from* MakeMyTrip and ClearTrip over cancellation handling, so in his
segment automation is a churn source. And his trust ceiling is absolute: asked what would
let him stop checking things himself, "**I have to quit the company.**"

**The useful part:** he said "everything is perfect, there is no loss for us" about sixty
seconds after describing a Rs 64,000 loss from the previous week. Twice across two calls he
reported perfection while describing losses.

### 02 + 02b. Quicklime processing, two plants (two calls)

**Hypothesis died, and he was right.** He is a **price-setter** with a quality premium, so
nobody computes his number.

Weighbridge variance exists but is immaterial: differences large enough to reach him
(400 to 500 kg) happen **two or three times a year**. At Rs 8,250/ton that is **~Rs 10,000
a year against roughly Rs 20 crore of revenue, about 0.005%.** Even the steelman (an
undetected bias in the sub-150kg noise, which nobody has measured) tops out near 0.15%.

Also dead: the order-status chain (he can be unreachable for a week and "it will go on like
regular only"), and the new mine's compliance burden (he is a passive investor; the
operating partner handles royalty and transit passes).

Payment-to-invoice matching is **already solved** by a tool called Reportec that converts
bank statements to Tally XML. Do not build there.

### 03. Teleradiology for the UK. **This is the finding.**

Three people: him, his wife, an accountant. Reads UK scans through an agency intermediary.

**He works entirely inside the client's hardware and VPN.** None of his own systems can be
used, on patient-privacy grounds.

**He is invoiced by his own customer and cannot verify it:**

- Who counts the studies? → **"Them."**
- **"The invoices are suggested by the company. If we agree, we kind of copy that invoice."**
- Audited for a few months at the start, then stopped. "There is a trust factor."
- Unprompted, at the end: **"Ideally, there should be a reasonable way of checking what you
  have done. But unfortunately, the company doesn't allow that. They have kind of limited
  what we can look into our own work."**

Three billing line types, all counted by them: studies (varying by modality and urgency),
addenda (unpaid on his own cases, paid when covering someone else's), peer review (5 to 10%
of work, randomly assigned, paid at a lower rate).

**The detail for the pitch:** the company says they may keep their own count and tally it.
Some colleagues "**religiously do it. They physically write down or put it on a Word** and
then count at the end of the month."

**And a second, separate pain, which was the most emphatic answer in four interviews.**
Since 1 October, he says RBI requires an **Export Declaration Form on every inward
remittance**. First filing: the bank refused to release the money and **cash was stuck
three weeks.** Now monthly. The accountant half-handles it, "finally it comes to me," and
he deals with the bank personally. Asked what he most wants off his plate: **"Absolutely.
That EDF is a bugbear."**

Properties: six weeks old, monthly, rule-governed, form-generating, stable repeated fields,
three weeks of blocked cash when it fails, undelegable so it lands on the most expensive
and least substitutable hour in the firm.

> **Verify before building:** EDF has historically applied to goods exports, with SOFTEX for
> services. An October 2026 extension to services remittances is plausible but unconfirmed.

**He then spec'd the product himself**, unprompted: a shared platform where he and the
accountant both work, replacing phone calls, email and WhatsApp, that collates what the
accountant enters, queries him for what is missing, and **pre-fills the EDF pro forma so he
completes only the changing field.** "I want a platform which can take away a lot of these
works, where my phone calls to accountants or email and WhatsApp conversations can be
minimised. And also my contact with the bank can be minimised."

---

## 5. What survived

**Three things, in order of strength.**

### A. The supplier side of the transaction is unbuilt

A supplier whose output is **counted and invoiced by its own customer**, with no independent
record to check against. That is self-billing, and in enterprise it is everywhere:
evaluated receipts settlement in automotive, consignment stock, royalty statements,
marketplace and aggregator payouts, freight self-billing. At enterprise scale a team absorbs
it. In a three-person firm it is a doctor with a Word document, which is why the mechanism
is visible at all.

**Zamp automates the buyer's accounts payable. This man is a supplier being self-billed by a
buyer.** The buyer has software; the supplier has a trust factor. This is the "two sides of
the transaction" argument from the whiteboard, now backed by a real interview.

### B. The owner knows every event and cannot see the aggregate

In all four interviews the owner had an accurate account of each individual incident and no
view at all of the sum. Travel: 500 unreconciled bookings a year, "everything is perfect."
Quicklime: a monthly variance he dismissed, correctly, but only confirmable by arithmetic he
had never done. **That is a measurement gap, not a processing gap**, and it is exactly what
an outside diagnostic closes.

### C. The empirical case for why FDEs exist

**The reason Zamp needs FDEs is the same reason three of these four interviews failed.** One
subject denied having a problem while describing a loss from the previous week. One correctly
judged his immaterial, and the only way to learn that was to extract a frequency and a unit
price and multiply them. In no case did the owner's self-report answer the question.

That is the empirical argument for why a diagnostic must be built from observable signals
rather than from asking, and it is now on tape across three unrelated industries.

---

## 6. Status

- Interview guide, 20-minute script, sector probes, and four interview logs written.
- **Nothing built. Nothing sent.**
- Hit rate: one usable finding from four subjects. That ratio is itself a result worth
  reporting, because a submission claiming every interview confirmed the thesis is less
  credible than one that reports the misses and explains the difference.

**Open decisions:** which of A, B or C the MVP demonstrates, and whether the subject is the
supplier side (grounded in interview 03) or the FDE diagnostic (grounded in Hemant plus the
method finding). The one number to own has also not been chosen.
