# Telegram Approval Setup

## 1. Create Your Bot

1. Open Telegram.
2. Search for `@BotFather`.
3. Send `/newbot`.
4. Copy the bot token.

## 2. Find Your Chat ID

Send a message to your new bot, then open this URL in a browser:

```text
https://api.telegram.org/botYOUR_TOKEN/getUpdates
```

Find the `chat.id` value.

## 3. Add These To `.env`

```text
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
APPROVED_PLATFORMS=dry_run
```

Later, after real API keys are ready, change `APPROVED_PLATFORMS`:

```text
APPROVED_PLATFORMS=instagram facebook linkedin
```

## 4. Start The Approval Listener

Keep this running on the machine or server:

```bash
python -m viral_publisher telegram-bot
```

## 5. Send The Daily Approval Request

```bash
python -m viral_publisher telegram-request --videos 2
```

Use Windows Task Scheduler to run `scripts/run_daily_telegram_request.ps1` every day at 11:00 AM.
