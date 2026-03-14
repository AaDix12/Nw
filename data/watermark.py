import asyncio
import os
import tempfile
import subprocess
from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from PIL import Image, ImageDraw, ImageFont

from bot import Bot
from config import *
from helper_func import admin

POSITIONS = {
    "top_left":     "↖️ ᴛᴏᴘ ʟᴇꜰᴛ",
    "top_right":    "↗️ ᴛᴏᴘ ʀɪɢʜᴛ",
    "bottom_left":  "↙️ ʙᴏᴛᴛᴏᴍ ʟᴇꜰᴛ",
    "bottom_right": "↘️ ʙᴏᴛᴛᴏᴍ ʀɪɢʜᴛ",
    "center":       "⊙ ᴄᴇɴᴛᴇʀ",
}

# ── Watermark functions ──────────────────────────────────────

def apply_photo_watermark(input_path, output_path, s):
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font_size = s["font_size"]
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    text = s["text"]
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 20
    pos_map = {
        "top_left":     (pad, pad),
        "top_right":    (w - tw - pad, pad),
        "bottom_left":  (pad, h - th - pad),
        "bottom_right": (w - tw - pad, h - th - pad),
        "center":       ((w - tw) // 2, (h - th) // 2),
    }
    x, y = pos_map.get(s["position"], pos_map["bottom_right"])
    op = s["opacity"]
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, op))
    draw.text((x, y),     text, font=font, fill=(255, 255, 255, op))
    Image.alpha_composite(img, layer).convert("RGB").save(output_path, "JPEG", quality=95)


def apply_video_watermark(input_path, output_path, s):
    text = s["text"].replace("'", "\\'").replace(":", "\\:")
    op   = round(s["opacity"] / 255, 2)
    fs   = s["font_size"]
    pos_map = {
        "top_left":     "x=10:y=10",
        "top_right":    "x=w-text_w-10:y=10",
        "bottom_left":  "x=10:y=h-text_h-10",
        "bottom_right": "x=w-text_w-10:y=h-text_h-10",
        "center":       "x=(w-text_w)/2:y=(h-text_h)/2",
    }
    pos = pos_map.get(s["position"], pos_map["bottom_right"])
    vf  = f"drawtext=text='{text}':fontsize={fs}:fontcolor=white@{op}:shadowcolor=black@{op}:shadowx=2:shadowy=2:{pos}"
    subprocess.run(
        ["ffmpeg", "-i", input_path, "-vf", vf, "-codec:a", "copy", "-y", output_path],
        capture_output=True, timeout=300
    )


# ── Settings panel helper ────────────────────────────────────

async def settings_panel(user_id, client_db):
    s = await client_db.get_wm_settings(user_id)
    text = (
        f"⚙️ <b>ᴡᴀᴛᴇʀᴍᴀʀᴋ sᴇᴛᴛɪɴɢs</b>\n\n"
        f"📝 ᴛᴇxᴛ: <code>{s['text']}</code>\n"
        f"📍 ᴘᴏsɪᴛɪᴏɴ: <code>{s['position']}</code>\n"
        f"🔆 ᴏᴘᴀᴄɪᴛʏ: <code>{round(s['opacity']/255*100)}%</code>\n"
        f"🔤 ꜰᴏɴᴛ sɪᴢᴇ: <code>{s['font_size']}px</code>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ ᴛᴇxᴛ",      callback_data="wm_text"),
         InlineKeyboardButton("📍 ᴘᴏsɪᴛɪᴏɴ",  callback_data="wm_pos")],
        [InlineKeyboardButton("🔆 ᴏᴘᴀᴄɪᴛʏ",   callback_data="wm_opacity"),
         InlineKeyboardButton("🔤 ꜰᴏɴᴛ sɪᴢᴇ", callback_data="wm_size")],
    ])
    return text, keyboard


# ── /addmark command ─────────────────────────────────────────

@Bot.on_message(filters.private & admin & filters.command("addmark"))
async def add_watermark(client: Client, message: Message):
    reply_text = await message.reply_text("ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...!", quote=True)

    if not message.reply_to_message:
        await reply_text.edit_text(
            "⚠️ <b>ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴠɪᴅᴇᴏ!</b>\n\n"
            "ʀᴇᴘʟʏ ᴋᴀʀᴏ ᴀɴᴅ ᴛʏᴘᴇ:\n"
            "<code>/addmark</code>  ʏᴀ  <code>/addmark @YourChannel</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    args = message.text.split(None, 1)
    s = await client.db.get_wm_settings(message.from_user.id)

    if len(args) > 1:
        s["text"] = args[1].strip()

    replied = message.reply_to_message
    is_photo = replied.photo is not None
    is_video = replied.video is not None or (
        replied.document and replied.document.mime_type
        and "video" in replied.document.mime_type
    )

    if not is_photo and not is_video:
        await reply_text.edit_text(
            "⚠️ <b>sɪʀꜰ ᴘʜᴏᴛᴏ ʏᴀ ᴠɪᴅᴇᴏ ᴘᴇ ʀᴇᴘʟʏ ᴋᴀʀᴏ!</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    try:
        with tempfile.TemporaryDirectory() as tmp:
            if is_photo:
                await reply_text.edit_text("⏳ ᴘʜᴏᴛᴏ ᴘʀᴏᴄᴇss ʜᴏ ʀᴀʜɪ ʜᴀɪ...")
                inp = os.path.join(tmp, "input.jpg")
                out = os.path.join(tmp, "output.jpg")
                await replied.download(inp)
                apply_photo_watermark(inp, out, s)
                await reply_text.delete()
                await message.reply_photo(
                    out,
                    caption=f"✅ <b>ᴡᴀᴛᴇʀᴍᴀʀᴋ:</b> <code>{s['text']}</code>",
                    parse_mode=enums.ParseMode.HTML, quote=True
                )

            elif is_video:
                await reply_text.edit_text("⏳ ᴠɪᴅᴇᴏ ᴘʀᴏᴄᴇss ʜᴏ ʀᴀʜɪ ʜᴀɪ, ᴡᴀɪᴛ ᴋᴀʀᴏ...")
                inp = os.path.join(tmp, "input.mp4")
                out = os.path.join(tmp, "output.mp4")
                await replied.download(inp)
                apply_video_watermark(inp, out, s)
                await reply_text.delete()
                await message.reply_video(
                    out,
                    caption=f"✅ <b>ᴡᴀᴛᴇʀᴍᴀʀᴋ:</b> <code>{s['text']}</code>",
                    parse_mode=enums.ParseMode.HTML, quote=True
                )

    except Exception as e:
        await reply_text.edit_text(f"❌ sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ: {e}")


# ── /wesettings command ──────────────────────────────────────

@Bot.on_message(filters.private & admin & filters.command("wesettings"))
async def wm_settings_cmd(client: Client, message: Message):
    text, keyboard = await settings_panel(message.from_user.id, client.db)
    await message.reply_text(text, parse_mode=enums.ParseMode.HTML,
                              reply_markup=keyboard, quote=True)


# ── Callback buttons ─────────────────────────────────────────

@Bot.on_callback_query(filters.regex("^wm_|^wmpos_|^wmop_|^wmfs_"))
async def wm_callback(client: Client, cq: CallbackQuery):
    data    = cq.data
    user_id = cq.from_user.id

    match data:
        case "wm_text":
            await cq.message.edit_text(
                "✏️ <b>ɴᴀʏᴀ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴇxᴛ ʙʜᴇᴊᴏ:</b>\n"
                "ᴇxᴀᴍᴘʟᴇ: <code>@MyChannel</code>",
                parse_mode=enums.ParseMode.HTML
            )
            await client.db.update_wm_settings(user_id, "__waiting__", "text")

        case "wm_pos":
            btns = [[InlineKeyboardButton(label, callback_data=f"wmpos_{key}")]
                    for key, label in POSITIONS.items()]
            btns.append([InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="wm_back")])
            await cq.message.edit_text(
                "📍 <b>ᴘᴏsɪᴛɪᴏɴ ᴄʜᴏᴏsᴇ ᴋᴀʀᴏ:</b>",
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(btns)
            )

        case "wm_opacity":
            btns = [[
                InlineKeyboardButton("25%",  callback_data="wmop_64"),
                InlineKeyboardButton("50%",  callback_data="wmop_128"),
                InlineKeyboardButton("75%",  callback_data="wmop_191"),
                InlineKeyboardButton("100%", callback_data="wmop_255"),
            ], [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="wm_back")]]
            await cq.message.edit_text(
                "🔆 <b>ᴏᴘᴀᴄɪᴛʏ ᴄʜᴏᴏsᴇ ᴋᴀʀᴏ:</b>",
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(btns)
            )

        case "wm_size":
            btns = [[
                InlineKeyboardButton("20px", callback_data="wmfs_20"),
                InlineKeyboardButton("30px", callback_data="wmfs_30"),
                InlineKeyboardButton("40px", callback_data="wmfs_40"),
                InlineKeyboardButton("60px", callback_data="wmfs_60"),
            ], [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="wm_back")]]
            await cq.message.edit_text(
                "🔤 <b>ꜰᴏɴᴛ sɪᴢᴇ ᴄʜᴏᴏsᴇ ᴋᴀʀᴏ:</b>",
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(btns)
            )

        case _ if data.startswith("wmpos_"):
            pos = data.split("_", 1)[1]
            await client.db.update_wm_settings(user_id, "position", pos)
            await cq.answer(f"✅ Position: {pos}", show_alert=True)
            text, keyboard = await settings_panel(user_id, client.db)
            await cq.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard)

        case _ if data.startswith("wmop_"):
            op = int(data.split("_")[1])
            await client.db.update_wm_settings(user_id, "opacity", op)
            await cq.answer(f"✅ Opacity: {round(op/255*100)}%", show_alert=True)
            text, keyboard = await settings_panel(user_id, client.db)
            await cq.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard)

        case _ if data.startswith("wmfs_"):
            fs = int(data.split("_")[1])
            await client.db.update_wm_settings(user_id, "font_size", fs)
            await cq.answer(f"✅ Font Size: {fs}px", show_alert=True)
            text, keyboard = await settings_panel(user_id, client.db)
            await cq.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard)

        case "wm_back":
            text, keyboard = await settings_panel(user_id, client.db)
            await cq.message.edit_text(text, parse_mode=enums.ParseMode.HTML, reply_markup=keyboard)


# ── Text input handler ───────────────────────────────────────

@Bot.on_message(filters.private & admin & filters.text
                & ~filters.command(["addmark", "wesettings", "gen_link"]))
async def wm_text_input(client: Client, message: Message):
    user_id = message.from_user.id
    s = await client.db.get_wm_settings(user_id)
    if s.get("__waiting__") == "text":
        new_text = message.text.strip()
        await client.db.update_wm_settings(user_id, "text", new_text)
        await client.db.update_wm_settings(user_id, "__waiting__", None)
        await message.reply_text(
            f"✅ <b>ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴇxᴛ sᴇᴛ:</b> <code>{new_text}</code>",
            parse_mode=enums.ParseMode.HTML, quote=True
        )
