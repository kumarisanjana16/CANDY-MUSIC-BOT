CANDY-MUSIC-BOT
Repository navigation
Code
Pull requests
Actions
1 star
0 forks
0 watching
1 branch
0 tags
Activity
Public repository
· Forked from akebchutiya24-web/ZEXXY_MUSIX_REPO
This branch is up to date with akebchutiya24-web/ZEXXY_MUSIX_REPO:main.
akebchutiya24-web
akebchutiya24-web
3 weeks ago
Name	
Dockerfile
last month
README.md
last month
app.py
last month
assistant_join.py
last month
botstate.py
last month
clients.py
last month
config.py
last month
db.py
last month
generate_session.py
last month
helpers.py
last month
Repository files navigation
README
Simple Telegram Music Bot (Flat Structure)
Saari files ek hi folder mein hain — koi subfolder nahi, isliye GitHub app se ek-ek karke upload karna aasan hai.

Files
config.py — env variables
clients.py — bot, assistant, pytgcalls, mongo setup
db.py — Mongo mein users/chats track karta hai (broadcast ke liye)
helpers.py — smallcaps text + random processing text/emoji
music_queue.py — per-chat queue aur now-playing state
nowplaying.py — thumbnail se "Now Playing" card image banata hai
youtube.py — YouTube search + stream URL (ShrutiAPI)
play.py — saare commands aur buttons (/start, /play, /skip, /pause, /resume, /stop, /id, /broadcast)
app.py — sab start karta hai (isi ko run karna hai), keep-alive ping bhi isi mein hai
generate_session.py — assistant ki STRING_SESSION banane ke liye
requirements.txt, Dockerfile, sample.env
Setup
Credentials lo: API_ID/API_HASH (my.telegram.org), BOT_TOKEN (@BotFather), MONGO_DB_URI (mongodb.com free cluster), LOG_GROUP_ID aur OWNER_ID (@userinfobot)

STRING_SESSION banao: python3 generate_session.py chalao (alag account use karo)

SUPPORT_URL / CHANNEL_URL: apne support group aur update channel ka link sample.env mein daal do — yeh /start message ke buttons mein use hote hain.

GitHub pe upload: is folder ki saari files apne repo mein daal do (sab root mein, koi folder nahi banana)

Render pe deploy: New + > Web Service > Docker > Environment tab mein sample.env ke saare variables bharo > Deploy. RENDER_EXTERNAL_URL khaali chhod do — Render khud set kar deta hai, bot isi URL ko har PING_INTERVAL seconds mein ping karke sula hone se bachta hai.

Group setup: Bot aur Assistant dono ko group mein add karo, VC start karo, /play <song> try karo

Commands
/play <song> — gaana bajao ya queue mein daalo (agar pehle se kuch baj raha ho)
/skip — agla gaana
/pause / /resume
/stop — VC se nikal jao, queue clear
/id — apni aur group ki ID
/reload (sirf group admin/owner) — check karta hai bot admin hai ya nahi
/broadcast <msg> (sirf OWNER_ID) — sab users ko message bhejo
/addvd (sirf OWNER_ID) — agli image/video/gif jo bhejoge, wahi ab se /start message ke saath sabko jayegi
/delvd (sirf OWNER_ID) — /start message se set kiya hua media hata deta hai
Note
/skip /pause /resume /stop sirf group admin ya OWNER_ID use kar sakte hain — normal user sirf /play use kar sakta hai.

"Peer id invalid" error fix
Yeh error tab aata tha jab assistant account ke pyrogram session mein us group ka peer/access_hash cache nahi hota tha (kyunki assistant sirf VC join karta hai, normal messages nahi padhta). Ab app.py startup par ek baar assistant.get_dialogs() chala kar sab groups/channels ka peer cache kar leta hai, aur agar phir bhi kabhi yeh error aaye to play.py automatically dialogs refresh karke ek baar retry karta hai.
