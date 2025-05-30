import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv #type: ignore
from motor.motor_asyncio import AsyncIOMotorClient #type:ignore




load_dotenv()


# Environmental
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")


# Clients

MONGO_CLIENT = AsyncIOMotorClient(MONGO_URI)

GMT_TIMEZONE = ZoneInfo("Etc/GMT")

__all__ = [
    "DISCORD_TOKEN",
    "MONGO_CLIENT",
    "GMT_TIMEZONE"
]