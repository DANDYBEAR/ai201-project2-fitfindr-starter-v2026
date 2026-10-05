# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr accepts a natural-language request for secondhand clothing, including an optional size and maximum price. It searches a mock thrift-listings dataset, ranks the matches, and selects the strongest result. The agent then suggests outfits using the user's saved wardrobe—or general styling advice when that wardrobe is empty—and creates a short shareable fit-card caption. If no listing matches, it stops before styling and tells the user to broaden the keywords, change the size, or raise the price limit.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings dataset for items matching a description and optional size and maximum-price filters, then ranks matches by relevance.
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
     `description` (`str`), `size` (`Optional[str]`), and `max_price` (`Optional[float]`).
- **Returns:** A relevance-ranked `list[dict]`, limited to `config.SEARCH_RESULT_LIMIT`; every listing dictionary contains `id`, `title`, `description`, `category`, `style_tags` (`list`), `size`, `condition`, `price` (`float`), `colors` (`list`), `brand` (`Optional[str]`), and `platform`.
- **When it has nothing:** Returns an empty list (`[]`).

### `suggest_outfit`

- **What it does:** Suggests one or two outfits for a selected thrift listing, using specific pieces the user owns when possible.
- **Inputs:** `new_item` (`dict`) containing one listing and `wardrobe` (`dict`) with an `items` key whose value is a `list[dict]` of wardrobe pieces.
- **Returns:** A non-empty `str` containing one or two wearable outfit suggestions; when wardrobe items exist, the suggestions name specific pieces from that list.
- **When it has nothing:** If the wardrobe `items` list is missing or empty, returns a non-empty `str` with general styling advice instead of raising an exception or returning an empty string.

### `create_fit_card`

- **What it does:** Turns an outfit suggestion and its selected thrift listing into a short, shareable caption.
- **Inputs:** `outfit` (`str`) and `new_item` (`dict`) containing the selected listing.
- **Returns:** A non-empty `str` of two to four sentences that mentions the item, its price, and its platform once each and describes the outfit's vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, returns a non-empty fallback caption based on `new_item` instead of raising an exception or calling the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a helpful no-results message in the session and stop. Otherwise, store the first result as the selected item and pass it to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Deterministic regular expressions extract `size` and `max_price`; after those filters and common request prefixes are removed, the remaining text becomes `description`.

**What moves through the session:** `query` becomes `parsed`, then `search_results`; the first result becomes `selected_item`, which is read from the session by `suggest_outfit`. Its result becomes `outfit_suggestion`, which is read with `selected_item` by `create_fit_card` to produce `fit_card`. An empty `search_results` list sets `error` and stops before those later fields are populated.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ & '.\.venv\Scripts\python.exe' app.py ask 'looking for a vintage graphic tee under $30' --empty-wardrobe
(running with an empty wardrobe)

  Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop

  Outfit:   Here are two easy, versatile ways to style your vintage-wash graphic tee:

**1. The Off-Duty Grunge (Casual & Edgy)**
* **Bottoms:** Straight-leg medium-wash blue jeans with a relaxed or slightly distressed fit.
* **Footwear:** Classic black canvas sneakers (like Converse or Vans) or beat-up combat boots.
* **Styling Tip:** Do a simple "tuck and pull" (tuck the tee in loosely and pull it out slightly) to balance the boxy fit with the straight-leg denim. Add a silver chain necklace if you have one.

**2. High-Low Contrast (Streetwear Vibe)**
* **Bottoms:** Tailored black trousers or pleated wide-leg pants (belted at the waist).
* **Footwear:** White leather low-top sneakers.
* **Styling Tip:** Fully tuck the tee into the trousers to define your waist and create a sharp contrast between the formal pants and the casual, worn-in top.

  Fit card: Channel some effortless off-duty grunge with this Graphic Tee — 2003 Tour Bootleg Style, now available for just $24.0. The faded black cotton and slightly boxy fit give it that ultimate worn-in streetwear edge. Grab it over on my depop before it’s gone!

2 model calls this session, 482 prompt + 284 output tokens
```

**The three tools, tested one at a time**

```
$ & '.\.venv\Scripts\python.exe' -c "from tools import search_listings; print(search_listings('graphic tee', size='M', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}]
```

```
$ & '.\.venv\Scripts\python.exe' -c "from tools import suggest_outfit; item={'title':'Test Graphic Tee','category':'tops','description':'black cotton graphic tee','colors':['black'],'style_tags':['casual']}; wardrobe={'items':[{'name':'Test Blue Jeans','category':'bottoms','colors':['blue'],'style_tags':['casual']},{'name':'Test White Sneakers','category':'shoes','colors':['white'],'style_tags':['casual']}]}; print(suggest_outfit(item, wardrobe))"
**Outfit 1: Classic Weekend**
* **Top:** Test Graphic Tee
* **Bottoms:** Test Blue Jeans
* **Shoes:** Test White Sneakers
```

```
$ $env:AI201_CACHE='0'; & '.\.venv\Scripts\python.exe' -c "from tools import create_fit_card; item={'title':'Test Graphic Tee','category':'tops','description':'black cotton graphic tee','price':18.0,'platform':'Test Market','colors':['black']}; outfit='Pair it with blue jeans and white sneakers.'; [print(f'RUN {i}: {create_fit_card(outfit, item)}') for i in range(1, 4)]"
RUN 1: Test Graphic Tee: Scored this black cotton graphic tee for just $18.0! It's giving off the ultimate effortless weekend vibe when paired with blue jeans and white sneakers. Grab it now on Test Market before someone else does!
RUN 2: Scored this ultimate Test Graphic Tee for just $18.0! It's giving off the best casual-cool energy, especially when styled with blue jeans and white sneakers. Grab it now exclusively on Test Market before someone else does!
RUN 3: Just scored this sleek Test Graphic Tee for only $18.0! It's got such a cool, effortless vibe when you pair it with blue jeans and white sneakers. Grab it soon over on Test Market before someone else does!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked AI to review `suggest_outfit` against the tool contract and check whether the selected search result was the item described to the model.
- *What came back:* It found that `item = new_item` was later overwritten by `for item in wardrobe_items`, so the prompt described the last wardrobe piece as the new thrift listing.
- *What I changed:* I renamed the values to `selected_item` and `wardrobe_item`, updated every prompt reference, and tested that the prompt contained `New item: Selected Item` rather than the final wardrobe item's name.

**Moment 2**

- *What I asked for:* I asked AI to attack three `create_fit_card` outputs using my criterion that a card must preserve the exact item title, price, and platform while allowing different wording.
- *What came back:* The three captions varied, but two omitted the exact title and the first outputs invented details such as a vintage fade that were not in the supplied item.
- *What I changed:* I tightened the prompt to require the supplied facts and forbid invented item details, then added a deterministic title-preservation guard. I reran the same input three times with caching disabled and confirmed that all three cards varied while retaining `Test Graphic Tee`, `$18.0`, and `Test Market`.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
