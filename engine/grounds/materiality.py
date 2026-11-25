"""The materiality floor.

Named for interview 02. A quicklime processor was asked about weighbridge
variance on inbound material. Differences large enough to reach him happened two
or three times a year at 400 to 500 kg, which at Rs 8,250 a tonne is about
Rs 10,000 a year against roughly Rs 20 crore of revenue. He said it did not
matter. He was right, and the only way to establish that was to extract a
frequency and a unit price and multiply them.

An engine that surfaces a finding like that has not found a problem, it has
wasted the one piece of attention it was given. So every finding is divided by
revenue and thrown out below this floor, however interesting it looks.
"""

from __future__ import annotations

# Interview 02 scored 0.005% of revenue. Interview 04's PO mismatches, the one
# case a subject independently named as a top-three time sink, scored well above
# 0.1%. The floor sits between them, an order of magnitude clear of the case we
# know to be noise.
QUICKLIME_FLOOR = 0.001  # 0.1% of annual revenue

# Below this, a finding is reported but never leads a brief.
LEAD_FLOOR = 0.005  # 0.5% of annual revenue


def share_of_revenue(magnitude: float, revenue: float) -> float:
    if revenue <= 0:
        raise ValueError("revenue must be positive to compute materiality")
    return magnitude / revenue


def is_material(magnitude: float, revenue: float) -> bool:
    return share_of_revenue(magnitude, revenue) >= QUICKLIME_FLOOR


def can_lead(magnitude: float, revenue: float) -> bool:
    return share_of_revenue(magnitude, revenue) >= LEAD_FLOOR
