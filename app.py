import asyncio
import threading

import aiohttp
import uvicorn
from fastapi import FastAPI
from pyrogram import idle
from pyrogram.types import BotCommand

import config
import db
import botstate
from clients import bot, assistant, call_py, LOGGER

# Handlers register karne ke liye import karna zaroori hai
import play  # noqa: F401

web = FastAPI()


@web.get("/")
async def root():
    return {"status": "running"}


def run_web():
    uvicorn.run(web, host="0.0.0.0", port=config.PORT, log_level="warning")


async def keep_alive():
    """
    Render free web services 15 min inactivity ke baad sula deta hai.
    Isliye bot khud apne hi URL ko periodically ping karta rehta hai taaki
    process kabhi offline na ho. RENDER_EXTERNAL_URL Render khud provide
    karta hai deploy ke time, isko manually set karne ki zaroorat nahi.
    """
    if not config.RENDER_EXTERNAL_URL:
        LOGGER.info("RENDER_EXTERNAL_URL set nahi hai — keep-alive ping skip ho raha hai.")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(config.RENDER_EXTERNAL_URL, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    LOGGER.info(f"Keep-alive ping: {resp.status}")
            except Exception as e:
                LOGGER.warning(f"Keep-alive ping fail: {e}")
            # Pehle ping turant, uske baad har PING_INTERVAL seconds par —
            # Render free tier ~15 min inactivity ke baad sula deta hai, isliye
            # start hote hi ping zaroori hai, sirf sleep ke baad nahi.
            await asyncio.sleep(config.PING_INTERVAL)


async def register_bot_commands():
    """Bot commands set karta hai taaki group mein '/' likhne par menu dikhe."""
    try:
        await bot.set_bot_commands(
            [
                BotCommand("start", "Bot ko start karo"),
                BotCommand("play", "Gaana bajao"),
                BotCommand("skip", "Agla gaana"),
                BotCommand("pause", "Pause karo"),
                BotCommand("resume", "Resume karo"),
                BotCommand("stop", "Band karo"),
                BotCommand("reload", "Bot ko refresh karo (admin only)"),
                BotCommand("id", "Apni/group ki ID dekho"),
            ]
        )
    except Exception as e:
        LOGGER.warning(f"Bot commands set nahi ho paye: {e}")


async def _run_once():
    await bot.start()
    LOGGER.info("✅ Bot started")

    await assistant.start()
    LOGGER.info("✅ Assistant started")

    # IMPORTANT: assistant ke dialogs ek baar fetch kar lo taaki pyrogram
    # har group/channel ka peer + access_hash cache kar le. Isके bina
    # thodi der baad "ValueError: Peer id invalid: ..." aata hai jab
    # bot change_stream/leave_group_call try karta hai kisi aise chat par
    # jiska peer assistant ke local cache mein nahi hai.
    try:
        async for _ in assistant.get_dialogs():
            pass
        LOGGER.info("✅ Assistant peers cached")
    except Exception as e:
        LOGGER.warning(f"Dialogs cache karne mein error: {e}")

    await call_py.start()
    LOGGER.info("✅ PyTgCalls started — ab bot music bajane ke liye taiyar hai")

    # Owner ke /on /off se pichhli baar jo status set kiya tha, wahi load karo
    try:
        botstate.set_enabled(await db.get_bot_status())
        LOGGER.info(f"✅ Bot status loaded: {'ON' if botstate.is_enabled() else 'OFF'}")
    except Exception as e:
        LOGGER.warning(f"Bot status load nahi ho paya, default ON rakh rahe hain: {e}")

    await register_bot_commands()

    if config.LOG_GROUP_ID:
        try:
            await bot.send_message(config.LOG_GROUP_ID, "✅ Bot restart ho gaya hai aur ab online hai.")
        except Exception as e:
            LOGGER.warning(f"Log group mein message nahi bhej paya: {e}")

    keep_alive_task = asyncio.create_task(keep_alive())

    try:
        await idle()
    finally:
        keep_alive_task.cancel()
        try:
            await bot.stop()
        except Exception:
            pass
        try:
            await assistant.stop()
        except Exception:
            pass
        LOGGER.info("🛑 Bot stopped")


async def main():
    """
    _run_once() ko wrap karta hai taaki koi bhi unexpected crash (network
    drop, connection reset, etc.) permanently bot ko offline na kar de —
    thodi der baad process khud ko restart kar leta hai, jab tak Render
    khud process kill na kare.
    """
    while True:
        try:
            await _run_once()
            break  # idle() sirf tabhi return karta hai jab process ko normally stop kiya jaaye
        except Exception as e:
            LOGGER.error(f"Bot crash ho gaya, 10 second mein restart kar raha hoon: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    asyncio.get_event_loop().run_until_complete(main())
