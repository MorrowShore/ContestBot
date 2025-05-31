import discord #type: ignore
from bot import DISCORD_TOKEN
from bot.config import Bot


if __name__ == "__main__":
    bot = Bot(command_prefix="c!", intents=discord.Intents.all(), help_command=None)
    bot.run(DISCORD_TOKEN)