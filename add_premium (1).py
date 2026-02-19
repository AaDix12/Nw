import pytz
import os
import asyncio
from datetime import datetime, timedelta
from info import *
from Script import script
from utils import get_seconds
from database.users_chats_db import db
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.errors import FloodWait

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


# ==================== UTILITY FUNCTIONS ====================

async def bcast_messages(user_id, message):
    """Send a broadcast message to a single user, handling FloodWait."""
    try:
        await message.copy(chat_id=user_id)
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await bcast_messages(user_id, message)
    except Exception:
        return "Error"


# ==================== COMMAND HANDLERS ====================

@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def give_premium_cmd_handler(client, message):
    """Add premium subscription via command: /add_premium USER_ID 1 month"""
    if len(message.command) != 4:
        await message.reply_text(
            "<b>❌ Cᴏᴍᴍᴀɴᴅ Iɴᴄᴏᴍᴘʟᴇᴛᴇ\n\n"
            "Fᴏʀᴍᴀᴛ: <code>/add_premium USER_ID 1 month</code>\n\n"
            "Exᴀᴍᴘʟᴇs:\n"
            "• <code>/add_premium 123456 1 day</code>\n"
            "• <code>/add_premium 123456 1 month</code>\n"
            "• <code>/add_premium 123456 1 year</code></b>"
        )
        return

    try:
        user_id = int(message.command[1])
        target_user = await client.get_users(user_id)
        duration = message.command[2] + " " + message.command[3]
        seconds = await get_seconds(duration)

        if seconds <= 0:
            await message.reply_text(
                "<b>❌ Iɴᴠᴀʟɪᴅ Dᴜʀᴀᴛɪᴏɴ Fᴏʀᴍᴀᴛ\n\n"
                "• <code>1 day</code> for days\n"
                "• <code>1 hour</code> for hours\n"
                "• <code>1 min</code> for minutes\n"
                "• <code>1 month</code> for months\n"
                "• <code>1 year</code> for year</b>"
            )
            return

        expiry_time = datetime.now() + timedelta(seconds=seconds)
        await db.update_user({"id": user_id, "expiry_time": expiry_time})

        data = await db.get_user(user_id)
        expiry = data.get("expiry_time")
        expiry_str = expiry.astimezone(pytz.timezone(TIMEZONE)).strftime("%d-%m-%Y %I:%M:%S %p")
        current_str = datetime.now(pytz.timezone(TIMEZONE)).strftime("%d-%m-%Y %I:%M:%S %p")

        await message.reply_text(
            f"<b>✅ #PREMIUM_ADDED\n\n"
            f"Usᴇʀ: {target_user.mention} [<code>{user_id}</code>]\n\n"
            f"Vᴀʟɪᴅɪᴛʏ: <code>{duration}</code>\n\n"
            f"Exᴘ Tɪᴍᴇ: <code>{expiry_str}</code></b>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴄʟᴏsᴇ ❌", callback_data="close_data")]
            ])
        )

        try:
            await client.send_message(
                chat_id=user_id,
                text=(
                    f"<b><i>Hᴇʏ Tʜᴇʀᴇ {target_user.mention} 👋</i>\n\n"
                    f"Yᴏᴜʀ {duration} Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Aᴅᴅᴇᴅ ✅\n\n"
                    f"Sᴜʙ Tɪᴍᴇ: <code>{current_str}</code>\n"
                    f"Exᴘ Tɪᴍᴇ: <code>{expiry_str}</code>\n\n"
                    f"<blockquote>Fᴏʀ Aɴʏ Hᴇʟᴘ Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ @MjSupport_Robot</blockquote></b>"
                ),
                disable_web_page_preview=True
            )
        except Exception:
            pass

        try:
            await client.send_message(
                PREMIUM_LOGS,
                text=(
                    f"<b>#PREMIUM_ADDED\n\n"
                    f"Usᴇʀ: {target_user.mention} [<code>{user_id}</code>]\n\n"
                    f"Vᴀʟɪᴅɪᴛʏ: <code>{duration}</code>\n\n"
                    f"Exᴘ Tɪᴍᴇ: <code>{expiry_str}</code></b>"
                ),
                disable_web_page_preview=True
            )
        except Exception:
            pass

        logger.info(f"Admin added premium to {user_id} for {duration}")

    except Exception as e:
        logger.error(f"Error in give_premium_cmd_handler: {e}", exc_info=True)
        await message.reply_text("<b>❌ Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>")


@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium(client, message):
    """Remove premium subscription via command: /remove_premium USER_ID"""
    if len(message.command) != 2:
        await message.reply_text(
            "<b>❌ Cᴏᴍᴍᴀɴᴅ Iɴᴄᴏᴍᴘʟᴇᴛᴇ\n\n"
            "Fᴏʀᴍᴀᴛ: <code>/remove_premium USER_ID</code></b>"
        )
        return

    try:
        user_id = int(message.command[1])
        target_user = await client.get_users(user_id)

        if await db.has_premium_access(user_id):
            await db.remove_premium_access(user_id)
            await db.delete_premium_user(user_id)
            await message.reply_text(
                f"<b>✅ Sᴜᴄᴄᴇssғᴜʟʟʏ Rᴇᴍᴏᴠᴇᴅ {target_user.mention}'s Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ ◀</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("ᴄʟᴏsᴇ ❌", callback_data="close_data")]
                ])
            )
            try:
                await client.send_message(
                    chat_id=user_id,
                    text=(
                        f"<b><i>Hᴇʏ Tʜᴇʀᴇ {target_user.mention} 👋</i>\n\n"
                        f"Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Hᴀs Bᴇᴇɴ Rᴇᴍᴏᴠᴇᴅ ❌\n\n"
                        f"<blockquote>Fᴏʀ Aɴʏ Hᴇʟᴘ Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ @MjSupport_Robot</blockquote></b>"
                    )
                )
            except Exception:
                pass
        else:
            await message.reply_text(
                f"<b>❓ {target_user.mention} ᴅᴏᴇs ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ.</b>"
            )

        logger.info(f"Admin removed premium from {user_id}")

    except Exception as e:
        logger.error(f"Error in remove_premium: {e}", exc_info=True)
        await message.reply_text("<b>❌ Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>")


@Client.on_message(filters.command("bcast") & filters.user(ADMINS) & filters.reply)
async def premium_user_broadcast(bot, message):
    """Broadcast a message to all active premium users via /bcast (reply to message)"""
    b_msg = message.reply_to_message
    status_msg = await message.reply_text("<b>📢 Bʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ Pʀᴇᴍɪᴜᴍ Usᴇʀs...</b>")
    total_users = await db.total_premium_users_count()
    done = success = failed = 0

    users = await db.get_all_premium_users()
    async for user in users:
        data = await db.get_user(user['id'])
        if data and data.get("expiry_time"):
            result = await bcast_messages(int(user['id']), b_msg)
            if result == "Success":
                success += 1
            else:
                failed += 1
            done += 1
            if done % 20 == 0:
                try:
                    await status_msg.edit(
                        f"<b>📢 Bʀᴏᴀᴅᴄᴀsᴛ ɪɴ Pʀᴏɢʀᴇss...\n\n"
                        f"Tᴏᴛᴀʟ: {total_users}\n"
                        f"Dᴏɴᴇ: {done} / {total_users}\n"
                        f"Sᴜᴄᴄᴇss: {success} | Fᴀɪʟᴇᴅ: {failed}</b>"
                    )
                except Exception:
                    pass

    await status_msg.edit(
        f"<b>✅ Bʀᴏᴀᴅᴄᴀsᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ!\n\n"
        f"Tᴏᴛᴀʟ: {total_users}\n"
        f"Sᴜᴄᴄᴇss: {success} | Fᴀɪʟᴇᴅ: {failed}</b>"
    )
    logger.info(f"Broadcast completed: {success} success, {failed} failed out of {done}")


@Client.on_message(filters.command("premium_users") & filters.user(ADMINS))
async def premium_user(client, message):
    """List all active premium users: /premium_users"""
    status_msg = await message.reply_text("<b>⏳ Fᴇᴛᴄʜɪɴɢ Pʀᴇᴍɪᴜᴍ Usᴇʀs...</b>")
    total_users = await db.total_premium_users_count()
    text = f"<b>👑 Tᴏᴛᴀʟ Pʀᴇᴍɪᴜᴍ Usᴇʀs: {total_users}</b>\n\n"
    count = 1

    users = await db.get_all_premium_users()
    async for user in users:
        data = await db.get_user(user['id'])
        if data and data.get("expiry_time"):
            expiry = data.get("expiry_time")
            expiry_ist = expiry.astimezone(pytz.timezone(TIMEZONE))
            expiry_str = expiry_ist.strftime("%d-%m-%Y %I:%M:%S %p")
            current_time = datetime.now(pytz.timezone(TIMEZONE))
            time_left = expiry_ist - current_time
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            time_left_str = f"{days}d {hours}h {minutes}m"
            user_info = await client.get_users(user['id'])
            text += (
                f"<b>{count}. {user_info.mention} [<code>{user['id']}</code>]\n"
                f"   Exᴘɪʀʏ: {expiry_str}\n"
                f"   Lᴇꜰᴛ: {time_left_str}</b>\n\n"
            )
            count += 1

    try:
        await status_msg.edit(text)
    except MessageTooLong:
        with open('premium_users.txt', 'w+') as outfile:
            outfile.write(text)
        await message.reply_document(
            'premium_users.txt',
            caption="<b>👑 Pʀᴇᴍɪᴜᴍ Usᴇʀs Lɪsᴛ</b>"
        )
        os.remove("premium_users.txt")
        await status_msg.delete()

    logger.info(f"Admin fetched {total_users} premium users list")
