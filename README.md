# Automated India Personal-Finance Telegram Channel

Posts 2x/day (morning + evening, IST) to a Telegram channel, fully automated via GitHub Actions. No LLM, no ongoing cost — content comes from rotating JSON banks (financial terms, money tips, myths vs facts, tax tips, quotes, SIP/mutual fund tips, Q&A) plus a free live Nifty/Sensex snapshot for the morning post. Every post includes a compliance disclaimer and never gives stock-specific buy/sell calls (see `plan` design notes — this follows the lower-regulatory-risk educational model, not the tip-sheet model).

## How it works

- `.github/workflows/post.yml` runs on a cron schedule (03:00 UTC / 08:30 IST = morning, 13:30 UTC / 19:00 IST = evening), plus a manual "Run workflow" button.
- Each run picks the next unused item from the relevant content bank (`content/*.json`), renders a branded image card (`src/render_image.py`), and posts it to your channel via the Telegram Bot API (`src/telegram_client.py`).
- Rotation progress is tracked in `state/rotation_state.json`, which the workflow commits back to the repo after each post — so content works through the full bank before repeating, then reshuffles.
- To change the posting times, edit the two `cron:` lines in `.github/workflows/post.yml` (cron is in UTC; IST = UTC+5:30).
- To add more content, just add more entries to the relevant `content/*.json` file (same shape as the existing entries) and push — no code changes needed.

## Setup — steps only you can do

### 1. Create the Telegram channel
In Telegram: **New Channel** → give it a name/description → choose public or private.

### 2. Create a bot via @BotFather
1. Open a chat with **@BotFather** in Telegram.
2. Send `/newbot`.
3. Give it a name, then a unique username ending in `bot` (e.g. `IndiaFinanceDailyBot`).
4. BotFather replies with a token like `123456789:AAH...` — this is your `TELEGRAM_BOT_TOKEN`. Keep it secret.

### 3. Add the bot to your channel as admin
1. Open your channel → **Administrators** → **Add Admin**.
2. Search for your bot's username and add it.
3. Make sure **Post Messages** permission is enabled.
4. Your `TELEGRAM_CHANNEL_ID` is your channel's `@username` if it's public (e.g. `@YourChannelName`). If the channel is private, you'll need its numeric chat ID instead — forward any message from the channel to `@userinfobot` to get it.

### 4. Create a GitHub repository and push this code
This machine doesn't have `gh` (GitHub CLI) authenticated, so do this manually:
1. On github.com, create a new **empty** repository (no README/license — this folder already has one), e.g. `telegram-finance-bot`.
2. Then run, from this folder:
   ```
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git branch -M main
   git push -u origin main
   ```
   (Git will prompt you to authenticate the first time — use a GitHub personal access token or your configured credential helper.)

### 5. Add the two secrets in GitHub
1. In your new repo on GitHub: **Settings → Secrets and variables → Actions → New repository secret**.
2. Add `TELEGRAM_BOT_TOKEN` with the token from step 2.
3. Add `TELEGRAM_CHANNEL_ID` with the value from step 3.

### 6. Test it
In your repo on GitHub: **Actions → Post to Telegram → Run workflow** (choose morning or evening) → confirm a post lands in your channel. After that, it runs automatically on schedule — nothing else to do.

## Local testing (optional, before pushing)

```
pip install -r requirements.txt
cp .env.example .env   # fill in your real token + channel id
python src/main.py --slot morning --dry-run
python src/main.py --slot evening --dry-run
```
`--dry-run` renders the image to `./out/` and prints the caption without posting to Telegram or advancing rotation state — safe to run repeatedly. Drop `--dry-run` (with real `.env` values loaded) to actually post.

## Compliance note

This channel is designed to stay in financial-literacy / educational territory — no individual stock buy/sell/target/stop-loss calls — and every post carries a disclaimer. Consider pinning a longer "About / Disclaimer" message on the channel itself (e.g. "Educational content only, not a SEBI-registered advisor, consult a certified financial advisor before investing") once it's created.
