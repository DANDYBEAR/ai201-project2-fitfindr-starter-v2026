"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

_STOPWORDS = {"a", "an", "the", "for", "with", "in", "of"}

def _keywords(text: str) -> set[str]:
    """ Lowercase words worth mataching on, stopwords removed. """
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    if not size:
        return set()
    cleaned = re.sub(r"\([^)]*\)", " ", str(size))
    tokens: set[str] = set()
    for part in re.split(r"[/,|]+", cleaned):
        upper_tokens = re.findall(r"[A-Z0-9]+", part.upper())
        if "ONE" in upper_tokens and "SIZE" in upper_tokens:
            tokens.add("ONE")
            tokens.add("SIZE")
        tokens.update(upper_tokens)
    return {token for token in tokens if token}


def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    wanted_tokens = _size_tokens(wanted)
    listing_tokens = _size_tokens(listing_size)
    if not listing_tokens:
        return False
    if "ONE" in listing_tokens and "SIZE" in listing_tokens:
        return True
    return bool(wanted_tokens & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()
    wanted_tokens = _keywords(description)

    filtered: list[tuple[int, dict]] = []
    for listing in listings:
        if max_price is not None:
            try:
                if float(listing.get("price", float("inf"))) > float(max_price):
                    continue
            except (TypeError, ValueError):
                continue

        if size is not None and not _size_matches(size, listing.get("size", "")):
            continue

        title_tokens = _keywords(listing.get("title", ""))
        desc_tokens = _keywords(listing.get("description", ""))
        tag_tokens = set()
        for tag in listing.get("style_tags", []) or []:
            tag_tokens |= _keywords(str(tag))
        category_tokens = _keywords(listing.get("category", ""))
        brand_tokens = _keywords(listing.get("brand") or "")

        if wanted_tokens:
            score = (
                5 * len(wanted_tokens & title_tokens)
                + 4 * len(wanted_tokens & desc_tokens)
                + 3 * len(wanted_tokens & tag_tokens)
                + 2 * len(wanted_tokens & category_tokens)
                + 1 * len(wanted_tokens & brand_tokens)
            )
        else:
            score = 1

        if score <= 0:
            continue

        filtered.append((score, listing))

    filtered.sort(key=lambda pair: (-pair[0], float(pair[1].get("price", 0.0))))
    return [listing for _, listing in filtered[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    selected_item = new_item or {}
    wardrobe_items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []

    if not wardrobe_items:
        prompt = (
            "You are a helpful fashion stylist. Suggest 1 or 2 outfits for this thrifted item. "
            "Keep the advice practical and specific.\n\n"
            f"Item: {selected_item.get('title', 'Unknown item')}\n"
            f"Category: {selected_item.get('category', 'unknown')}\n"
            f"Description: {selected_item.get('description', '')}\n"
            f"Colors: {', '.join(selected_item.get('colors', []) or [])}\n"
            f"Style tags: {', '.join(selected_item.get('style_tags', []) or [])}\n"
            "Give general styling ideas that work without needing the user to own a lot of pieces."
        )
        return generate(prompt, system="You are a concise but useful fashion stylist.")

    wardrobe_lines = []
    for wardrobe_item in wardrobe_items:
        if not isinstance(wardrobe_item, dict):
            continue
        name = wardrobe_item.get("name", "Unknown piece")
        category = wardrobe_item.get("category", "")
        colors = ", ".join(wardrobe_item.get("colors", []) or []) or "neutral"
        tags = ", ".join(wardrobe_item.get("style_tags", []) or []) or "basic"
        wardrobe_lines.append(f"- {name} ({category}; colors: {colors}; tags: {tags})")

    prompt = (
        "You are a fashion stylist. Recommend 1 or 2 outfits for the thrifted item using pieces the user already owns. "
        "Name the pieces from the wardrobe explicitly and keep the suggestions wearable.\n\n"
        f"New item: {selected_item.get('title', 'Unknown item')}\n"
        f"Category: {selected_item.get('category', 'unknown')}\n"
        f"Description: {selected_item.get('description', '')}\n"
        f"Colors: {', '.join(selected_item.get('colors', []) or [])}\n"
        f"Style tags: {', '.join(selected_item.get('style_tags', []) or [])}\n\n"
        "Wardrobe:\n" + "\n".join(wardrobe_lines)
    )
    return generate(prompt, system="You are a concise fashion stylist who names wardrobe pieces.")


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not isinstance(outfit, str) or not outfit.strip():
        item = new_item or {}
        title = item.get("title", "This thrifted piece")
        price = item.get("price")
        platform = item.get("platform", "the listing")
        if price is None:
            return f"{title} is the kind of piece that instantly upgrades a basic outfit — a thrift find worth styling around."
        return f"{title} for ${price} on {platform} is exactly the kind of thrift score that makes a basic outfit feel intentional."

    item = new_item or {}
    prompt = (
        "Write exactly 3 sentences for a short, natural thrift-find caption. "
        "Include the exact item title, exact price, and exact platform supplied "
        "below, each at least once. Describe the outfit's vibe without inventing "
        "item details. Before returning, silently verify the caption has exactly "
        "3 sentences and contains all three exact facts.\n\n"
        f"Exact item title: {item.get('title', 'Unknown item')}\n"
        f"Category: {item.get('category', 'unknown')}\n"
        f"Price: ${item.get('price', 'unknown')}\n"
        f"Platform: {item.get('platform', 'unknown')}\n"
        f"Colors: {', '.join(item.get('colors', []) or [])}\n"
        f"Description: {item.get('description', '')}\n"
        f"Outfit idea: {outfit.strip()}"
    )
    caption = generate(prompt, system="You are a social caption writer for thrift finds.")
    title = str(item.get("title") or "").strip()
    if title and title.casefold() not in caption.casefold():
        caption = f"{title}: {caption}"
    return caption
