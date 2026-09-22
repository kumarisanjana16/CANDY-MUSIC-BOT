import logging
import time
from pyrogram import Client
from pytgcalls import PyTgCalls
from motor.motor_asyncio import AsyncIOMotorClient

import config

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - %(name)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pytgcalls").setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# Compatibility shim: py-tgcalls==0.9.7 (bahut purana) ka raw-update handler
# yeh assume karta hai ki UpdateGroupCall object ke paas seedha `.chat_id`
# attribute hota hai (data2[update.chat_id]). Naye kurigram/pyrogram schema
# mein yeh field hata diya gaya — ab sirf `.peer` (PeerChat/PeerChannel)
# milta hai. Isi wajah se ye error aata tha:
#   AttributeError: 'UpdateGroupCall' object has no attribute 'chat_id'
# Yeh patch `.chat_id` ko ek computed property bana deta hai jo `.peer` se
# nikal ke wahi purana behaviour de deta hai — bina py-tgcalls ya kurigram
# ka version chede.
# ---------------------------------------------------------------------------
try:
    from pyrogram.raw.types import UpdateGroupCall, PeerChat, PeerChannel

    if "chat_id" not in UpdateGroupCall.__dict__:
        def _shim_chat_id(self):
            peer = getattr(self, "peer", None)
            if isinstance(peer, PeerChat):
                return peer.chat_id
            if isinstance(peer, PeerChannel):
                return peer.channel_id
            raise AttributeError("chat_id")

        UpdateGroupCall.chat_id = property(_shim_chat_id)
        logging.getLogger("MusicBot").info(
            "✅ UpdateGroupCall.chat_id compatibility shim applied"
        )
except Exception as _shim_err:  # kabhi bhi patch fail ho to bot crash na ho
    logging.getLogger("MusicBot").warning(
        f"⚠️ UpdateGroupCall compatibility shim skip ho gaya: {_shim_err}"
    )

LOGGER = logging.getLogger("MusicBot")

# Process shuru hone ka time — group start message mein uptime dikhane ke liye
START_TIME = time.monotonic()

bot = Client(
    name="MusicBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    in_memory=True,
)

assistant = Client(
    name="Assistant",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.STRING_SESSION,
    in_memory=True,
)

call_py = PyTgCalls(assistant)

mongo_client = AsyncIOMotorClient(config.MONGO_DB_URI)
db = mongo_client["MusicBotDB"]
