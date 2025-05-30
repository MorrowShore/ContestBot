import discord


def log_embed(
        title: str,
        description: str,
        color: discord.Color,
        thumbnail: str = None,
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    embed.timestamp = discord.utils.utcnow().timestamp()
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    return embed
