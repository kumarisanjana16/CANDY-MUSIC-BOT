"""
Now Playing message ke andar LIVE progress bar chalata hai — har kuch second
baad caption edit karke elapsed time + bar aage badhata hai, bilkul waise jaise
screenshot mein "00:35 ▬▬▬▬▬▬▬▬▬▬ 4:38" dikh raha tha.

Bar khud aage badhta hai jab tak:
  - gaana duration tak pahunch na jaaye (khatam),
  - track skip/stop/replay na ho jaaye,
  - ya pause na kar diya jaaye (tab bar wahi ruk jaata hai jahan tha).
"""

import asyncio
import time

from clients import LOGGER
from helpers import format_duration

UPDATE_INTERVAL = 10          # seconds — Telegram flood-wait se bachne ke liye itna safe hai
BAR_LENGTH = 12
FILLED_CHAR = "▰"
EMPTY_CHAR = "▱"
MAX_EDIT_FAILURES = 3         # itni baar edit fail hone par task khud band ho jaata hai

# chat_id -> {"start": monotonic ts, "paused_at": ts|None, "paused_total": float, "video_id": str}
_progress: dict[int, dict] = {}

# chat_id -> background asyncio.Task jo caption update karta rehta hai
_tasks: dict[int, asyncio.Task] = {}


def _now() -> float:
    return time.monotonic()


def start(chat_id: int, video_id: str):
    """Naya track shuru hone par elapsed-time tracking (0 se) reset karta hai."""
    _progress[chat_id] = {
        "start": _now(),
        "paused_at": None,
        "paused_total": 0.0,
        "video_id": video_id,
    }


def pause(chat_id: int):
    """Bar ko wahi rok deta hai jahan abhi tha."""
    p = _progress.get(chat_id)
    if p and p["paused_at"] is None:
        p["paused_at"] = _now()


def resume(chat_id: int):
    """Pause ke waqt jitna time ruka tha, usko elapsed count se bahar rakhta hai."""
    p = _progress.get(chat_id)
    if p and p["paused_at"] is not None:
        p["paused_total"] += _now() - p["paused_at"]
        p["paused_at"] = None


def replay(chat_id: int):
    """Bar ko 00:00 se dobara shuru karta hai (🔁 button ke liye)."""
    p = _progress.get(chat_id)
    if p:
        p["start"] = _now()
        p["paused_at"] = None
        p["paused_total"] = 0.0


def elapsed(chat_id: int) -> float:
    """Ab tak kitna waqt beet gaya (seconds mein), pause ka time ginte hue nahi."""
    p = _progress.get(chat_id)
    if not p:
        return 0.0
    ref = p["paused_at"] if p["paused_at"] is not None else _now()
    return max(0.0, ref - p["start"] - p["paused_total"])


def cancel_task(chat_id: int):
    """Sirf background updater band karta hai (tracking data chhua nahi jaata)."""
    task = _tasks.pop(chat_id, None)
    if task and not task.done():
        task.cancel()


def clear(chat_id: int):
    """Track/session poori tarah khatam — tracking + updater dono band."""
    _progress.pop(chat_id, None)
    cancel_task(chat_id)


def render_bar(elapsed_sec: float, total_sec: int) -> str:
    total_sec = max(total_sec, 1)
    ratio = min(max(elapsed_sec / total_sec, 0.0), 1.0)
    filled = int(round(ratio * BAR_LENGTH))
    bar = FILLED_CHAR * filled + EMPTY_CHAR * (BAR_LENGTH - filled)
    return f"`{format_duration(int(elapsed_sec))}` {bar} `{format_duration(int(total_sec))}`"


def start_updater(chat_id: int, message, caption_fn, markup_fn, video_id: str, total_sec: int):
    """
    Background task chalu karta hai jo har UPDATE_INTERVAL seconds baad
    `message` ka caption edit karke naya progress bar dikhata hai.

    - `caption_fn()` -> current "Now Playing" caption text (bina progress bar ke)
    - `markup_fn()`  -> inline keyboard (buttons waise hi rehte hain)
    - Track change/stop/duration-khatam hone par yeh khud ruk jaata hai.
    """
    cancel_task(chat_id)

    if total_sec <= 0:
        return  # duration hi pata nahi to bar dikhane ka fayda nahi

    async def _runner():
        failures = 0
        try:
            while True:
                await asyncio.sleep(UPDATE_INTERVAL)

                p = _progress.get(chat_id)
                if not p or p.get("video_id") != video_id:
                    return  # track badal gaya, skip/stop ho gaya, ya replay/naya track shuru hua

                el = min(elapsed(chat_id), total_sec)
                try:
                    text = f"{caption_fn()}\n\n{render_bar(el, total_sec)}"
                    await message.edit_caption(text, reply_markup=markup_fn())
                    failures = 0
                except Exception as e:
                    if "MESSAGE_NOT_MODIFIED" in str(e):
                        pass
                    else:
                        failures += 1
                        LOGGER.warning(f"Progress bar update fail ({failures}): {e}")
                        if failures >= MAX_EDIT_FAILURES:
                            return

                if el >= total_sec:
                    return
        except asyncio.CancelledError:
            pass

    _tasks[chat_id] = asyncio.create_task(_runner())


def seek(chat_id: int, position: float):
    """
    ⏪ -10s / ⏩ +10s buttons ke liye — bar ko seedha `position` seconds par
    set kar deta hai (pause state waisa hi rehta hai).
    """
    p = _progress.get(chat_id)
    if not p:
        return
    position = max(0.0, position)
    p["start"] = _now() - position
    p["paused_total"] = 0.0
    if p["paused_at"] is not None:
        p["paused_at"] = _now()
