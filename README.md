<h1 align="left">
    <a target="_blank">
        Telegram Forward UserBot
        <img src="http://www.randomnoun.com/wpf/shell32-avi/tshell32_160.gif" width="272" height="60">
    </a>
</h1>

A simple yet powerful **Telegram UserBot** built using [Pyrogram](https://docs.pyrogram.org/),  
designed to **forward media (videos, documents)** from one channel/group to another with user-defined filters and commands.  

Repository: [lx-0980/telegram-Forward-UserBot](https://github.com/lx-0980/telegram-Forward-UserBot/tree/userbot-v2)

---

## 🚀 Features

- ✅ Forward videos and documents from source chats to target channels  
- 🔧 Filter by content type:
  - Movies only
  - Series only
  - Forward all  
- 🔢 Skip a given number of messages before forwarding starts  
- 💬 Interactive confirmation system (Yes/No) before forwarding  
- 🛑 Cancel ongoing forwarding process any time  
- ⚙️ Configurable target channel  
- 🧠 Automatically handles flood-waits and limits forwarding sessions  
- 🪶 Lightweight and easy to deploy

---

## ⚙️ Configuration

The configuration is defined in **[`config.py`](https://raw.githubusercontent.com/lx-0980/telegram-Forward-UserBot/refs/heads/userbot-v2/config.py)**:

```python
class Config(object):
    APP_ID = int(getenv("APP_ID", ""))
    API_HASH = getenv("API_HASH", "")
    TG_USER_SESSION = getenv("TG_USER_SESSION", "")
    ADMINS = [x.strip("@ ") for x in str(getenv("ADMINS", "") or "").split(",") if x.strip("@ ")]

Environment Variables

Variable	Description

APP_ID	Telegram API ID from https://my.telegram.org/apps
API_HASH	Telegram API Hash from https://my.telegram.org/apps
TG_USER_SESSION	Pyrogram session string for your user account
ADMINS	Comma-separated list of allowed admin IDs or usernames


Example .env file:

APP_ID=123456
API_HASH=abcdef1234567890abcdef1234567890
TG_USER_SESSION=YOUR_SESSION_STRING
ADMINS=123456789


---

🧠 How It Works

1. The userbot runs as your Telegram account (not a bot token).


2. You interact with it via private chat.


3. You send a channel link or forwarded message.


4. The bot asks for confirmation before forwarding.


5. Once confirmed, it forwards media from the source chat to your configured target channel.




---

🧩 Commands

Command	Description

/set_channel <channel_id>	Set the target channel where files will be forwarded.
/set_skip <number>	Skip the first <number> messages in the source.
/copy_movies_only on/off	Enable/disable forwarding only movies.
/copy_series_only on/off	Enable/disable forwarding only series.
/forwardall on/off	Forward all media (disables filters).
cancel	Stop an ongoing forwarding session.


Example:

/set_channel -1001234567890
/set_skip 50
/copy_movies_only on

Then send:

https://t.me/c/123456789/987

Bot → Do you want to forward? If you want forward send me yes else send me no
You → yes
Bot → Starts forwarding.
You → cancel (to stop early)
Bot → Summary report (processed, forwarded, skipped).


---

🧰 Installation

git clone https://github.com/lx-0980/telegram-Forward-UserBot.git
cd telegram-Forward-UserBot
pip install pyrogram tgcrypto asyncio

Set up environment variables (as shown above).

Run the bot:

python3 bot.py

Or deploy using Heroku with Procfile:

worker: python3 bot.py


---

🔍 File Overview

bot.py

Initializes the Pyrogram client using your session.

Implements iter_messages for efficient message fetching.

Handles startup and plugin loading logic.


plugins/clone.py

Main forwarding engine.

Processes commands like /set_channel, /set_skip, etc.

Detects media and applies “movies only” or “series only” filters.

Forwards messages using send_cached_media or copy_message.

Tracks status and supports cancellation.



---

⚠️ Important Notes

Only videos and documents are forwarded.

Forwarding limit: 1000 messages per session.

“Movies only” and “Series only” detection is based on title parsing via PTT.parse_title.

User must be admin in target channel.

The bot will pause automatically if a Telegram flood-wait occurs.

This is a userbot, not a bot token — use responsibly according to Telegram’s TOS.

⚠️ Forwarding Limits & Safety

🚨 Important Anti-Ban Rules:

Forward Limit:
The bot automatically stops after 5000 forwards per session.
Exceeding this limit can trigger Telegram’s anti-spam system and may lead to temporary or permanent account bans.

Delay Between Forwards:
Each media (video/document) is forwarded with a 7-second delay.
This helps avoid flood-waits and reduces Telegram’s detection of automated activity.

Why This Matters:
Telegram monitors excessive or rapid forwarding from user accounts.
Respecting these limits ensures your account remains safe and functional.

Recommendation:
Run multiple small sessions instead of one large batch.
Avoid forwarding copyrighted or restricted material.


---

🧾 Example Workflow

/set_channel -1001234567890
/set_skip 20
/copy_movies_only on

Then send:

https://t.me/c/123456789/100

Bot asks for confirmation → Reply yes
Bot starts forwarding messages → Sends summary when done.


---

🧩 Deployment on Heroku

1. Fork this repository.


2. Go to Heroku.


3. Create a new app and connect your forked repo.


4. Add environment variables (APP_ID, API_HASH, TG_USER_SESSION, ADMINS).


5. Deploy and start the worker process.



Procfile contents:

worker: python3 bot.py


---

