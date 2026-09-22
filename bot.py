import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())

import os
from pyrogram import Client, filters

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client(
    "candy_music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("🎵 Candy Music Bot Online ❤️")


@app.on_message(filters.command("test"))
async def test_command(client, message):
    await message.reply_text("✅ Candy Bot को message मिल रहा है!")


@app.on_message(filters.command("play"))
async def play_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("🎵 ऐसे लिखो:\n/play Tere Liye")
        return

    song = " ".join(message.command[1:])
    await message.reply_text(f"🔎 Song मिला: {song}\n🎵 Music system तैयार किया जा रहा है...")


print("🎵 Candy Music Bot starting...")
app.run()
