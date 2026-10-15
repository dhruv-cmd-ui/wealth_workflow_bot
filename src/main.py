"""Orchestrator: pick content for a slot, render an image card, post to Telegram, persist rotation state."""
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

from content_picker import load_state, pick_content, save_state  # noqa: E402
from market_data import fetch_market_recap  # noqa: E402
from render_image import render_card  # noqa: E402

DISCLAIMER = (
    "⚠️ Educational content only — not investment advice. Not a SEBI-registered "
    "advisor. Please consult a certified financial advisor before investing."
)

CHANNEL_TAG = "#PersonalFinanceIndia"


def build_post(bank_name: str, item: dict | None):
    """Returns (category, heading, body, caption)."""
    if bank_name == "market_recap":
        data = fetch_market_recap()
        if data is None:
            # Graceful fallback: a generic market-watch note instead of failing the run.
            heading = "Markets Move, Discipline Doesn't Have To"
            body = (
                "Live index data wasn't available for today's snapshot. Either way — "
                "your SIPs and long-term plan don't need to react to a single day's move."
            )
        else:
            lines = []
            for label, stats in data.items():
                arrow = "▲" if stats["change_pct"] >= 0 else "▼"
                lines.append(f"{label}: {stats['close']:,} ({arrow}{stats['change_pct']}%)")
            heading = "Yesterday's Market Close"
            body = "\n".join(lines)
        category = "market_recap"

    elif bank_name == "terms":
        heading, body, category = item["term"], item["definition"], "terms"

    elif bank_name == "tips":
        heading, body, category = "Money Tip of the Day", item["tip"], "tips"

    elif bank_name == "myths":
        heading = "Myth vs Fact"
        body = f"Myth: {item['myth']}\n\nFact: {item['fact']}"
        category = "myths"

    elif bank_name == "tax_tips":
        heading, body, category = "Tax & Rules Tip", item["tip"], "tax_tips"

    elif bank_name == "quotes":
        heading = "Finance Quote"
        body = f"“{item['quote']}”\n\n— {item['author']}"
        category = "quotes"

    elif bank_name == "did_you_know":
        heading, body, category = "Did You Know?", item["fact"], "did_you_know"

    elif bank_name == "sip_mutual_funds":
        heading, body, category = "SIP / Mutual Fund Corner", item["tip"], "sip_mutual_funds"

    elif bank_name == "qna":
        heading, body, category = item["question"], item["answer"], "qna"

    else:
        raise ValueError(f"Unknown content bank: {bank_name}")

    caption_body = body if len(body) <= 600 else body[:597] + "..."
    caption = f"<b>{heading}</b>\n\n{caption_body}\n\n{DISCLAIMER}\n{CHANNEL_TAG}"
    if len(caption) > 1024:
        caption = caption[:1021] + "..."

    return category, heading, body, caption


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True, choices=["morning", "evening"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    state = load_state()
    bank_name, item = pick_content(args.slot, state)
    category, heading, body, caption = build_post(bank_name, item)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"out/{args.slot}_{category}_{timestamp}.png"
    render_card(category, heading, body, DISCLAIMER, out_path)

    print(f"[{args.slot}] bank={bank_name} category={category}")
    print(f"Heading: {heading}")
    print(f"Body:\n{body}")
    print(f"Caption:\n{caption}")
    print(f"Image saved to: {out_path}")

    if args.dry_run:
        print("Dry run — skipping Telegram post and state save.")
        return

    from telegram_client import send_photo

    send_photo(out_path, caption)
    save_state(state)
    print("Posted to Telegram and rotation state saved.")


if __name__ == "__main__":
    main()
