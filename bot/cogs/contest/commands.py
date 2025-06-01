import discord
from discord.ext import commands

from bot.cogs.contest.utils import get_logs_channel
from bot.core.error_embed import create_logs_embed


class ContestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = self.bot.db["ServerConfig"]


    @commands.hybrid_command(name="contest_submission_channel", description="Select submission channel")
    async def contest_submission_channel(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
        await ctx.defer()

        logs_channel = await get_logs_channel(self.bot, guild_id=ctx.guild.id)
        if logs_channel:
            logs_embed = create_logs_embed(
                title="Submission channel set",
                description=f"Submission channel set to <#{channel.id}>" if channel else "Submission channel unset",
                color=discord.Color.green() if channel else discord.Color.red()
            )
            await logs_channel.send(
                embed=logs_embed
            )

        if channel is None:
            channel = ctx.channel

        try:
            await self.collection.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"submission_channel": channel.id}},
                upsert=True)
            await ctx.send(f"<#{channel.id}> is set as submission channel")
        except Exception as e:
            if logs_channel:
                await logs_channel.send(
                    embed=create_logs_embed(
                        title="Error setting submission channel",
                        description=f"Error: {e}",
                        color=discord.Color.red()
                    )
                )
            await ctx.send(f"Error: {e}")

    @commands.hybrid_command(name="contest_voting_channel", description="Select voting channel")
    async def contest_voting_channel(self, ctx: commands.Context, *, channel: discord.ForumChannel = None):
        await ctx.defer()
        if channel is None:
            channel = ctx.channel

        if not isinstance(channel, discord.ForumChannel):
            await ctx.send("Please select a valid forum channel for voting.")
            return

        try:
            update = await self.collection.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"voting_channel": channel.id}},
                upsert=True
            )
            if update.modified_count == 0:
                await ctx.send(f"Voting channel already set to <#{channel.id}>")
            else:
                await ctx.send(f"<#{channel.id}> is set as voting channel")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.hybrid_command(name="contest_role", description="Select contest role")
    async def contest_role(self, ctx: commands.Context, *, role: discord.Role = None):
        await ctx.defer()
        if role is None:
            await ctx.send("Please specify a role.")
            return
        if not isinstance(role, discord.Role):
            await ctx.send("Please select a valid role.")
            return

        bot_member = ctx.guild.me

        server_config = await self.collection.find_one({"_id": ctx.guild.id})
        announcement_channel = ctx.guild.get_channel(server_config.get("contest_announcement_channel"))
        if announcement_channel:
            if role not in announcement_channel.overwrites:
                overwrites = {
                    bot_member: discord.PermissionOverwrite(view_channel=True, manage_channels=True, send_messages=True,
                                                            manage_threads=True, read_message_history=True),
                    role: discord.PermissionOverwrite(view_channel=True, read_message_history=True,
                                                      send_messages=False),
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False, read_message_history=False,
                                                                        send_messages=False)
                }
                await announcement_channel.edit(overwrites=overwrites)
            else:
                print("role already in announcement channel")

        try:
            await self.collection.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"contest_role": role.id}},
                upsert=True)
            await ctx.send(f"{role.mention} is set as contest role")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.hybrid_command(name="contest_announcement_channel", description="Select announcement channel")
    async def contest_announcement_channel(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
        await ctx.defer()
        if channel is None:
            channel = ctx.channel

        if not isinstance(channel, discord.TextChannel):
            await ctx.send("Please select a valid text channel for announcement.")
            return

        try:
            await self.collection.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"contest_announcement_channel": channel.id}},
                upsert=True
            )
            await ctx.send(f"<#{channel.id}> is set as announcement channel")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.hybrid_command(name="contest_ping_role", description="Select contest ping role")
    async def contest_ping_role(self, ctx: commands.Context, *, role: discord.Role = None):
        await ctx.defer()
        if role is None:
            await ctx.send("Please specify a role.")
            return
        if not isinstance(role, discord.Role):
            await ctx.send("Please select a valid role.")
            return
        try:
            await self.collection.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"contest_ping_role": role.id}},
                upsert=True
            )
            await ctx.send(f"{role.mention} is set as contest ping role")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.hybrid_command(name="contest_archive_channel", description="Select art archive channel")
    async def contest_archive_channel(self, ctx: commands.Context, *, channel: discord.ForumChannel = None):
        await ctx.defer()
        if channel is None:
            channel = ctx.channel

        if not isinstance(channel, discord.ForumChannel):
            await ctx.send("Please select a valid forum channel for art archive.")
            return

        try:
            await self.collection.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"contest_archive_channel": channel.id}},
                upsert=True)
            await ctx.send(f"<#{channel.id}> is set as art archive channel")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.hybrid_command(name="contest_logs_channel", description="Select bot log channel")
    async def contest_logs_channel(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
        await ctx.defer()
        if channel is None:
            channel = ctx.channel

        if not isinstance(channel, discord.TextChannel):
            await ctx.send("Please select a valid text channel for bot log.")
            return

        try:
            await self.collection.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"contest_logs_channel": channel.id}},
                upsert=True)
            await ctx.send(f"<#{channel.id}> is set as bot log channel")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.hybrid_command(name="contest_create_channel", description="Create contest channel")
    async def contest_create_channel(self, ctx: commands.Context):
        await ctx.defer()
        guild = ctx.guild

        bot_member = guild.me
        server_config = await self.collection.find_one({"_id": guild.id})

        default_overwrites = {
            bot_member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False,
                send_messages=False
            )
        }

        contest_category = discord.utils.get(guild.categories, name="Contest")
        if contest_category is None:
            try:
                contest_category = await guild.create_category("Contest")
                await contest_category.set_permissions(bot_member, overwrite=default_overwrites[bot_member])
                await contest_category.set_permissions(guild.default_role, overwrite=default_overwrites[guild.default_role])
            except discord.Forbidden:
                print(f"Bot does not have permission to create category{discord.Forbidden}")
                return
        try:
            await contest_category.set_permissions(
                bot_member,
                overwrite=discord.PermissionOverwrite(
                    manage_channels=True,
                    view_channel=True,
                    send_messages=True,
                    manage_threads=True,
                    read_message_history=True
                )
            )
        except Exception as e:
            print(f"Could not update category permissions for bot: {e}")

        contest_role = guild.get_role(server_config.get("contest_role")) if server_config else None
        print(f"Contest role: {contest_role}")

        view_only_overwrite = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=False
            )
        }

        print(f"View only overwrite: {view_only_overwrite}")

        async def get_or_create_role(name):
            return discord.utils.get(guild.roles, name=name) or await guild.create_role(name=name)

        ping_role = await get_or_create_role("Contest Ping")

        async def get_or_create_channel(name, cls, reason, extra_overwrite=None,
                                        inactivity_timeout=None):
            existing = discord.utils.get(guild.channels, name=name)
            if existing:
                return existing

            overwrites = {**default_overwrites}

            if extra_overwrite:
                for role, perms in extra_overwrite.items():
                    if isinstance(role, discord.Role) and role.position >= guild.me.top_role.position:
                        print(f"⚠️ Skipping overwrite for {role.name} due to role hierarchy (bot role too low).")
                        continue
                    overwrites[role] = perms

            overwrites[bot_member] = discord.PermissionOverwrite(
                view_channel=True,
                manage_channels=True,
                send_messages=True,
                manage_threads=True,
                read_message_history=True
            )

            try:
                if cls == discord.TextChannel:
                    return await guild.create_text_channel(
                        name,
                        category=contest_category,
                        reason=reason,
                        overwrites=overwrites,
                    )

                elif cls == discord.ForumChannel:
                    kwargs = {
                        "category": contest_category,
                        "reason": reason,
                        "default_layout": discord.ForumLayoutType.gallery_view,
                        "overwrites": overwrites
                    }
                    if inactivity_timeout:
                        kwargs["default_auto_archive_duration"] = inactivity_timeout
                    return await guild.create_forum(name, **kwargs)
                return None

            except discord.Forbidden:
                print(
                    f"Bot does not have permission to create {cls.__name__}: Missing permissions or role hierarchy issue.")
                return None

        submission_channel = await get_or_create_channel("contest-submit", discord.TextChannel, "Submission channel")
        voting_channel = await get_or_create_channel("contest-vote", discord.ForumChannel, "Voting channel",
                                                     inactivity_timeout=10080)
        announcement_channel = await get_or_create_channel("contest-announcement", discord.TextChannel,
                                                           "Announcement channel", extra_overwrite=view_only_overwrite)
        contest_archive_channel = await get_or_create_channel("contest-archive", discord.ForumChannel,
                                                              "Contest archive channel")
        logs_channel = await get_or_create_channel("bot-logs", discord.TextChannel, "Bot log channel")

        try:
            await self.collection.update_one(
                {"_id": ctx.guild.id},
                {"$set": {
                    "submission_channel": submission_channel.id,
                    "voting_channel": voting_channel.id,
                    "contest_announcement_channel": announcement_channel.id,
                    "contest_archive_channel": contest_archive_channel.id,
                    "contest_logs_channel": logs_channel.id,
                    "contest_ping_role": ping_role.id
                }},
                upsert=True
            )
            await ctx.send("Contest channels created successfully.")
        except Exception as e:
            await ctx.send(f"Error: {e}")
