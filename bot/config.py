import discord  # type: ignore
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from discord import Message
from discord.ext import commands  # type: ignore

from bot import MONGO_CLIENT

exts = [
    # "bot.cogs.contest_manager",
    "bot.cogs.contest"
]

class Bot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents,  **kwargs):
        super().__init__(command_prefix, intents=intents, **kwargs)
        self.mongo_client = MONGO_CLIENT
        self.db = self.mongo_client["contest_bot"]
        self.scheduler = AsyncIOScheduler()


    async def on_ready(self):
        for ext in exts:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(f"Failed to load extension {ext}: {e}")

        print(f"Loaded All Cog")

        synced = await  self.tree.sync()
        print(f"Synced {len(synced)} commands")
        print(f"{self.user.name} is ready")

        if not self.scheduler.running:
            self.scheduler.start()

    async def on_message(self, message: Message):
        if message.author.bot:
            return

        cogs = [
            ("ContestManager", "track_image_upload")
        ]

        for cog_name, func_name in cogs:
            cog = self.get_cog(cog_name)
            if cog:
                func = getattr(cog, func_name, None)
                if func:
                    await func(message)
                else:
                    print(f"Cog {cog_name} has no function {func_name}")
            else:
                print(f"Cog {cog_name} not found")
        await self.process_commands(message)