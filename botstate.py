"""
Bot ka global ON/OFF switch — sirf OWNER_ID `/on` aur `/off` command se
control karta hai. Jab OFF hota hai to bot kisi bhi message ya button ka
jawab nahi deta (sirf `/on` / `/off` chalte rehte hain).

Fast in-memory cache use hota hai (har message par DB call na karna pade),
lekin state DB mein bhi persist hota hai (dekho db.py: set_bot_status /
get_bot_status) — isliye restart ke baad bhi yaad rehta hai.
"""

_enabled = True


def is_enabled() -> bool:
    return _enabled


def set_enabled(value: bool):
    global _enabled
    _enabled = bool(value)
