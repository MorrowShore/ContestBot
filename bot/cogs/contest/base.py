import os
from datetime import datetime

import discord
from discord.ext import commands

from bot import GMT_TIMEZONE
from bot.cogs.contest.jobs import ContestJobs
from bot.cogs.contest.utils import get_submission_channel
from bot.config import Bot
from bot.utils.image_utils import resize_and_save_image


class ContestManager(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.server_config_collection = bot.db["ServerConfig"]
        self.jobs = ContestJobs(cog=self)

    async def track_image_upload(self, message: discord.Message):
        submission_channel = await get_submission_channel(self.bot, message.guild.id)
        if submission_channel is None:
            return
        if message.channel.id != submission_channel.id or not message.attachments:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        attachment = message.attachments[0]
        current_month = datetime.now(GMT_TIMEZONE).strftime("%Y-%m")

        submissions = self.bot.db.submissions

        image_bytes = await attachment.read()
        folder_path = f"bot/data/submissions/{guild_id}"
        os.makedirs(folder_path, exist_ok=True)

        output_path = os.path.join(folder_path, f"{user_id}.webp")

        # Normalize for cross-platform safety
        db_path = output_path.replace("\\", "/")

        await resize_and_save_image(image_bytes, output_path)
        print(f"Saved image for {user_id} at {output_path}")

        # Delete old submission from this guild only
        await submissions.delete_many({
            "user_id": user_id,
            "guild_id": guild_id,
            "month": current_month
        })

        await submissions.insert_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "month": current_month,
            "file_path": db_path,
            "message_id": message.id
        })

