import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from viral_publisher.cli import DRAFT_PATH, build_draft, load_draft
from viral_publisher.publishers import get_publisher


TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"
STATE_PATH = Path("output") / "telegram_state.json"


def send_approval_request(config_path: str = "config.example.yaml", video_count: int | None = None) -> dict[str, Any]:
    load_dotenv()
    draft = build_draft(config_path, video_count=video_count)
    token, chat_id = _telegram_credentials()
    text = (
        f"Approval needed\n\n"
        f"Hook: {draft.hook}\n\n"
        f"Caption:\n{draft.caption[:1500]}\n\n"
        f"Image: {draft.image_path}\n"
        f"Videos: {', '.join(draft.video_paths) if draft.video_paths else 'not generated'}"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Save package", "callback_data": "save_latest"},
                {"text": "Direct post", "callback_data": "post_latest"},
            ],
            [
                {"text": "Reject", "callback_data": "reject_latest"},
            ],
        ]
    }
    response = _post(
        token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps(keyboard),
        },
    )
    if draft.video_path and Path(draft.video_path).exists():
        _post_file(
            token,
            "sendVideo",
            {"chat_id": chat_id, "caption": "Preview video draft"},
            "video",
            Path(draft.video_path),
        )
    _save_state({"last_update_id": 0, "status": "pending", "draft_path": str(DRAFT_PATH)})
    return response


def run_approval_bot() -> None:
    load_dotenv()
    token, _ = _telegram_credentials()
    state = _load_state()
    offset = int(state.get("last_update_id", 0)) + 1
    print("Telegram approval bot is running. Press Ctrl+C to stop.")

    while True:
        updates = _post(token, "getUpdates", {"timeout": 30, "offset": offset}).get("result", [])
        for update in updates:
            offset = update["update_id"] + 1
            state["last_update_id"] = update["update_id"]
            callback = update.get("callback_query")
            if callback:
                _handle_callback(token, callback)
        _save_state(state)


def _handle_callback(token: str, callback: dict[str, Any]) -> None:
    data = callback.get("data")
    callback_id = callback["id"]
    if data == "reject_latest":
        _post(token, "answerCallbackQuery", {"callback_query_id": callback_id, "text": "Rejected. Nothing posted."})
        _save_state({"status": "rejected", "draft_path": str(DRAFT_PATH)})
        return

    if data == "save_latest":
        draft = load_draft()
        result = get_publisher("dry_run").publish(draft)
        _save_state({"status": "saved", "draft_path": str(DRAFT_PATH), "results": [result]})
        _post(token, "answerCallbackQuery", {"callback_query_id": callback_id, "text": "Saved for manual upload."})
        _send_saved_package(token, callback["message"]["chat"]["id"], draft, result)
        return

    if data != "post_latest":
        _post(token, "answerCallbackQuery", {"callback_query_id": callback_id, "text": "Unknown action."})
        return

    draft = load_draft()
    platforms = os.getenv("APPROVED_PLATFORMS", "dry_run").split()
    results = []
    for platform in platforms:
        results.append(get_publisher(platform).publish(draft))

    _save_state({"status": "approved", "draft_path": str(DRAFT_PATH), "results": results})
    _post(token, "answerCallbackQuery", {"callback_query_id": callback_id, "text": "Approved."})
    chat_id = callback["message"]["chat"]["id"]
    _post(token, "sendMessage", {"chat_id": chat_id, "text": f"Done:\n{json.dumps(results, indent=2)[:3000]}"})


def _send_saved_package(token: str, chat_id: int, draft, result: dict[str, Any]) -> None:
    text = (
        "Saved package is ready for manual upload.\n\n"
        f"Hook:\n{draft.hook}\n\n"
        f"Caption and hashtags:\n{draft.caption}\n\n"
        f"Local saved file: {result.get('path')}"
    )
    _post(token, "sendMessage", {"chat_id": chat_id, "text": text[:3500]})
    if draft.image_path and Path(draft.image_path).exists():
        _post_file(token, "sendPhoto", {"chat_id": chat_id, "caption": "Image post"}, "photo", Path(draft.image_path))
    for index, video_path in enumerate(draft.video_paths, start=1):
        path = Path(video_path)
        if path.exists():
            _post_file(token, "sendVideo", {"chat_id": chat_id, "caption": f"Video {index}"}, "video", path)


def _telegram_credentials() -> tuple[str, str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required.")
    return token, chat_id


def _post(token: str, method: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(TELEGRAM_API.format(token=token, method=method), data=payload, timeout=45)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data


def _post_file(token: str, method: str, payload: dict[str, Any], field_name: str, path: Path) -> dict[str, Any]:
    with path.open("rb") as file:
        response = requests.post(
            TELEGRAM_API.format(token=token, method=method),
            data=payload,
            files={field_name: file},
            timeout=90,
        )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
