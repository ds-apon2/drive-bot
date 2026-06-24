import os
import json
import tempfile

from telegram import Update
from telegram.ext import (
Application,
CommandHandler,
MessageHandler,
ContextTypes,
filters,
)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BOT_TOKEN = os.environ["BOT_TOKEN"]

PHOTO_FOLDER_ID = os.environ["PHOTO_FOLDER_ID"]
VIDEO_FOLDER_ID = os.environ["VIDEO_FOLDER_ID"]
DOCUMENT_FOLDER_ID = os.environ["DOCUMENT_FOLDER_ID"]
AUDIO_FOLDER_ID = os.environ["AUDIO_FOLDER_ID"]

creds = Credentials.from_authorized_user_info(
json.loads(os.environ["GOOGLE_TOKEN"]),
["https://www.googleapis.com/auth/drive"]
)

drive = build("drive", "v3", credentials=creds)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "📷 Photos → Photos Folder\n"
        "🎥 Videos → Videos Folder\n"
        "📄 Documents → Documents Folder\n"
        "🎵 Audio → Audio Folder\n\n"
        "Send any file and I'll upload it to Google Drive."
    )

def upload_to_drive(path, filename, folder_id):
    media = MediaFileUpload(path, resumable=True)

    drive.files().create(
        body={
            "name": filename,
            "parents": [folder_id]
        },
        media_body=media,
        fields="id"
    ).execute()
```

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
msg = update.message

```
item = None
folder_id = None
filename = "file.bin"

if msg.photo:
    item = msg.photo[-1]
    folder_id = PHOTO_FOLDER_ID
    filename = f"{item.file_unique_id}.jpg"

elif msg.video:
    item = msg.video
    folder_id = VIDEO_FOLDER_ID
    filename = item.file_name or f"{item.file_unique_id}.mp4"

elif msg.document:
    item = msg.document
    folder_id = DOCUMENT_FOLDER_ID
    filename = item.file_name or f"{item.file_unique_id}.bin"

elif msg.audio:
    item = msg.audio
    folder_id = AUDIO_FOLDER_ID
    filename = item.file_name or f"{item.file_unique_id}.mp3"

elif msg.voice:
    item = msg.voice
    folder_id = AUDIO_FOLDER_ID
    filename = f"{item.file_unique_id}.ogg"

else:
    return

try:
    await msg.reply_text("⏳ Uploading...")

    tg_file = await item.get_file()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        temp_path = tmp.name

    await tg_file.download_to_drive(temp_path)

    upload_to_drive(
        temp_path,
        filename,
        folder_id
    )

    os.remove(temp_path)

    await msg.reply_text(
        "✅ Successfully uploaded to Google Drive"
    )

except Exception as e:
    await msg.reply_text(
        f"❌ Error\n\n{e}"
    )
```

def main():
app = Application.builder().token(BOT_TOKEN).build()

```
app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.PHOTO
        | filters.VIDEO
        | filters.Document.ALL
        | filters.AUDIO
        | filters.VOICE,
        handle_file
    )
)

print("Bot Started...")
app.run_polling()
```

if **name** == "**main**":
main()
