import pytz
import os
import asyncio
from datetime import datetime
from info import *
from Script import script
from database.users_chats_db import db
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait

async def bcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await bcast_messages(user_id, message)
    except Exception as e:
        return "Error"

@Client.on_message(filters.private & filters.command("myplan") & filters.user(ADMINS))
async def myplan(client, message):
    user = message.from_user.mention
    user_id = message.from_user.id
    data = await db.get_user(message.from_user.id)
    if data and data.get("expiry_time"):
        expiry = data.get("expiry_time") 
        expiry_ist = expiry.astimezone(pytz.timezone(TIMEZONE))
        expiry_str_in_ist = expiry.astimezone(pytz.timezone(TIMEZONE)).strftime("%d-%m-%Y %I:%M:%S %p")            

        current_time = datetime.now(pytz.timezone(TIMEZONE))
        time_left = expiry_ist - current_time

        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
        await message.reply_text(f"<b><u>Cᴜʀʀᴇɴᴛ Pʟᴀɴ Dᴇᴛᴀɪʟs 📊</u>\n\nUꜱᴇʀ : {user}\n\nUꜱᴇʀ Iᴅ : <code>{user_id}</code>\n\n<blockquote>Tɪᴍᴇ Lᴇꜰᴛ : <code>{time_left_str}</code></blockquote>\n\nExᴘ Tɪᴍᴇ : <code>{expiry_str_in_ist}</code></b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 Uᴘɢʀᴀᴅᴇ", url="t.me/MjSupport_Robot"), InlineKeyboardButton("Cʟᴏsᴇ ❌", callback_data="close_data")]])) 
    else:
        await message.reply_text(f"<b>ʜᴇʏ {user},\n\nʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴʏ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs, ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴛᴀᴋᴇ ᴘʀᴇᴍɪᴜᴍ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ /plans ᴛᴏ ᴋɴᴏᴡ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴘʟᴀɴs...</b>")

@Client.on_message(filters.command("bcast") & filters.user(ADMINS) & filters.reply)
async def premium_user_broadcast(bot, message):
    users = await db.get_all_premium_users()
    b_msg = message.reply_to_message
    mh8 = await message.reply_text(text='Broadcasting your message...')
    total_users = await db.total_premium_users_count()
    done = 0
    blocked = 0
    failed = 0
    success = 0
    async for user in users:
        data = await db.get_user(user['id'])
        if data and data.get("expiry_time"):                        
            kd = await bcast_messages(int(user['id']), b_msg)
            if kd == 'Success':
                success += 1
            elif kd == 'Error':
                failed += 1
            done += 1
            if not done % 20:
                await mh8.edit(f"**Premium Users Broadcast in progress :)\n\nTotal Users: {total_users}\n\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {failed}**")    
            await mh8.edit(f"**Premium Users Broadcast Completed :)\n\nTotal Users: {total_users}\n\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {failed}**")
        else:
            pass

@Client.on_message(filters.private & filters.command("plans") & filters.user(ADMINS))
async def allplans(bot, message):
    btn = [[
            InlineKeyboardButton("❗ Bᴜʏ Pʀᴇᴍɪᴜᴍ Pʟᴀɴ / Sᴇɴᴅ Sᴄʀᴇᴇɴsʜᴏᴛ ❗", url="t.me/MjSupport_Robot")
          ],[
            InlineKeyboardButton("Pʀᴇᴍɪᴜᴍ Pʟᴀɴ Pʀᴇᴠɪᴇᴡ", callback_data="premium_video")
          ]]
    await message.reply_photo(
        photo="https://graph.org/file/0b88dee3a5e6a7fb32505.jpg",
        caption=script.PLANS,
        reply_markup=InlineKeyboardMarkup(btn)
    )
