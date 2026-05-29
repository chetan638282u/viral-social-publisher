# Viral Social Publisher

Python starter project for a daily, approval-first social media content pipeline.

It can:

- Research source notes, then draft original hooks, captions, hashtags, and platform-specific copy.
- Use Gemini when `GEMINI_API_KEY` is provided, with a built-in non-AI fallback.
- Create a simple square image with text overlay.
- Create an original audio track and 1-2 MP4 short videos per day.
- Save an approval package for review.
- Send approval requests to Telegram with approve/reject buttons.
- Publish only after you approve.
- Use official platform APIs through publisher modules.

Important: this project avoids unsafe automation by default. It does not steal copyrighted music, scrape private pages, or publish unverified political claims. Real posting requires official API access and your account tokens.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m viral_publisher draft
python -m viral_publisher approve --platforms dry_run
```

Generated drafts and media are saved in `output/`.

## Daily Workflow

Run this at 11:00 AM to prepare a draft and ask for confirmation:

```bash
python -m viral_publisher daily --videos 2
```

For Telegram approval:

```bash
python -m viral_publisher telegram-bot
python -m viral_publisher telegram-request --videos 2
```

For hands-off scheduling, use Windows Task Scheduler, a server cron job, or GitHub Actions. Keep the approval step enabled so nothing posts without your permission.

## Gemini Setup

Add your Gemini API key to `.env`:

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
```

The writer uses source feeds as research notes only. It is instructed not to copy article sentences or headlines into the public post. If Gemini is unavailable or the free tier limit is reached, the app falls back to a simpler original template.

## Real Platform Posting

You will need official API credentials:

- Instagram and Facebook: Meta Graph API with a Business/Creator account and Page connection.
- LinkedIn: LinkedIn developer app with posting permissions.
- YouTube Shorts: YouTube Data API, OAuth credentials, and a valid short video file.

Add credentials to `.env`, then replace `dry_run` with the target platforms.

```bash
python -m viral_publisher approve --platforms instagram facebook linkedin youtube
```

## Why It Does Not Use "Any Trending Music"

Using random trending music can get accounts restricted because music rights differ by platform, region, and account type. This project creates original audio locally for free. You can also replace it with licensed music that you have the right to use.

## About Platform Drafts

Instagram and LinkedIn let humans save drafts in their apps, but their official publishing APIs are designed around creating and publishing media through authenticated endpoints. This project saves a local draft package in `output/` and can publish through official APIs after Telegram approval when your accounts and API permissions are connected. That is the reliable automation path.
