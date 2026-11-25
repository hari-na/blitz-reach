# Interview 01: travel, DMC / IATA agent, Erode / Tamil Nadu

Date: 2026-11-15. Duration: ~20 min. Recorded, transcript available.
Second conversation: agreed, yes.

## Who

- Travel business, 9 years old. Domestic and international tourism.
- **DMC (destination management company)**, not a B2B reseller. Deals directly with
  resorts, no intermediary. This turns out to matter enormously, see below.
- IATA agent. Does both B2B and B2C.
- Sells flights, visas, cruises, holiday packages.
- Customers: honeymooners and corporates. Demand comes from BNI (Business Network
  International, he is currently chapter president) plus a 300,000+ Instagram and
  Facebook following.
- **150+ bookings per month.**
- Runs a CRM called Kaya. Separate sales team and accounts team.
- Last booking: ~Rs 5 lakh, customer in Canada, paid immediately.

## Headline: the hypothesis did not survive

Every probe built around unilateral counterparty deductions came back empty:

| Probe | Answer |
|---|---|
| Outstanding commission | "There is no outstanding commission" |
| ADMs | Does not get them (but see technique note) |
| Chargebacks | Never had one |
| GST notice / penalty / lost credit | Never. "It's been 9 years, everything is systemized" |
| Supplier billing errors | Checks them, no systemic issue |
| Money owed to suppliers today | None |
| Pays suppliers before customers pay | No, never |
| Tried to hire the work away | No |
| Trust ever proved wrong | "Nothing like that" |
| Ever bought software to fix any of this | "No, no, no" |

**Why it came back empty, and this is the actual finding:** he is a DMC with direct
resort relationships. He said it himself, "there is no middleman between us." Resort
cancellation refunds reach him in 2 to 3 hours. He eliminated the intermediary that
generates the deduction-and-dispute pattern we went looking for. The structure that
creates the pain in limestone is absent here by design.

## What is genuinely in the transcript

### 1. The Maldives commission settlement (the one real lead)

Volunteered in the last two minutes, when asked for a settlement file, and it directly
contradicts his earlier "no outstanding commission":

- **500+ bookings per year** with Maldives resorts.
- Those resorts **settle commission once a year**, at their own financial year end.
- "So we can't calculate that in the gateway terms." He has no way to tie the annual
  settlement back to individual bookings.

So the counterparty calculates the number, on their own calendar, a year late, against
500 transactions, and he has stopped trying to verify it. That is precisely the pattern
we were hunting. He does not experience it as a problem because he has never attempted
the reconciliation.

**This is the thread to pull in the follow-up call.** The question is simply: when the
Maldives settlement arrives, has anyone ever checked it against the 500 bookings, and
what would it take to find out it was short?

### 2. A real operator objection to automation (the most important thing he said)

Unprompted, he argued that automating cancellations is actively harmful, citing a
competitor by name:

> "Cancellation we can't automate. We have to follow everything. That's why if you were
> checking MakeMyTrip, you can get lots of negative feedback... because the cancellation
> part is automated there. The client will be waiting 7 to 8 months for cancellations."

His stated differentiation **is** the human handling. He believes automation in his
industry produces bad outcomes and bad reviews, and he has a named example.

Any pitch has to survive this objection, and it is better to have heard it now from a
real operator than from Amit in the room.

### 3. The trust ceiling

Asked what would have to be true for him to stop checking things himself:

> "I have to quit the company."

Not a joke, and not about capability. The owner's oversight threshold is effectively
infinite. For a business this size the barrier to autonomy is not whether the software
works.

### 4. The only hard money number in the call

One week ago: the sales team booked a single 17-seater coach instead of a double coach
for a Singapore to Malaysia leg. **Rs 64,000 cancellation cost.** Absorbed, because the
client happened to be his friend.

A human mis-specifying a booking. Recent, quantified, and caused by manual work. Worth
noting that this is a *sales* data-entry error, not a finance-ops error.

### 5. His own stated bottleneck is demand, not back office

Asked what he would hand over, he picked priority over money ("money I can earn anyway")
and then named what he actually needs: **a social media team.** He kept steering the
conversation back to brand, community and "the route" a company takes.

He is not shopping for finance automation. He thinks his constraint is distribution.

### 6. Real pain, but not finance pain

Last out-of-hours work: 2 AM on Thursday, the week before. A client in transit in
Singapore or Malaysia, a Tamil speaker with limited English, needed guidance through a
transit problem. He personally handled it.

Escalations that need language capability and real-time judgment reach the owner at 2 AM.
That is genuine, recent, specific pain. It is customer operations, not finance, and Zamp
does list customer operations as a function.

## Technique notes for the next call

- **ADM was mis-defined on the call** as "automated deduction management." It is an
  Agency Debit Memo. For an IATA agent issuing tickets, ADMs are close to universal, so
  the "no" is not reliable. Re-ask by description rather than by acronym: has an airline
  ever billed you back after a ticket was issued, for a fare rule or a booking class or
  a name change?
- **Several answers were policy, not events,** and were not pushed. "We have a
  cancellation policy." "Everything is systemized." The probes existed but were not
  deployed. Note that the two questions that *were* pushed to a specific instance
  produced the only hard facts in the call: the 2 AM escalation and the Rs 64,000 coach.
- **The subject's self-report was wrong**, and it is on tape. He said there was no
  outstanding commission, then described an unverifiable 500-booking annual settlement.
  That is Hemant's thesis demonstrated on the first attempt: people cannot tell you
  their problem, and when they do the description is useless. Keep this for the writeup.
- Ask "how do you know" rather than "do you have a problem with." He answers the second
  one with his self-image as a well-run operator, which is probably accurate and tells
  you nothing.

## Verdict

Not the wedge. Keep for three reasons: the Maldives settlement lead, the MakeMyTrip
objection that any pitch must survive, and as a documented negative result with a
structural explanation (DMC, no intermediary) rather than a shrug.

A submission that reports two misses and one hit, and explains the difference, is more
credible than one where every interview conveniently confirmed the thesis.
