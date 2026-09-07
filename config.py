import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise RuntimeError(
        "Missing BOT_TOKEN or GEMINI_API_KEY. Check your .env file."
    )

if not OWNER_ID:
    raise RuntimeError(
        "Missing OWNER_ID in .env. Set it to your numeric Telegram user ID."
    )
