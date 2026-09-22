import os

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "0"))
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "")
PORT = int(os.getenv("PORT", "10000"))

# Start message ke buttons ke links (support group / update channel / owner)
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/")
OWNER_URL = os.getenv("OWNER_URL", "https://t.me/NEXOR_BLAZE")

# Render apne aap yeh env variable deta hai (e.g. https://your-app.onrender.com)
# Isse bot khud ko periodically ping karke sleep hone se bachata hai.
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")
PING_INTERVAL = int(os.getenv("PING_INTERVAL", "600"))  # seconds (10 min default)

# Assistant (userbot) ka username — /play chalne par bot check karta hai ki
# yeh account group mein hai ya nahi, aur agar nahi hai to isi username se
# (ya invite link se) join karwane ki koshish karta hai.
ASSISTANT_USERNAME = os.getenv("ASSISTANT_USERNAME", "Mitsuriass")
