import os
from dotenv import load_dotenv
load_dotenv()

# bot 
BOT_TOKEN = os.getenv("BOT_TOKEN")

# db 
DB_NAME = "database.db"
DB_URL = f"sqlite+aiosqlite:///../{DB_NAME}"
DB_LOGGING = False

MIGRATIONS_DB_URL = f"sqlite:///../{DB_NAME}"


MODELS_TIME_ZONE = "Europe/Kyiv"

# datetime
DATETIME_TIME_ZONE = "Europe/Kyiv"

# scheduler
SCHD_TIME_ZONE = "Europe/Kyiv"
SCHD_TRAINING_START_SECONDS = 0 

# training timers
TIMER_UPDATE_DALAY = 3 # seconds 