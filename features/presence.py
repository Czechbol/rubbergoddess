import datetime

import discord
from discord.ext.commands import Bot

from core import utils
from config.config import config
from features.base_feature import BaseFeature


class Presence(BaseFeature):
    def __init__(self, bot: Bot):
        super().__init__(bot)

        self.activity = discord.Game(
            start=datetime.datetime.utcnow(),
            name=config.prefix + 'goddess | ' + utils.git_hash()[:7])

    async def set_presence(self):
        await self.bot.change_presence(activity=self.activity)
