import re

import discord
from discord.ext import commands
import asyncio

from core.config import config
from core.text import text
from core import check, rubbercog, utils

class Janitor(rubbercog.Rubbercog):
    """Manage channels"""
    def __init__(self, bot):
        super().__init__(bot)
        self.visible = False

    #TODO Add docstring
    #TODO Use parameter to get 'warn'
    #TODO Add autoremove
    @commands.cooldown(rate=2, per=20.0, type=commands.BucketType.user)
    @commands.check(check.is_in_modroom)
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def hoarders(self, ctx: commands.Context):
        message = tuple(re.split(r'\s+', str(ctx.message.content).strip("\r\n\t")))
        guild = self.getGuild()
        members = guild.members
        channel = ctx.channel
        if len(message) == 2 and message[1] == "warn":
            warn = True
        else:
            warn = False

        hoarders = []
        for member in members:
            prog =[]
            for role in member.roles:
                if role < discord.utils.get(guild.roles, name='---FEKT') \
                and role > discord.utils.get(guild.roles, name='---'):
                    prog.append(role.name)
            if len(prog) > 1:
                hoarders.append([member, prog])

        if len(hoarders) == 0:
            await ctx.send(text.get("warden","no hoarders"))
        else:
            all = len(hoarders)
            if warn:
                mess = await ctx.send("Odesílání zprávy 1/{all}.".format(all=all))
            embed = discord.Embed(title="Programme hoarders", color=config.color)
            for num, (hoarder, progs) in enumerate(hoarders, start=1):
                embed.add_field(name="User", value=hoarder.mention, inline = True)
                embed.add_field(name="Status", value=hoarder.status, inline = True)
                embed.add_field(name="Programmes", value=', '.join(progs), inline = True)
                if warn:
                    if num %5 == 0: #Don't want to stress the API too much
                        await mess.edit(content="Odesílání zprávy {num}/{all}.".format(num=num, all=all))
                    await hoarder.send(utils.fill_message("hoarders_warn", user=hoarder.id))
                if num % 8 == 0: #Can't have more than 25 fields in an embed
                    await channel.send(embed=embed)
                    embed = discord.Embed(title="Programme hoarders", color=config.color)
            if warn and num % 5 != 0:
                await mess.edit(content="Odesílání zprávy {num}/{all}.".format(num=num, all=all))
            await channel.send(embed=embed)


    @commands.check(check.is_elevated)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command()
    async def purge(self, ctx, channel, limit = None, pinMode = "pinSkip"):
        #TODO Add user argument
        if channel == ".":
            ch = ctx.channel
            channel = ch.name
        else:            
            ch = discord.utils.get(self.getGuild().text_channels, name=channel.replace("#", ""))

        if limit:
            try:
                limit = int(limit) + 1
            except ValueError:
                self.purgeHelp()

        if limit:
            msgs = ch.history(limit=limit)
        else:
            msgs = ch.history()
        ctr_del = 0
        ctr_skip = 0
        ctr_pin = 0
        ctr_err = 0
        async for m in msgs:
            if m.pinned and pinMode == "pinStop":
                break
            elif m.pinned and pinMode == "pinSkip":
                ctr_skip += 1
                continue
            elif m.pinned and pinMode == "pinIgnore":
                ctr_pin += 1
            try:
                await m.delete()
                ctr_del += 1
            except discord.HTTPException:
                ctr_err += 1

        embed = discord.Embed(title="?purge", color=config.color)
        embed.add_field(name="Settings", value="Channel **{}**, limit **{}**, pinMode **{}**".
            format(channel, limit-1 if limit else "none", pinMode if pinMode else "ignore"))
        embed.add_field(name="Result",
            value="**{deleted}** removed (**{pinned}** were pinned), **{skipped}** skipped.\n" \
                "**{err}** errors occured.".format(
                deleted=ctr_del-1 + ctr_pin, skipped=ctr_skip, pinned=ctr_pin, err=ctr_err))
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        channel = self.getGuild().get_channel(config.channel_botlog)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Janitor(bot))
