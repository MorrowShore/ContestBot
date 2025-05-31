from bot.cogs.contest.base import ContestManager
from bot.cogs.contest.commands import ContestCommands


async def setup(bot):
    cog = ContestManager(bot)
    await bot.add_cog(ContestManager(bot))
    await bot.add_cog(ContestCommands(bot))
    await cog.jobs.schedule_job()
