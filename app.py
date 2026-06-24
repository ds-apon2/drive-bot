import os
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

with open("service_account.json", "w", encoding="utf-8") as f:
    f.write(os.environ["GOOGLE_CREDENTIALS"])

BOT_TOKEN = os.environ["BOT_TOKEN"]
PHOTO_FOLDER_ID = os.environ["PHOTO_FOLDER_ID"]
VIDEO_FOLDER_ID = os.environ["VIDEO_FOLDER_ID"]
DOCUMENT_FOLDER_ID = os.environ["DOCUMENT_FOLDER_ID"]
AUDIO_FOLDER_ID = os.environ["AUDIO_FOLDER_ID"]

creds = service_account.Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/drive"]
)

drive = build("drive", "v3", credentials=creds)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "📷 Photos → Photos Folder\n"
        "🎥 Videos → Videos Folder\n"
        "📄 Documents → Documents Folder\n"
        "🎵 Audio → Audio Folder\n\n"
        "Send any file."
    )

def upload_file(path, name, folder_id):
    media = MediaFileUpload(path, resumable=True)
    drive.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media,
        fields="id"
    ).execute()

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    item = None
    folder = None
    filename = "file.bin"

    if msg.photo:
        item = msg.photo[-1]
        folder = PHOTO_FOLDER_ID
        filename = f"{item.file_unique_id}.jpg"

    elif msg.video:
        item = msg.video
        folder = VIDEO_FOLDER_ID
        filename = item.file_name or f"{item.file_unique_id}.mp4"

    elif msg.document:
        item = msg.document
        folder = DOCUMENT_FOLDER_ID
        filename = item.file_name or f"{item.file_unique_id}.bin"

    elif msg.audio or msg.voice:
        item = msg.audio or msg.voice
        folder = AUDIO_FOLDER_ID
        filename = getattr(item, "file_name", None) or f"{item.file_unique_id}.ogg"

    else:
        return

    try:
        tg_file = await item.get_file()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name

        await tg_file.download_to_drive(temp_path)
        upload_file(temp_path, filename, folder)

        os.remove(temp_path)
        await msg.reply_text("✅ Uploaded to Google Drive")

    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(
    filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO | filters.VOICE,
    handle
))

print("Bot Started...")
app.run_polling()
