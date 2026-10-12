"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "suggest_outfit_item_id": None,  # ID actually handed to suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

_PRICE_PATTERN = re.compile(
    r"\b(?:under|below|up\s+to|max(?:imum)?(?:\s+price)?(?:\s+of)?|budget(?:\s+of)?)"
    r"\s*\$?\s*(\d+(?:\.\d+)?)|\$(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_SIZE_PATTERN = re.compile(
    r"\bsize\s+((?:one\s+size)|(?:[a-z0-9]+(?:[/.-][a-z0-9]+)*))\b",
    re.IGNORECASE,
)


def _parse_query(query: str) -> dict:
    """Extract deterministic search inputs from a plain-language query."""
    text = (query or "").strip()
    price_match = _PRICE_PATTERN.search(text)
    price_text = (price_match.group(1) or price_match.group(2)) if price_match else None
    size_match = _SIZE_PATTERN.search(text)
    size = size_match.group(1).upper() if size_match else None

    description = _PRICE_PATTERN.sub(" ", text)
    description = _SIZE_PATTERN.sub(" ", description)
    description = re.sub(
        r"^(?:(?:i(?:'m| am)?\s+)?(?:looking|searching)\s+for|"
        r"(?:i\s+)?(?:want|need)|find\s+me|show\s+me)\s+",
        "",
        description,
        flags=re.IGNORECASE,
    )
    description = re.sub(r"\s+", " ", description).strip(" ,.;:-")

    return {
        "description": description,
        "size": size,
        "max_price": float(price_text) if price_text is not None else None,
    }


def _no_results_message(parsed: dict) -> str:
    changes = ["broader description keywords"]
    if parsed.get("size"):
        changes.append("a different size")
    if parsed.get("max_price") is not None:
        changes.append("a higher maximum price")
    return "No listings matched those filters. Try " + ", ".join(changes) + "."


def _model_unavailable_message(stage: str) -> str:
    """Turn a model failure into a stage-specific, actionable user message."""
    return (
        f"The model couldn't be reached, so I couldn't generate the {stage}. "
        "Check your internet connection and GEMINI_API_KEY, then try again."
    )


def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    The loop follows the branch rule written in Milestone 2:

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    stage = "search"
    iteration = 0

    while stage is not None:
        iteration += 1
        trace.check_iterations(iteration)

        if stage == "search":
            parsed = _parse_query(session["query"])
            results = call_tool("search_listings", {
                "description": parsed["description"],
                "size": parsed["size"],
                "max_price": parsed["max_price"],
            })

            session["parsed"] = parsed
            trace.step("parse_query", inputs=query, returned=str(parsed))

            session["search_results"] = results
            trace.step(
                "search_listings (via MCP)",
                inputs=str(parsed),
                returned=results,
                note=f"{len(results)} match(es)",
            )

            if not results:
                session["error"] = _no_results_message(parsed)
                trace.step(
                    "branch",
                    note="search returned []: stopping before suggest_outfit",
                )
                return session

            session["selected_item"] = results[0]
            trace.step("select_item", returned=session["selected_item"])
            stage = "outfit"
            continue

        if stage == "outfit":
            outfit_inputs = {
                "new_item": session["selected_item"],
                "wardrobe": session["wardrobe"],
            }
            session["suggest_outfit_item_id"] = outfit_inputs["new_item"].get("id")
            outfit_trace_inputs = (
                f"new_item_id={session['suggest_outfit_item_id']}; "
                f"new_item={session['selected_item'].get('title')}; "
                f"wardrobe_items={len(session['wardrobe'].get('items', []))}"
            )
            try:
                session["outfit_suggestion"] = suggest_outfit(**outfit_inputs)
            except ModelUnavailable:
                session["error"] = _model_unavailable_message("outfit")
                trace.step(
                    "suggest_outfit",
                    inputs=outfit_trace_inputs,
                    returned=session["error"],
                    note="model unavailable: stopping before create_fit_card",
                )
                return session
            trace.step(
                "suggest_outfit",
                inputs=outfit_trace_inputs,
                returned=session["outfit_suggestion"],
            )
            stage = "fit_card"
            continue

        if stage == "fit_card":
            fit_card_inputs = {
                "outfit": session["outfit_suggestion"],
                "new_item": session["selected_item"],
            }
            fit_card_trace_inputs = (
                f"new_item={session['selected_item'].get('title')}; "
                f"outfit={session['outfit_suggestion']}"
            )
            try:
                session["fit_card"] = create_fit_card(**fit_card_inputs)
            except ModelUnavailable:
                session["error"] = _model_unavailable_message("fit card")
                trace.step(
                    "create_fit_card",
                    inputs=fit_card_trace_inputs,
                    returned=session["error"],
                    note="model unavailable: stopping",
                )
                return session
            trace.step(
                "create_fit_card",
                inputs=fit_card_trace_inputs,
                returned=session["fit_card"],
            )
            stage = None

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
