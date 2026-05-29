# Simple Explanation

This project is like a daily social media assistant.

## What It Does

1. It reads trusted news feeds from `config.example.yaml`.
2. It uses those feeds as research notes.
3. It creates:
   - a hook
   - a caption
   - hashtags
   - a short video script
   - a simple image with text on it
   - an original audio beat
   - 1 or 2 short MP4 videos
4. It saves everything inside the `output/` folder.
5. It posts only after you approve.

The public post is not copied from the articles. If you add a Gemini API key, Gemini writes the post in fresh words from the research notes. If Gemini is not available, the code uses a simple original fallback.

## What You Will See

When you run:

```bash
python -m viral_publisher daily --videos 2
```

You will see a draft in the terminal, including the caption, sources, and short video script.

If you type:

```text
YES
```

it saves the approved dry-run post. Later, when your real API keys are added, the same approval step can post to your connected platforms.

You can also receive the approval request inside Telegram:

```bash
python -m viral_publisher telegram-request
python -m viral_publisher telegram-bot
```

## What It Does Not Do Automatically Yet

It does not fully upload YouTube Shorts videos yet. For that, the project needs YouTube OAuth setup.

It does not use random trending music because that can create copyright problems. Instead, it creates original audio for free.

It cannot reliably save private Instagram or LinkedIn app drafts through official APIs. It saves a local draft package and can publish through official APIs after approval.

## Free API Key

Put this in `.env`:

```text
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash
```

Free limits can change, so the project also works without Gemini.

It does not post political claims without review because wrong information can damage your account and reputation.

## What You Need To Provide Later

- Meta API access for Instagram and Facebook.
- LinkedIn API access.
- YouTube API access if you want Shorts uploads.
- A public image/video hosting URL for Instagram publishing.
- Final approval before posting.
