if await db.get_setting("verification", True):
        if not await db.has_premium_access(m.from_user.id):
            user_id = m.from_user.id
            VFY_TIME = int(await db.get_setting("third_verify_time", 300))
            user_verified = await db.is_user_verified(user_id)
            is_second_shortener = await db.use_second_shortener(user_id, VFY_TIME)
            how_to_download_link = TUTORIAL_LINK_2 if is_second_shortener else TUTORIAL_LINK_1
            if not user_verified or is_second_shortener:
                verify_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))
                await db.create_verify_id(user_id, verify_id)
                if message.command[1].startswith('all'):
                    verifylink = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=notcopy_{user_id}_{verify_id}_{file_id}", is_second_shortener)
                else:
                    verifylink = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=kdbotz_{user_id}_{verify_id}_{file_id}", is_second_shortener)
                buttons = [[InlineKeyboardButton(text="⚠️ ᴠᴇʀɪғʏ ⚠️", url=verifylink), InlineKeyboardButton(text="❗ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ❗", url=how_to_download_link)]]
                reply_markup=InlineKeyboardMarkup(buttons)
                bin_text = SECOND_VERIFICATION_TEXT if is_second_shortener else VERIFICATION_TEXT
                dmb = await m.reply_text(
                    text=(bin_text.format(message.from_user.first_name)),
                    protect_content=True,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                video_msg = await send_verify_video(client, m.from_user.id) if not is_second_shortener else None
                asyncio.create_task(safe_delete(dmb, video_msg, m, delay=600))
                return


@Client.on_message(filters.private & filters.text & filters.incoming)
async def pv_filter(client, message):
    if not await db.get_setting("verification", True):
        await auto_filter(client, message)
    else:
        if not await db.has_premium_access(message.from_user.id):
            user_id = message.from_user.id
            VFY_TIME = int(await db.get_setting("third_verify_time", 300))
            user_verified = await db.is_user_verified(user_id)
            is_second_shortener = await db.use_second_shortener(user_id, VFY_TIME)
            how_to_download_link = TUTORIAL_LINK_2 if is_second_shortener else TUTORIAL_LINK_1
            if not user_verified or is_second_shortener:
                verify_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))
                await db.create_verify_id(user_id, verify_id)
                verifylink = await get_shortlink(
                    f"https://telegram.me/{temp.U_NAME}?start=kdbotz_{user_id}_{verify_id}",
                    is_second_shortener
                )
                buttons = [[
                    InlineKeyboardButton(text="⚠️ ᴠᴇʀɪғʏ ⚠️", url=verifylink),
                    InlineKeyboardButton(text="❗ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ❗", url=how_to_download_link)
                ]]
                reply_markup = InlineKeyboardMarkup(buttons)
                bin_text = SECOND_VERIFICATION_TEXT if is_second_shortener else VERIFICATION_TEXT
                dmb = await message.reply_text(
                    text=(bin_text.format(message.from_user.first_name)),
                    protect_content=True,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                video_msg = await send_verify_video(client, message.from_user.id) if not is_second_shortener else None
                asyncio.create_task(safe_delete(dmb, video_msg, message, delay=600))
                return
        await auto_filter(client, message)


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client: Client, message):
    m = message
    if len(m.command) == 2 and m.command[1].startswith(('kdbotz', 'notcopy')):
        parts = m.command[1].split("_", 3)
        prefix = parts[0]
        verify_user_id = int(parts[1])
        verify_id = parts[2]

        if m.from_user.id != verify_user_id:
            await message.reply("<i><b>Tʜɪs Lɪɴᴋ Wᴀs Nᴏᴛ Gᴇɴᴇʀᴀᴛᴇᴅ Fᴏʀ Yᴏᴜ!</b></i>")
            return

        file_id = parts[3].removeprefix("file_") if len(parts) > 3 else None

        verify_id_info = await db.get_verify_id_info(verify_user_id, verify_id)
        if not verify_id_info or verify_id_info["verified"]:
            await message.reply("<i><b>Lɪɴᴋ Exᴘɪʀᴇᴅ Tʀʏ Aɢᴀɪɴ...</b></i>")
            return

        ist_timezone = pytz.timezone(TIMEZONE)
        created_at = verify_id_info.get("created_at")
        if created_at:
            created_at = created_at.astimezone(ist_timezone)
            current_time = datetime.now(tz=ist_timezone)
            time_taken = (current_time - created_at).total_seconds()
            if time_taken < 90:
                await db.update_verify_id_info(verify_user_id, verify_id, {"verified": True})
                bypass_msg = await message.reply("<b><i>🚨 Bʏᴘᴀss Dᴇᴛᴇᴄᴛᴇᴅ !</i>\n\nRᴇᴘᴇᴀᴛᴇᴅ Aᴛᴛᴇᴍᴘᴛs Mᴀʏ Rᴇsᴜʟᴛ Iɴ A Pᴇʀᴍᴀɴᴇɴᴛ Bᴀɴ.</b>")
                await client.send_message(PREMIUM_LOGS, f"<b><i>🚨 Bʏᴘᴀss Aᴛᴛᴇᴍᴘᴛ Dᴇᴛᴇᴄᴛᴇᴅ!</i>\n\nUsᴇʀ : {m.from_user.mention}\nUsᴇʀ ID : <code>{verify_user_id}</code>\nTɪᴍᴇ Tᴀᴋᴇɴ : <code>{time_taken:.2f} sᴇᴄᴏɴᴅs</code></b>")
                asyncio.create_task(safe_delete(bypass_msg, delay=30))
                return

        key = "second_time_verified" if await db.is_user_verified(verify_user_id) else "last_verified"
        current_time = datetime.now(tz=ist_timezone)
        await db.update_notcopy_user(verify_user_id, {key: current_time})
        await db.update_verify_id_info(verify_user_id, verify_id, {"verified": True})
        txt = SECOND_VERIFY_COMPLETE_TEXT if key == "second_time_verified" else VERIFY_COMPLETE_TEXT
        vrfy = 2 if key == "second_time_verified" else 1
        await client.send_message(VRFY_LOG_CHANNEL, VERIFIED_TXT.format(m.from_user.mention, verify_user_id, current_time.strftime('#%d_%B_%Y'), vrfy))

        if file_id:
            button_text = "Cʟɪᴄᴋ Hᴇʀᴇ Tᴏ Gᴇᴛ Yᴏᴜʀ Fɪʟᴇs"
            callback_value = f"file#{file_id}" if prefix == "kdbotz" else f"del_send_all#{file_id}"
        else:
            button_text = "Rᴇǫᴜᴇsᴛ Aɢᴀɪɴ"
            callback_value = "close_data"

        await m.reply_photo(
            photo=VERIFY_IMG,
            caption=txt.format(m.from_user.mention),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(button_text, callback_data=callback_value)]]),
            parse_mode=enums.ParseMode.HTML
        )
        return


async def send_verify_video(client, chat_id):
    try:
        if not VERIFY_VIDEO:
            return None
        from_chat_id, msg_id = VERIFY_VIDEO.split(":")
        return await client.copy_message(
            chat_id=chat_id,
            from_chat_id=int(from_chat_id),
            message_id=int(msg_id),
            protect_content=True
        )
    except Exception as e:
        print(f"Verify video send error: {e}")
        return None


async def safe_delete(*msgs, delay: int = 0):
    if delay > 0:
        await asyncio.sleep(delay)
    for msg in msgs:
        if msg is None:
            continue
        try:
            await msg.delete()
        except Exception:
            pass
