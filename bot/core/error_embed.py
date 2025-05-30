import discord
import datetime


def create_error_embed(title: str = "Error Occurred", *, error_message: str) -> discord.Embed:
    embed = discord.Embed(
        title  = title,
        description = error_message,
        color = discord.Color.red(),
        timestamp = datetime.datetime.utcnow()
    )
    embed.set_footer(text="Please contact support if the issue persists.")
    return embed