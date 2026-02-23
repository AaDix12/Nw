import asyncio
import datetime
import secrets
import string

import pytz
from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ============================================================
#  CONFIG  (apni config file se import karo)
# ============================================================
from config import (
    TIMEZONE,
    TUTORIAL_LINK_1,
    TUTORIAL_LINK_2,
    VERIFICATION_TEXT,
    SECOND_VERIFICATION_TEXT,
    VERIFY_COMPLETE_TEXT,
    SECOND_VERIFY_COMPLETE_TEXT,
    VERIFIED_TXT,
    VERIFY_IMG,
    VRFY_LOG_CHANNEL,
)
from bot import temp  # temp.U_NAME ke liye
from database import db  # apna db object
from utils import get_shortlink, auto_filter  # helper functions


# ============================================================
#  DATABASE METHODS  (apni DB class mein add karo)
# ============================================================

class VerificationDB:
    """
    Ye methods apni existing DB class mein paste karo.
    self.misc       → 'misc' collection (user verification times)
    self.verify_id  → 'verify_id' collection (tokens)
    """

    # ----------------------------------------------------------
    #  User record — create / fetch / update
    # ----------------------------------------------------------

    async def get_notcopy_user(self, user_id):
        user_id = int(user_id)
        user = await self.misc.find_one({"user_id": user_id})
        ist_timezone = pytz.timezone(TIMEZONE)
        if not user:
            res = {
                "user_id": user_id,
                "last_verified": datetime.datetime(2020, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
            }
            await self.misc.insert_one(res)
            user = await self.misc.find_one({"user_id": user_id})
        return user

    async def update_notcopy_user(self, user_id, value: dict):
        user_id = int(user_id)
        myquery = {"user_id": user_id}
        newvalues = {"$set": value}
        return await self.misc.update_one(myquery, newvalues)

    # ----------------------------------------------------------
    #  Verification status checks
    # ----------------------------------------------------------

    async def is_user_verified(self, user_id):
        """Return True agar user ne last 24 ghante mein verify kiya ho."""
        user = await self.get_notcopy_user(user_id)
        try:
            past_date = user["last_verified"]
        except Exception:
            user = await self.get_notcopy_user(user_id)
            past_date = user["last_verified"]

        ist_timezone = pytz.timezone(TIMEZONE)
        past_date = past_date.astimezone(ist_timezone)
        current_time = datetime.datetime.now(tz=ist_timezone)
        time_diff = current_time - past_date
        return time_diff.total_seconds() <= 86400  # 24 hours

    async def use_second_shortener(self, user_id, time):
        """
        Return True agar user ko second shortener se verify karna chahiye.
        Condition: user already verified hai AND VFY_TIME seconds nikal gaye
                   AND second_time_verified, last_verified se purana hai.
        """
        user = await self.get_notcopy_user(user_id)

        # Ensure second_time_verified field exists
        if not user.get("second_time_verified"):
            ist_timezone = pytz.timezone(TIMEZONE)
            await self.update_notcopy_user(
                user_id,
                {"second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone)},
            )
            user = await self.get_notcopy_user(user_id)

        if await self.is_user_verified(user_id):
            try:
                past_date = user["last_verified"]
            except Exception:
                user = await self.get_notcopy_user(user_id)
                past_date = user["last_verified"]

            ist_timezone = pytz.timezone(TIMEZONE)
            past_date = past_date.astimezone(ist_timezone)
            current_time = datetime.datetime.now(tz=ist_timezone)
            time_difference = current_time - past_date

            if time_difference > datetime.timedelta(seconds=time):
                past_date = user["last_verified"].astimezone(ist_timezone)
                second_time = user["second_time_verified"].astimezone(ist_timezone)
                return second_time < past_date

        return False

    # ----------------------------------------------------------
    #  Token (verify_id) — create / fetch / update
    # ----------------------------------------------------------

    async def create_verify_id(self, user_id: int, hash):
        """Naya token banao with created_at timestamp."""
        ist_timezone = pytz.timezone(TIMEZONE)
        current_time = datetime.datetime.now(tz=ist_timezone)
        res = {
            "user_id": user_id,
            "hash": hash,
            "verified": False,
            "created_at": current_time,
        }
        return await self.verify_id.insert_one(res)

    async def get_verify_id_info(self, user_id: int, hash):
        return await self.verify_id.find_one({"user_id": user_id, "hash": hash})

    async def get_existing_verify_id(self, user_id: int):
        """
        Return existing unverified token agar pehle se hai to.
        Sirf wahi token return karo jo 24 ghante se purana na ho (TTL check).
        """
        ist_timezone = pytz.timezone(TIMEZONE)
        expiry_time = datetime.datetime.now(tz=ist_timezone) - datetime.timedelta(hours=24)
        return await self.verify_id.find_one({
            "user_id": user_id,
            "verified": False,
            "created_at": {"$gte": expiry_time},  # Sirf fresh tokens (24hr ke andar)
        })

    async def update_verify_id_info(self, user_id, hash, value: dict):
        myquery = {"user_id": user_id, "hash": hash}
        newvalues = {"$set": value}
        return await self.verify_id.update_one(myquery, newvalues)

    # ----------------------------------------------------------
    #  DB Index Setup — Bot start hone par ek baar call karo
    # ----------------------------------------------------------

    async def setup_indexes(self):
        """
        MongoDB TTL index lagao taaki purane tokens automatically delete hon.
        Ye method bot ke startup mein ek baar call karo:
            await db.setup_indexes()
        """
        # verify_id collection: 24 ghante (86400 sec) baad auto-delete
        await self.verify_id.create_index(
            "created_at",
            expireAfterSeconds=86400,  # 24 hours
            name="token_ttl_index",
        )

    # ----------------------------------------------------------
    #  Stats
    # ----------------------------------------------------------

    async def get_verification_stats(self):
        ist_timezone = pytz.timezone(TIMEZONE)
        current_time = datetime.datetime.now(tz=ist_timezone)
        midnight = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        midnight_utc = midnight.astimezone(pytz.utc)

        level1_count = await self.misc.count_documents(
            {"last_verified": {"$gte": midnight_utc}}
        )
        level2_count = await self.misc.count_documents(
            {"second_time_verified": {"$gte": midnight_utc}}
        )
        return level1_count, level2_count


# ============================================================
#  HELPER — token lao ya banao (reuse logic)
# ============================================================

async def _get_or_create_token(user_id: int) -> str:
    """
    Agar user ka koi unverified token pehle se hai to wahi return karo,
    warna naya banao aur DB mein save karo.
    """
    existing = await db.get_existing_verify_id(user_id)
    if existing:
        return existing["hash"]  # purana token reuse

    verify_id = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7)
    )
    await db.create_verify_id(user_id, verify_id)
    return verify_id


# ============================================================
#  HANDLER 1 — Private text messages (pv_filter)
# ============================================================

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pv_filter(client, message):
    if not await db.get_setting("verification", True):
        await auto_filter(client, message)
        return

    if not await db.has_premium_access(message.from_user.id):
        user_id = message.from_user.id
        VFY_TIME = int(await db.get_setting("third_verify_time", 300))
        user_verified = await db.is_user_verified(user_id)
        is_second_shortener = await db.use_second_shortener(user_id, VFY_TIME)
        how_to_download_link = TUTORIAL_LINK_2 if is_second_shortener else TUTORIAL_LINK_1

        if not user_verified or is_second_shortener:
            verify_id = await _get_or_create_token(user_id)  # reuse or new

            verifylink = await get_shortlink(
                f"https://telegram.me/{temp.U_NAME}?start=kdbotz_{user_id}_{verify_id}",
                is_second_shortener,
            )
            buttons = [[
                InlineKeyboardButton(text="⚠️ ᴠᴇʀɪғʏ ⚠️", url=verifylink),
                InlineKeyboardButton(text="❗ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ❗", url=how_to_download_link),
            ]]
            bin_text = SECOND_VERIFICATION_TEXT if is_second_shortener else VERIFICATION_TEXT
            dmb = await message.reply_text(
                text=bin_text.format(message.from_user.first_name),
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
            )
            await asyncio.sleep(120)
            await dmb.delete()
            await message.delete()
            return

    await auto_filter(client, message)


# ============================================================
#  HANDLER 2 — /start with verification token
# ============================================================

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client: Client, message):
    m = message

    # ── Verification flow ──────────────────────────────────
    if len(m.command) == 2 and m.command[1].startswith(("kdbotz", "notcopy")):
        parts = m.command[1].split("_", 3)
        prefix = parts[0]
        verify_user_id = int(parts[1])
        verify_id = parts[2]

        # Link kisi aur ke liye generate hua tha
        if m.from_user.id != verify_user_id:
            await message.reply("<i><b>Tʜɪs Lɪɴᴋ Wᴀs Nᴏᴛ Gᴇɴᴇʀᴀᴛᴇᴅ Fᴏʀ Yᴏᴜ!</b></i>")
            return

        file_id = parts[3].removeprefix("file_") if len(parts) > 3 else None

        # Token valid hai?
        verify_id_info = await db.get_verify_id_info(verify_user_id, verify_id)
        if not verify_id_info or verify_id_info["verified"]:
            await message.reply("<i><b>Lɪɴᴋ Exᴘɪʀᴇᴅ Tʀʏ Aɢᴀɪɴ...</b></i>")
            return

        # ── Bypass Detection (1 minute check) ──────────────
        ist_timezone = pytz.timezone(TIMEZONE)
        current_time = datetime.datetime.now(tz=ist_timezone)

        created_at = verify_id_info.get("created_at")
        if created_at:
            created_at = created_at.astimezone(ist_timezone)
            time_since_creation = (current_time - created_at).total_seconds()

            if time_since_creation < 60:  # 60 seconds se kam = suspicious
                await client.send_message(
                    VRFY_LOG_CHANNEL,
                    f"⚠️ <b>Bypass Detected!</b>\n"
                    f"👤 User: {m.from_user.mention} (<code>{verify_user_id}</code>)\n"
                    f"⏱️ Verified in: <b>{int(time_since_creation)} seconds</b>\n"
                    f"📅 Date: {current_time.strftime('#%d_%B_%Y')}\n"
                    f"🔑 Hash: <code>{verify_id}</code>",
                    parse_mode=enums.ParseMode.HTML,
                )
                await message.reply(
                    "<i><b>⚠️ Bypass Detected!\n\n"
                    "Tᴜᴍ Bʜᴏᴏᴛ Hᴏ Kʏᴀ? Iᴛɴᴀ Jᴀʟᴅɪ Vᴇʀɪғʏ?\n"
                    "Pʟᴇᴀsᴇ Mᴀɴᴜᴀʟʟʏ Vᴇʀɪғʏ Kᴀʀᴏ!</b></i>",
                    parse_mode=enums.ParseMode.HTML,
                )
                return  # Token expire nahi, user dobara try kar sakta hai

        # ── Verification complete ───────────────────────────
        key = "second_time_verified" if await db.is_user_verified(verify_user_id) else "last_verified"
        await db.update_notcopy_user(verify_user_id, {key: current_time})
        await db.update_verify_id_info(verify_user_id, verify_id, {"verified": True})

        txt = SECOND_VERIFY_COMPLETE_TEXT if key == "second_time_verified" else VERIFY_COMPLETE_TEXT
        vrfy = 2 if key == "second_time_verified" else 1

        await client.send_message(
            VRFY_LOG_CHANNEL,
            VERIFIED_TXT.format(
                m.from_user.mention,
                verify_user_id,
                current_time.strftime("#%d_%B_%Y"),
                vrfy,
            ),
        )

        # Button decide karo
        if file_id:
            button_text = "Cʟɪᴄᴋ Hᴇʀᴇ Tᴏ Gᴇᴛ Yᴏᴜʀ Fɪʟᴇs"
            callback_value = f"file#{file_id}" if prefix == "kdbotz" else f"del_send_all#{file_id}"
        else:
            button_text = "Rᴇǫᴜᴇsᴛ Aɢᴀɪɴ"
            callback_value = "close_data"

        await m.reply_photo(
            photo=VERIFY_IMG,
            caption=txt.format(m.from_user.mention),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(button_text, callback_data=callback_value)]]
            ),
            parse_mode=enums.ParseMode.HTML,
        )
        return

    # ── Normal /start (no token) — apna existing start logic yahan ──
    # await your_normal_start_handler(client, message)


# ============================================================
#  INLINE — file request ke saath verification (group filter)
# ============================================================
#
#  Ye block apne existing inline/callback handler mein paste karo
#  jahan file_id ke saath verification trigger hoti hai.
#
#  if await db.get_setting("verification", True):
#      if not await db.has_premium_access(m.from_user.id):
#          user_id = m.from_user.id
#          VFY_TIME = int(await db.get_setting("third_verify_time", 300))
#          user_verified = await db.is_user_verified(user_id)
#          is_second_shortener = await db.use_second_shortener(user_id, VFY_TIME)
#          how_to_download_link = TUTORIAL_LINK_2 if is_second_shortener else TUTORIAL_LINK_1
#
#          if not user_verified or is_second_shortener:
#              verify_id = await _get_or_create_token(user_id)  # reuse or new
#
#              if message.command[1].startswith('all'):
#                  verifylink = await get_shortlink(
#                      f"https://telegram.me/{temp.U_NAME}?start=notcopy_{user_id}_{verify_id}_{file_id}",
#                      is_second_shortener
#                  )
#              else:
#                  verifylink = await get_shortlink(
#                      f"https://telegram.me/{temp.U_NAME}?start=kdbotz_{user_id}_{verify_id}_{file_id}",
#                      is_second_shortener
#                  )
#
#              buttons = [[
#                  InlineKeyboardButton(text="⚠️ ᴠᴇʀɪғʏ ⚠️", url=verifylink),
#                  InlineKeyboardButton(text="❗ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ❗", url=how_to_download_link)
#              ]]
#              bin_text = SECOND_VERIFICATION_TEXT if is_second_shortener else VERIFICATION_TEXT
#              dmb = await m.reply_text(
#                  text=bin_text.format(message.from_user.first_name),
#                  protect_content=True,
#                  reply_markup=InlineKeyboardMarkup(buttons),
#                  parse_mode=enums.ParseMode.HTML
#              )
#              await asyncio.sleep(120)
#              await dmb.delete()
#              await m.delete()
#              return
