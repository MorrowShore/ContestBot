import io

import aiohttp
import discord


# def get_guild(cog):
#     return cog.bot.get_guild(GUILD_ID)

async def get_submission_channel(bot, guild_id):
    config = await bot.db["ServerConfig"].find_one({"_id": guild_id})
    if not config:
        return None
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.NotFound:
            print(f"❌ Guild not found. {guild_id}")
            return None
    return guild.get_channel(config["submission_channel"]) if "submission_channel" in config else None


async def get_voting_channel(bot, guild_id):
    config = await bot.db["ServerConfig"].find_one({"_id": guild_id})
    if not config:
        return None
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.NotFound:
            print(f"❌ Guild not found. {guild_id}")
            return None
    return guild.get_channel(config["voting_channel"]) if "voting_channel" in config else None


async def get_contest_role(bot, guild_id):
    config = await bot.db["ServerConfig"].find_one({"_id": guild_id})
    if not config:
        return None
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.NotFound:
            print(f"❌ Guild not found. {guild_id}")
            return None
    return guild.get_role(config["contest_role"]) if "contest_role" in config else None


async def get_contest_announcement_channel(bot, guild_id):
    config = await bot.db["ServerConfig"].find_one({"_id": guild_id})
    if not config:
        return None
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.NotFound:
            print(f"❌ Guild not found. {guild_id}")
            return None
    return guild.get_channel(config["contest_announcement_channel"]) if "contest_announcement_channel" in config else None


async def get_contest_ping_role(bot, guild_id):
    config = await bot.db["ServerConfig"].find_one({"_id": guild_id})
    if not config:
        return None
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.NotFound:
            print(f"❌ Guild not found. {guild_id}")
            return None
    return guild.get_role(config["contest_ping_role"]) if "contest_ping_role" in config else None


async def get_contest_archive_channel(bot, guild_id):
    config = await bot.db["ServerConfig"].find_one({"_id": guild_id})
    if not config:
        return None
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.NotFound:
            print(f"❌ Guild not found. {guild_id}")
            return None
    return guild.get_channel(config["contest_archive_channel"]) if "contest_archive_channel" in config else None


async def get_logs_channel(bot, guild_id):
    config = await bot.db["ServerConfig"].find_one({"_id": guild_id})
    if not config:
        return None
    guild = bot.get_guild(guild_id)
    if guild is None:
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.NotFound:
            print(f"❌ Guild not found. {guild_id}")
            return None
    return guild.get_channel(config["contest_logs_channel"]) if "contest_logs_channel" in config else None



async def get_discord_file_from_url(url: str, filename: str = None) -> discord.File:
    """
    Downloads a file from a URL and returns a discord.File object.

    :param url: The direct URL to the file.
    :param filename: Optional custom filename. If not provided, tries to infer from URL.
    :return: discord.File object
    :raises: Exception if the file can't be downloaded
    """
    if filename is None:
        filename = url.split("/")[-1] or "file"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to fetch file: HTTP {resp.status}")
            data = io.BytesIO(await resp.read())
            return discord.File(data, filename=filename)