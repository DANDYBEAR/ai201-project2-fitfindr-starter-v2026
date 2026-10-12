"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A normal run whose state IDs can be compared. Criterion 3.
        "name": "selected listing passes through state",
        "query": "black leather jacket under $60",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # The same query is repeated five times so criterion 4 sees the same
        # selected item and can score each fit card against the same facts.
        "name": "fit card preserves selected item facts",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # A matching query with no saved wardrobe pieces. Criterion 5.
        "name": "empty wardrobe completes",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
        if scenario.get("criterion") not in range(1, 6):
            problems.append(
                f"scenario {i} has criterion {scenario.get('criterion')!r} — "
                "it should be an integer from 1 through 5"
            )

    criterion_numbers = [scenario.get("criterion") for scenario in SCENARIOS]
    for criterion in range(1, 6):
        count = criterion_numbers.count(criterion)
        if count != 1:
            problems.append(
                f"criterion {criterion} has {count} scenarios — it should have exactly 1"
            )
    return problems
