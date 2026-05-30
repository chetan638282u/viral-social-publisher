# Viral Social Publisher

Python starter project for a daily, approval-first social media content pipeline. It also includes a Windows PowerShell runner for PCs where Python is not installed.

It can:

- Collect fresh story ideas from configured RSS/news feeds.
- Research source notes, then draft original hooks, captions, hashtags, and platform-specific copy.
- Use Gemini/OpenRouter when keys are provided, with a built-in fallback.
- Create a simple square image with text overlay.
- Save an approval package for review.
- Send approval requests to Telegram with Save package, Direct post, and Reject buttons.
- Publish only after you approve.
- Use official platform APIs through publisher modules.

Important: this project avoids unsafe automation by default. It does not steal copyrighted music, scrape private pages, or publish unverified political claims. Real posting requires official API access and your account tokens.

## Fast Windows Workflow

This works without installing Python:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\viral-social-publisher.ps1 -Command telegram-request
powershell -ExecutionPolicy Bypass -File scripts\viral-social-publisher.ps1 -Command telegram-bot
```

The first command creates today's image/caption and sends the Telegram approval buttons. The second command listens for your Telegram button click.

## Python Workflow

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m viral_publisher draft
python -m viral_publisher approve --platforms dry_run
```

Generated drafts and media are saved in `output/`.

## Gemini / OpenRouter Setup

Add keys to `.env`:

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openrouter/free
```

The writer uses source feeds as research notes only. It is instructed not to copy article sentences or headlines into the public post.

## Real Platform Posting

You will need official API credentials:

- Instagram and Facebook: Meta/Instagram API permissions and access tokens.
- LinkedIn: LinkedIn developer app with posting permissions.
- YouTube Shorts: YouTube Data API, OAuth credentials, and a valid short video file.

For Telegram direct posting, set:

```text
APPROVED_PLATFORMS=instagram
```

## Media Hosting

Instagram direct posting needs a public URL for the generated image or video. The PowerShell runner tries these in order:

1. If `GITHUB_TOKEN` is set, upload media to your GitHub repo and use the raw GitHub URL.
2. If `GITHUB_TOKEN` is blank, upload the image to Catbox anonymous hosting and use that public URL.

```text
GITHUB_TOKEN=your_github_personal_access_token_optional
GITHUB_REPOSITORY=chetan638282u/viral-social-publisher
GITHUB_MEDIA_BRANCH=main
GITHUB_MEDIA_PATH=media
```

Catbox is faster to start with because it needs no token, but GitHub-hosted media is more reliable for daily automation.

The PowerShell runner currently posts an image to Instagram. The Python path can generate short videos when Python and FFmpeg/moviepy dependencies are available.

## Why It Does Not Use "Any Trending Music"

Using random trending music can get accounts restricted because music rights differ by platform, region, and account type. This project creates original audio locally for free. You can also replace it with licensed music that you have the right to use.
