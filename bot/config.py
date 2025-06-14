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

BASE_TIME_ZONE = "Europe/Kiev"

MODELS_TIME_ZONE = BASE_TIME_ZONE

# datetime
DATETIME_TIME_ZONE = BASE_TIME_ZONE

# scheduler
SCHD_TIME_ZONE = BASE_TIME_ZONE
SCHD_TRAINING_START_SECONDS = 0 

# training timers
TIMER_UPDATE_DALAY = 3 # seconds 

# training reps names and body parts
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
        "uk": "брусья",
    }
]

# help
# for commit database changes
#* alembic revision --autogenerate -m "commit message"
#* alembic upgrade head   
#* alembic stamp head   