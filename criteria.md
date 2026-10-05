# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** I chose 4 of 5 because query parsing and keyword matching can miss an unusual phrasing even when a relevant listing exists, while most ordinary queries should still complete the full workflow.
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** I chose 5 of 5 because this branch checks a deterministic empty list rather than judging model-generated text; any call to the next tool would be a loop-control error.
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. The selected listing is passed through state unchanged

For 5 matching queries, `session['selected_item']['id']` equals
`session['search_results'][0]['id']`, and the recorded `new_item` argument sent
to `suggest_outfit` has that same `id` -- 5 of 5 tries.

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->



**Why this target:** I chose 5 of 5 because selecting and passing a dictionary is deterministic state handling, not model output. One mismatched `id` would mean later tools are styling a different item from the one shown to the user.



---

## 4. The fit card preserves the facts while wording can vary

Given the same valid item and outfit input in 5 tries, at least 4 fit cards are
two to four sentences and mention the selected item's title, exact price, and
platform.

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->



**Why this target:** I chose 4 of 5 because model wording is nondeterministic and one response may miss a formatting or detail requirement. The title, price, platform, and length checks still make acceptable output objectively scorable.



---

## 5. An empty wardrobe still produces a complete result

Given a matching query and a wardrobe whose `items` list is empty, the agent
completes both remaining tool calls and returns non-empty strings in
`session['outfit_suggestion']` and `session['fit_card']` in at least 4 of 5 tries.

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->



**Why this target:** I chose 4 of 5 because the empty-wardrobe branch still depends on model-generated advice, which may occasionally fail or return unusable text. It should nevertheless degrade gracefully and finish the workflow in most runs.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
