# Interview 03: Dr Vishwanatha Acharya, teleradiology for the UK

Date: 2026-11-15. Recorded. **The best interview of the four. This is the subject.**

## Who

- Medical services company. **Teleradiology**: reads scans for UK hospitals.
- Work arrives **through an agency intermediary**, which holds the contracts with the
  hospitals.
- **Three people: him, his wife, an accountant.**
- He is GMC-registered, annual appraisal feeding a 5-year revalidation cycle.
- Declined to give daily study volume ("it varies") and all money figures. He knew the
  call was recorded. Everything below is structure and time, not rupees.

## The system he works in, which is the whole point

> "Their system. It's entirely locked in. They only provide all the hardware and the VPN
> and everything, because it has to be patient data, privacy and all that, **so none of
> our systems can be used.**"

He works entirely inside the client's infrastructure. He generates the output and has no
copy of the record of it.

## Finding 1: he is invoiced by his own customer, and cannot verify it

This is the cleanest instance of the pattern across all four interviews, and unlike the
others **he named it himself.**

> "When you invoice, who counts how many studies you read? You or them?"
> **"Them."**

> **"The invoices are suggested by the company. If we agree, we kind of copy that invoice."**

On checking:

> "We do **random audits**. There is a **trust factor** between us. Initially we audited
> probably a few months." (Then stopped.)

> "Has your number ever not matched theirs?" → "Very rarely... it depends on the
> perceptions of what particular studies [are]. There can be disagreements with the
> principles, **rather than undercounting.**"

And then, unprompted, at the very end of the call:

> **"Ideally, there should be a reasonable way of checking what you have done. But
> unfortunately, the company doesn't allow that. They have kind of limited what we can
> look into our own work, what we have done in last month."** Reason given: privacy, their
> software.

**Why this is stronger than the travel and quicklime findings:**

| | Travel | Quicklime | **Teleradiology** |
|---|---|---|---|
| Who computes the number | Resort | **He does** | **The customer** |
| Who issues the invoice | He does | He does | **The customer drafts it, he copies it** |
| Can he verify? | Could, never tries | Yes, and it's immaterial | **No. Access is denied by design** |
| Does he want to? | No | No | **Yes, said so unprompted** |
| Frequency | Annual | Monthly, trivial | **Monthly, every remittance** |

He is not in denial and he is not wrong about the magnitude. He is **structurally locked
out**, on privacy grounds that are entirely legitimate, which makes the gap durable rather
than a vendor behaving badly.

**The colleague workaround, which is the detail to put in the pitch:**

> The company "says you can document your work and count, and tally it against what we do
> ... but it's up to you. Some people do it. I know some of our friends **religiously do
> it. They physically write down or put it on a Word** and then count at the end of the
> month."

Manual reconciliation of an unverifiable counterparty statement, performed in a Word
document by a consultant radiologist. That is the enterprise problem at n=1.

**There are at least three billing line types, all counted by them:**

1. **Studies**, at rates varying by modality and urgency. "Who keeps track of which was
   which?" → "Them. Them."
2. **Addenda.** On his own cases: unpaid, treated as duty. On *someone else's* case (the
   original radiologist has gone home and an emergency patient needs it): **paid.**
3. **Peer review.** 5 to 10% of his work is randomly distributed to peers, and he receives
   others' work to grade on a miss severity scale. **Paid, at a lower rate.**

Three different rate structures, assigned randomly by the client, counted by the client,
invoiced by the client, unverifiable by him.

## Finding 2: the EDF bugbear. His own answer to "what would you take off your plate"

This is the most emphatic thing anyone said across four interviews.

> "Recently, **from 1st of October, there is a huge layer added by RBI.** There is an
> **export declaration form, EDF**, that needs to be filled, which is a very complex
> thing... **the bank refused to release the money** and the bank was not very helpful...
> that lady was either ignorant or not helpful, despite being a private bank. So I had to
> struggle and **money got released after 3 weeks.**"

> **"Every month, for every remittance, we have to fill EDF now."**

> "What is one thing you would want off your plate?" → **"Yes, absolutely. That EDF is a
> bugbear. I wish my accountant can handle that. They are also kind of half handling it.
> Finally it comes to me... Finally I had to deal with the banks."**

Characteristics, and they are close to a specification:

- **Brand new.** Six weeks old at the time of the interview.
- **Recurring monthly**, per remittance. High frequency.
- **Rule-governed** and form-generating. The repeated fields are stable: "once we fill a
  few times, a few of the informations are similar."
- **High cost of failure:** three weeks of blocked cash on the first attempt.
- **Cannot be delegated down.** The accountant half-handles it, the bank is unhelpful, so
  it lands on **a doctor**, who is the single most expensive hour in the firm and the only
  person who can do the revenue-generating work.

> **VERIFY BEFORE BUILDING:** he attributes this to an RBI change effective 1 October.
> EDF historically applies to goods exports, with SOFTEX for software and services. An
> October 2026 extension to services remittances is plausible but unconfirmed. Check the
> RBI circular and the FEMA export-of-services position before any MVP depends on the
> specifics.

## Finding 3: he designed the product, unprompted

Asked what he had not been asked, he answered with a product spec:

> "If there is an accounting process or a software or a platform **where I can also work
> on and the accountant can also work on**, and there can be fluidity... At the moment, a
> lot of this is through **phone calls, through emails, through WhatsApp messages.**
> Whereas if there is a common platform where both of us can [work]... the accounting
> provider and the customer, such as us... The accountant can add the data and **it
> automatically picks up and collates**, and sends me a query: what about this, can you
> send this, fill this. Or when I say I need EDF, **it should prepare a pro forma for EDF
> and fill it automatically and tell me just fill that particular thing**, and then I will
> email it to the bank."

> **"I want a platform which can take away a lot of these works, where my phone calls to
> accountants or email and WhatsApp conversations can be minimised. And also my contact
> with the bank can be minimised."**

And his own summary of where the pain sits, confirming it back:

> "Not with the middleman, not with the agent, neither with your actual work, but rather
> post that: processing the invoices, with the logistics and legalities of the country."
> → **"Correct, correct, correct. The accounting side of things, and the inward remittance
> side of things. There are a lot of little bugbears."**

On the client relationship, for contrast: "with the company as such, it's been fine tuned
to such an extent that everyone's life is comfortable."

**So the pain is precisely located.** Not the clinical work. Not the agency. Not the
client relationship. It is the post-delivery layer: getting invoiced correctly, getting
paid across a border, and the accountant handoff that currently runs on WhatsApp.

## Other detail worth keeping

- **Turnaround time:** the agency holds TAT commitments with the hospitals; he gets
  notified per scan and works to avoid breaching. A breach means "a palaver of explaining
  why there was a breach." He is **sometimes assigned already-breached cases** because
  they have bounced through other radiologists who could not report them.
- **Timesheets are optional.** He used to keep one, stopped, because "this system is
  relatively foolproof and digital and we have got a trust with our particular contractor."
- **Interruptions are clinical, not admin.** Direct phone line from the UK for scan
  justification (legally a radiologist must justify a CT or MRI). He was careful to say
  this is clinical discussion, not overhead.
- **If the accountant is away, nothing breaks.** "We have kept it pretty simple... we have
  modified the business in a very simple way." The simplicity is deliberate, and it is a
  coping strategy, not an absence of pain.
- He asked why Hari was asking, and Hari disclosed the job application honestly. Fine, and
  he engaged more usefully afterwards.

## Why this subject matters for the submission

### It is the only one where the owner wanted the thing

Travel denied the problem. Quicklime correctly judged it immaterial. **This subject named
the problem, named the reason he cannot solve it, and described the product.** That is the
difference between a hypothesis and a finding.

### The structure generalizes upward, which is what makes it Zamp-relevant

A three-person firm is obviously not a Fortune 500 buyer. The finding is not "sell to
teleradiologists." The finding is the **shape**:

**A supplier whose output is counted and invoiced by its own customer, with no
independent record to check it against.**

That is self-billing, and in enterprise it is everywhere: evaluated receipts settlement
in automotive, consignment stock, royalty statements, marketplace and aggregator payouts,
freight self-billing. At enterprise scale it is a team. Here it is a radiologist typing
into a Word document at month end. **The three-person firm shows the mechanism in its
purest form because there is no team to absorb it.**

### And it puts us on the opposite side of Zamp's product

Zamp automates the **buyer's** accounts payable. This man is a **supplier being
self-billed by a buyer.** The buyer has software. The supplier has a Word document and a
trust factor.

That is the earlier "two sides of the transaction" idea, except now it is evidence from a
real interview instead of a whiteboard argument. The asymmetry is not hypothetical: he is
locked out of his own production data, for good reasons, and nobody has built the
supplier's side.

### The EDF finding generalizes too

A regulatory requirement appeared six weeks ago, and the entire burden fell on the least
appropriate person in the organization, because neither the accountant nor the bank
absorbed it. That is what every regulatory change does at every scale: it lands as
unallocated manual work on whoever cannot refuse it.

## Follow-ups to get

1. Can he show the EDF, blank or redacted? Which fields repeat month to month and which
   change?
2. What did the company's invoice look like versus what he expected, the last time they
   disagreed on "perceptions of what particular studies" were?
3. During the few months he did audit: what did he compare against, and did he ever find
   a discrepancy?
4. The colleagues who "religiously" keep a Word tally. What do they do when it does not
   match?
5. Which bank, and what exactly did it refuse? Three weeks of blocked cash is the
   quantified cost here, and it is in weeks rather than rupees, so he may well answer.
