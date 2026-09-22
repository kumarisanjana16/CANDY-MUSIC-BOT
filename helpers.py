import random

# Style overrides — screenshot wala fancy look (Nσᴡ Pʟᴧʏɪηɢ / Dυʀᴧᴛɪση jaisa).
# Yeh 5 letters khaas glyphs use karte hain, baaki sab smallcaps hi rehte hain.
_STYLE = {"a": "ᴧ", "e": "є", "o": "σ", "n": "η", "u": "υ"}

_SMALLCAPS = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ғ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
}

# Processing / "searching" ke waqt dikhne wala random emoji (sirf emoji, koi text nahi)
PROCESSING_EMOJIS = ["🧪", "🦋", "🔍"]


def smallcaps(text: str) -> str:
    """Har letter ko smallcaps mein badalta hai (lowercase style — labels ke liye)."""
    return "".join(
        _STYLE.get(ch.lower()) or _SMALLCAPS.get(ch.lower(), ch) if ch.isalpha() else ch
        for ch in text
    )


def smallcaps_title(text: str) -> str:
    """Har word ka pehla letter normal capital, baaki smallcaps — headings ke liye."""
    out = []
    new_word = True
    for ch in text:
        if ch.isalpha():
            out.append(
                ch.upper()
                if new_word
                else (_STYLE.get(ch.lower()) or _SMALLCAPS.get(ch.lower(), ch))
            )
            new_word = False
        else:
            out.append(ch)
            new_word = ch in " -_/\n"
    return "".join(out)


def fancy_italic(text: str) -> str:
    """A-Z/a-z ko Mathematical Sans-Serif Bold Italic unicode mein badalta hai
    (jaise 𝙌𝙪𝙚𝙚𝙣 𝙭 𝙢𝙪𝙨𝙞𝙘 style) — baaki characters (space, emoji) waise hi rehte hain."""
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(chr(0x1D63C + (ord(ch) - ord("A"))))
        elif "a" <= ch <= "z":
            out.append(chr(0x1D656 + (ord(ch) - ord("a"))))
        else:
            out.append(ch)
    return "".join(out)


def random_processing_text() -> str:
    """Sirf ek random emoji deta hai (3 me se) — koi text nahi."""
    return random.choice(PROCESSING_EMOJIS)


def format_duration(seconds) -> str:
    """Seconds ko MM:SS ya H:MM:SS format mein badalta hai. Already-string ho to wahi wapas."""
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return str(seconds) if seconds else "??:??"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def duration_to_seconds(duration_str: str) -> int:
    """'4:38' ya '1:04:38' jaisi string ko seconds mein badalta hai."""
    if not duration_str:
        return 0
    parts = str(duration_str).split(":")
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return 0
    seconds = 0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def format_uptime(seconds) -> str:
    """Seconds ko 'ʜʜ:ᴍᴍ:ss' jaisa smallcaps uptime string banata hai
    (jaise '12ʜ:4ᴍ:10s') — Now Playing/group start message ke liye."""
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        seconds = 0
    h, rem = divmod(max(seconds, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{h}ʜ:{m}ᴍ:{s}s"


# ---------------------------------------------------------------------------
# Expandable quote — screenshot/video wala effect: message ka body ek quote
# block ke andar aata hai jisme "click karke neeche scroll / expand" hota hai.
# Pyrogram default parse mode HTML + Markdown dono samajhta hai, isliye baaki
# text style (bold, links, smallcaps) bilkul waisa hi rehta hai.
# ---------------------------------------------------------------------------
def expandable_quote(text: str) -> str:
    return f"<blockquote expandable>{text}</blockquote>"


def quote(text: str) -> str:
    return f"<blockquote>{text}</blockquote>"


def strip_quotes(text: str) -> str:
    """Agar library expandable blockquote support na kare to fallback ke liye."""
    return (
        text.replace("<blockquote expandable>", "")
        .replace("<blockquote>", "")
        .replace("</blockquote>", "")
    )


# ---------------------------------------------------------------------------
# Now Playing wala decorative divider (screenshot jaisa)
# ---------------------------------------------------------------------------
DIVIDER = "•── ⋅ ⋅  ────── ⋅᯽⋅ ────── ⋅ ⋅ ⋅──•"


def bullet_lines(items) -> str:
    """Har item ko '╰┈➤ ' ke saath alag line mein deta hai."""
    return "\n".join(f"╰┈➤ {i}" for i in items if i)
