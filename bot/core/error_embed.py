import discord


def create_logs_embed(title: str = "Error Occurred", description: str = "", thumbnails=None, image=None, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    embed = discord.Embed(
        title  = title,
        description = description,
        color =color,
        timestamp = discord.utils.utcnow()
    )
    embed.set_author(name="Contest Bot Logs")
    if thumbnails:
        embed.set_thumbnail(url=thumbnails)
    if image:
        embed.set_image(url=image)
    return embed