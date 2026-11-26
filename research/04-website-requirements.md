# Website requirements

Captured from Hari, 2026-11-26.

## The screen must show everything it rejected

The CLI's `--capacity N` returns N companies and refuses to fill the rest. On the
web that is the wrong presentation: a visitor who sees one row cannot tell
whether the engine is sharp or broken.

So the portal shows **all ten**, ranked, with:

- a **dashed cutoff line** at the capacity boundary, labeled as the line we chose
- a **why** column on every row, including every row below the line
- the refusal reasons in full, not abbreviated

The rejections are the evidence of judgment. Hiding them hides the product.
"No hypothesis fired", "every finding came in below the 0.1% materiality floor"
and "no revenue figure was captured" are three different refusals and the page
should say which one applied.
