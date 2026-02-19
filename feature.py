from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import ListenerTimeout
from datetime import datetime
from pytz import timezone
from info import *
from typing import Callable, Dict, Tuple, Optional
from Script import script
from database.users_chats_db import db
from utils import check_shortner
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

TEMP_IMPORT_DATA = {}

# BUTTON_TEXT constants
BUTTON_TEXT = {
    'VERIFICATION_ON': "🟢 ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴏɴ",
    'VERIFICATION_OFF': "🔴 ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴏꜰꜰ",
    'FSUB_MODE_ON': "🟢 ғsᴜʙ ᴍᴏᴅᴇ ᴏɴ",
    'FSUB_MODE_OFF': "🔴 ғsᴜʙ ᴍᴏᴅᴇ ᴏꜰꜰ",
    'GROUP_SEARCH_ENABLED': "ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ: ᴇɴᴀʙʟᴇᴅ ✅",
    'GROUP_SEARCH_DISABLED': "ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ: ᴅɪsᴀʙʟᴇᴅ ❌",
    'FSUB_ENABLED': "ғᴏʀᴄᴇ sᴜʙ: ᴇɴᴀʙʟᴇᴅ ✅",
    'FSUB_DISABLED': "ғᴏʀᴄᴇ sᴜʙ: ᴅɪsᴀʙʟᴇᴅ ❌",
    'FILE_DELETE_ENABLED': "ғɪʟᴇ ᴅᴇʟᴇᴛᴇ: ᴇɴᴀʙʟᴇᴅ ✅",
    'FILE_DELETE_DISABLED': "ғɪʟᴇ ᴅᴇʟᴇᴛᴇ: ᴅɪsᴀʙʟᴇᴅ ❌",
    'BACK': "⇋ ʙᴀᴄᴋ ⇌",
    'CONFIRM': "✅ Cᴏɴꜰɪʀᴍ",
    'CANCEL': "❌ Cᴀɴᴄᴇʟ"
}

# MESSAGES constants
MESSAGES = {
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
    'MAIN_SETTINGS': "<b>ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ ᴀꜱ ʏᴏᴜ ᴡᴀɴᴛ ⚙:</b>",
    'ERROR': "❌ Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.",
    'CHOOSE_SHORTNER': "<b>ᴄʜᴏᴏꜱᴇ ꜱʜᴏʀᴛɴᴇʀ ᴀɴᴅ ᴄʜᴀɴɢᴇ ᴛʜᴇ ᴠᴀʟᴜᴇꜱ ᴀꜱ ʏᴏᴜ ᴡᴀɴᴛ ✅</b>",
    'PREMIUM_MODE': (
        "<b>👑 ᴘʀᴇᴍɪᴜᴍ ᴍᴏᴅᴇ ⚙\n\n"
        "ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs, ᴀᴅᴅ/ʀᴇᴍᴏᴠᴇ ꜱᴜʙsᴄʀɪᴘᴛɪᴏɴs ꜰʀᴏᴍ ʜᴇʀᴇ ✅\n"
        "ᴄʜᴏᴏꜱᴇ ꜰʀᴏᴍ ʙᴇʟᴏᴡ 👇</b>"
    )
}

@Client.on_message(filters.command("custom_settings") & filters.user(ADMINS))
async def settings(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ", callback_data="verification_mode")],
        [
            InlineKeyboardButton("ʙᴏᴛ sᴇᴛᴛɪɴɢs", callback_data="group_settings"),
            InlineKeyboardButton("ғsᴜʙ ᴍᴏᴅᴇ", callback_data="fsub_management")
        ],
        [InlineKeyboardButton("👑 ᴘʀᴇᴍɪᴜᴍ ᴍᴏᴅᴇ", callback_data="premium_mode")],
        [
            InlineKeyboardButton("ʀᴇsᴇᴛ ᴀʟʟ", callback_data="reset_all"),
            InlineKeyboardButton("ᴠɪᴇᴡ sᴇᴛᴛɪɴɢs", callback_data="view_settings"),
        ],
        [
            InlineKeyboardButton("📤 ᴇxᴘᴏʀᴛ", callback_data="export_settings"),
            InlineKeyboardButton("📥 ɪᴍᴘᴏʀᴛ", callback_data="import_settings")
        ],
        [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_data")]
    ])

    await message.reply_text(
        "<b>ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ ᴀꜱ ʏᴏᴜ ᴡᴀɴᴛ ⚙:</b>",
        reply_markup=keyboard,
        quote=True
    )

# ==================== UTILITY FUNCTIONS ====================

async def is_check_admin(query, ADMINS):
    """Check if user is admin"""
    if query.from_user.id not in ADMINS:
        await query.answer("Oɴʟʏ Fᴏʀ Mʏ Aᴅᴍɪɴꜱ", show_alert=True)
        return False
    return True


# ==================== KEYBOARD BUILDERS ====================

def build_verification_keyboard(verify_status: bool) -> InlineKeyboardMarkup:
    """Build verification mode keyboard"""
    verify_btn = BUTTON_TEXT['VERIFICATION_ON'] if verify_status else BUTTON_TEXT['VERIFICATION_OFF']
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(verify_btn, callback_data="toggle_verification")],
        [
            InlineKeyboardButton("ꜱʜᴏʀᴛɴᴇʀ", callback_data="edit_shortner"),
            InlineKeyboardButton("ᴛɪᴍᴇ", callback_data="edit_time")
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="back_to_main")]
    ])


def build_group_settings_keyboard(grp_search: bool, file_delete: bool) -> InlineKeyboardMarkup:
    """Build group settings keyboard"""
    grp_btn = BUTTON_TEXT['GROUP_SEARCH_ENABLED'] if grp_search else BUTTON_TEXT['GROUP_SEARCH_DISABLED']
    file_delete_btn = BUTTON_TEXT['FILE_DELETE_ENABLED'] if file_delete else BUTTON_TEXT['FILE_DELETE_DISABLED']
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(grp_btn, callback_data="toggle_search")],
        [InlineKeyboardButton("ʀᴇsᴜʟᴛ ᴘᴀɢᴇ", callback_data="edit_mode")],
        [InlineKeyboardButton(file_delete_btn, callback_data="toggle_file_delete")],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="back_to_main")]
    ])


def build_main_settings_keyboard() -> InlineKeyboardMarkup:
    """Build main settings menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ", callback_data="verification_mode")],
        [
            InlineKeyboardButton("ʙᴏᴛ sᴇᴛᴛɪɴɢs", callback_data="group_settings"),
            InlineKeyboardButton("ғsᴜʙ ᴍᴏᴅᴇ", callback_data="fsub_management")
        ],
        [InlineKeyboardButton("👑 ᴘʀᴇᴍɪᴜᴍ ᴍᴏᴅᴇ", callback_data="premium_mode")],
        [
            InlineKeyboardButton("ʀᴇsᴇᴛ ᴀʟʟ", callback_data="reset_all"),
            InlineKeyboardButton("ᴠɪᴇᴡ sᴇᴛᴛɪɴɢs", callback_data="view_settings"),
        ],
        [
            InlineKeyboardButton("📤 ᴇxᴘᴏʀᴛ", callback_data="export_settings"),
            InlineKeyboardButton("📥 ɪᴍᴘᴏʀᴛ", callback_data="import_settings")
        ],
        [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_data")]
    ])


def build_fsub_management_keyboard(fsub_mode: bool) -> InlineKeyboardMarkup:
    """Build fsub management keyboard"""
    fsub_btn = BUTTON_TEXT['FSUB_MODE_ON'] if fsub_mode else BUTTON_TEXT['FSUB_MODE_OFF']
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(fsub_btn, callback_data="toggle_fsub_mode")],
        [
            InlineKeyboardButton("ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", callback_data="add_fsub_channel"),
            InlineKeyboardButton("ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ", callback_data="remove_fsub_channel")
        ],
        [
            InlineKeyboardButton("ʟɪsᴛ ᴄʜᴀɴɴᴇʟs", callback_data="list_fsub_channels"),
            InlineKeyboardButton("ᴄʟᴇᴀʀ ᴀʟʟ", callback_data="clear_all_fsub")
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="back_to_main")]
    ])


def build_add_fsub_keyboard() -> InlineKeyboardMarkup:
    """Build add fsub channel type selection keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴀᴅᴅ ɴᴏʀᴍᴀʟ ғsᴜʙ", callback_data="add_normal_fsub"),
            InlineKeyboardButton("ᴀᴅᴅ ʀᴇǫ ғsᴜʙ", callback_data="add_req_fsub")
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="fsub_management")]
    ])


def build_shortner_menu_keyboard() -> InlineKeyboardMarkup:
    """Build shortner selection menu"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1ꜱᴛ sʜᴏʀᴛɴᴇʀ", callback_data="edit_shortner1"),
            InlineKeyboardButton("2ɴᴅ sʜᴏʀᴛɴᴇʀ", callback_data="edit_shortner2")
        ],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="verification_mode")]
    ])


def build_back_button_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Build simple back button keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data=callback_data)]
    ])


def build_confirm_cancel_keyboard(confirm_data: str, cancel_data: str) -> InlineKeyboardMarkup:
    """Build confirm/cancel keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(BUTTON_TEXT['CONFIRM'], callback_data=confirm_data),
            InlineKeyboardButton(BUTTON_TEXT['CANCEL'], callback_data=cancel_data)
        ]
    ])


def build_premium_mode_keyboard() -> InlineKeyboardMarkup:
    """Build premium mode management keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ", callback_data="pm_add_user"),
            InlineKeyboardButton("➖ ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ", callback_data="pm_remove_user")
        ],
        [InlineKeyboardButton("👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs", callback_data="pm_total_users")],
        [InlineKeyboardButton(BUTTON_TEXT['BACK'], callback_data="back_to_main")]
    ])


def format_settings_display(settings: dict) -> str:
    """Format settings into display text"""
    verification_enabled = settings.get("verification", True)
    verification_status = "✓ <b>ᴇɴᴀʙʟᴇᴅ</b>" if verification_enabled else "<b>✗ ᴅɪsᴀʙʟᴇᴅ</b>"
    
    domain1 = settings.get("shortner_one", "Nᴏᴛ Sᴇᴛ")
    api1 = settings.get("api_one", "Nᴏᴛ Sᴇᴛ")
    domain2 = settings.get("shortner_two", "Nᴏᴛ Sᴇᴛ")
    api2 = settings.get("api_two", "Nᴏᴛ Sᴇᴛ")
    verify_time = settings.get("third_verify_time", "Nᴏᴛ Sᴇᴛ")
    
    file_mode = settings.get("file_mode", False)
    file_status = "🧩 <b>ʙᴜᴛᴛᴏɴs</b>" if file_mode else "🔗 <b>ʟɪɴᴋs</b>"
    
    grp_mode = settings.get("group_search", False)
    grp_status = "✓ <b>ᴇɴᴀʙʟᴇᴅ</b>" if grp_mode else "✗ <b>ᴅɪsᴀʙʟᴇᴅ</b>"
    
    fsub_mode = settings.get("fsub_mode", True)
    fsub_status = "✓ <b>ᴇɴᴀʙʟᴇᴅ</b>" if fsub_mode else "✗ <b>ᴅɪsᴀʙʟᴇᴅ</b>"
    
    file_delete = settings.get("file_delete", False)
    file_delete_status = "✓ <b>ᴇɴᴀʙʟᴇᴅ</b>" if file_delete else "✗ <b>ᴅɪsᴀʙʟᴇᴅ</b>"
    
    # Get FSUB channels count
    auth_channels = settings.get("auth_channels", [])
    auth_req_channels = settings.get("auth_req_channels", [])
    auth_count = len(auth_channels) if isinstance(auth_channels, list) else 0
    req_count = len(auth_req_channels) if isinstance(auth_req_channels, list) else 0
    
    return (
        "<b>⚙️ ɢʟᴏʙᴀʟ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔐 <b>ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ :</b> {verification_status}\n"
        f"👥 <b>ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ :</b> {grp_status}\n"
        f"🔒 <b>ғᴏʀᴄᴇ sᴜʙ :</b> {fsub_status}\n"
        f"📢 <b>ғsᴜʙ ᴄʜᴀɴɴᴇʟs :</b> <b>{auth_count} ɴᴏʀᴍᴀʟ, {req_count} ʀᴇǫᴜᴇsᴛ</b>\n"
        f"🗃️ <b>ʀᴇsᴜʟᴛ ᴍᴏᴅᴇ :</b> {file_status}\n"
        f"🗑️ <b>ғɪʟᴇ ᴅᴇʟᴇᴛᴇ :</b> {file_delete_status}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>🔗 sʜᴏʀᴛɴᴇʀ #1</b>\n"
        f"• 🌐 ᴅᴏᴍᴀɪɴ : <code>{domain1}</code>\n"
        f"• 🔑 ᴀᴘɪ : <code>{api1}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>🔗 sʜᴏʀᴛɴᴇʀ #2</b>\n"
        f"• 🌐 ᴅᴏᴍᴀɪɴ : <code>{domain2}</code>\n"
        f"• 🔑 ᴀᴘɪ : <code>{api2}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ <b>ᴠᴇʀɪғʏ ᴛɪᴍᴇ :</b> <code>{verify_time}</code> <i>seconds</i>\n"
        "━━━━━━━━━━━━━━━━━━"
    )


# ==================== HANDLER FUNCTIONS ====================



async def handle_verification_mode(query, db, **kwargs):
    """Display verification mode settings"""
    try:
        settings = await db.get_all_settings()
        verify = settings.get("verification", True)
        
        await query.message.edit(
            MESSAGES['VERIFICATION_MODE'],
            reply_markup=build_verification_keyboard(verify)
        )
        logger.info(f"User {query.from_user.id} opened verification mode")
    except Exception as e:
        logger.error(f"Error in verification_mode handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_group_settings(query, db, **kwargs):
    """Display group settings"""
    try:
        settings = await db.get_all_settings()
        grp_search = settings.get("group_search", False)
        file_delete = settings.get("file_delete", False)
        
        await query.message.edit(
            MESSAGES['GROUP_SETTINGS'],
            reply_markup=build_group_settings_keyboard(grp_search, file_delete)
        )
        logger.info(f"User {query.from_user.id} opened group settings")
    except Exception as e:
        logger.error(f"Error in group_settings handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_fsub_management(query, db, **kwargs):
    """Display fsub management menu"""
    try:
        settings = await db.get_all_settings()
        fsub_mode = settings.get("fsub_mode", True)
        
        await query.message.edit(
            MESSAGES['FSUB_MODE'],
            reply_markup=build_fsub_management_keyboard(fsub_mode)
        )
        logger.info(f"User {query.from_user.id} opened fsub management")
    except Exception as e:
        logger.error(f"Error in fsub_management handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_toggle_fsub_mode(query, db, **kwargs):
    """Toggle fsub mode on/off"""
    try:
        settings = await db.get_all_settings()
        new_status = not settings.get("fsub_mode", True)
        
        await db.set_setting("fsub_mode", new_status)
        await query.message.edit_reply_markup(
            build_fsub_management_keyboard(new_status)
        )
        
        status_text = BUTTON_TEXT['FSUB_MODE_ON'] if new_status else BUTTON_TEXT['FSUB_MODE_OFF']
        await query.answer(status_text)
        
        logger.info(f"User {query.from_user.id} toggled fsub_mode to {new_status}")
    except Exception as e:
        logger.error(f"Error in toggle_fsub_mode handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("fsub_management")
            )
        except:
            pass


async def handle_add_fsub_channel(query, db, **kwargs):
    """Show add fsub channel type selection"""
    await query.message.edit(
        MESSAGES['ADD_FSUB_CHANNEL'],
        reply_markup=build_add_fsub_keyboard()
    )


async def handle_add_normal_fsub(query, db, client, AUTH_CHANNELS, **kwargs):
    """Add normal fsub channel"""
    msg = None
    try:
        user_id = query.from_user.id
        
        await query.message.edit(
            "<b>🔧 Sᴇɴᴅ Nᴏʀᴍᴀʟ Fsᴜʙ Cʜᴀɴɴᴇʟ IDs\n\n"
            "Fᴏʀᴍᴀᴛ: <code>-100xxxx -100yyyy</code>\n"
            "Yᴏᴜ ᴄᴀɴ sᴇɴᴅ ᴍᴜʟᴛɪᴘʟᴇ IDs sᴘᴀᴄᴇ sᴇᴘᴀʀᴀᴛᴇᴅ\n\n"
            "<blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )
        
        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60
        )
        
        if msg.text and msg.text.strip().lower() == '/cancel':
            await msg.delete()
            await query.message.edit(
                "<b>✋ Tᴀsᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
                "Nᴏ ᴄʜᴀɴɴᴇʟs ᴡᴇʀᴇ ᴀᴅᴅᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("add_fsub_channel")
            )
            return
        
        if not msg.text:
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀꜱᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ IDs.</b>",
                reply_markup=build_back_button_keyboard("add_fsub_channel")
            )
            return
        
        existing = await db.get_setting("auth_channels", AUTH_CHANNELS)
        if type(existing).__name__ != 'list':
            existing = []

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
            
            if ch_id in existing:
                skipped.append(ch_id)
                continue
            
            try:
                # Get channel info
                chat = await client.get_chat(ch_id)
                
                # Check if bot is admin
                try:
                    bot_member = await client.get_chat_member(ch_id, "me")
                    if bot_member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                        not_admin.append(f"{chat.title or 'Unknown'} (<code>{ch_id}</code>)")
                        continue
                except Exception as admin_err:
                    logger.error(f"Admin check failed for {ch_id}: {admin_err}")
                    not_admin.append(f"<code>{ch_id}</code>")
                    continue
                
                # All checks passed - add channel
                existing.append(ch_id)
                added.append(ch_id)
                
                title = chat.title or "Unknown"
                if chat.username:
                    link = f"https://t.me/{chat.username}"
                else:
                    link = f"https://t.me/c/{str(ch_id)[4:]}/1"
                added_details.append(f"• <a href='{link}'>{title}</a> [<code>{ch_id}</code>]")
                
            except Exception as e:
                logger.warning(f"Could not fetch info for channel {ch_id}: {e}")
                invalid.append(str(ch_id))
        
        await msg.delete()
        
        # Build result message
        result_parts = []
        
        if added:
            await db.set_setting("auth_channels", existing)
            result_parts.append(
                f"<b>✅ Sᴜᴄᴄᴇssғᴜʟʟʏ Aᴅᴅᴇᴅ ({len(added)}):</b>\n" + "\n".join(added_details)
            )
        
        if not_admin:
            result_parts.append(
                f"\n\n<b>🚫 Bᴏᴛ Nᴏᴛ Aᴅᴍɪɴ ({len(not_admin)}):</b>\n" + 
                "\n".join([f"• {ch}" for ch in not_admin]) +
                f"\n\n<i>Mᴀᴋᴇ ʙᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇsᴇ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!</i>"
            )
        
        if invalid:
            result_parts.append(
                f"\n\n<b>❌ Iɴᴠᴀʟɪᴅ/Nᴏᴛ Fᴏᴜɴᴅ ({len(invalid)}):</b>\n" + 
                "\n".join([f"• <code>{ch}</code>" for ch in invalid])
            )
        
        if skipped:
            result_parts.append(
                f"\n\n<b>⚠️ Aʟʀᴇᴀᴅʏ Exɪsᴛs ({len(skipped)}):</b>\n" + 
                "\n".join([f"• <code>{ch}</code>" for ch in skipped])
            )
        
        if not result_parts:
            await query.message.edit(
                "<b>⚠️ Nᴏ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ IDs ᴘʀᴏᴠɪᴅᴇᴅ!</b>",
                reply_markup=build_back_button_keyboard("add_fsub_channel")
            )
            return
        
        final_message = "\n".join(result_parts)
        await query.message.edit(
            final_message,
            reply_markup=build_back_button_keyboard("add_fsub_channel")
        )
        
        logger.info(f"User {query.from_user.id} added normal fsub channels: {added}, not_admin: {not_admin}, invalid: {invalid}")
    
    except ListenerTimeout:
        await query.message.edit(
            "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ!\n\n"
            "Yᴏᴜ ᴛᴏᴏᴋ ᴛᴏᴏ ʟᴏɴɢ ᴛᴏ ʀᴇsᴘᴏɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
            reply_markup=build_back_button_keyboard("add_fsub_channel")
        )
    
    except Exception as e:
        logger.error(f"Error in handle_add_normal_fsub: {e}", exc_info=True)
        try:
            if msg:
                await msg.delete()
        except:
            pass
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("add_fsub_channel")
            )
        except:
            pass


async def handle_add_req_fsub(query, db, client, AUTH_REQ_CHANNELS, **kwargs):
    """Add request fsub channel"""
    msg = None
    try:
        user_id = query.from_user.id
        
        await query.message.edit(
            "<b>🔧 Sᴇɴᴅ Rᴇǫᴜᴇsᴛ Fsᴜʙ Cʜᴀɴɴᴇʟ IDs\n\n"
            "Fᴏʀᴍᴀᴛ: <code>-100xxxx -100yyyy</code>\n"
            "Yᴏᴜ ᴄᴀɴ sᴇɴᴅ ᴍᴜʟᴛɪᴘʟᴇ IDs sᴘᴀᴄᴇ sᴇᴘᴀʀᴀᴛᴇᴅ\n\n"
            "<blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )
        
        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60
        )
        
        if msg.text and msg.text.strip().lower() == '/cancel':
            await msg.delete()
            await query.message.edit(
                "<b>✋ Tᴀsᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
                "Nᴏ ᴄʜᴀɴɴᴇʟs ᴡᴇʀᴇ ᴀᴅᴅᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("add_fsub_channel")
            )
            return
        
        if not msg.text:
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀꜱᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ IDs.</b>",
                reply_markup=build_back_button_keyboard("add_fsub_channel")
            )
            return
        
        existing = await db.get_setting("auth_req_channels", AUTH_REQ_CHANNELS)
        if type(existing).__name__ != 'list':
            existing = []

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
            
            if ch_id in existing:
                skipped.append(ch_id)
                continue
            
            try:
                # Get channel info
                chat = await client.get_chat(ch_id)
                
                # Check if bot is admin
                try:
                    bot_member = await client.get_chat_member(ch_id, "me")
                    if bot_member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                        not_admin.append(f"{chat.title or 'Unknown'} (<code>{ch_id}</code>)")
                        continue
                except Exception as admin_err:
                    logger.error(f"Admin check failed for {ch_id}: {admin_err}")
                    not_admin.append(f"<code>{ch_id}</code>")
                    continue
                
                # All checks passed - add channel
                existing.append(ch_id)
                added.append(ch_id)
                
                title = chat.title or "Unknown"
                if chat.username:
                    link = f"https://t.me/{chat.username}"
                else:
                    link = f"https://t.me/c/{str(ch_id)[4:]}/1"
                added_details.append(f"• <a href='{link}'>{title}</a> [<code>{ch_id}</code>]")
                
            except Exception as e:
                logger.warning(f"Could not fetch info for channel {ch_id}: {e}")
                invalid.append(str(ch_id))
        
        await msg.delete()
        
        # Build result message
        result_parts = []
        
        if added:
            await db.set_setting("auth_req_channels", existing)
            result_parts.append(
                f"<b>✅ Sᴜᴄᴄᴇssғᴜʟʟʏ Aᴅᴅᴇᴅ ({len(added)}):</b>\n" + "\n".join(added_details)
            )
        
        if not_admin:
            result_parts.append(
                f"\n\n<b>🚫 Bᴏᴛ Nᴏᴛ Aᴅᴍɪɴ ({len(not_admin)}):</b>\n" + 
                "\n".join([f"• {ch}" for ch in not_admin]) +
                f"\n\n<i>Mᴀᴋᴇ ʙᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇsᴇ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!</i>"
            )
        
        if invalid:
            result_parts.append(
                f"\n\n<b>❌ Iɴᴠᴀʟɪᴅ/Nᴏᴛ Fᴏᴜɴᴅ ({len(invalid)}):</b>\n" + 
                "\n".join([f"• <code>{ch}</code>" for ch in invalid])
            )
        
        if skipped:
            result_parts.append(
                f"\n\n<b>⚠️ Aʟʀᴇᴀᴅʏ Exɪsᴛs ({len(skipped)}):</b>\n" + 
                "\n".join([f"• <code>{ch}</code>" for ch in skipped])
            )
        
        if not result_parts:
            await query.message.edit(
                "<b>⚠️ Nᴏ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ IDs ᴘʀᴏᴠɪᴅᴇᴅ!</b>",
                reply_markup=build_back_button_keyboard("add_fsub_channel")
            )
            return
        
        final_message = "\n".join(result_parts)
        await query.message.edit(
            final_message,
            reply_markup=build_back_button_keyboard("add_fsub_channel")
        )
        
        logger.info(f"User {query.from_user.id} added req fsub channels: {added}, not_admin: {not_admin}, invalid: {invalid}")
    
    except ListenerTimeout:
        await query.message.edit(
            "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ!\n\n"
            "Yᴏᴜ ᴛᴏᴏᴋ ᴛᴏᴏ ʟᴏɴɢ ᴛᴏ ʀᴇsᴘᴏɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
            reply_markup=build_back_button_keyboard("add_fsub_channel")
        )
    
    except Exception as e:
        logger.error(f"Error in handle_add_req_fsub: {e}", exc_info=True)
        try:
            if msg:
                await msg.delete()
        except:
            pass
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("add_fsub_channel")
            )
        except:
            pass


async def handle_remove_fsub_channel(query, db, client, AUTH_CHANNELS, AUTH_REQ_CHANNELS, **kwargs):
    """Remove fsub channel"""
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
            timeout=60
        )
        
        if msg.text and msg.text.strip().lower() == '/cancel':
            await msg.delete()
            await query.message.edit(
                "<b>✋ Tᴀsᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
                "Nᴏ ᴄʜᴀɴɴᴇʟs ᴡᴇʀᴇ ʀᴇᴍᴏᴠᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("fsub_management")
            )
            return
        
        if not msg.text or not msg.text.strip().lstrip("-").isdigit():
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Iɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID.</b>",
                reply_markup=build_back_button_keyboard("fsub_management")
            )
            return
        
        ch_id = int(msg.text.strip())
        auth = await db.get_setting("auth_channels", AUTH_CHANNELS)
        req = await db.get_setting("auth_req_channels", AUTH_REQ_CHANNELS)
        
        # Get channel info once before removing
        channel_info = None
        try:
            chat = await client.get_chat(ch_id)
            title = chat.title or "Unknown"
            if chat.username:
                link = f"https://t.me/{chat.username}"
            else:
                link = f"https://t.me/c/{str(ch_id)[4:]}/1"
            channel_info = f"<a href='{link}'>{title}</a> [<code>{ch_id}</code>]"
        except Exception as e:
            logger.warning(f"Could not fetch info for channel {ch_id}: {e}")
            channel_info = f"<code>{ch_id}</code>"
        
        removed_from = []
        if isinstance(auth, list) and ch_id in auth:
            auth.remove(ch_id)
            await db.set_setting("auth_channels", auth)
            removed_from.append("Nᴏʀᴍᴀʟ Fsᴜʙ")
        
        if isinstance(req, list) and ch_id in req:
            req.remove(ch_id)
            await db.set_setting("auth_req_channels", req)
            removed_from.append("Rᴇǫ Fsᴜʙ")
        
        await msg.delete()
        
        if not removed_from:
            await query.message.edit(
                f"<b>⚠️ Cʜᴀɴɴᴇʟ {channel_info} ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴀɴʏ ʟɪsᴛ.</b>",
                reply_markup=build_back_button_keyboard("fsub_management")
            )
            return
        
        await query.message.edit(
            f"<b>🗑️ Rᴇᴍᴏᴠᴇᴅ {channel_info}\n\n"
            f"Fʀᴏᴍ: {', '.join(removed_from)}</b>",
            reply_markup=build_back_button_keyboard("fsub_management")
        )
        
        logger.info(f"User {query.from_user.id} removed fsub channel {ch_id}")
    
    except ListenerTimeout:
        await query.message.edit(
            "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ!\n\n"
            "Yᴏᴜ ᴛᴏᴏᴋ ᴛᴏᴏ ʟᴏɴɢ ᴛᴏ ʀᴇsᴘᴏɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
            reply_markup=build_back_button_keyboard("fsub_management")
        )
    
    except Exception as e:
        logger.error(f"Error in handle_remove_fsub_channel: {e}", exc_info=True)
        try:
            if msg:
                await msg.delete()
        except:
            pass
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("fsub_management")
            )
        except:
            pass


async def handle_list_fsub_channels(query, db, client, AUTH_CHANNELS, AUTH_REQ_CHANNELS, **kwargs):
    """List all fsub channels with titles"""
    try:
        auth_channels = await db.get_setting("auth_channels", AUTH_CHANNELS)
        auth_req_channels = await db.get_setting("auth_req_channels", AUTH_REQ_CHANNELS)
        
        async def format_channel_list(channel_ids):
            if not channel_ids:
                return "Nᴏɴᴇ"
            
            formatted_list = []
            for ch_id in channel_ids:
                try:
                    chat = await client.get_chat(ch_id)
                    title = chat.title or "Unknown"
                    if chat.username:
                        link = f"https://t.me/{chat.username}"
                    else:
                        link = f"https://t.me/c/{str(ch_id)[4:]}/1"
                    formatted_list.append(f"• <a href='{link}'>{title}</a> [<code>{ch_id}</code>]")
                except Exception as e:
                    logger.warning(f"Could not fetch info for channel {ch_id}: {e}")
                    formatted_list.append(f"• <code>{ch_id}</code>")
            
            return "\n".join(formatted_list)
        
        auth_list = await format_channel_list(auth_channels)
        req_list = await format_channel_list(auth_req_channels)
        
        text = (
            "<b>📜 Fsᴜʙ Cʜᴀɴɴᴇʟs Lɪsᴛ</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>📢 Nᴏʀᴍᴀʟ Fsᴜʙ Cʜᴀɴɴᴇʟs:\n{auth_list}</b>\n\n"
            f"<b>🔔 Rᴇǫᴜᴇsᴛ Fsᴜʙ Cʜᴀɴɴᴇʟs:\n{req_list}</b>"
        )
        
        await query.message.edit(
            text,
            reply_markup=build_back_button_keyboard("fsub_management")
        )
    except Exception as e:
        logger.error(f"Error in list_fsub_channels handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("fsub_management")
            )
        except:
            pass


async def handle_clear_all_fsub(query, db, **kwargs):
    """Show clear all fsub confirmation"""
    await query.message.edit(
        "<b>⚠️ Aʀᴇ Yᴏᴜ Sᴜʀᴇ?\n\n"
        "Tʜɪs ᴡɪʟʟ ʀᴇᴍᴏᴠᴇ <u>ᴀʟʟ</u> ғsᴜʙ ᴄʜᴀɴɴᴇʟs (ʙᴏᴛʜ ɴᴏʀᴍᴀʟ ᴀɴᴅ ʀᴇǫᴜᴇsᴛ).</b>",
        reply_markup=build_confirm_cancel_keyboard("confirm_clear_fsub", "fsub_management")
    )


async def handle_confirm_clear_fsub(query, db, **kwargs):
    """Execute clear all fsub channels"""
    try:
        await db.set_setting("auth_channels", [])
        await db.set_setting("auth_req_channels", [])
        
        await query.message.edit(
            "<b>🗑️ Aʟʟ Fsᴜʙ Cʜᴀɴɴᴇʟs Cʟᴇᴀʀᴇᴅ!</b>",
            reply_markup=build_back_button_keyboard("fsub_management")
        )
        
        logger.info(f"User {query.from_user.id} cleared all fsub channels")
    except Exception as e:
        logger.error(f"Error clearing fsub channels: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("fsub_management")
            )
        except:
            pass


async def handle_back_to_main(query, db, **kwargs):
    """Return to main settings menu"""
    try:
        await query.message.edit(
            MESSAGES['MAIN_SETTINGS'],
            reply_markup=build_main_settings_keyboard()
        )
        logger.info(f"User {query.from_user.id} returned to main settings")
    except Exception as e:
        logger.error(f"Error in back_to_main handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_view_settings(query, db, **kwargs):
    """Display all current settings"""
    try:
        settings = await db.get_all_settings()
        
        if not settings:
            await query.message.edit(
                "<b>⚠️ 𝙉𝙤 𝙎𝙚𝙩𝙩𝙞𝙣𝙜𝙨 𝙁𝙤𝙪𝙣𝙙!</b>",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
            return
        
        msg_text = format_settings_display(settings)
        await query.message.edit(
            msg_text,
            reply_markup=build_back_button_keyboard("back_to_main")
        )
    except Exception as e:
        logger.error(f"Error in view_settings handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_reset_all(query, db, **kwargs):
    """Show reset confirmation"""
    await query.message.edit(
        "<b>⚠️ Aʀᴇ Yᴏᴜ sᴜʀᴇ Yᴏᴜ Wᴀɴᴛ Tᴏ Rᴇsᴇᴛ Aʟʟ Sᴇᴛᴛɪɴɢs?</b>",
        reply_markup=build_confirm_cancel_keyboard("confirm_reset_all", "back_to_main")
    )


async def handle_confirm_reset_all(query, db, **kwargs):
    """Execute settings reset"""
    try:
        await db.reset_all_settings()
        await query.message.edit(
            "<b>✅ Aʟʟ Sᴇᴛᴛɪɴɢs Hᴀᴠᴇ Bᴇᴇɴ Rᴇsᴇᴛ!</b>",
            reply_markup=build_back_button_keyboard("back_to_main")
        )
        logger.info(f"User {query.from_user.id} reset all settings")
    except Exception as e:
        logger.error(f"Error resetting settings: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_toggle_verification(query, db, **kwargs):
    """Toggle verification on/off"""
    try:
        settings = await db.get_all_settings()
        new_status = not settings.get("verification", True)
        
        await db.set_setting("verification", new_status)
        await query.message.edit_reply_markup(
            build_verification_keyboard(new_status)
        )
        
        status_text = BUTTON_TEXT['VERIFICATION_ON'] if new_status else BUTTON_TEXT['VERIFICATION_OFF']
        await query.answer(status_text)
        
        logger.info(f"User {query.from_user.id} toggled verification to {new_status}")
    except Exception as e:
        logger.error(f"Error in toggle_verification handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("verification_mode")
            )
        except:
            pass


async def handle_toggle_search(query, db, **kwargs):
    """Toggle group search on/off"""
    try:
        settings = await db.get_all_settings()
        new_status = not settings.get("group_search", False)
        file_delete = settings.get("file_delete", False)
        
        await db.set_setting("group_search", new_status)
        await query.message.edit_reply_markup(
            build_group_settings_keyboard(new_status, file_delete)
        )
        
        status_text = "ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ ᴇɴᴀʙʟᴇᴅ ✅" if new_status else "ɢʀᴏᴜᴘ sᴇᴀʀᴄʜ ᴅɪsᴀʙʟᴇᴅ ❌"
        await query.answer(status_text)
        
        logger.info(f"User {query.from_user.id} toggled group_search to {new_status}")
    except Exception as e:
        logger.error(f"Error in toggle_search handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("group_settings")
            )
        except:
            pass


async def handle_edit_mode(query, db, **kwargs):
    """Toggle file mode (buttons vs links)"""
    try:
        settings = await db.get_all_settings()
        new_status = not settings.get("file_mode", False)
        await db.set_setting("file_mode", new_status)
        
        status_text = "ᴄʜᴀɴɢᴇ ᴛᴏ ʙᴜᴛᴛᴏɴ ᴍᴏᴅᴇ sᴜᴄᴄᴇssғᴜʟʟʏ" if new_status else "ᴄʜᴀɴɢᴇ ᴛᴏ ᴛᴇxᴛ ʟɪɴᴋ ᴍᴏᴅᴇ sᴜᴄᴄᴇssғᴜʟʟʏ"
        await query.answer(status_text, show_alert=True)
        
        logger.info(f"User {query.from_user.id} toggled file_mode to {new_status}")
    except Exception as e:
        logger.error(f"Error in edit_mode handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("group_settings")
            )
        except:
            pass


async def handle_toggle_file_delete(query, db, **kwargs):
    """Toggle file delete on/off"""
    try:
        settings = await db.get_all_settings()
        new_status = not settings.get("file_delete", False)
        grp_search = settings.get("group_search", False)
        
        await db.set_setting("file_delete", new_status)
        await query.message.edit_reply_markup(
            build_group_settings_keyboard(grp_search, new_status)
        )
        
        status_text = BUTTON_TEXT['FILE_DELETE_ENABLED'] if new_status else BUTTON_TEXT['FILE_DELETE_DISABLED']
        await query.answer(status_text)
        
        logger.info(f"User {query.from_user.id} toggled file_delete to {new_status}")
    except Exception as e:
        logger.error(f"Error in toggle_file_delete handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("group_settings")
            )
        except:
            pass


async def handle_edit_shortner(query, db, **kwargs):
    """Show shortner selection menu"""
    await query.message.edit(
        MESSAGES['CHOOSE_SHORTNER'],
        reply_markup=build_shortner_menu_keyboard()
    )


async def handle_edit_shortner1(query, db, client, check_shortner, **kwargs):
    """Edit first shortner"""
    await _edit_shortner_common(query, db, client, check_shortner, "shortner_one", "api_one", "1ꜱᴛ")


async def handle_edit_shortner2(query, db, client, check_shortner, **kwargs):
    """Edit second shortner"""
    await _edit_shortner_common(query, db, client, check_shortner, "shortner_two", "api_two", "2ɴᴅ")


async def _edit_shortner_common(query, db, client, check_shortner, domain_key: str, api_key_key: str, label: str):
    """Generic shortner edit handler"""
    msg = None
    try:
        user_id = query.from_user.id
        
        await query.message.edit(
            f"<b>🔧 Sᴇɴᴅ {label} Sʜᴏʀᴛᴇɴᴇʀ Dᴏᴍᴀɪɴ ᴀɴᴅ Aᴘɪ Kᴇʏ\n\n"
            f"Fᴏʀᴍᴀᴛ: <code>domain.com API_KEY</code>\n\n"
            f"<blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )
        
        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60
        )
        
        if msg.text and msg.text.strip().lower() == '/cancel':
            await msg.delete()
            await query.message.edit(
                "<b>✋ Tᴀsᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
                "Sʜᴏʀᴛɴᴇʀ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ ʀᴇᴍᴀɪɴs ᴜɴᴄʜᴀɴɢᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("edit_shortner")
            )
            return
        
        try:
            domain, api_key = msg.text.strip().split(maxsplit=1)
        except ValueError:
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Sᴇɴᴅ ʙᴏᴛʜ Dᴏᴍᴀɪɴ ᴀɴᴅ Aᴘɪ Kᴇʏ ꜱᴘᴀᴄᴇ ꜱᴇᴘᴀʀᴀᴛᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("edit_shortner")
            )
            return
        
        await msg.delete()
        await query.message.edit("<b>⏳ Cʜᴇᴄᴋɪɴɢ Sʜᴏʀᴛᴇɴᴇʀ...\n\nPʟᴇᴀꜱᴇ ᴡᴀɪᴛ.</b>")
        
        try:
            ok, result = await check_shortner(domain, api_key)
        except Exception as e:
            logger.error(f"Shortner check failed: {e}")
            await query.message.edit(
                "<b>❌ Sʜᴏʀᴛᴇɴᴇʀ Cʜᴇᴄᴋ Fᴀɪʟᴇᴅ!</b>\n\n<b>Pʟᴇᴀꜱᴇ Tʀʏ Aɢᴀɪɴ.</b>",
                reply_markup=build_back_button_keyboard("edit_shortner")
            )
            return
        
        if not ok:
            await query.message.edit(
                f"<b>❌ Sʜᴏʀᴛᴇɴᴇʀ Nᴏᴛ Wᴏʀᴋɪɴɢ.</b>\n\n<b>{result}</b>",
                reply_markup=build_back_button_keyboard("edit_shortner")
            )
            return
        
        # Save to database
        await db.set_setting(domain_key, domain)
        await db.set_setting(api_key_key, api_key)
        
        await query.message.edit(
            f"<b>✅ {label} Sʜᴏʀᴛᴇɴᴇʀ Sᴇᴛ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n\n"
            f"<b>🌐 Dᴏᴍᴀɪɴ:</b> <code>{domain}</code>\n"
            f"<b>🔑 Aᴘɪ Kᴇʏ:</b> <code>{api_key}</code>\n\n"
            f"<b>🔗 Tᴇꜱᴛᴇᴅ Lɪɴᴋ:</b>\n<b>{result}</b>",
            disable_web_page_preview=True,
            reply_markup=build_back_button_keyboard("edit_shortner")
        )
        
        logger.info(f"User {query.from_user.id} updated {label} shortner")
    
    except ListenerTimeout:
        await query.message.edit(
            "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ!\n\n"
            "Yᴏᴜ ᴛᴏᴏᴋ ᴛᴏᴏ ʟᴏɴɢ ᴛᴏ ʀᴇsᴘᴏɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
            reply_markup=build_back_button_keyboard("edit_shortner")
        )
    
    except Exception as e:
        logger.error(f"Error in _edit_shortner_common: {e}", exc_info=True)
        try:
            if msg:
                await msg.delete()
        except:
            pass
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("edit_shortner")
            )
        except:
            pass


async def handle_edit_time(query, db, client, **kwargs):
    """Edit verification time"""
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
            timeout=60
        )
        
        if msg.text and msg.text.strip().lower() == '/cancel':
            await msg.delete()
            await query.message.edit(
                "<b>✋ Tᴀsᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
                "Vᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴛɪᴍᴇ ʀᴇᴍᴀɪɴs ᴜɴᴄʜᴀɴɢᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("verification_mode")
            )
            return
        
        try:
            verification_time = int(msg.text.strip())
        except ValueError:
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.</b>",
                reply_markup=build_back_button_keyboard("verification_mode")
            )
            return
        
        await msg.delete()
        await db.set_setting("third_verify_time", verification_time)
        
        await query.message.edit(
            f"<b>✅ 2ɴᴅ Vᴇʀɪꜰɪᴄᴀᴛɪᴏɴ Tɪᴍᴇ Sᴇᴛ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n\n"
            f"<b>⏰ Tɪᴍᴇ:</b> <code>{verification_time}</code> ꜱᴇᴄᴏɴᴅꜱ",
            reply_markup=build_back_button_keyboard("verification_mode")
        )
        
        logger.info(f"User {query.from_user.id} set verification time to {verification_time}")
    
    except ListenerTimeout:
        await query.message.edit(
            "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ!\n\n"
            "Yᴏᴜ ᴛᴏᴏᴋ ᴛᴏᴏ ʟᴏɴɢ ᴛᴏ ʀᴇsᴘᴏɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
            reply_markup=build_back_button_keyboard("verification_mode")
        )
    
    except Exception as e:
        logger.error(f"Error in handle_edit_time: {e}", exc_info=True)
        try:
            if msg:
                await msg.delete()
        except:
            pass
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("verification_mode")
            )
        except:
            pass


async def handle_export_settings(query, db, client, **kwargs):
    """Export all settings as a JSON file"""
    try:
        import json
        from datetime import datetime
        from io import BytesIO
        
        settings = await db.get_all_settings()
        
        if not settings:
            await query.message.edit(
                "<b>⚠️ Nᴏ sᴇᴛᴛɪɴɢs ᴛᴏ ᴇxᴘᴏʀᴛ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
            return
        
        # Create export data with metadata
        export_data = {
            "export_info": {
                "date": datetime.now(timezone(TIMEZONE)).strftime("%d %B, %Y %I:%M:%S %p"),
                "total_settings": len(settings),
                "exported_by": query.from_user.id,
                "version": "1.0"
            },
            "settings": settings
        }
        
        # Format as pretty JSON
        json_text = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Create file
        file = BytesIO(json_text.encode('utf-8'))
        file.name = f"settings_backup_{datetime.now(timezone(TIMEZONE)).strftime('%d_%B_%Y_%I:%M:%S_%p')}.json"
        
        # Send file
        await query.message.reply_document(
            document=file,
            caption=(
                f"<b>📤 Sᴇᴛᴛɪɴɢs Exᴘᴏʀᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                f"<b>📊 Tᴏᴛᴀʟ Sᴇᴛᴛɪɴɢs:</b> <code>{len(settings)}</code>\n"
                f"<b>📅 Exᴘᴏʀᴛ Dᴀᴛᴇ:</b> <code>{export_data['export_info']['date']}</code>\n\n"
                f"<b><blockquote>💡 Usᴇ ᴛʜɪs ғɪʟᴇ ᴛᴏ ʀᴇsᴛᴏʀᴇ sᴇᴛᴛɪɴɢs ʟᴀᴛᴇʀ</blockquote></b>"
            )
        )
        
        await query.message.edit(
            "<b>✅ Sᴇᴛᴛɪɴɢs ᴇxᴘᴏʀᴛᴇᴅ!\n\n"
            "<i>Cʜᴇᴄᴋ ᴛʜᴇ ғɪʟᴇ ʙᴇʟᴏᴡ 👇</i></b>",
            reply_markup=build_back_button_keyboard("back_to_main")
        )
        
        logger.info(f"User {query.from_user.id} exported {len(settings)} settings")
    
    except Exception as e:
        logger.error(f"Error in handle_export_settings: {e}", exc_info=True)
        try:
            await query.message.edit(
                "❌ Exᴘᴏʀᴛ Fᴀɪʟᴇᴅ!",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_import_settings(query, db, client, **kwargs):
    """Import settings from a JSON file"""
    msg = None
    try:
        user_id = query.from_user.id
        
        await query.message.edit(
            "<b>📥 Iᴍᴘᴏʀᴛ Sᴇᴛᴛɪɴɢs</b>\n\n"
            "<b>📎 Sᴇɴᴅ ᴛʜᴇ JSON ғɪʟᴇ ᴛᴏ ɪᴍᴘᴏʀᴛ sᴇᴛᴛɪɴɢs</b>\n\n"
            "<b>⚠️ Wᴀʀɴɪɴɢ: Tʜɪs ᴡɪʟʟ ᴏᴠᴇʀᴡʀɪᴛᴇ ᴇxɪsᴛɪɴɢ sᴇᴛᴛɪɴɢs!</b>\n\n"
            "<b><blockquote>Oʀ ꜱᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀꜱᴋ</blockquote></b>"
        )
        
        # Listen for file upload
        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id) & (filters.document | filters.text),
            timeout=120
        )
        
        # Check for cancellation
        if msg.text and msg.text.strip().lower() == '/cancel':
            await msg.delete()
            await query.message.edit(
                "<b>✋ Iᴍᴘᴏʀᴛ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
                "Yᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs ʀᴇᴍᴀɪɴ ᴜɴᴄʜᴀɴɢᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
            return
        
        # Validate file
        if not msg.document:
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ JSON ғɪʟᴇ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
            return
        
        # Check file extension
        if not msg.document.file_name.endswith('.json'):
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Oɴʟʏ JSON ғɪʟᴇs ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ.</b>",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
            return
        
        # Download and parse file
        await query.message.edit("<b>⏳ Pʀᴏᴄᴇssɪɴɢ ғɪʟᴇ...</b>")
        
        try:
            import json
            
            # Download file
            file_path = await msg.download()
            
            # Read and parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Clean up downloaded file
            import os
            os.remove(file_path)
            
            # Validate structure
            if "settings" not in import_data:
                await msg.delete()
                await query.message.edit(
                    "<b>❌ Iɴᴠᴀʟɪᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ!</b>\n\n"
                    "<i>Tʜᴇ ғɪʟᴇ ᴅᴏᴇsɴ'ᴛ ᴄᴏɴᴛᴀɪɴ sᴇᴛᴛɪɴɢs ᴅᴀᴛᴀ.</i>",
                    reply_markup=build_back_button_keyboard("back_to_main")
                )
                return
            
            settings_to_import = import_data["settings"]
            
            if not settings_to_import:
                await msg.delete()
                await query.message.edit(
                    "<b>⚠️ Nᴏ sᴇᴛᴛɪɴɢs ғᴏᴜɴᴅ ɪɴ ғɪʟᴇ.</b>",
                    reply_markup=build_back_button_keyboard("back_to_main")
                )
                return
            
            # Show confirmation
            await msg.delete()
            
            file_info = import_data.get("export_info", {})
            export_date = file_info.get("date", "Unknown")
            total_count = len(settings_to_import)
            
            confirm_text = (
                "<b>📥 Cᴏɴғɪʀᴍ Iᴍᴘᴏʀᴛ</b>\n\n"
                f"<b>📊 Sᴇᴛᴛɪɴɢs ᴛᴏ ɪᴍᴘᴏʀᴛ:</b> <code>{total_count}</code>\n"
                f"<b>📅 Exᴘᴏʀᴛᴇᴅ Oɴ:</b> <code>{export_date}</code>\n\n"
                "<b>⚠️ Wᴀʀɴɪɴɢ:</b>\n"
                "<b><blockquote>• Tʜɪs ᴡɪʟʟ ᴏᴠᴇʀᴡʀɪᴛᴇ ᴇxɪsᴛɪɴɢ sᴇᴛᴛɪɴɢs\n"
                "• Mᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴀ ʙᴀᴄᴋᴜᴘ</blockquote></b>\n\n"
                "<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ?</b>"
            )
            
            # Store import data temporarily for confirmation callback
            global TEMP_IMPORT_DATA
            TEMP_IMPORT_DATA[user_id] = settings_to_import
            
            await query.message.edit(
                confirm_text,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Cᴏɴғɪʀᴍ Iᴍᴘᴏʀᴛ", callback_data=f"confirm_import"),
                        InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ", callback_data="back_to_main")
                    ]
                ])
            )
        
        except json.JSONDecodeError:
            if msg:
                await msg.delete()
            await query.message.edit(
                "<b>❌ Iɴᴠᴀʟɪᴅ JSON ғɪʟᴇ!</b>\n\n"
                "<i>Tʜᴇ ғɪʟᴇ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ᴘᴀʀsᴇᴅ.</i>",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except Exception as e:
            logger.error(f"Error parsing import file: {e}")
            if msg:
                await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ғɪʟᴇ!</b>",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
    
    except ListenerTimeout:
        await query.message.edit(
            "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ!\n\n"
            "Yᴏᴜ ᴛᴏᴏᴋ ᴛᴏᴏ ʟᴏɴɢ ᴛᴏ ʀᴇsᴘᴏɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
            reply_markup=build_back_button_keyboard("back_to_main")
        )
    
    except Exception as e:
        logger.error(f"Error in handle_import_settings: {e}", exc_info=True)
        try:
            if msg:
                await msg.delete()
        except:
            pass
        try:
            await query.message.edit(
                "❌ Iᴍᴘᴏʀᴛ Fᴀɪʟᴇᴅ!",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_confirm_import(query, db, **kwargs):
    """Handle import confirmation callback"""
    try:
        user_id = query.from_user.id
        
        # Get stored import data
        global TEMP_IMPORT_DATA
        if user_id not in TEMP_IMPORT_DATA:
            try:
                await query.answer("⚠️ Iᴍᴘᴏʀᴛ ᴅᴀᴛᴀ ɴᴏᴛ ғᴏᴜɴᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.", show_alert=True)
            except:
                pass
            await query.message.edit(
                "<b>❌ Iᴍᴘᴏʀᴛ ғᴀɪʟᴇᴅ!</b>",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
            return
        
        settings_to_import = TEMP_IMPORT_DATA[user_id]
        
        # Import settings
        imported = 0
        failed = 0
        
        await query.message.edit("<b>⏳ Iᴍᴘᴏʀᴛɪɴɢ sᴇᴛᴛɪɴɢs...</b>")
        
        for key, value in settings_to_import.items():
            try:
                await db.set_setting(key, value)
                imported += 1
            except Exception as e:
                logger.error(f"Failed to import {key}: {e}")
                failed += 1
        
        # Clean up temporary data
        del TEMP_IMPORT_DATA[user_id]
        
        await query.message.edit(
            f"<b>✅ Iᴍᴘᴏʀᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
            f"<b>📊 Rᴇsᴜʟᴛs:</b>\n"
            f"• <b>Sᴜᴄᴄᴇss:</b> <code>{imported}</code>\n"
            f"• <b>Fᴀɪʟᴇᴅ:</b> <code>{failed}</code>",
            reply_markup=build_back_button_keyboard("back_to_main")
        )
        
        logger.info(f"User {user_id} imported {imported} settings (failed: {failed})")
        
    except Exception as e:
        logger.error(f"Error in handle_confirm_import: {e}", exc_info=True)
        try:
            await query.message.edit(
                "❌ Iᴍᴘᴏʀᴛ Fᴀɪʟᴇᴅ!",
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


# ==================== PREMIUM MODE HANDLERS ====================

async def handle_premium_mode(query, db, **kwargs):
    """Display premium mode management menu"""
    try:
        await query.message.edit(
            MESSAGES['PREMIUM_MODE'],
            reply_markup=build_premium_mode_keyboard()
        )
        logger.info(f"User {query.from_user.id} opened premium mode")
    except Exception as e:
        logger.error(f"Error in premium_mode handler: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("back_to_main")
            )
        except:
            pass


async def handle_pm_add_user(query, db, client, **kwargs):
    """Add premium subscription to a user via inline flow"""
    from datetime import timedelta
    import pytz
    from utils import get_seconds
    msg = None
    try:
        user_id = query.from_user.id

        await query.message.edit(
            "<b>➕ Aᴅᴅ Pʀᴇᴍɪᴜᴍ Usᴇʀ\n\n"
            "Sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴀɴᴅ ᴅᴜʀᴀᴛɪᴏɴ:\n"
            "Fᴏʀᴍᴀᴛ: <code>USER_ID 1 month</code>\n\n"
            "Exᴀᴍᴘʟᴇs:\n"
            "• <code>123456789 1 day</code>\n"
            "• <code>123456789 1 month</code>\n"
            "• <code>123456789 1 year</code>\n\n"
            "<blockquote>Oʀ sᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀsᴋ</blockquote></b>"
        )

        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60
        )

        if msg.text and msg.text.strip().lower() == '/cancel':
            await msg.delete()
            await query.message.edit(
                "<b>✋ Tᴀsᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )
            return

        if not msg.text:
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀsᴇ sᴇɴᴅ ᴠᴀʟɪᴅ ɪɴᴘᴜᴛ.</b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )
            return

        parts = msg.text.strip().split(maxsplit=2)
        await msg.delete()

        if len(parts) != 3 or not parts[0].isdigit():
            await query.message.edit(
                "<b>❌ Iɴᴠᴀʟɪᴅ Fᴏʀᴍᴀᴛ!\n\nUse: <code>USER_ID 1 month</code></b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )
            return

        target_id = int(parts[0])
        duration = parts[1] + " " + parts[2]
        seconds = await get_seconds(duration)

        if seconds <= 0:
            await query.message.edit(
                "<b>❌ Iɴᴠᴀʟɪᴅ Dᴜʀᴀᴛɪᴏɴ Fᴏʀᴍᴀᴛ!\n\n"
                "Usᴇ: 1 day / 1 hour / 1 min / 1 month / 1 year</b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )
            return

        target_user = await client.get_users(target_id)
        expiry_time = datetime.now() + timedelta(seconds=seconds)
        await db.update_user({"id": target_id, "expiry_time": expiry_time})

        data = await db.get_user(target_id)
        expiry = data.get("expiry_time")
        expiry_str = expiry.astimezone(pytz.timezone(TIMEZONE)).strftime("%d-%m-%Y %I:%M:%S %p")
        current_str = datetime.now(pytz.timezone(TIMEZONE)).strftime("%d-%m-%Y %I:%M:%S %p")

        await query.message.edit(
            f"<b>✅ #PREMIUM_ADDED\n\n"
            f"Usᴇʀ: {target_user.mention} [<code>{target_id}</code>]\n\n"
            f"Vᴀʟɪᴅɪᴛʏ: <code>{duration}</code>\n\n"
            f"Exᴘ Tɪᴍᴇ: <code>{expiry_str}</code></b>",
            disable_web_page_preview=True,
            reply_markup=build_back_button_keyboard("premium_mode")
        )

        try:
            await client.send_message(
                chat_id=target_id,
                text=(
                    f"<b><i>Hᴇʏ Tʜᴇʀᴇ {target_user.mention} 👋</i>\n\n"
                    f"Yᴏᴜʀ {duration} Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Aᴅᴅᴇᴅ ✅\n\n"
                    f"Sᴜʙ Tɪᴍᴇ: <code>{current_str}</code>\n"
                    f"Exᴘ Tɪᴍᴇ: <code>{expiry_str}</code>\n\n"
                    f"<blockquote>Fᴏʀ Aɴʏ Hᴇʟᴘ Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ @MjSupport_Robot</blockquote></b>"
                ),
                disable_web_page_preview=True
            )
        except:
            pass

        try:
            await client.send_message(
                PREMIUM_LOGS,
                text=(
                    f"<b>#PREMIUM_ADDED\n\n"
                    f"Usᴇʀ: {target_user.mention} [<code>{target_id}</code>]\n\n"
                    f"Vᴀʟɪᴅɪᴛʏ: <code>{duration}</code>\n\n"
                    f"Exᴘ Tɪᴍᴇ: <code>{expiry_str}</code></b>"
                ),
                disable_web_page_preview=True
            )
        except:
            pass

        logger.info(f"Admin {user_id} added premium to {target_id} for {duration}")

    except ListenerTimeout:
        await query.message.edit(
            "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ! Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
            reply_markup=build_back_button_keyboard("premium_mode")
        )
    except Exception as e:
        logger.error(f"Error in handle_pm_add_user: {e}", exc_info=True)
        try:
            if msg:
                await msg.delete()
        except:
            pass
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("premium_mode")
            )
        except:
            pass


async def handle_pm_remove_user(query, db, client, **kwargs):
    """Remove premium subscription from a user via inline flow"""
    msg = None
    try:
        user_id = query.from_user.id

        await query.message.edit(
            "<b>➖ Rᴇᴍᴏᴠᴇ Pʀᴇᴍɪᴜᴍ Usᴇʀ\n\n"
            "Sᴇɴᴅ ᴛʜᴇ Usᴇʀ ID:\n"
            "Fᴏʀᴍᴀᴛ: <code>USER_ID</code>\n\n"
            "<blockquote>Oʀ sᴇɴᴅ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ ᴛᴀsᴋ</blockquote></b>"
        )

        msg = await client.listen(
            chat_id=query.message.chat.id,
            filters=filters.user(user_id),
            timeout=60
        )

        if msg.text and msg.text.strip().lower() == '/cancel':
            await msg.delete()
            await query.message.edit(
                "<b>✋ Tᴀsᴋ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!</b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )
            return

        if not msg.text or not msg.text.strip().isdigit():
            await msg.delete()
            await query.message.edit(
                "<b>❌ Eʀʀᴏʀ: Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ Usᴇʀ ID.</b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )
            return

        target_id = int(msg.text.strip())
        await msg.delete()

        target_user = await client.get_users(target_id)

        if await db.has_premium_access(target_id):
            await db.remove_premium_access(target_id)
            await db.delete_premium_user(target_id)
            await query.message.edit(
                f"<b>✅ Sᴜᴄᴄᴇssғᴜʟʟʏ Rᴇᴍᴏᴠᴇᴅ {target_user.mention}'s Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ ◀</b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )
            try:
                await client.send_message(
                    chat_id=target_id,
                    text=(
                        f"<b><i>Hᴇʏ Tʜᴇʀᴇ {target_user.mention} 👋</i>\n\n"
                        f"Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Hᴀs Bᴇᴇɴ Rᴇᴍᴏᴠᴇᴅ ❌\n\n"
                        f"<blockquote>Fᴏʀ Aɴʏ Hᴇʟᴘ Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ @MjSupport_Robot</blockquote></b>"
                    )
                )
            except:
                pass
        else:
            await query.message.edit(
                f"<b>❓ {target_user.mention} ᴅᴏᴇs ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ.</b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )

        logger.info(f"Admin {user_id} removed premium from {target_id}")

    except ListenerTimeout:
        await query.message.edit(
            "<b>⏱️ Tɪᴍᴇᴏᴜᴛ Exᴘɪʀᴇᴅ! Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>",
            reply_markup=build_back_button_keyboard("premium_mode")
        )
    except Exception as e:
        logger.error(f"Error in handle_pm_remove_user: {e}", exc_info=True)
        try:
            if msg:
                await msg.delete()
        except:
            pass
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("premium_mode")
            )
        except:
            pass


async def handle_pm_total_users(query, db, client, **kwargs):
    """Display list of all premium users"""
    import pytz
    from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
    import os
    try:
        await query.message.edit("<b>⏳ Fᴇᴛᴄʜɪɴɢ Pʀᴇᴍɪᴜᴍ Usᴇʀs...</b>")

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
            await query.message.edit(
                text,
                reply_markup=build_back_button_keyboard("premium_mode")
            )
        except MessageTooLong:
            with open('premium_users.txt', 'w+') as f:
                f.write(text)
            await query.message.reply_document(
                'premium_users.txt',
                caption="<b>👑 Pʀᴇᴍɪᴜᴍ Usᴇʀs Lɪsᴛ</b>"
            )
            os.remove("premium_users.txt")
            await query.message.edit(
                f"<b>📄 Lɪsᴛ sᴇɴᴛ ᴀs ᴀ ᴅᴏᴄᴜᴍᴇɴᴛ ({total_users} ᴜsᴇʀs)</b>",
                reply_markup=build_back_button_keyboard("premium_mode")
            )

        logger.info(f"Admin {query.from_user.id} viewed {total_users} premium users")

    except Exception as e:
        logger.error(f"Error in handle_pm_total_users: {e}", exc_info=True)
        try:
            await query.message.edit(
                MESSAGES['ERROR'],
                reply_markup=build_back_button_keyboard("premium_mode")
            )
        except:
            pass



