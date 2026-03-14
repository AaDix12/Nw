# Watermark Plugin - Setup Guide

## Files
- watermark.py  → plugins/ folder mein daalo
- db_methods.py → apni Database class mein methods copy karo
- requirements.txt → existing requirements mein Pillow add karo

## Steps

### 1. watermark.py
Apne bot ke plugins/ folder mein daalo.

### 2. Database class mein add karo
db_methods.py se dono methods copy karo apni Database class mein.
Constructor mein yeh line bhi add karo:
    self.wm_settings = self.database['wm_settings']

### 3. requirements.txt
Apni existing requirements.txt mein sirf yeh add karo:
    Pillow

### 4. Koyeb pe deploy karo
ffmpeg Koyeb pe pre-installed hai, kuch extra nahi karna.

## Commands
/addmark          → Reply to photo/video, watermark lagao (saved text use hoga)
/addmark @Channel → Reply to photo/video, custom text se watermark lagao
/wesettings       → Watermark settings panel (text, position, opacity, font size)
