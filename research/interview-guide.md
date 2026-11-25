# SMB discovery interviews: who to talk to, what to ask, and why

Working document for the Zamp AI PM submission. Written to be used live, on a phone,
in a real conversation.

The whole premise comes from one observation: **people cannot tell you their problem.**
Ask a business owner what their biggest problem is and you get "cash flow" or "finding
good people." Both true, both useless. So almost nothing below asks for an opinion.
Everything asks what actually happened, when, and how long it took.

---

## Part 0: Choosing who to talk to

### What makes a good subject

Rank candidates on these, in order:

1. **They touch money moving between their business and someone else's.** Invoices,
   payments, claims, payouts, reimbursements. This is the shape of work Zamp automates,
   so pain here is directly transferable.
2. **They are the owner, or one step from the owner.** An employee will describe the
   process. An owner will tell you what it costs them, and owners are the ones who buy.
3. **The business is 5 to 200 people.** Below 5 there is no process to automate, just a
   person doing everything. Above 200 they have a finance team and software already.
4. **It has grown recently, or is trying to.** Growth is what turns a tolerable manual
   process into an unbearable one. A flat business has already made peace with its pain.
5. **You can get a second conversation.** The first conversation finds the problem. The
   second one is where you show them something and find out if you were right.

### Business types with the most Zamp-shaped pain

Listed because the shape matters more than the industry. The pattern to look for is
**two parties holding different records, reconciled by a human reading documents.**

| Type | The specific pain to probe |
|---|---|
| Distribution / wholesale | Vendor ledger disputes, GST input credit mismatch, customer credit (udhaar) tracking |
| Restaurant or retail with aggregators | Swiggy / Zomato / Amazon / Flipkart payout reconciliation against actual orders. Commission, penalties and ad deductions buried in a settlement file |
| Logistics / transport | Freight invoice vs proof of delivery matching, detention and demurrage claims |
| Clinics / diagnostics / pharmacy | Insurance and TPA claim submission, rejection, resubmission |
| Manufacturing / job work | Purchase orders, e-way bills, job work challans, material reconciliation |
| Export house | Shipping documents, customs paperwork, GST refund claims |
| Contractors / construction | Running account bills, retention money, subcontractor payments |
| Agency / professional services | Timesheets to invoices, retainer billing, TDS deducted by clients |

Aggregator payout reconciliation is the single best candidate pattern. It is literally
two sides holding different records, settled through a file nobody reads properly, with
real money leaking every month, at a scale where nobody can afford enterprise software.

### What to say when you ask for the conversation

Do not say you are building something. The moment they think you want to sell them
software, you stop hearing about their week and start hearing objections to a product
that does not exist yet.

> I'm doing some research on how businesses your size actually handle their back office
> paperwork. Not selling anything, I just want to understand how it really works. Can I
> get 30 minutes and ask you about your last couple of weeks?

### Document for each person
Name, business, what it does, revenue band or headcount, their role, how you know them,
date, how long you spoke, and whether you can go back to them.

---

## Part 1: The shape of the business

Fast and factual. Five minutes. You are building a map so later answers make sense.

1. What does the business actually do, and who pays you?
2. How many people work here, and how many touch paperwork, billing or accounts?
3. Roughly how many invoices do you send a month? How many do you receive?
4. Who are your customers: a few big ones, or many small ones?
5. How do customers pay you, and how long do they take?
6. What software do you run on? Tally, Zoho, Excel, a notebook, something custom?
7. Who does your GST and income tax filing? In-house or a CA?
8. Has the business grown in the last two years? By how much?

**Why these:** the invoice count and customer concentration tell you whether there is
enough volume for automation to matter. The software answer tells you what an agent
would have to work with. The CA question matters because in Indian SMBs an enormous
amount of finance work is outsourced to a CA and the owner has no visibility into it,
which is both a pain and a competitor.

---

## Part 2: The calendar walk

This is the most important section. It replaces every question of the form "what takes
you the most time," which people cannot answer accurately about themselves.

9. Walk me through last Monday. What did you actually do, hour by hour?
10. Which of those things do you do every week?
11. Now walk me through the last day of last month. What is different about month end?
12. What about the week before a GST filing deadline?
13. When was the last time you worked late or on a weekend? What were you doing?
14. What did you do last week that you had also done the week before, almost identically?

**Why these:** memory of specific recent days is evidence. A prediction about a typical
week is a story. Question 14 is the single highest-yield question in this document:
repetition at a fixed cadence is the definition of automatable work, and asking it this
way surfaces repetition the person has stopped noticing.

Question 13 finds the pain that is bad enough to cost them personal time, which is a
much stronger willingness-to-pay signal than anything they say about priorities.

---

## Part 3: The money path

Follow one rupee from "we did the work" to "the money is in the account and the books
agree." Every handoff in that chain is a candidate.

### Getting paid
15. Take your last invoice. Who created it, from what, and how long did it take?
16. What information did you have to gather before you could raise it?
17. How does it reach the customer? Email, WhatsApp, portal, courier, by hand?
18. How do you know when it has been paid?
19. How do you find out it has *not* been paid? Does something tell you, or do you notice?
20. Who chases late payments, and how? Show me the last time you chased someone.
21. Has a customer ever disputed an invoice? What happened, start to finish?
22. When money lands in the bank, how do you work out which invoices it covers?
23. Does a customer ever pay a different amount than you invoiced? What do you do then?

### Paying out
24. How does a supplier invoice reach you, and where does it sit until it is paid?
25. Who checks it is correct before you pay? What do they check it against?
26. Has a supplier ever billed you for something you did not receive, or at the wrong
    rate? How did you catch it? How long after?
27. How do you decide what to pay this week when cash is tight?
28. How do you know what you owe each supplier right now? Could you tell me today?

### Reconciliation
29. Do your records and your customers' or suppliers' records ever disagree? Tell me
    about the last time.
30. How did you find the difference, and how long did it take to resolve?
31. If you sell through a marketplace or aggregator: when a payout arrives, how do you
    check it is correct? Has it ever been wrong?
32. How much money would you guess leaks out each month that you never find?

**Why these:** questions 19, 23, 26 and 29 all look for the same thing from different
angles, which is the **exception**. The happy path in any business is already smooth,
because if it were not the business would have died. All the cost sits in the cases that
do not match, and those are invisible to the owner because each one feels like a one-off.
Asking four times from four directions is how you find the pattern they cannot see.

Question 28 is a trap in the good sense. If the owner cannot tell you what they owe
without calling someone or opening three files, that is the answer, regardless of what
they say next.

Question 32 is the only estimate question I would keep, because the *reaction* is the
data. An owner who laughs and says "no idea" has an unmeasured leak, which is worse
than a measured one.

---

## Part 4: Paperwork and compliance

33. What filings or returns do you have to do, and on what dates?
34. Walk me through the last GST filing. Who did what?
35. Where does the data come from, and how is it assembled?
36. Have you ever had a mismatch notice, a penalty, or input credit you could not claim?
37. What happened? How long did fixing it take, and what did it cost?
38. How much of your CA's bill is them doing work versus them advising you?
39. If your accountant left tomorrow, what would break?

**Why these:** compliance work is the best automation target in Indian SMB because it is
high frequency, deadline-driven, rule-governed, and expensive to get wrong. Question 36
finds whether they have already been punished, which converts a tolerable annoyance into
a funded problem. Question 39 finds the knowledge that exists only in one person's head,
which is the same single-point-of-failure problem large enterprises have, just visible.

---

## Part 5: People and handoffs

40. Who else touches this work besides you?
41. What happens to it when that person is on leave or sick?
42. Have you tried hiring someone to take this off you? How did it go?
43. If it did not work, why not?
44. What do you still do yourself that you know you should have handed off by now?
45. Why have you not handed it off?
46. How do you train a new person on this? Is any of it written down?

**Why these:** questions 42 to 45 are the commercial core of the whole interview. If
they have never tried to delegate a task, it does not hurt enough to pay for. If they
tried and it failed, the reason it failed is the product specification. And question 45
is where you find out whether the blocker is cost, trust, or the fact that the task
requires judgment that is hard to transfer, which is exactly the gap an agent fills.

Question 46 tells you whether the process is documented, which determines whether an
agent could learn it at all. "It's all in my head" is both the problem and the moat.

---

## Part 6: Failure and rework

47. What is the most expensive mistake this business made in the last year that came
    from paperwork rather than from a business decision?
48. What goes wrong often but cheaply?
49. What do you double-check because you do not trust it?
50. What do you check twice that has not actually been wrong in years?
51. When something goes wrong, how do you find out? Does a customer tell you?

**Why these:** 49 and 50 are a deliberate pair. The gap between what someone verifies
and what actually fails is pure waste, and it is also the exact place where an agent
earns trust fastest, because you can automate a check that has never failed with
essentially no downside. That is the right wedge for a first deployment.

Question 51 matters because finding out from a customer means there is no internal
control, which is both the risk and the opening.

---

## Part 7: Money and willingness to pay

Ask these last. They change the tone of the conversation.

52. If I could take one of the things we discussed off your plate completely, which one
    would you pick?
53. Why that one and not the others?
54. What do you spend today on getting that done? Salary, CA fees, software, your own time?
55. Have you ever paid for software to fix this? What happened to it?
56. If it is still running, what made it stick? If not, why did you stop?
57. What would have to be true for you to trust something to do this without you
    checking it?

**Why these:** 52 and 53 give you the priority ordering from the person who would pay,
not from you. 54 establishes the existing budget line, which is the only honest pricing
anchor. 55 and 56 are the most underrated questions here: a history of abandoned software
tells you the real adoption barrier, and it is almost never features.

57 is the question whose answer defines the product. In finance nobody wants autonomy,
they want to stop checking. Those are different things, and the answer tells you what
level of proof the product has to produce before anyone lets it run unsupervised.

---

## Part 8: Closing

58. What did I not ask about that I should have?
59. Who else should I talk to?
60. Can I come back to you once I have looked at this properly?

**Why these:** 58 regularly produces the best material in the entire conversation,
because by this point they are thinking in the right frame and they know their business
better than your question list does. 60 is what makes the second conversation possible,
and the second conversation is where you find out whether you were right.

---

## The 12 questions if you only get 15 minutes

9, 14, 15, 19, 26, 29, 36, 42, 44, 49, 52, 54.

One of each kind: the real week, the repetition, the artifact, the exception, the
reconciliation break, the punishment, the failed delegation, the thing they cannot let
go of, the distrust, the priority, and the budget.

---

## Questions I deliberately left out, and why

These are the obvious ones. Each is excluded for a reason, and the reasons are the
method.

- **"What is your biggest problem?"** Produces a category, not a problem. People name
  things that sound respectable, and they name the thing they were already thinking
  about that morning.
- **"How much time do you spend on X?"** Every estimate is wrong, usually by 2 to 3x,
  and biased by how much they dislike the task. Reconstruct it from a specific day instead.
- **"Would you use a tool that did X?"** Everyone says yes. It costs nothing to say yes
  to a hypothetical and it predicts nothing about behavior.
- **"How much would you pay for this?"** People cannot price something that does not
  exist. Ask what they spend today on the problem instead.
- **"Do you think AI could help with this?"** Invites them to speculate about technology
  instead of describing their work, and it leaks what you are building, which turns the
  rest of the conversation into politeness.
- **"What features would you want?"** Outsources the product design to someone who has
  never thought about it. Their job is to describe the problem accurately. The design is
  mine.
- Anything about their future plans. Intentions are not evidence.

The single rule underneath all of it: **ask about the past, in specifics, about their
life rather than your idea.** Anything that fails that test got cut.

---

## What to capture during and after

**During, verbatim where possible:**
- Numbers, with their units and the period they cover
- The exact words they use for things. Their vocabulary is the product's vocabulary
- Names of software, portals, forms and documents
- Any moment they get visibly annoyed, and what triggered it

**Ask to see, not to hear about:**
- The last invoice they sent
- The spreadsheet they track payments in
- The WhatsApp thread where they chased a customer
- The settlement or payout file from an aggregator
- The notice, if there was one

An artifact is worth ten minutes of description. The description is a summary written
for your benefit; the artifact is what they actually work with, including everything
they have stopped noticing.

**Immediately after, before you forget:**
1. The three tasks that came up which are repetitive, rule-governed and done at a fixed
   cadence
2. For each: frequency, who does it, how long it takes, and what it costs when it is wrong
3. The one thing they said they would hand over first
4. Whether they have already paid money to try to fix it
5. One sentence in their own words that captures the pain. Verbatim, for the pitch

---

## The analysis frame

Plot every task on two axes: **how often it happens** against **what it costs when it
is wrong.**

- High frequency, low cost of error: automate first. Boring, safe, builds trust, and the
  fastest route to someone letting the thing run unsupervised.
- High frequency, high cost of error: the real prize, and where the money is, but it
  needs the proof layer before anyone will allow it.
- Low frequency, high cost of error: looks dramatic, usually not worth automating. This
  is where founders waste their first six months.
- Low frequency, low cost of error: ignore.

Agents win where frequency is high, the rules are knowable, and the inputs arrive as
documents from outside the business. Score every task that comes up against those three
and the shortlist writes itself.
