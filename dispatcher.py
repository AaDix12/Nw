from feature import (
    is_check_admin,
    handle_verification_mode,
    handle_group_settings,
    handle_back_to_main,
    handle_view_settings,
    handle_reset_all,
    handle_confirm_reset_all,
    handle_toggle_verification,
    handle_toggle_search,
    handle_fsub_management,
    handle_toggle_fsub_mode,
    handle_add_fsub_channel,
    handle_add_normal_fsub,
    handle_add_req_fsub,
    handle_remove_fsub_channel,
    handle_list_fsub_channels,
    handle_clear_all_fsub,
    handle_confirm_clear_fsub,
    handle_edit_mode,
    handle_toggle_file_delete,
    handle_edit_shortner,
    handle_edit_shortner1,
    handle_edit_shortner2,
    handle_edit_time,
    handle_broadcast_type,
    handle_manual_broadcast,
    handle_auto_broadcast,
    handle_export_settings,
    handle_import_settings,
    handle_confirm_import,
    chat_ids,
)
from database.users_chats_db import db
from info import *


# ==================== DISPATCH TABLE ====================
# Maps callback_data → handler function and its extra kwargs.
# All handlers receive (query, db) at minimum; extra kwargs are merged in.

CALLBACK_DISPATCH = {
    # ── Main navigation ──────────────────────────────────────
    "back_to_main":         (handle_back_to_main,          {}),
    "view_settings":        (handle_view_settings,         {}),

    # ── Verification ─────────────────────────────────────────
    "verification_mode":    (handle_verification_mode,     {}),
    "toggle_verification":  (handle_toggle_verification,   {}),
    "edit_shortner":        (handle_edit_shortner,         {}),
    "edit_shortner1":       (handle_edit_shortner1,        {}),
    "edit_shortner2":       (handle_edit_shortner2,        {}),
    "edit_time":            (handle_edit_time,             {}),

    # ── Group / bot settings ──────────────────────────────────
    "group_settings":       (handle_group_settings,        {}),
    "toggle_search":        (handle_toggle_search,         {}),
    "toggle_file_delete":   (handle_toggle_file_delete,    {}),
    "edit_mode":            (handle_edit_mode,             {}),

    # ── Broadcast ─────────────────────────────────────────────
    "broadcast_type":       (handle_broadcast_type,        {}),
    "manual_broadcast":     (handle_manual_broadcast,      {}),
    "auto_broadcast":       (handle_auto_broadcast,        {}),

    # ── Reset ─────────────────────────────────────────────────
    "reset_all":            (handle_reset_all,             {}),
    "confirm_reset_all":    (handle_confirm_reset_all,     {}),

    # ── Fsub management ───────────────────────────────────────
    "fsub_management":      (handle_fsub_management,       {}),
    "toggle_fsub_mode":     (handle_toggle_fsub_mode,      {}),
    "add_fsub_channel":     (handle_add_fsub_channel,      {}),
    "add_normal_fsub":      (handle_add_normal_fsub,       {"AUTH_CHANNELS":     AUTH_CHANNELS}),
    "add_req_fsub":         (handle_add_req_fsub,          {"AUTH_REQ_CHANNELS": AUTH_REQ_CHANNELS}),
    "remove_fsub_channel":  (handle_remove_fsub_channel,   {"AUTH_CHANNELS":     AUTH_CHANNELS,
                                                             "AUTH_REQ_CHANNELS": AUTH_REQ_CHANNELS}),
    "list_fsub_channels":   (handle_list_fsub_channels,    {"AUTH_CHANNELS":     AUTH_CHANNELS,
                                                             "AUTH_REQ_CHANNELS": AUTH_REQ_CHANNELS}),
    "clear_all_fsub":       (handle_clear_all_fsub,        {}),
    "confirm_clear_fsub":   (handle_confirm_clear_fsub,    {}),

    # ── Export / import ───────────────────────────────────────
    "export_settings":      (handle_export_settings,       {}),
    "import_settings":      (handle_import_settings,       {}),
    "confirm_import":       (handle_confirm_import,        {}),
}


# ==================== MAIN CALLBACK ROUTER ====================

async def route_callback(client, query):
    """
    Single entry-point for all settings-related callbacks.
    - Checks admin access once.
    - Looks up the handler in CALLBACK_DISPATCH.
    - Passes (query, db, client, **extra_kwargs) to the handler.
    """
    if not await is_check_admin(query, ADMINS):
        return

    data = query.data
    entry = CALLBACK_DISPATCH.get(data)

    if entry is None:
        return  # Unknown callback — ignore silently

    handler, extra_kwargs = entry
    await handler(query, db, client=client, **extra_kwargs)
