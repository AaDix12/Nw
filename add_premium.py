import pytz
from datetime import datetime
from info import *
from Script import script
from database.users_chats_db import db
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


# ==================== COMMAND HANDLERS ====================

@Client.on_message(filters.private & filters.command("myplan"))
async def myplan(client, message):
    """Show the current premium plan details of a user."""
    user = message.from_user.mention
    user_id = message.from_user.id
    data = await db.get_user(user_id)

    if data and data.get("expiry_time"):
        expiry = data.get("expiry_time")
        expiry_ist = expiry.astimezone(pytz.timezone(TIMEZONE))
        expiry_str = expiry_ist.strftime("%d-%m-%Y %I:%M:%S %p")

        current_time = datetime.now(pytz.timezone(TIMEZONE))
        time_left = expiry_ist - current_time
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"

        await message.reply_text(
            f"<b><u>Cᴜʀʀᴇɴᴛ Pʟᴀɴ Dᴇᴛᴀɪʟs 📊</u>\n\n"
            f"Usᴇʀ : {user}\n\n"
            f"Usᴇʀ Iᴅ : <code>{user_id}</code>\n\n"
            f"<blockquote>Tɪᴍᴇ Lᴇꜰᴛ : <code>{time_left_str}</code></blockquote>\n\n"
            f"Exᴘ Tɪᴍᴇ : <code>{expiry_str}</code></b>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("💰 Uᴘɢʀᴀᴅᴇ", url="t.me/MjSupport_Robot"),
                    InlineKeyboardButton("Cʟᴏsᴇ ❌", callback_data="close_data")
                ]
            ])
        )
    else:
        await message.reply_text(
            f"<b>ʜᴇʏ {user},\n\n"
            f"ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴʏ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs, "
            f"ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴛᴀᴋᴇ ᴘʀᴇᴍɪᴜᴍ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ /plans ᴛᴏ ᴋɴᴏᴡ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴘʟᴀɴs...</b>"
        )


@Client.on_message(filters.private & filters.command("plans"))
async def allplans(bot, message):
    """Show available premium plans."""
    btn = [
        [InlineKeyboardButton("◉ Bᴜʏ Pʀᴇᴍɪᴜᴍ Pʟᴀɴ / Sᴇɴᴅ Sᴄʀᴇᴇɴsʜᴏᴛ ◉", url="t.me/MjSupport_Robot")],
        [InlineKeyboardButton("Pʀᴇᴍɪᴜᴍ Pʟᴀɴ Pʀᴇᴠɪᴇᴡ", callback_data="premium_video")]
    ]
    await message.reply_photo(
        photo="https://graph.org/file/0b88dee3a5e6a7fb32505.jpg",
        caption=script.PLANS,
        reply_markup=InlineKeyboardMarkup(btn)
    )
