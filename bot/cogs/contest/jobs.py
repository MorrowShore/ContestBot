import os
from datetime import datetime
from pathlib import Path

import discord

from bot import GMT_TIMEZONE
from bot.cogs.contest.utils import get_submission_channel, get_contest_role, get_voting_channel, \
    get_contest_announcement_channel, get_contest_ping_role, get_contest_archive_channel, get_discord_file_from_url, \
    get_logs_channel
from bot.core.error_embed import create_logs_embed


class ContestJobs:
    def __init__(self, cog):
        self.cog = cog
        self.bot = self.cog.bot
        self.collection = self.bot.db["ServerConfig"]
        self.submissions_collection = self.bot.db["submissions"]

    async def schedule_job(self):
        scheduler = self.bot.scheduler
        async for config in self.collection.find({}):
            guild_id = config["_id"]

            scheduler.add_job(self.open_submission_channel, "cron", day=1, hour=0, minute=0, timezone=GMT_TIMEZONE, kwargs={"guild_id": guild_id})
            scheduler.add_job(self.close_submission_channel, "cron", day=14, hour=23, minute=0, second = 0,  timezone=GMT_TIMEZONE, kwargs={"guild_id": guild_id})
            scheduler.add_job(self.post_submission_to_forum, "cron", day=14, hour=23, minute=30, second = 0, timezone=GMT_TIMEZONE, kwargs={"guild_id": guild_id})
            scheduler.add_job(self.open_voting_channel, "cron", day=16, hour=23, minute=59,second = 0, timezone=GMT_TIMEZONE, kwargs={"guild_id": guild_id})
            scheduler.add_job(self.close_voting_channel, "cron", day=23, hour=23, minute=59, timezone=GMT_TIMEZONE, kwargs={"guild_id": guild_id})
            scheduler.add_job(self.announce_winner, "cron", day=24, hour=0, minute=0, timezone=GMT_TIMEZONE, kwargs={"guild_id": guild_id})
            scheduler.add_job(self.close_contest, "cron", day=24, hour=22, minute=0, timezone=GMT_TIMEZONE, kwargs={"guild_id": guild_id})

    async def open_submission_channel(self, guild_id: int = None):
        submission_channel = await get_submission_channel(self.bot, guild_id= guild_id)
        member = await get_contest_role(self.bot, guild_id= guild_id)
        logs_channel = await get_logs_channel(self.bot, guild_id= guild_id)
        if submission_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Submission channel Not Found",
                        description=f"Submission channel not found When opening the submission channel.",
                        color=discord.Color.red()
                    )
                )
            print("Submission channel not set.")
            return

        if member is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Contest Role Not Found",
                        description=f"Contest role not found When opening the submission channel. Make sure to set the contest role using the `contest_role` command.",
                        color=discord.Color.red()
                    )
                )
            print("Contest role not set.")
            return



        if submission_channel and isinstance(submission_channel, discord.TextChannel) and member:
            overwrites = discord.PermissionOverwrite()
            overwrites.send_messages = True
            overwrites.view_channel = True
            overwrites.read_message_history = False
            overwrites.attach_files = True
            try:
                await submission_channel.set_permissions(member, overwrite=overwrites)
            except discord.Forbidden:
                print("Bot does not have permission to set permissions in the submission channel.")
                return

        announcement_channel = await  get_contest_announcement_channel(self.bot, guild_id= guild_id)
        contest_ping_role = await get_contest_ping_role(self.bot, guild_id=guild_id)
        print(f"Contest ping role: {contest_ping_role}")
        if announcement_channel is not None:
            await announcement_channel.send(
                f"{contest_ping_role.mention if contest_ping_role else ''}The submission channel is now open! Please submit your entries here: <#{submission_channel.id}>."
            )
        print("🔓 Opened submission channel at", datetime.utcnow())

    async def close_submission_channel(self, guild_id: int = None):
        logs_channel = await get_logs_channel(self.bot, guild_id=guild_id)
        submission_channel = await get_submission_channel(self.bot, guild_id=guild_id)
        member = await get_contest_role(self.bot, guild_id= guild_id)
        if submission_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Submission channel Not Found",
                        description=f"Submission channel not found When closing the submission channel.",
                        color=discord.Color.red()
                    )
                )
            print("Submission channel not set.")
            return

        if member is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Contest Role Not Found",
                        description=f"Contest role not found When closing the submission channel. Make sure to set the contest role using the `contest_role` command.",
                        color=discord.Color.red()
                    )
                )
            print("Contest role not set.")
            return

        if submission_channel and isinstance(submission_channel, discord.TextChannel) and member:
            overwrites = discord.PermissionOverwrite()
            overwrites.view_channel = False
            overwrites.read_message_history = False
            await submission_channel.set_permissions(member, overwrite=overwrites)

        announcement_channel = await  get_contest_announcement_channel(self.bot, guild_id=guild_id)
        contest_ping_role = await get_contest_ping_role(self.bot, guild_id=guild_id)
        print(f"Contest ping role: {contest_ping_role}")
        if announcement_channel is not None:
            await announcement_channel.send(
                f"{contest_ping_role.mention if contest_ping_role else ''}The submission channel is now closed. Please submit your entries again in the next Month."
            )


        print("🔒 Closed submission channel at", datetime.utcnow())

    async def post_submission_to_forum(self, guild_id: int = None,):
        guild = self.bot.get_guild(guild_id)
        logs_channel = await get_logs_channel(self.bot, guild_id=guild_id)
        if guild is None:
            print("Guild not found.")
            return None

        voting_channel = await get_voting_channel(self.bot, guild_id= guild_id)
        if voting_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Voting Channel Not Found",
                        description=f"Voting channel not found When posting submissions to the forum. Make sure to set the voting channel using the `contest_voting_channel` command.",
                        color=discord.Color.red()
                    )
                )
            return print("Voting channel not set.")

        current_month = datetime.now(GMT_TIMEZONE).strftime("%Y-%m")
        submissions = self.submissions_collection.find({
            "month": current_month,
            "guild_id": guild_id  
        })

        member = await get_contest_role(self.bot, guild_id= guild_id)
        if member is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Contest Role Not Found",
                        description=f"Contest role not found When posting submissions to the forum. Make sure to set the contest role using the `contest_role` command.",
                        color=discord.Color.red()
                    )
                )
            print("Contest role not set.")
            return None

        async for entry in submissions:
            user = guild.get_member(entry["user_id"])
            if not user:
                continue

            file_path = os.path.normpath(entry["file_path"])

            if not os.path.exists(file_path):
                print(f"File not found at {file_path}")
                continue

            file = discord.File(file_path, filename="submission.webp")

            thread = await voting_channel.create_thread(
                name=f"{user.display_name}'s Submission",
                content=f" ",
                file=file
            )

            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Submission Posted to Forum",
                        description=f"Submission posted to the forum by {user.mention}.",
                        color=discord.Color.green(),
                        thumbnails=user.avatar.url
                    )
                )

            try:
                await thread.message.add_reaction("🏆")
            except Exception as e:
                print(f"Error reacting to submission: {e}")

            await self.submissions_collection.update_one(
                {"_id": entry["_id"]},
                {"$set": {"thread_id": thread.message.id}}
            )
        return None

    async def open_voting_channel(self, guild_id: int = None,):
        logs_channel = await get_logs_channel(self.bot, guild_id=guild_id)
        voting_channel = await get_voting_channel(self.bot, guild_id= guild_id)
        announcement_channel = await get_contest_announcement_channel(self.bot, guild_id= guild_id)
        if voting_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Voting Channel Not Found",
                        description=f"Voting channel not found When opening the voting channel. Make sure to set the voting channel using the `contest_voting_channel` command.",
                        color=discord.Color.red()
                    )
                )
            print("Voting channel not set.")
            return
        member = await get_contest_role(self.bot, guild_id= guild_id)
        if member is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Contest Role Not Found",
                        description=f"Contest role not found When opening the voting channel. Make sure to set the contest role using the `contest_role` command.",
                        color=discord.Color.red()
                    )
                )
            print("Contest role not set.")
            return

        if voting_channel and isinstance(voting_channel, discord.ForumChannel) and member:
            overwrites = discord.PermissionOverwrite()
            overwrites.view_channel = True
            overwrites.send_messages =False
            overwrites.read_message_history = True
            try:
                await voting_channel.set_permissions(target=member, overwrite=overwrites)
                await announcement_channel.send(f"{member.mention}The voting channel is now open! Please vote for your art submission here: <#{voting_channel.id}>.")
            except discord.Forbidden:
                if logs_channel:
                    await logs_channel.send(
                        embed=create_logs_embed(
                            title="Bot Does Not Have Permission to Set Permissions in the Voting Channel",
                            description=f"Bot does not have permission to set permissions in the voting channel. Make sure the bot has the `manage_channels` permission in the voting channel.",
                            color=discord.Color.red()
                        )
                    )
                print("Bot does not have permission to set permissions in the voting channel.")
                return

    async def close_voting_channel(self, guild_id: int = None,):
        logs_channel = await get_logs_channel(self.bot, guild_id=guild_id)
        voting_channel = await get_voting_channel(self.bot, guild_id= guild_id)
        if voting_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Voting Channel Not Found",
                        description=f"Voting channel not found When closing the voting channel. Make sure to set the voting channel using the `contest_voting_channel` command.",
                        color=discord.Color.red()
                    )
                )
            print("Voting channel not set.")
            return
        member = await get_contest_role(self.bot, guild_id= guild_id)
        if member is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Contest Role Not Found",
                        description=f"Contest role not found When closing the voting channel. Make sure to set the contest role using the `contest_role` command.",
                        color=discord.Color.red()
                    )
                )
            print("Contest role not set.")
            return

        if voting_channel and isinstance(voting_channel, discord.ForumChannel) and member:
            overwrites = discord.PermissionOverwrite()
            overwrites.view_channel = False
            overwrites.read_message_history = False
            try:
                await voting_channel.set_permissions(target=member, overwrite=overwrites)
                announcement_channel = await  get_contest_announcement_channel(self.bot, guild_id=guild_id)
                contest_ping_role = await get_contest_ping_role(self.bot, guild_id=guild_id)
                if announcement_channel is not None:
                    await announcement_channel.send(
                        f"{contest_ping_role.mention if contest_ping_role else ''}The voting channel is now closed. Please vote for your art submission again in the next Month."
                    )
            except discord.Forbidden:
                if logs_channel:
                    await logs_channel.send(
                        embed=create_logs_embed(
                            title="Bot Does Not Have Permission to Set Permissions in the Voting Channel",
                            description=f"Bot does not have permission to set permissions in the voting channel. Make sure the bot has the `manage_channels` permission in the voting channel.",
                            color=discord.Color.red()
                        )
                    )
                print("Bot does not have permission to set permissions in the voting channel.")


    async def announce_winner(self, guild_id: int = None,):
        guild = self.bot.get_guild(guild_id)
        logs_channel = await get_logs_channel(self.bot, guild_id=guild_id)
        if guild is None:
            print("Guild not found.")
            return None

        voting_channel = await get_voting_channel(self.bot, guild_id= guild_id)
        if voting_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Voting Channel Not Found",
                        description=f"Voting channel not found When announcing the winner. Make sure to set the voting channel using the `contest_voting_channel` command.",
                        color=discord.Color.red()
                    )
                )
            return print("Voting channel not set.")

        now = datetime.now(GMT_TIMEZONE)
        current_month = now.month
        current_year = now.year

        top_votes = 0
        winners = []

        for thread in voting_channel.threads:
            if thread.created_at.month != current_month or thread.created_at.year != current_year:
                continue
            async for msg in thread.history(limit=1):
                vote_count = sum(r.count for r in msg.reactions)
                if vote_count > 1 and vote_count > top_votes:
                    top_votes = vote_count
                    winners = [(msg.id, msg.attachments[0].url, top_votes)]
                elif vote_count == top_votes:
                    winners.append((msg.id, msg.attachments[0].url, top_votes))

        if not winners:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="No Winner Found",
                        description=f"No winner found in the voting channel.",
                        color=discord.Color.red()
                    )
                )
            print("No winner found.")
            return None

        announcement_channel = await get_contest_announcement_channel(self.bot, guild_id= guild_id)
        if announcement_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Announcement Channel Not Found",
                        description=f"Announcement channel not found When announcing the winner. Make sure to set the announcement channel using the `contest_announcement_channel` command.",
                        color=discord.Color.red()
                    )
                )
            print("Announcement channel not set.")
            return None

        contest_ping_role = await get_contest_ping_role(self.bot, guild_id=guild_id)
        print(f"Contest ping role: {contest_ping_role}")
        if contest_ping_role is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Contest Ping Role Not Found",
                        description=f"Contest ping role not found When announcing the winner. Make sure to set the contest ping role using the `contest_ping_role` command.",
                        color=discord.Color.red()
                    )
                )
            print("Contest ping role not set.")

        for thread_id, image_url, votes in winners:

            winner = await self.submissions_collection.find_one({"thread_id": thread_id})
            if not winner:
                continue
            user = guild.get_member(winner["user_id"])
            if not user:
                continue

            embed = discord.Embed(
                title="🎉 Art Contest Winner 🎉",
                description=f"Congratulations {user}! You have won the Art Contest!",
                color=0x00FF00
            )
            embed.set_image(url=image_url)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Total votes: {votes}")

            content = (
                f"The winner of the Art Contest is:\n{user.mention} {contest_ping_role.mention if contest_ping_role else ''}"
            )
            await announcement_channel.send(
                embed=embed,
                content=content
            )

            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Winner Announced",
                        description=f"Winner announced in the voting channel.",
                        color=discord.Color.green(),
                        thumbnails=user.avatar.url
                    )
                )
            return None
        return None

    async def close_contest(self, guild_id: int = None,):
        guild = self.bot.get_guild(guild_id)
        logs_channel = await get_logs_channel(self.bot, guild_id=guild_id)
        voting_channel = await get_voting_channel(self.bot, guild_id= guild_id)
        art_archive_channel = await get_contest_archive_channel(self.bot, guild_id= guild_id)
        if voting_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Voting Channel Not Found",
                        description=f"Voting channel not found When closing the contest. Make sure to set the voting channel using the `contest_voting_channel` command.",
                        color=discord.Color.red()
                    )
                )
            print("Voting channel not set.")
            return
        if art_archive_channel is None:
            if logs_channel:
                await logs_channel.send(
                    embed = create_logs_embed(
                        title="Art Archive Channel Not Found",
                        description=f"Art archive channel not found When closing the contest. Make sure to set the art archive channel using the `contest_archive_channel` command.",
                        color=discord.Color.red()
                    )
                )
            print("Art archive channel not set.")
            return
        threads = voting_channel.threads
        print(f"Archiving {len(threads)} threads...")
        for thread in threads:
            try:
                if art_archive_channel is None:
                    continue

                user_data = await self.submissions_collection.find_one({"thread_id": thread.id})
                user = guild.get_member(user_data["user_id"])

                async for msg in thread.history(limit=1, oldest_first=True):
                    if msg.attachments:
                        attachment = msg.attachments[0]
                        file  = await get_discord_file_from_url(attachment.url ,attachment.filename)
                        await art_archive_channel.create_thread(
                            name=f"{user.display_name}'s Art Submission",
                            content=f"{user.display_name} \nTotal votes: {sum(r.count for r in msg.reactions)}",
                            file= file,
                            reason=f"Archived from the {voting_channel.name} contest."
                        )



                        guild_folder  = Path(f"bot/data/submissions/{guild_id}")
                        if guild_folder.exists():
                            for file in guild_folder.iterdir():
                                try:
                                    file.unlink()
                                    print(f"Deleted {file}")
                                except Exception as e:
                                    print(f"Error deleting {file}: {e}")
                        else:
                            print(f"No guild folder found for {guild_id}")

                await thread.delete()
            except Exception as e:
                if logs_channel:
                    await logs_channel.send(
                        embed = create_logs_embed(
                            title="Error Archiving Thread",
                            description=f"Error archiving thread {thread.name}: {e}",
                            color=discord.Color.red()
                        )
                    )
                print(f"Error archiving thread {thread.name}: {e}")


