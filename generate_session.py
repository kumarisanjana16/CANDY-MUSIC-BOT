"""
Apne computer ya Render ke 'Shell' tab mein chalao:
    python3 generate_session.py

Phone number + OTP daalo, jo string milegi wahi STRING_SESSION hai.
Ek alag Telegram account use karo, apna personal account nahi.
"""

from pyrogram import Client

API_ID = int(input("API_ID daalo: "))
API_HASH = input("API_HASH daalo: ")

with Client(name="assistant_session", api_id=API_ID, api_hash=API_HASH, in_memory=True) as app:
    print("\n\n✅ Ye raha tumhara STRING_SESSION, ise Render ke env mein daalo:\n")
    print(app.export_session_string())
    print("\n\n")
