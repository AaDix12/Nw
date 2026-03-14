# ============================================================
# YEH METHODS APNI DATABASE CLASS MEIN ADD KARO
# ============================================================

# Constructor mein add karo:
# self.wm_settings = self.database['wm_settings']


async def get_wm_settings(self, user_id: int) -> dict:
    doc = await self.wm_settings.find_one({"_id": user_id})
    if doc:
        doc.pop("_id", None)
        return doc
    return {
        "text": "@YourChannel",
        "opacity": 180,
        "position": "bottom_right",
        "font_size": 40,
    }

async def update_wm_settings(self, user_id: int, key: str, value):
    await self.wm_settings.update_one(
        {"_id": user_id},
        {"$set": {key: value}},
        upsert=True
    )
