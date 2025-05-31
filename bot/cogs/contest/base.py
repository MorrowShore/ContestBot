import os
from datetime import datetime

import discord
from discord.ext import commands

from bot import GMT_TIMEZONE
from bot.cogs.contest.jobs import ContestJobs
from bot.cogs.contest.utils import get_submission_channel, get_logs_channel
from bot.config import Bot
from bot.core.error_embed import create_logs_embed
from bot.utils.image_utils import resize_and_save_image


class ContestManager(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.server_config_collection = bot.db["ServerConfig"]
        self.jobs = ContestJobs(cog=self)

    async def track_image_upload(self, message: discord.Message):
        user_id = message.author.id
        guild_id = message.guild.id
        attachment = message.attachments[0] if message.attachments else None

        logs_channel = await get_logs_channel(self.bot, guild_id=guild_id)
        submission_channel = await get_submission_channel(self.bot, message.guild.id)

        def log_to_logs_channel(title, description, color=discord.Color.default(), image=None):
            if logs_channel:
                embed = create_logs_embed(
                    title=title,
                    description=description,
                    color=color,
                    image=image,
                    thumbnails=message.author.avatar.url if message.author.avatar else None
                )
                return logs_channel.send(embed=embed)
            return None

        if not submission_channel:
            await log_to_logs_channel(
                title="❌ Submission Channel Not Configured",
                description=f"{message.author.mention} attempted to submit but the submission channel is not set.\nUse `/contest_submission_channel` to set it.",
                color=discord.Color.red()
            )
            return

        if message.channel.id != submission_channel.id:
            await log_to_logs_channel(
                title="❌ Invalid Submission Location",
                description=f"{message.author.mention} tried to submit in <#{message.channel.id}> instead of <#{submission_channel.id}>.",
                color=discord.Color.orange()
            )
            return

        if not attachment:
            await log_to_logs_channel(
                title="❌ No Attachment Found",
                description=f"{message.author.mention} submitted a message without an image attachment.",
                color=discord.Color.orange()
            )
            return

        current_month = datetime.now(GMT_TIMEZONE).strftime("%Y-%m")
        submissions = self.bot.db.submissions
        image_bytes = await attachment.read()

        folder_path = f"bot/data/submissions/{guild_id}"
        os.makedirs(folder_path, exist_ok=True)
        output_path = os.path.join(folder_path, f"{user_id}.webp")
        db_path = output_path.replace("\\", "/")

        try:
            await resize_and_save_image(image_bytes, output_path)
            print(f"✅ Saved image for {user_id} at {output_path}")
        except Exception as e:
            await log_to_logs_channel(
                title="❌ Image Processing Failed",
                description=f"{message.author.mention} submitted an image, but it couldn't be resized.\nError: `{str(e)}`",
                color=discord.Color.red()
            )
            return

        await log_to_logs_channel(
            title="✅ New Contest Submission",
            description=f"{message.author.mention} submitted an image for the contest.",
            color=discord.Color.green(),
            image=attachment.url
        )

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


