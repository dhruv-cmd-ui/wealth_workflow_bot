"""Picks the next piece of content for a given posting slot, with no-repeat rotation."""
import json
import random
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
STATE_PATH = Path(__file__).resolve().parent.parent / "state" / "rotation_state.json"

# Maps a scheduled slot name to the content banks eligible for it.
# "market_recap" is handled specially by main.py (live data), not loaded from a JSON bank here.
SLOT_BANKS = {
    "morning": ["market_recap", "terms", "did_you_know"],
    "evening": ["tips", "myths", "tax_tips", "quotes", "sip_mutual_funds", "qna"],
}

BANK_FILES = {
    "terms": "terms.json",
    "tips": "tips.json",
    "myths": "myths.json",
    "tax_tips": "tax_tips.json",
    "quotes": "quotes.json",
    "did_you_know": "did_you_know.json",
    "sip_mutual_funds": "sip_mutual_funds.json",
    "qna": "qna.json",
}


def load_bank(bank_name: str) -> list:
    path = CONTENT_DIR / BANK_FILES[bank_name]
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _next_index(state: dict, bank_name: str, bank_size: int) -> int:
    """Advances a shuffled-order cursor for a bank, reshuffling on wraparound."""
    bank_state = state.setdefault(bank_name, {})
    order = bank_state.get("order")
    cursor = bank_state.get("cursor", 0)

    if not order or len(order) != bank_size or cursor >= len(order):
        order = list(range(bank_size))
        random.shuffle(order)
        cursor = 0

    index = order[cursor]
    bank_state["order"] = order
    bank_state["cursor"] = cursor + 1
    return index


def pick_bank_for_slot(slot: str, state: dict) -> str:
    """Picks which content bank to use for this slot, rotating across the slot's eligible banks."""
    eligible = SLOT_BANKS[slot]
    slot_state = state.setdefault("_slot_cursor", {})
    cursor = slot_state.get(slot, 0) % len(eligible)
    slot_state[slot] = cursor + 1
    return eligible[cursor]


def pick_content(slot: str, state: dict):
    """Returns (bank_name, item_dict_or_None). item is None for 'market_recap' (handled by caller)."""
    bank_name = pick_bank_for_slot(slot, state)
    if bank_name == "market_recap":
        return bank_name, None

    items = load_bank(bank_name)
    index = _next_index(state, bank_name, len(items))
    return bank_name, items[index]
