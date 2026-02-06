import os
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv('BOT_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')

# Validation
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

if not BOT_API_TOKEN:
    raise ValueError("BOT_API_TOKEN environment variable is required")
