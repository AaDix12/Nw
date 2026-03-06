from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import ListenerTimeout
from datetime import datetime
from info import *
from Script import script
from database.users_chats_db import db
from utils import check_shortner
from io import BytesIO
import pytz
import os
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

TEMP_IMPORT_DATA = {}

# ==================== CONSTANTS ====================

BUTTON_TEXT = {
    'VERIFICATION_ON':       "🟢 ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴏɴ",
    'VERIFICATION_OFF':      "🔴 ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴏꜰꜰ",
    'FSUB_MODE_ON':          "🟢 ғsᴜʙ ᴍᴏᴅᴇ ᴏɴ",
    'FSUB_MODE_OFF':         "🔴 ғsᴜʙ ᴍᴏᴅᴇ ᴏꜰꜰ",
    'GROUP_SEARCH_ENABLED':  "ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ: ᴇɴᴀʙʟᴇᴅ ✅",
    'GROUP_SEARCH_DISABLED': "ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ: ᴅɪsᴀʙʟᴇᴅ ❌",
    'FILE_DELETE_ENABLED':   "ғɪʟᴇ ᴅᴇʟᴇᴛᴇ: ᴇɴᴀʙʟᴇᴅ ✅",
    'FILE_DELETE_DISABLED':  "ғɪʟᴇ ᴅᴇʟᴇᴛᴇ: ᴅɪsᴀʙʟᴇᴅ ❌",
    'BACK':                  "⇋ ʙᴀᴄᴋ ⇌",
    'CONFIRM':               "✅ Cᴏɴꜰɪʀᴍ",
    'CANCEL':                "❌ Cᴀɴᴄᴇʟ",
}

MESSAGES = {
    'MAIN_SETTINGS':     "<b>ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ ᴀꜱ ʏᴏᴜ ᴡᴀɴᴛ ⚙:</b>",
    'VERIFICATION_MODE': (
        "<b>ᴀᴅᴠᴀɴᴄᴇ ꜱᴇᴛᴛɪɴɢꜱ ᴍᴏᴅᴇ ⚙\n\n"
        "ʏᴏᴜ ᴄᴀɴ ᴄᴜꜱᴛᴏᴍɪᴢᴇᴅ ꜱʜᴏʀᴛɴᴇʀ ᴠᴀʟᴜᴇꜱ, ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴛɪᴍᴇ ɢᴀᴘ ꜰʀᴏᴍ ʜᴇʀᴇ ✅\n"
        "ᴄʜᴏᴏꜱᴇ ꜰʀᴏᴍ ʙᴇʟᴏᴡ 👇</b>"
    ),
    'FSUB_MODE': (
        "<b>ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴍᴏᴅᴇ ⚙\n\n"
        "ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟs ꜰʀᴏᴍ ʜᴇʀᴇ ✅\n"
        "ᴄʜᴏᴏꜱᴇ ꜰʀᴏᴍ ʙᴇʟᴏᴡ 👇</b>"
    ),
    'ADD_FSUB_CHANNEL': (
        "<b>ᴀᴅᴅ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ 📢\n\n"
        "ᴄʜᴏᴏꜱᴇ ᴛʏᴘᴇ ᴏғ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴅᴅ 👇</b>"
    ),
    'GROUP_SETTINGS': (
        "<b>ᴀᴅᴠᴀɴᴄᴇ ꜱᴇᴛᴛɪɴɢꜱ ᴍᴏᴅᴇ ⚙\n\n"
        "ʏᴏᴜ ᴄᴀɴ ᴄᴜꜱᴛᴏᴍɪᴢᴇᴅ ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs, ғɪʟᴇ ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ ᴀɴᴅ "
        "sᴇɴᴅ ʙʀᴏᴀᴅᴄᴀsᴛ ꜰʀᴏᴍ ʜᴇʀᴇ ✅\n"
        "ᴄʜᴏᴏꜱᴇ ꜰʀᴏᴍ ʙᴇʟᴏᴡ 👇</b>"
    ),
    'CHOOSE_SHORTNER':   "<b>ᴄʜᴏᴏꜱᴇ ꜱʜᴏʀᴛɴᴇʀ ᴀɴᴅ ᴄʜᴀɴɢᴇ ᴛʜᴇ ᴠᴀʟᴜᴇꜱ ᴀꜱ ʏᴏᴜ ᴡᴀɴᴛ ✅</b>",
    'BROADCAST_STARTED': "<b>📢 Bʀᴏᴀᴅᴄᴀꜱᴛ Mᴇꜱꜱᴀɢᴇ Sᴛᴀʀᴛᴇᴅ...</b>",
    'ERROR':             "❌ Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.",
    'TIMEOUT': (
        "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ!\n\n"
        "Yᴏᴜ ᴛᴏᴏᴋ ᴛᴏᴏ ʟᴏɴɢ ᴛᴏ ʀᴇsᴘᴏɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>"
    ),
    'TASK_CANCELLED':    "<b>✋ Tᴀsᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>",
}

chat_ids = ["-1002213447148", "-1002244057599", "-1002151372918", "-1001657350576", "-1001623282553"]


# ==================== UTILITY FUNCTIONS ====================

async def is_check_admin(query, ADMINS):
    """Check if user is admin; show alert if not."""
    if query.from_user.id not in ADMINS:
        await query.answer("Oɴʟʏ Fᴏʀ Mʏ Aᴅᴍɪɴꜱ", show_alert=True)
        return False
    return True


async def safe_delete(msg):
    """Silently delete a message, ignoring any errors."""
    if msg:
        try:
            await msg.delete()
        except Exception:
            pass


def get_channel_link(chat, ch_id: int) -> str:
    """Return an HTML hyperlink for a channel."""
    title = chat.title or "Unknown"
    link = f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{str(ch_id)[4:]}/1"
    return f"<a href='{link}'>{title}</a> [<code>{ch_id}</code>]"


# ==================== KEYBOARD BUILDERS ====================

def build_main_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ", callback_data="verification_mode")],
        [
            InlineKeyboardButton("ʙᴏᴛ sᴇᴛᴛɪɴɢs", callback_data="group_settings"),
            InlineKeyboardButton("ғsᴜʙ ᴍᴏᴅᴇ", callback_data="fsub_management"),
        ],
        [
            InlineKeyboardButton("ʀᴇsᴇᴛ ᴀʟʟ", callback_data="reset_all"),
            InlineKeyboardButton("ᴠɪᴇᴡ sᴇᴛᴛɪɴɢs", callback_data="view_settings"),
        ],
        [
            InlineKeyboardButton("📤 ᴇxᴘᴏʀᴛ", callback_data="export_settings"),
            InlineKeyboardButton("📥 ɪᴍᴘᴏʀᴛ", callback_data="import_settings"),
        ],
        [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_data")],
    ])


def build_verification_keyboard(verify_status: bool) -> InlineKeyboardMarkup:
    verify_btn = BUTTON_TEXT['VERIFICATION_ON'] if verify_status else BUTTON_TEXT['VERIFICATION_OFF']
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(verify_btn, callback_data="toggle_verification")],
        [
            InlineKeyboardButton("ꜱʜᴏʀᴛɴᴇʀ", callback_data="edit_shortner"),
            InlineKeyboardButton("ᴛɪᴍᴇ", callback_data="edit_time"),
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="back_to_main")],
    ])


def build_group_settings_keyboard(grp_search: bool, file_delete: bool) -> InlineKeyboardMarkup:
    grp_btn = BUTTON_TEXT['GROUP_SEARCH_ENABLED'] if grp_search else BUTTON_TEXT['GROUP_SEARCH_DISABLED']
    file_delete_btn = BUTTON_TEXT['FILE_DELETE_ENABLED'] if file_delete else BUTTON_TEXT['FILE_DELETE_DISABLED']
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(grp_btn, callback_data="toggle_search")],
        [
            InlineKeyboardButton("ʀᴇsᴜʟᴛ ᴘᴀɢᴇ", callback_data="edit_mode"),
            InlineKeyboardButton("ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="broadcast_type"),
        ],
        [InlineKeyboardButton(file_delete_btn, callback_data="toggle_file_delete")],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="back_to_main")],
    ])


def build_fsub_management_keyboard(fsub_mode: bool) -> InlineKeyboardMarkup:
    fsub_btn = BUTTON_TEXT['FSUB_MODE_ON'] if fsub_mode else BUTTON_TEXT['FSUB_MODE_OFF']
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(fsub_btn, callback_data="toggle_fsub_mode")],
        [
            InlineKeyboardButton("ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", callback_data="add_fsub_channel"),
            InlineKeyboardButton("ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ", callback_data="remove_fsub_channel"),
        ],
        [
            InlineKeyboardButton("ʟɪsᴛ ᴄʜᴀɴɴᴇʟs", callback_data="list_fsub_channels"),
            InlineKeyboardButton("ᴄʟᴇᴀʀ ᴀʟʟ", callback_data="clear_all_fsub"),
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="back_to_main")],
    ])


def build_add_fsub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴀᴅᴅ ɴᴏʀᴍᴀʟ ғsᴜʙ", callback_data="add_normal_fsub"),
            InlineKeyboardButton("ᴀᴅᴅ ʀᴇǫ ғsᴜʙ", callback_data="add_req_fsub"),
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="fsub_management")],
    ])


def build_shortner_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1ꜱᴛ sʜᴏʀᴛɴᴇʀ", callback_data="edit_shortner1"),
            InlineKeyboardButton("2ɴᴅ sʜᴏʀᴛɴᴇʀ", callback_data="edit_shortner2"),
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="verification_mode")],
    ])


def build_broadcast_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 ᴍᴀɴᴜᴀʟ", callback_data="manual_broadcast"),
            InlineKeyboardButton("🤖 ᴀᴜᴛᴏ", callback_data="auto_broadcast"),
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="group_settings")],
    ])


def build_back_button_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data=callback_data)],
    ])


def build_confirm_cancel_keyboard(confirm_data: str, cancel_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(BUTTON_TEXT['CONFIRM'], callback_data=confirm_data),
            InlineKeyboardButton(BUTTON_TEXT['CANCEL'], callback_data=cancel_data),
        ]
    ])


# ==================== DISPLAY FORMATTER ====================

def format_settings_display(settings: dict) -> str:
    def status(key, default=False):
        return "✓ <b>ᴇɴᴀʙʟᴇᴅ</b>" if settings.get(key, default) else "✗ <b>ᴅɪsᴀʙʟᴇᴅ</b>"

    file_mode = settings.get("file_mode", False)
    file_status = "🧩 <b>ʙᴜᴛᴛᴏɴs</b>" if file_mode else "🔗 <b>ʟɪɴᴋs</b>"
    auth_channels = settings.get("auth_channels", [])
    auth_req_channels = settings.get("auth_req_channels", [])
    auth_count = len(auth_channels) if isinstance(auth_channels, list) else 0
    req_count = len(auth_req_channels) if isinstance(auth_req_channels, list) else 0

    return (
        "<b>⚙️ ɢʟᴏʙᴀʟ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔐 <b>ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ :</b> {status('verification', True)}\n"
        f"👥 <b>ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ :</b> {status('group_search')}\n"
        f"🔒 <b>ғᴏʀᴄᴇ sᴜʙ :</b> {status('fsub_mode', True)}\n"
        f"📢 <b>ғsᴜʙ ᴄʜᴀɴɴᴇʟs :</b> <b>{auth_count} ɴᴏʀᴍᴀʟ, {req_count} ʀᴇǫᴜᴇsᴛ</b>\n"
        f"🗃️ <b>ʀᴇsᴜʟᴛ ᴍᴏᴅᴇ :</b> {file_status}\n"
        f"🗑️ <b>ғɪʟᴇ ᴅᴇʟᴇᴛᴇ :</b> {status('file_delete')}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>🔗 sʜᴏʀᴛɴᴇʀ #1</b>\n"
        f"• 🌐 ᴅᴏᴍᴀɪɴ : <code>{settings.get('shortner_one', 'Nᴏᴛ Sᴇᴛ')}</code>\n"
        f"• 🔑 ᴀᴘɪ : <code>{settings.get('api_one', 'Nᴏᴛ Sᴇᴛ')}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>🔗 sʜᴏʀᴛɴᴇʀ #2</b>\n"
        f"• 🌐 ᴅᴏᴍᴀɪɴ : <code>{settings.get('shortner_two', 'Nᴏᴛ Sᴇᴛ')}</code>\n"
        f"• 🔑 ᴀᴘɪ : <code>{settings.get('api_two', 'Nᴏᴛ Sᴇᴛ')}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ <b>ᴠᴇʀɪғʏ ᴛɪᴍᴇ :</b> <code>{settings.get('third_verify_time', 'Nᴏᴛ Sᴇᴛ')}</code> <i>seconds</i>\n"
        "━━━━━━━━━━━━━━━━━━"
    )


# ==================== SHARED BROADCAST ENGINE ====================

async def _execute_broadcast(client, db, chat_ids, *, from_chat_id=None, msg_id=None, use_script=False):
    """
    Shared broadcast engine for manual and auto modes.
      use_script=True  -> sends script.HELP_INFO via send_message
      use_script=False -> copies the message at (from_chat_id, msg_id)
    Returns (success, failed, pinned).
    """
    success = failed = pinned = 0
    for chat_id in map(int, chat_ids):
        try:
            last_id = await db.get_last_broadcast(chat_id)
            if last_id:
                try:
                    await client.delete_messages(chat_id, last_id)
                except Exception:
                    pass

            if use_script:
                sent = await client.send_message(chat_id, script.HELP_INFO)
            else:
                sent = await client.copy_message(
                    chat_id=chat_id,
                    from_chat_id=from_chat_id,
                    message_id=msg_id,
                )

            await db.set_last_broadcast(chat_id, sent.id)
            success += 1

            try:
                pin_service_msg = await client.pin_chat_message(
                    chat_id=chat_id,
                    message_id=sent.id,
                    disable_notification=True,
                )
                pinned += 1
                if pin_service_msg and pin_service_msg.id:
                    try:
                        await client.delete_messages(chat_id, pin_service_msg.id)
                    except Exception as sm_err:
                        logger.warning(f"Service msg delete failed for {chat_id}: {sm_err}")
            except Exception as pin_err:
                logger.warning(f"Pin failed for {chat_id}: {pin_err}")

        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed for {chat_id}: {e}")

    return success, failed, pinned


# ==================== SHARED FSUB ADD ENGINE ====================

async def _add_fsub_common(query, db, client, db_key: str, existing_ids: list, label: str):
    """
    Shared logic for adding normal or request fsub channels.
      db_key       : 'auth_channels' or 'auth_req_channels'
      existing_ids : current list of channel IDs from db
      label        : 'normal' or 'request' (for logging)
    """
    msg = None
    user_id = query.from_user.id
    type_label = "Nᴏʀᴍᴀʟ" if db_key == "auth_channels" else "Rᴇǫᴜᴇsᴛ"

    try:
        await query.message.edit(
            f"<b>🔧 Sᴇɴᴅ {type_label} Fsᴜʙ Cʜᴀɴɴᴇʟ IDs\n\n"
            "Fᴏʀᴍᴀᴛ: <code>-100xxxx -100yyyy</code>\n"
            "Yᴏᴜ ᴄᴀɴ sᴇɴᴅ ᴍᴜʟᴛɪᴘʟᴇ IDs sᴘᴀᴄᴇ sᴇᴘᴀʀᴀᴛᴇᴅ\n\n"
            "<blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )

        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60,
        )

        if msg.text and msg.text.strip().lower() == "/cancel":
            await safe_delete(msg)
            await query.message.edit(
                f"{MESSAGES['TASK_CANCELLED']}\n\nNᴏ ᴄʜᴀɴɴᴇʟs ᴡᴇʀᴇ ᴀᴅᴅᴇᴅ.",
                reply_markup=build_back_button_keyboard("add_fsub_channel"),
            )
            return

        if not msg.text:
            await safe_delete(msg)
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀꜱᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ IDs.</b>",
                reply_markup=build_back_button_keyboard("add_fsub_channel"),
            )
            return

        added = []
        added_details = []
        skipped = []
        invalid = []
        not_admin = []

        for ch in msg.text.split():
            if not (ch.startswith("-100") and ch.lstrip("-").isdigit()):
                invalid.append(ch)
                continue
            ch_id = int(ch)
            if ch_id in existing_ids:
                skipped.append(ch_id)
                continue
            try:
                chat = await client.get_chat(ch_id)
                try:
                    bot_member = await client.get_chat_member(ch_id, "me")
                    if bot_member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                        not_admin.append(f"{chat.title or 'Unknown'} (<code>{ch_id}</code>)")
                        continue
                except Exception as admin_err:
                    logger.error(f"Admin check failed for {ch_id}: {admin_err}")
                    not_admin.append(f"<code>{ch_id}</code>")
                    continue
                existing_ids.append(ch_id)
                added.append(ch_id)
                added_details.append(f"• {get_channel_link(chat, ch_id)}")
            except Exception as e:
                logger.warning(f"Could not fetch info for channel {ch_id}: {e}")
                invalid.append(str(ch_id))

        await safe_delete(msg)

        result_parts = []
        if added:
            await db.set_setting(db_key, existing_ids)
            result_parts.append(
                f"<b>✅ Sᴜᴄᴄᴇssғᴜʟʟʏ Aᴅᴅᴇᴅ ({len(added)}):</b>\n" + "\n".join(added_details)
            )
        if not_admin:
            result_parts.append(
                f"\n\n<b>🚫 Bᴏᴛ Nᴏᴛ Aᴅᴍɪɴ ({len(not_admin)}):</b>\n"
                + "\n".join([f"• {ch}" for ch in not_admin])
                + "\n\n<i>Mᴀᴋᴇ ʙᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇsᴇ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!</i>"
            )
        if invalid:
            result_parts.append(
                f"\n\n<b>❌ Iɴᴠᴀʟɪᴅ/Nᴏᴛ Fᴏᴜɴᴅ ({len(invalid)}):</b>\n"
                + "\n".join([f"• <code>{ch}</code>" for ch in invalid])
            )
        if skipped:
            result_parts.append(
                f"\n\n<b>⚠️ Aʟʀᴇᴀᴅʏ Exɪsᴛs ({len(skipped)}):</b>\n"
                + "\n".join([f"• <code>{ch}</code>" for ch in skipped])
            )

        if not result_parts:
            await query.message.edit(
                "<b>⚠️ Nᴏ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ IDs ᴘʀᴏᴠɪᴅᴇᴅ!</b>",
                reply_markup=build_back_button_keyboard("add_fsub_channel"),
            )
            return

        await query.message.edit(
            "\n".join(result_parts),
            reply_markup=build_back_button_keyboard("add_fsub_channel"),
        )
        logger.info(f"User {user_id} added {label} fsub: added={added}, not_admin={not_admin}, invalid={invalid}")

    except ListenerTimeout:
        await query.message.edit(MESSAGES['TIMEOUT'], reply_markup=build_back_button_keyboard("add_fsub_channel"))
    except Exception as e:
        logger.error(f"Error in _add_fsub_common ({label}): {e}", exc_info=True)
        await safe_delete(msg)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("add_fsub_channel"))
        except Exception:
            pass


# ==================== COMMAND HANDLER ====================

@Client.on_message(filters.command("custom_settings") & filters.user(ADMINS))
async def settings(client, message):
    await message.reply_text(
        MESSAGES['MAIN_SETTINGS'],
        reply_markup=build_main_settings_keyboard(),
        quote=True,
    )


# ==================== CALLBACK HANDLERS ====================

async def handle_back_to_main(query, db, **kwargs):
    """Return to main settings menu."""
    try:
        await query.message.edit(MESSAGES['MAIN_SETTINGS'], reply_markup=build_main_settings_keyboard())
        logger.info(f"User {query.from_user.id} returned to main settings")
    except Exception as e:
        logger.error(f"Error in back_to_main: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass


async def handle_verification_mode(query, db, **kwargs):
    """Display verification mode settings."""
    try:
        s = await db.get_all_settings()
        await query.message.edit(
            MESSAGES['VERIFICATION_MODE'],
            reply_markup=build_verification_keyboard(s.get("verification", True)),
        )
        logger.info(f"User {query.from_user.id} opened verification mode")
    except Exception as e:
        logger.error(f"Error in verification_mode: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass


async def handle_group_settings(query, db, **kwargs):
    """Display group settings."""
    try:
        s = await db.get_all_settings()
        await query.message.edit(
            MESSAGES['GROUP_SETTINGS'],
            reply_markup=build_group_settings_keyboard(s.get("group_search", False), s.get("file_delete", False)),
        )
        logger.info(f"User {query.from_user.id} opened group settings")
    except Exception as e:
        logger.error(f"Error in group_settings: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass


async def handle_fsub_management(query, db, **kwargs):
    """Display fsub management menu."""
    try:
        s = await db.get_all_settings()
        await query.message.edit(
            MESSAGES['FSUB_MODE'],
            reply_markup=build_fsub_management_keyboard(s.get("fsub_mode", True)),
        )
        logger.info(f"User {query.from_user.id} opened fsub management")
    except Exception as e:
        logger.error(f"Error in fsub_management: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass


async def handle_toggle_verification(query, db, **kwargs):
    """Toggle verification on/off."""
    try:
        s = await db.get_all_settings()
        new_status = not s.get("verification", True)
        await db.set_setting("verification", new_status)
        await query.message.edit_reply_markup(build_verification_keyboard(new_status))
        await query.answer(BUTTON_TEXT['VERIFICATION_ON'] if new_status else BUTTON_TEXT['VERIFICATION_OFF'])
        logger.info(f"User {query.from_user.id} toggled verification to {new_status}")
    except Exception as e:
        logger.error(f"Error in toggle_verification: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("verification_mode"))
        except Exception:
            pass


async def handle_toggle_fsub_mode(query, db, **kwargs):
    """Toggle fsub mode on/off."""
    try:
        s = await db.get_all_settings()
        new_status = not s.get("fsub_mode", True)
        await db.set_setting("fsub_mode", new_status)
        await query.message.edit_reply_markup(build_fsub_management_keyboard(new_status))
        await query.answer(BUTTON_TEXT['FSUB_MODE_ON'] if new_status else BUTTON_TEXT['FSUB_MODE_OFF'])
        logger.info(f"User {query.from_user.id} toggled fsub_mode to {new_status}")
    except Exception as e:
        logger.error(f"Error in toggle_fsub_mode: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("fsub_management"))
        except Exception:
            pass


async def handle_toggle_search(query, db, **kwargs):
    """Toggle group search on/off."""
    try:
        s = await db.get_all_settings()
        new_status = not s.get("group_search", False)
        await db.set_setting("group_search", new_status)
        await query.message.edit_reply_markup(build_group_settings_keyboard(new_status, s.get("file_delete", False)))
        await query.answer("ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ ᴇɴᴀʙʟᴇᴅ ✅" if new_status else "ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ ᴅɪsᴀʙʟᴇᴅ ❌")
        logger.info(f"User {query.from_user.id} toggled group_search to {new_status}")
    except Exception as e:
        logger.error(f"Error in toggle_search: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("group_settings"))
        except Exception:
            pass


async def handle_toggle_file_delete(query, db, **kwargs):
    """Toggle file delete on/off."""
    try:
        s = await db.get_all_settings()
        new_status = not s.get("file_delete", False)
        await db.set_setting("file_delete", new_status)
        await query.message.edit_reply_markup(build_group_settings_keyboard(s.get("group_search", False), new_status))
        await query.answer(BUTTON_TEXT['FILE_DELETE_ENABLED'] if new_status else BUTTON_TEXT['FILE_DELETE_DISABLED'])
        logger.info(f"User {query.from_user.id} toggled file_delete to {new_status}")
    except Exception as e:
        logger.error(f"Error in toggle_file_delete: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("group_settings"))
        except Exception:
            pass


async def handle_edit_mode(query, db, **kwargs):
    """Toggle file result mode (buttons vs links)."""
    try:
        s = await db.get_all_settings()
        new_status = not s.get("file_mode", False)
        await db.set_setting("file_mode", new_status)
        await query.answer(
            "ᴄʜᴀɴɢᴇ ᴛᴏ ʙᴜᴛᴛᴏɴ ᴍᴏᴅᴇ sᴜᴄᴄᴇssғᴜʟʟʏ" if new_status else "ᴄʜᴀɴɢᴇ ᴛᴏ ᴛᴇxᴛ ʟɪɴᴋ ᴍᴏᴅᴇ sᴜᴄᴄᴇssғᴜʟʟʏ",
            show_alert=True,
        )
        logger.info(f"User {query.from_user.id} toggled file_mode to {new_status}")
    except Exception as e:
        logger.error(f"Error in edit_mode: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("group_settings"))
        except Exception:
            pass


async def handle_add_fsub_channel(query, db, **kwargs):
    """Show add fsub channel type selection."""
    await query.message.edit(MESSAGES['ADD_FSUB_CHANNEL'], reply_markup=build_add_fsub_keyboard())


async def handle_add_normal_fsub(query, db, client, **kwargs):
    """Add normal fsub channels."""
    existing = await db.get_setting("auth_channels", AUTH_CHANNELS)
    if not isinstance(existing, list):
        existing = []
    await _add_fsub_common(query, db, client, "auth_channels", existing, "normal")


async def handle_add_req_fsub(query, db, client, **kwargs):
    """Add request fsub channels."""
    existing = await db.get_setting("auth_req_channels", AUTH_REQ_CHANNELS)
    if not isinstance(existing, list):
        existing = []
    await _add_fsub_common(query, db, client, "auth_req_channels", existing, "request")


async def handle_remove_fsub_channel(query, db, client, **kwargs):
    """Remove a fsub channel by ID."""
    msg = None
    try:
        user_id = query.from_user.id
        await query.message.edit(
            "<b>🗑️ Sᴇɴᴅ Cʜᴀɴɴᴇʟ ID ᴛᴏ Rᴇᴍᴏᴠᴇ\n\n"
            "Fᴏʀᴍᴀᴛ: <code>-100xxxx</code>\n\n"
            "<blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )

        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60,
        )

        if msg.text and msg.text.strip().lower() == "/cancel":
            await safe_delete(msg)
            await query.message.edit(
                f"{MESSAGES['TASK_CANCELLED']}\n\nNᴏ ᴄʜᴀɴɴᴇʟs ᴡᴇʀᴇ ʀᴇᴍᴏᴠᴇᴅ.",
                reply_markup=build_back_button_keyboard("fsub_management"),
            )
            return

        if not msg.text or not msg.text.strip().lstrip("-").isdigit():
            await safe_delete(msg)
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Iɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID.</b>",
                reply_markup=build_back_button_keyboard("fsub_management"),
            )
            return

        ch_id = int(msg.text.strip())
        auth = await db.get_setting("auth_channels", AUTH_CHANNELS)
        req = await db.get_setting("auth_req_channels", AUTH_REQ_CHANNELS)

        channel_info = f"<code>{ch_id}</code>"
        try:
            chat = await client.get_chat(ch_id)
            channel_info = get_channel_link(chat, ch_id)
        except Exception as e:
            logger.warning(f"Could not fetch channel info for {ch_id}: {e}")

        removed_from = []
        if isinstance(auth, list) and ch_id in auth:
            auth.remove(ch_id)
            await db.set_setting("auth_channels", auth)
            removed_from.append("Nᴏʀᴍᴀʟ Fsᴜʙ")
        if isinstance(req, list) and ch_id in req:
            req.remove(ch_id)
            await db.set_setting("auth_req_channels", req)
            removed_from.append("Rᴇǫ Fsᴜʙ")

        await safe_delete(msg)

        if not removed_from:
            await query.message.edit(
                f"<b>⚠️ Cʜᴀɴɴᴇʟ {channel_info} ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴀɴʏ ʟɪsᴛ.</b>",
                reply_markup=build_back_button_keyboard("fsub_management"),
            )
            return

        await query.message.edit(
            f"<b>🗑️ Rᴇᴍᴏᴠᴇᴅ {channel_info}\n\nFʀᴏᴍ: {', '.join(removed_from)}</b>",
            reply_markup=build_back_button_keyboard("fsub_management"),
        )
        logger.info(f"User {user_id} removed fsub channel {ch_id}")

    except ListenerTimeout:
        await query.message.edit(MESSAGES['TIMEOUT'], reply_markup=build_back_button_keyboard("fsub_management"))
    except Exception as e:
        logger.error(f"Error in handle_remove_fsub_channel: {e}", exc_info=True)
        await safe_delete(msg)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("fsub_management"))
        except Exception:
            pass


async def handle_list_fsub_channels(query, db, client, **kwargs):
    """List all fsub channels with titles."""
    try:
        auth_channels = await db.get_setting("auth_channels", AUTH_CHANNELS)
        auth_req_channels = await db.get_setting("auth_req_channels", AUTH_REQ_CHANNELS)

        async def format_channel_list(channel_ids):
            if not channel_ids:
                return "Nᴏɴᴇ"
            lines = []
            for ch_id in channel_ids:
                try:
                    chat = await client.get_chat(ch_id)
                    lines.append(f"• {get_channel_link(chat, ch_id)}")
                except Exception as e:
                    logger.warning(f"Could not fetch info for channel {ch_id}: {e}")
                    lines.append(f"• <code>{ch_id}</code>")
            return "\n".join(lines)

        auth_list = await format_channel_list(auth_channels)
        req_list = await format_channel_list(auth_req_channels)

        await query.message.edit(
            "<b>📜 Fsᴜʙ Cʜᴀɴɴᴇʟs Lɪsᴛ</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>📢 Nᴏʀᴍᴀʟ Fsᴜʙ Cʜᴀɴɴᴇʟs:</b>\n{auth_list}\n\n"
            f"<b>🔔 Rᴇǫᴜᴇsᴛ Fsᴜʙ Cʜᴀɴɴᴇʟs:</b>\n{req_list}",
            reply_markup=build_back_button_keyboard("fsub_management"),
        )
    except Exception as e:
        logger.error(f"Error in list_fsub_channels: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("fsub_management"))
        except Exception:
            pass


async def handle_clear_all_fsub(query, db, **kwargs):
    """Show clear all fsub confirmation."""
    await query.message.edit(
        "<b>⚠️ Aʀᴇ Yᴏᴜ Sᴜʀᴇ?\n\n"
        "Tʜɪs ᴡɪʟʟ ʀᴇᴍᴏᴠᴇ <u>ᴀʟʟ</u> ғsᴜʙ ᴄʜᴀɴɴᴇʟs (ʙᴏᴛʜ ɴᴏʀᴍᴀʟ ᴀɴᴅ ʀᴇǫᴜᴇsᴛ).</b>",
        reply_markup=build_confirm_cancel_keyboard("confirm_clear_fsub", "fsub_management"),
    )


async def handle_confirm_clear_fsub(query, db, **kwargs):
    """Execute clear all fsub channels."""
    try:
        await db.set_setting("auth_channels", [])
        await db.set_setting("auth_req_channels", [])
        await query.message.edit(
            "<b>🗑️ Aʟʟ Fsᴜʙ Cʜᴀɴɴᴇʟs Cʟᴇᴀʀᴇᴅ!</b>",
            reply_markup=build_back_button_keyboard("fsub_management"),
        )
        logger.info(f"User {query.from_user.id} cleared all fsub channels")
    except Exception as e:
        logger.error(f"Error clearing fsub channels: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("fsub_management"))
        except Exception:
            pass


async def handle_view_settings(query, db, **kwargs):
    """Display all current settings."""
    try:
        s = await db.get_all_settings()
        if not s:
            await query.message.edit(
                "<b>⚠️ Nᴏ Sᴇᴛᴛɪɴɢs Fᴏᴜɴᴅ!</b>",
                reply_markup=build_back_button_keyboard("back_to_main"),
            )
            return
        await query.message.edit(format_settings_display(s), reply_markup=build_back_button_keyboard("back_to_main"))
    except Exception as e:
        logger.error(f"Error in view_settings: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass


async def handle_reset_all(query, db, **kwargs):
    """Show reset confirmation."""
    await query.message.edit(
        "<b>⚠️ Aʀᴇ Yᴏᴜ Sᴜʀᴇ Yᴏᴜ Wᴀɴᴛ Tᴏ Rᴇsᴇᴛ Aʟʟ Sᴇᴛᴛɪɴɢs?</b>",
        reply_markup=build_confirm_cancel_keyboard("confirm_reset_all", "back_to_main"),
    )


async def handle_confirm_reset_all(query, db, **kwargs):
    """Execute settings reset."""
    try:
        await db.reset_all_settings()
        await query.message.edit(
            "<b>✅ Aʟʟ Sᴇᴛᴛɪɴɢs Hᴀᴠᴇ Bᴇᴇɴ Rᴇsᴇᴛ!</b>",
            reply_markup=build_back_button_keyboard("back_to_main"),
        )
        logger.info(f"User {query.from_user.id} reset all settings")
    except Exception as e:
        logger.error(f"Error resetting settings: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass


async def handle_edit_shortner(query, db, **kwargs):
    """Show shortner selection menu."""
    await query.message.edit(MESSAGES['CHOOSE_SHORTNER'], reply_markup=build_shortner_menu_keyboard())


async def handle_edit_shortner1(query, db, client, **kwargs):
    """Edit first shortner."""
    await _edit_shortner_common(query, db, client, "shortner_one", "api_one", "1ꜱᴛ")


async def handle_edit_shortner2(query, db, client, **kwargs):
    """Edit second shortner."""
    await _edit_shortner_common(query, db, client, "shortner_two", "api_two", "2ɴᴅ")


async def _edit_shortner_common(query, db, client, domain_key: str, api_key_key: str, label: str):
    """Generic shortner edit handler."""
    msg = None
    try:
        user_id = query.from_user.id
        await query.message.edit(
            f"<b>🔧 Sᴇɴᴅ {label} Sʜᴏʀᴛᴇɴᴇʀ Dᴏᴍᴀɪɴ ᴀɴᴅ Aᴘɪ Kᴇʏ\n\n"
            "Fᴏʀᴍᴀᴛ: <code>domain.com API_KEY</code>\n\n"
            "<blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )

        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60,
        )

        if msg.text and msg.text.strip().lower() == "/cancel":
            await safe_delete(msg)
            await query.message.edit(
                f"{MESSAGES['TASK_CANCELLED']}\n\nSʜᴏʀᴛɴᴇʀ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ ʀᴇᴍᴀɪɴs ᴜɴᴄʜᴀɴɢᴇᴅ.",
                reply_markup=build_back_button_keyboard("edit_shortner"),
            )
            return

        try:
            domain, api_key = msg.text.strip().split(maxsplit=1)
        except ValueError:
            await safe_delete(msg)
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Sᴇɴᴅ ʙᴏᴛʜ Dᴏᴍᴀɪɴ ᴀɴᴅ Aᴘɪ Kᴇʏ ꜱᴘᴀᴄᴇ ꜱᴇᴘᴀʀᴀᴛᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("edit_shortner"),
            )
            return

        await safe_delete(msg)
        await query.message.edit("<b>⏳ Cʜᴇᴄᴋɪɴɢ Sʜᴏʀᴛᴇɴᴇʀ... Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ.</b>")

        try:
            ok, result = await check_shortner(domain, api_key)
        except Exception as e:
            logger.error(f"Shortner check failed: {e}")
            await query.message.edit(
                "<b>❌ Sʜᴏʀᴛᴇɴᴇʀ Cʜᴇᴄᴋ Fᴀɪʟᴇᴅ! Pʟᴇᴀꜱᴇ Tʀʏ Aɢᴀɪɴ.</b>",
                reply_markup=build_back_button_keyboard("edit_shortner"),
            )
            return

        if not ok:
            await query.message.edit(
                f"<b>❌ Sʜᴏʀᴛᴇɴᴇʀ Nᴏᴛ Wᴏʀᴋɪɴɢ.</b>\n\n<b>{result}</b>",
                reply_markup=build_back_button_keyboard("edit_shortner"),
            )
            return

        await db.set_setting(domain_key, domain)
        await db.set_setting(api_key_key, api_key)
        await query.message.edit(
            f"<b>✅ {label} Sʜᴏʀᴛᴇɴᴇʀ Sᴇᴛ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n\n"
            f"<b>🌐 Dᴏᴍᴀɪɴ:</b> <code>{domain}</code>\n"
            f"<b>🔑 Aᴘɪ Kᴇʏ:</b> <code>{api_key}</code>\n\n"
            f"<b>🔗 Tᴇꜱᴛᴇᴅ Lɪɴᴋ:</b>\n<b>{result}</b>",
            disable_web_page_preview=True,
            reply_markup=build_back_button_keyboard("edit_shortner"),
        )
        logger.info(f"User {query.from_user.id} updated {label} shortner")

    except ListenerTimeout:
        await query.message.edit(MESSAGES['TIMEOUT'], reply_markup=build_back_button_keyboard("edit_shortner"))
    except Exception as e:
        logger.error(f"Error in _edit_shortner_common: {e}", exc_info=True)
        await safe_delete(msg)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("edit_shortner"))
        except Exception:
            pass


async def handle_edit_time(query, db, client, **kwargs):
    """Edit verification time gap."""
    msg = None
    try:
        user_id = query.from_user.id
        await query.message.edit(
            "<b>🔧 Sᴇɴᴅ 2ɴᴅ Vᴇʀɪꜰɪᴄᴀᴛɪᴏɴ Tɪᴍᴇ (ɪɴ ɴᴜᴍʙᴇʀs)\n\n"
            "Fᴏʀᴍᴀᴛ: <code>600</code>\n\n"
            "<blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )

        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60,
        )

        if msg.text and msg.text.strip().lower() == "/cancel":
            await safe_delete(msg)
            await query.message.edit(
                f"{MESSAGES['TASK_CANCELLED']}\n\nVᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴛɪᴍᴇ ʀᴇᴍᴀɪɴs ᴜɴᴄʜᴀɴɢᴇᴅ.",
                reply_markup=build_back_button_keyboard("verification_mode"),
            )
            return

        try:
            verification_time = int(msg.text.strip())
            if verification_time <= 0:
                raise ValueError("Must be positive")
        except ValueError:
            await safe_delete(msg)
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴘᴏsɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ.</b>",
                reply_markup=build_back_button_keyboard("verification_mode"),
            )
            return

        await safe_delete(msg)
        await db.set_setting("third_verify_time", verification_time)
        await query.message.edit(
            f"<b>✅ 2ɴᴅ Vᴇʀɪꜰɪᴄᴀᴛɪᴏɴ Tɪᴍᴇ Sᴇᴛ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n\n"
            f"<b>⏰ Tɪᴍᴇ:</b> <code>{verification_time}</code> ꜱᴇᴄᴏɴᴅꜱ",
            reply_markup=build_back_button_keyboard("verification_mode"),
        )
        logger.info(f"User {query.from_user.id} set verification time to {verification_time}")

    except ListenerTimeout:
        await query.message.edit(MESSAGES['TIMEOUT'], reply_markup=build_back_button_keyboard("verification_mode"))
    except Exception as e:
        logger.error(f"Error in handle_edit_time: {e}", exc_info=True)
        await safe_delete(msg)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("verification_mode"))
        except Exception:
            pass


async def handle_broadcast_type(query, db, **kwargs):
    """Show broadcast type selection (manual or auto)."""
    try:
        await query.message.edit(
            "<b>📢 Bʀᴏᴀᴅᴄᴀꜱᴛ Tʏᴘᴇ\n\n"
            "ᴄʜᴏᴏꜱᴇ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴛʏᴘᴇ 👇\n\n"
            "📝 <b>ᴍᴀɴᴜᴀʟ</b> — Sᴇɴᴅ ʏᴏᴜʀ ᴏᴡɴ ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇ\n"
            "🤖 <b>ᴀᴜᴛᴏ</b> — Sᴇɴᴅ ᴅᴇꜰᴀᴜʟᴛ ʜᴇʟᴘ ɪɴꜰᴏ ᴍᴇssᴀɢᴇ</b>",
            reply_markup=build_broadcast_type_keyboard(),
        )
    except Exception as e:
        logger.error(f"Error in handle_broadcast_type: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("group_settings"))
        except Exception:
            pass


async def handle_manual_broadcast(query, db, client, **kwargs):
    """Execute manual broadcast with user-provided message."""
    msg = None
    try:
        user_id = query.from_user.id
        await query.message.edit(
            "<b>📝 ᴍᴀɴᴜᴀʟ Bʀᴏᴀᴅᴄᴀꜱᴛ\n\n"
            "Sᴇɴᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴀʟʟ ᴄʜᴀᴛs.\n\n"
            "<b><blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )

        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=120,
        )

        if msg.text and msg.text.strip().lower() == "/cancel":
            await safe_delete(msg)
            await query.message.edit(
                f"{MESSAGES['TASK_CANCELLED']}\n\nNᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴡᴀs sᴇɴᴛ.",
                reply_markup=build_back_button_keyboard("broadcast_type"),
            )
            return

        await query.message.edit(MESSAGES['BROADCAST_STARTED'])
        success, failed, pinned = await _execute_broadcast(
            client, db, chat_ids, from_chat_id=msg.chat.id, msg_id=msg.id
        )
        await safe_delete(msg)
        await query.message.edit(
            f"<b>✅ ᴍᴀɴᴜᴀʟ Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ\n\n"
            f"• Sᴜᴄᴄᴇꜱꜱ: {success}\n• Fᴀɪʟᴇᴅ: {failed}\n• Pɪɴɴᴇᴅ: {pinned}</b>",
            reply_markup=build_back_button_keyboard("broadcast_type"),
        )
        logger.info(f"Manual broadcast: {success} success, {failed} failed, {pinned} pinned")

    except ListenerTimeout:
        await query.message.edit(MESSAGES['TIMEOUT'], reply_markup=build_back_button_keyboard("broadcast_type"))
    except Exception as e:
        logger.error(f"Error in handle_manual_broadcast: {e}", exc_info=True)
        await safe_delete(msg)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("broadcast_type"))
        except Exception:
            pass


async def handle_auto_broadcast(query, db, client, **kwargs):
    """Execute auto broadcast using default HELP_INFO script."""
    try:
        await query.message.edit(MESSAGES['BROADCAST_STARTED'])
        success, failed, pinned = await _execute_broadcast(client, db, chat_ids, use_script=True)
        await query.message.edit(
            f"<b>✅ Aᴜᴛᴏ Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ\n\n"
            f"• Sᴜᴄᴄᴇꜱꜱ: {success}\n• Fᴀɪʟᴇᴅ: {failed}\n• Pɪɴɴᴇᴅ: {pinned}</b>",
            reply_markup=build_back_button_keyboard("broadcast_type"),
        )
        logger.info(f"Auto broadcast: {success} success, {failed} failed, {pinned} pinned")
    except Exception as e:
        logger.error(f"Error in handle_auto_broadcast: {e}", exc_info=True)
        try:
            await query.message.edit(MESSAGES['ERROR'], reply_markup=build_back_button_keyboard("broadcast_type"))
        except Exception:
            pass


async def handle_export_settings(query, db, client, **kwargs):
    """Export all settings as a JSON file."""
    try:
        s = await db.get_all_settings()
        if not s:
            await query.message.edit(
                "<b>⚠️ Nᴏ sᴇᴛᴛɪɴɢs ᴛᴏ ᴇxᴘᴏʀᴛ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main"),
            )
            return

        now_str = datetime.now(pytz.timezone(TIMEZONE)).strftime("%d %B, %Y %I:%M:%S %p")
        export_data = {
            "export_info": {
                "date": now_str,
                "total_settings": len(s),
                "exported_by": query.from_user.id,
                "version": "1.0",
            },
            "settings": s,
        }

        file = BytesIO(json.dumps(export_data, indent=2, ensure_ascii=False).encode("utf-8"))
        file.name = f"settings_backup_{datetime.now(pytz.timezone(TIMEZONE)).strftime('%d_%B_%Y_%I_%M_%S_%p')}.json"

        await query.message.reply_document(
            document=file,
            caption=(
                f"<b>📤 Sᴇᴛᴛɪɴɢs Exᴘᴏʀᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                f"<b>📊 Tᴏᴛᴀʟ Sᴇᴛᴛɪɴɢs:</b> <code>{len(s)}</code>\n"
                f"<b>📅 Exᴘᴏʀᴛ Dᴀᴛᴇ:</b> <code>{now_str}</code>\n\n"
                "<b><blockquote>💡 Usᴇ ᴛʜɪs ғɪʟᴇ ᴛᴏ ʀᴇsᴛᴏʀᴇ sᴇᴛᴛɪɴɢs ʟᴀᴛᴇʀ</blockquote></b>"
            ),
        )
        await query.message.edit(
            "<b>✅ Sᴇᴛᴛɪɴɢs ᴇxᴘᴏʀᴛᴇᴅ!\n\n<i>Cʜᴇᴄᴋ ᴛʜᴇ ғɪʟᴇ ʙᴇʟᴏᴡ 👇</i></b>",
            reply_markup=build_back_button_keyboard("back_to_main"),
        )
        logger.info(f"User {query.from_user.id} exported {len(s)} settings")

    except Exception as e:
        logger.error(f"Error in handle_export_settings: {e}", exc_info=True)
        try:
            await query.message.edit("❌ Exᴘᴏʀᴛ Fᴀɪʟᴇᴅ!", reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass


async def handle_import_settings(query, db, client, **kwargs):
    """Import settings from a JSON file."""
    msg = None
    try:
        user_id = query.from_user.id
        await query.message.edit(
            "<b>📥 Iᴍᴘᴏʀᴛ Sᴇᴛᴛɪɴɢs</b>\n\n"
            "<b>📎 Sᴇɴᴅ ᴛʜᴇ JSON ғɪʟᴇ ᴛᴏ ɪᴍᴘᴏʀᴛ sᴇᴛᴛɪɴɢs</b>\n\n"
            "<b>⚠️ Wᴀʀɴɪɴɢ: Tʜɪs ᴡɪʟʟ ᴏᴠᴇʀᴡʀɪᴛᴇ ᴇxɪsᴛɪɴɢ sᴇᴛᴛɪɴɢs!</b>\n\n"
            "<b><blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )

        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id) & (filters.document | filters.text),
            timeout=120,
        )

        if msg.text and msg.text.strip().lower() == "/cancel":
            await safe_delete(msg)
            await query.message.edit(
                "<b>✋ Iᴍᴘᴏʀᴛ Cᴀɴᴄᴇʟʟᴇᴅ!\n\nYᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs ʀᴇᴍᴀɪɴ ᴜɴᴄʜᴀɴɢᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main"),
            )
            return

        if not msg.document:
            await safe_delete(msg)
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ JSON ғɪʟᴇ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main"),
            )
            return

        if not msg.document.file_name.endswith(".json"):
            await safe_delete(msg)
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Oɴʟʏ JSON ғɪʟᴇs ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main"),
            )
            return

        await query.message.edit("<b>⏳ Pʀᴏᴄᴇssɪɴɢ ғɪʟᴇ...</b>")

        try:
            file_path = await msg.download()
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
            os.remove(file_path)

            if "settings" not in import_data or not import_data["settings"]:
                await safe_delete(msg)
                await query.message.edit(
                    "<b>❌ Iɴᴠᴀʟɪᴅ ᴏʀ ᴇᴍᴘᴛʏ sᴇᴛᴛɪɴɢs ғɪʟᴇ!</b>",
                    reply_markup=build_back_button_keyboard("back_to_main"),
                )
                return

            settings_to_import = import_data["settings"]
            export_date = import_data.get("export_info", {}).get("date", "Unknown")

            global TEMP_IMPORT_DATA
            TEMP_IMPORT_DATA[user_id] = settings_to_import
            await safe_delete(msg)

            await query.message.edit(
                "<b>📥 Cᴏɴғɪʀᴍ Iᴍᴘᴏʀᴛ</b>\n\n"
                f"<b>📊 Sᴇᴛᴛɪɴɢs ᴛᴏ ɪᴍᴘᴏʀᴛ:</b> <code>{len(settings_to_import)}</code>\n"
                f"<b>📅 Exᴘᴏʀᴛᴇᴅ Oɴ:</b> <code>{export_date}</code>\n\n"
                "<b>⚠️ Wᴀʀɴɪɴɢ:</b>\n"
                "<b><blockquote>• Tʜɪs ᴡɪʟʟ ᴏᴠᴇʀᴡʀɪᴛᴇ ᴇxɪsᴛɪɴɢ sᴇᴛᴛɪɴɢs\n"
                "• Mᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴀ ʙᴀᴄᴋᴜᴘ</blockquote></b>\n\n"
                "<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ?</b>",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Cᴏɴғɪʀᴍ Iᴍᴘᴏʀᴛ", callback_data="confirm_import"),
                        InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ", callback_data="back_to_main"),
                    ]
                ]),
            )

        except json.JSONDecodeError:
            await safe_delete(msg)
            await query.message.edit(
                "<b>❌ Iɴᴠᴀʟɪᴅ JSON ғɪʟᴇ! Tʜᴇ ғɪʟᴇ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ᴘᴀʀsᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main"),
            )
        except Exception as e:
            logger.error(f"Error parsing import file: {e}")
            await safe_delete(msg)
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ғɪʟᴇ!</b>",
                reply_markup=build_back_button_keyboard("back_to_main"),
            )

    except ListenerTimeout:
        await query.message.edit(MESSAGES['TIMEOUT'], reply_markup=build_back_button_keyboard("back_to_main"))
    except Exception as e:
        logger.error(f"Error in handle_import_settings: {e}", exc_info=True)
        await safe_delete(msg)
        try:
            await query.message.edit("❌ Iᴍᴘᴏʀᴛ Fᴀɪʟᴇᴅ!", reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass


async def handle_confirm_import(query, db, **kwargs):
    """Handle import confirmation callback."""
    try:
        user_id = query.from_user.id
        global TEMP_IMPORT_DATA

        if user_id not in TEMP_IMPORT_DATA:
            await query.answer("⚠️ Iᴍᴘᴏʀᴛ ᴅᴀᴛᴀ ɴᴏᴛ ғᴏᴜɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", show_alert=True)
            await query.message.edit(
                "<b>❌ Iᴍᴘᴏʀᴛ ғᴀɪʟᴇᴅ — sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main"),
            )
            return

        settings_to_import = TEMP_IMPORT_DATA.pop(user_id)
        await query.message.edit("<b>⏳ Iᴍᴘᴏʀᴛɪɴɢ sᴇᴛᴛɪɴɢs...</b>")

        imported = failed = 0
        for key, value in settings_to_import.items():
            try:
                await db.set_setting(key, value)
                imported += 1
            except Exception as e:
                logger.error(f"Failed to import {key}: {e}")
                failed += 1

        await query.message.edit(
            f"<b>✅ Iᴍᴘᴏʀᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
            f"<b>📊 Rᴇsᴜʟᴛs:</b>\n"
            f"• <b>Sᴜᴄᴄᴇss:</b> <code>{imported}</code>\n"
            f"• <b>Fᴀɪʟᴇᴅ:</b> <code>{failed}</code>",
            reply_markup=build_back_button_keyboard("back_to_main"),
        )
        logger.info(f"User {user_id} imported {imported} settings (failed: {failed})")

    except Exception as e:
        logger.error(f"Error in handle_confirm_import: {e}", exc_info=True)
        try:
            await query.message.edit("❌ Iᴍᴘᴏʀᴛ Fᴀɪʟᴇᴅ!", reply_markup=build_back_button_keyboard("back_to_main"))
        except Exception:
            pass
