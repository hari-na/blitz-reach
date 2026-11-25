# Interview 04: Anish Mark, Pearl Engineering (motor rewinding and overhaul)

Date: 2026-11-16. Recorded. **Independently reproduces the interview 03 finding. N=2.**

## Who

Electric motor rewinding shop, Coimbatore, plus comprehensive service for rotating
electrical machinery: motors, generators, alternators, AC/DC, HT/LT. Industries served:
cement, steel, sugar, textile, paper, wind.

**The client structure is the whole reason this subject matters:**

- ~**50 clients: 40 small, 10 large.**
- He defines large as **companies doing more than Rs 2,000 crore turnover.**
- **80% of revenue comes from those 10 large clients.** 20% from the 40 small ones.

So: a single workshop deriving four fifths of its revenue from ten enterprises, each big
enough to be a plausible Zamp prospect. That is the asymmetry we were looking for, and
unlike the travel and quicklime subjects he is clearly the smaller party.

## The process, and where the scope uncertainty bites

1. Motor arrives, is tagged and given a job card with a number.
2. Disassembly, with an **inspection report generated as it is stripped.**
3. Chief engineer verifies the report.
4. Quotation prepared and sent.
5. Customer confirms by **email, purchase order, or work order.**
6. Work performed, then painted and tested, customer informed.
7. Small clients pay before the motor leaves. Large clients get credit terms.

**Scope is genuinely unknowable at quote time, exactly as hypothesized.** The rewinding
cost can be estimated from nameplate details. Everything else (bearings, core damage)
is only visible after dismantling.

**And it can increase mid-job.** After removing a winding they may find a coil flashover
in the core, a hotspot. Then an additional quote goes back through the purchase
department. Customers handle it one of two ways: a separate quotation and separate PO for
the extra work, or **they cancel the original PO and ask for a fresh combined quotation
and issue a new PO.**

To his credit, he said the large customers are reasonable about this: "they do understand
the rates of this work and they do know that only during certain processes can certain
things be found out."

## Finding 1: he invoices to the buyer's number, not his own, by policy

Asked whether an invoice has ever been held because it did not match the PO:

> **"Yeah, oh dude, that is a thing that we have faced in the past. That actually leads to
> a lot of complications, especially in large MNCs."**

Their defensive rule, adopted because of it:

> "That's the reason we **always generate the invoice after the customer has given us a
> PO**... **Even if the customer has made a small mistake in the PO amount, we raise the
> invoice for that PO amount.**"

The specific failure mode he described: a customer decides to take a discount and issues
a PO at a value below the agreed quotation. If Pearl invoices its own quoted figure, the
invoice will not match, and then "we end up in the purchase department and the accounts
department... we go through various complications... we'll have to send them [a revised
invoice] and go through the whole thing."

**So Pearl absorbs unilateral customer discounts as a matter of process, because
contesting the difference costs more than the difference.** The buyer sets the number and
Pearl invoices to it deliberately.

This is the interview 03 pattern in a different form. In teleradiology the customer
counts the work and drafts the invoice. Here the customer sets the amount via the PO and
the supplier matches it rather than argue.

## Finding 2: how a mismatch actually gets resolved

This is the best single image across all five interviews.

> "We have an account staff, usually her, who does it. Sometimes it requires us to go to
> the actual site of the company, go into the accounts department. Either me, my dad, or
> one of our engineers will go. **We'll take printouts of all the mail that has been back
> and forth**, and all the POs, the work orders and the invoices. **We carry the documents
> in my hand, go there, sit there**, see whoever is responsible for this, talk to them,
> make them understand, and they will take note of it, but **eventually for the change to
> happen, it might take months.**"

Resolution comes as a credit note or debit note against pending payments.

**The owner or his father physically drives to a customer's accounts department carrying
printed email threads to explain a mismatch, and the correction takes months.**

Zamp's headline metric is Instacart's AP approval going from two weeks to two days.
**Anish is the man in the waiting room with the folder of printouts.** Nobody is building
for him.

Payment timing: small clients pay before the motor leaves. The MNCs take **30 to 45 days,
some 60.**

## Finding 3: warranty is NOT the self-billing case. Hypothesis corrected.

I expected warranty claims to be the purest instance. They are not.

How it works: warranty work comes via the OEM (e.g. WEG). The OEM says where the motor is
and what to do. Pearl attends, dismantles, submits a detailed report, and the OEM decides
the remedy, sometimes asking Pearl's recommendation since they are not on site. **"Then
ultimately they will bill the customer and they will tell us how much to charge."** Out of
warranty, Pearl prices freely.

Rates are suppressed: **"Generally it has always been lesser. Whatever we want, we won't
get. Warranty work is always... the OEM wants to cut down their costs."**

**But it is negotiated up front, not deducted afterwards:** "We both come to a mutual
understanding... it's not like we charge them and then they come back and tell us no, you
charged too much. We already agree upon a price, and then we send them the quotation, then
they send us a PO. **The discussions happen telephonically before we even give our final
quote.**"

So warranty is rate pressure, not an unverifiable post-hoc deduction. Honest correction:
my hypothesis was wrong, and the real finding is the PO mismatch instead.

**Portals were also a miss.** Some OEMs have portals, some take email. "Quite simple. You
just go in, you submit the quotation." There is always a named point of contact. Not a
pain point. Question 12 produced nothing.

## Finding 4: he spec'd the same product the radiologist did, unprompted

Asked what he had not been asked, with the purpose of the research disclosed:

> "Small companies like us, we might implement ERP, but even after implementing ERP, there
> are lots of these customers that have **different ERPs.** So their ERP and ours don't
> sort of think together. And when they send us a purchase order, **it just comes as a PDF
> document in our mail.** Even the ERP software doesn't have the ability to recognise that
> what they have sent is the PO, and add it onto our list.
>
> **So sometimes these get missed.** They send us hundreds of mails basically every day.
> One motor receiving the PO might get missed, that's gone somewhere... we think we haven't
> received the PO, but the customer sent it a long time ago.
>
> **Manually every PO or every conversation is being manually recorded and manually noted
> in the Excel sheet** or something like that.
>
> So if there is some sort of software platform that can recognise, from say a PDF
> document, scan the document, **this is the PO, this is the invoice, this is the bank
> statement, and add it into that company's accounts in our ERP platform, it will be
> great. I don't think [ERP] can do that. You still have to manually feed it.**"

### Compare with interview 03, two days earlier, different industry, no prompting

| | Teleradiologist | Anish |
|---|---|---|
| What arrives | Invoice drafted by the customer | PO as a PDF in email |
| Channel | Email and WhatsApp | Email, hundreds a day |
| What happens to it | Copied manually | Manually noted into Excel |
| What they asked for | A shared platform that collates what arrives and pre-fills the form | A platform that recognises a PDF as a PO or invoice and posts it into the ERP |

**Two people, unrelated industries, two days apart, independently described the same
product: inbound business documents arrive as PDFs in email, and a human transcribes them
into the system of record by hand.**

## What else eats his time (he named three, unprompted)

1. **Firefighting.** A completed job develops a problem on site, so he takes engineers and
   technicians out to fix it. He framed the cost himself: **"I'd like to be going and
   bringing a new client"** instead.
2. **"This invoicing issue... wrong invoicing. I have to go there, sit with them if the PO
   is not received correctly."** He independently named the PO mismatch as a personal
   top-three time sink, after we had already finished discussing it.
3. **Undertrained technical staff.** Anything non-standard pulls him onto the floor. His
   example: dynamic balancing a rotor with a mass overhanging the shaft end, where he has
   to calibrate the machine himself.

## Why this closes the research phase

**The pattern is now N=2 across unrelated industries, and in both cases the subject named
it first.** That is the bar we set: travel denied the problem, quicklime correctly judged
his immaterial, and these two both asked for the same thing without being led.

**The structural claim, now evidenced rather than argued:**

Zamp automates the enterprise buyer's inbound document problem. All six of their published
workflows are the same machine: a document arrives from outside, is checked against
internal records and rules, then approved, routed or filed. Instacart's AP went from two
weeks to two days.

**Anish is the supplier at the other end of that same pipe, and he has none of it.** He
receives POs as PDFs inside hundreds of daily emails, misses some, transcribes the rest
into Excel by hand, invoices to the buyer's figure rather than his own to avoid AP
friction, and when a mismatch happens he drives to the customer's office with printouts and
waits months.

**And the asymmetry gets worse as Zamp succeeds**, which is what makes it defensible rather
than merely unserved: an automated buyer demands exact matching. Every efficiency gained on
the buyer's side raises the precision required from a supplier who is still working by
hand. Pearl's ten large customers at Rs 2,000+ crore are exactly the companies being
automated.

**The buyer got an AI employee. The supplier got a PDF.**

## Follow-ups worth getting (short)

1. How often does a PO actually get missed? What happened the last time, and how long did
   the motor sit before anyone noticed?
2. How often does a customer's PO come in below your quotation? Does anyone record the
   difference? (Unlike the quicklime variance, **both documents exist**, so this is
   measurable.)
3. The last time you or your dad drove to a customer's accounts department: which customer,
   how long had the payment been sitting, how many visits did it take?
4. Hundreds of emails a day. Who reads them, and how does anyone spot that one is a PO?
5. Which ERP are you on, and what happened when you implemented it?
6. Of the 30 to 45 day payment cycle, how much is waiting on their approval versus the
   agreed terms?
