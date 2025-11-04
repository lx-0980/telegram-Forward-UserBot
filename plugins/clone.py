import asyncio
import re 
import logging
from pyrogram.enums import MessageMediaType, MessagesFilter
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from config import Config
from PTT import parse_title

logger = logging.getLogger(__name__)

CURRENT = {}
CHANNEL = {}
CANCEL = {}
FORWARDING = {}
COPY_MOVIES_ONLY = {} 
COPY_SERIES_ONLY = {}

@Client.on_message(filters.regex('cancel'))
async def cancel_forward(bot, message):
    cancel = await message.reply("Trying to cancel forwarding...")
    if FORWARDING.get(message.from_user.id):
        CANCEL[message.from_user.id] = True
        await cancel.edit("Successfully Forward Canceled!")
    else:
        await cancel.edit("No Forward Countinue Currently!")

@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text) & filters.private & filters.incoming)
async def send_for_forward(bot, message):
    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid link for forward!')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif message.forward_from_chat.type in [enums.ChatType.CHANNEL, enums.ChatType.GROUP]:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return

    try:
        source_chat = await bot.get_chat(chat_id)
    except Exception as e:
        return await message.reply(f'Error - {e}')

    if source_chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply("I can forward only channels and groups.")

    target_chat_id = CHANNEL.get(message.from_user.id)
    if not target_chat_id:
        return await message.reply("You not added target channel.\nAdd using /set_channel command.")

    try:
        target_chat = await bot.get_chat(target_chat_id)
    except Exception as e:
        return await message.reply(f'Error - {e}')
    # last_msg_id is same to total messages
    approval = await message.chat.ask(
        text = f'''Do You Want Forward? If You Want Forward Send Me "<code>yes</code>" Else Send Me "<code>no</code>"'''
    )
    approval = approval.text.lower()  
    if approval.strip() == "yes":
        if FORWARDING.get(message.from_user.id):
            return await message.reply('Wait until previous process complete.')
        msg = await message.reply('Starting Forwarding...')
        try:
            chat = int(chat_id)
        except:
            chat = chat_id
        lst_msg_id = last_msg_id
        await forward_files(int(lst_msg_id), chat, msg, bot, message.from_user.id)
    else:
        if approval.strip() == "no":
            return await message.reply("Okay")
        else:
            return await message.reply("Invalid reply, Try Again!")
            
                    
@Client.on_message(filters.private & filters.command(['set_skip']))
async def set_skip_number(bot, message):
    try:
        _, skip = message.text.split(" ")
    except:
        return await message.reply("Give me a skip number.")
    try:
        skip = int(skip)
    except:
        return await message.reply("Only support in numbers.")
    CURRENT[message.from_user.id] = int(skip)
    await message.reply(f"Successfully set <code>{skip}</code> skip number.")


@Client.on_message(filters.private & filters.command(['set_channel']))
async def set_target_channel(bot, message):    
    if Config.ADMINS and not ((str(message.from_user.id) in Config.ADMINS) or (message.from_user.username in Config.ADMINS)):
        return await message.reply("You Are Not Allowed To Use This UserBot")
    try:
        _, chat_id = message.text.split(" ")
    except:
        return await message.reply("Give me a target channel ID")
    try:
        chat_id = int(chat_id)
    except:
        return await message.reply("Give me a valid ID")

    try:
        chat = await bot.get_chat(chat_id)
    except:
        return await message.reply("Make me a admin in your target channel.")
    CHANNEL[message.from_user.id] = int(chat.id)
    await message.reply(f"Successfully set {chat.title} target channel.")

@Client.on_message(filters.private & filters.command(['copy_movies_only']))
async def copy_movies_only(bot, message):
    if Config.ADMINS and not ((str(message.from_user.id) in Config.ADMINS) or (message.from_user.username in Config.ADMINS)):
        return await message.reply("You Are Not Allowed To Use This UserBot")
    user_id = message.from_user.id
    parts = message.text.split(" ")
    if len(parts) != 2 or parts[1].lower() not in ["on", "off"]:
        return await message.reply("Usage: /copy_movies_only on or /copy_movies_only off")
    if COPY_SERIES_ONLY.get(user_id):
        COPY_SERIES_ONLY[user_id] = False

    COPY_MOVIES_ONLY[user_id] = (parts[1].lower() == "on")

    await message.reply(
        f"✅ Copy movies only is now <b>{'ENABLED' if COPY_MOVIES_ONLY[user_id] else 'DISABLED'}</b>"
    )
    
@Client.on_message(filters.private & filters.command(['copy_series_only']))
async def copy_series_only(bot, message):
    if Config.ADMINS and not ((str(message.from_user.id) in Config.ADMINS) or (message.from_user.username in Config.ADMINS)):
        return await message.reply("You Are Not Allowed To Use This UserBot")
    user_id = message.from_user.id
    parts = message.text.split(" ")
    if len(parts) != 2 or parts[1].lower() not in ["on", "off"]:
        return await message.reply("Usage: /copy_movies_only on or /copy_movies_only off")
    if COPY_MOVIES_ONLY.get(user_id):
        COPY_MOVIES_ONLY[user_id] = False

    COPY_SERIES_ONLY[user_id] = (parts[1].lower() == "on")

    await message.reply(
        "✅ <b>{'ENABLED' if COPY_MOVIES_ONLY[user_id] else 'DISABLED'}</b>"
    )
    
@Client.on_message(filters.private & filters.command(['forwardall']))
async def forward_all(bot, message):
    if Config.ADMINS and not ((str(message.from_user.id) in Config.ADMINS) or (message.from_user.username in Config.ADMINS)):
        return await message.reply("You Are Not Allowed To Use This UserBot")
    user_id = message.from_user.id
    parts = message.text.split(" ")
    if len(parts) != 2 or parts[1].lower() not in ["on", "off"]:
        return await message.reply("Usage: /forwardall on or /forwardall off")
    COPY_MOVIES_ONLY[user_id] = False
    COPY_SERIES_ONLY[user_id] = False
    await message.reply("Now userbot will forward all type video's and documents") 
    
async def forward_files(lst_msg_id, chat, msg, bot, user_id):
    current = CURRENT.get(user_id) if CURRENT.get(user_id) else 0
    forwarded = 0
    deleted = 0
    unsupported = 0
    fetched = 0
    CANCEL[user_id] = False
    FORWARDING[user_id] = True
    copy_movies = COPY_MOVIES_ONLY.get(user_id)
    copy_series = COPY_SERIES_ONLY.get(user_id)
    # lst_msg_id is same to total messages
    try:
        async for message in bot.iter_messages(chat, lst_msg_id, CURRENT.get(user_id) if CURRENT.get(user_id) else 0):
            if CANCEL.get(user_id):
                await msg.edit(f"Successfully Forward Canceled!")
                FORWARDING[user_id] = False 
                break
            if forwarded == 5000:
                await msg.edit(f"Forward stopped! You Reached Max Limit\n<b>Message ID</b>: <code>{message.id}</code>\n<b>Forwarded</b>: <code>{forwarded}</code>")
                FORWARDING[user_id] = False 
                break
            current += 1
            fetched += 1
            if current % 20 == 0:
                await msg.edit_text(text=f'''Forward Processing...\n\nTotal Messages: <code>{lst_msg_id}</code>\nCompleted Messages: <code>{current} / {lst_msg_id}</code>\nForwarded Files: <code>{forwarded}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon Media Files: <code>{unsupported}</code>\n\n send "<code>cancel</code>" for stop''')
            if message.empty:
                deleted += 1
                continue
            if not message.media:
                unsupported += 1
                continue
            if message.media not in [MessageMediaType.DOCUMENT, MessageMediaType.VIDEO]:
                continue
            if message.caption:
                title = message.caption
            else:
                title = message.video.file_name if message.video.file_name else message.document.file_name
            if copy_movies:
                data = parse_title(title, translate_languages=True)
                seasons = data.get("seasons", [])
                episodes = data.get("episodes", [])
                if seasons or episodes:
                    unsupported +=1
                    continue
            if copy_series:
                data = parse_title(title, translate_languages=True)
                seasons = data.get("seasons", [])
                episodes = data.get("episodes", [])
                if not seasons and not episodes:
                    unsupported += 1
                    continue
            try:         
                media = getattr(message, message.media.value, None)
                if media:
                    try:
                        await bot.send_cached_media(
                            chat_id=CHANNEL.get(user_id),
                            file_id=media.file_id,
                            caption=message.caption
                        )
                    except FloodWait as e:
                        await asyncio.sleep(e.value)  # Wait "value" seconds before continuing
                        await bot.send_cached_media(
                                chat_id=CHANNEL.get(user_id),
                                file_id=media.file_id,
                                caption=message.caption
                        )
                else:
                    try:
                        await bot.copy_message(
                            chat_id=CHANNEL.get(user_id),
                            from_chat_id=chat,
                            caption=message.caption,
                            message_id=message.id,
                            parse_mode=enums.ParseMode.MARKDOWN
                        )
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        await bot.copy_message(
                            chat_id=CHANNEL.get(user_id),
                            from_chat_id=chat,
                            caption=message.caption,
                            message_id=message.id,
                            parse_mode=enums.ParseMode.MARKDOWN
                        )
            except Exception as e:
                logger.exception(e)
                return await msg.reply(f"Forward Canceled!\n\nError - {e}")               
            forwarded += 1
            await asyncio.sleep(7)            
    except Exception as e:
        logger.exception(e)
        await msg.reply(f"Forward Canceled!\n\nError - {e}")
        FORWARDING[user_id] = False
    else:
        await msg.edit(f'Forward Completed!\n\nTotal Messages: <code>{lst_msg_id}</code>\nCompleted Messages: <code>{current} / {lst_msg_id}</code>\nFetched Messages: <code>{fetched}</code>\nTotal Forwarded Files: <code>{forwarded}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon Media Files: <code>{unsupported}</code>')
        FORWARDING[user_id] = False
