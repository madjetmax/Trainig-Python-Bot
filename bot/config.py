import os
from dotenv import load_dotenv
load_dotenv()

# *bot 
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [859261869] # todo maybe i will add more functional for it and them should be in the database

# *database
# postgresql
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")

DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")

DB_NAME=os.getenv("DB_NAME")

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
MIGRATIONS_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# sqlite
# DB_NAME = "database.db"
# DB_URL = f"sqlite+aiosqlite:///../{DB_NAME}"

# MIGRATIONS_DB_URL = f"sqlite:///../{DB_NAME}"

DB_LOGGING = False

# *timezones
# time zone for all time zones jusst to make easy it 
_BASE_TIME_ZONE = "Europe/Kiev"

# database
MODELS_TIME_ZONE = _BASE_TIME_ZONE

# datetime
DATETIME_TIME_ZONE = _BASE_TIME_ZONE

# scheduler
SCHD_TIME_ZONE = _BASE_TIME_ZONE

# *scheduler
SCHD_TRAINING_START_SECONDS = 0 
SCHD_SKIPPEND_TRAINING_START_SECONDS = 0 

SCHD_SEND_TRAINIG_SKIPPED_HOURS = 6 # 6 AM at morning
SCHD_SEND_TRAINIG_SKIPPED_MINUTES = 0

# *training timers
TIMER_UPDATE_DALAY = 3 # seconds 
WARMUP_TIME = 3 * 60 # seconds

# *training reps names and body parts
ALL_BODY_PARTS = [
    {
        "name": "legs",
        "en": "Legs", 
        "uk": "Ноги", 
    },
    {
        "name": "chest",
        "en": "Chest",
        "uk": "Груди",
    },
    {
        "name": "back",
        "en": "back",
        "uk": "Спина",
    },
    {
        "name": "arms",
        "en": "Arms",
        "uk": "Руки",
    }
]

ALL_REPS_NAMES = [
    {
        "name": "horizontal bar",
        "en": "Horizontal Bar", 
        "uk": "Турнік", 
    },
    {
        "name": "push ups",
        "en": "Push Ups",
        "uk": "Віджимання",
    },
    {
        "name": "brusya",
        "en": "Brusya",
        "uk": "Брусья",
    }
]

# *week days
WEEK_DAYS_SORT = {
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
    "sun": 7,
}

ALL_WEEK_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# *help
# to commit database changes with alembic
#* alembic revision --autogenerate -m "commit message"
#* alembic stamp head
#* alembic upgrade head