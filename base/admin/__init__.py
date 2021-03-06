"""Commands for admins"""
import discord
import bot
import logger

class Admin(bot.Extension):
    """Provides information about the Bot and loaded extensions"""

    @bot.argument("[channel]", discord.TextChannel, "here")
    @bot.argument("text+", str)
    @bot.command()
    async def speak(ctx, message):
        """Says something in the specified channel"""
        await ctx.args.channel.send(ctx.args.text)
        await message.add_reaction("✅")

    @bot.role("moderator")
    @bot.argument("channel*", discord.TextChannel, "here")
    @bot.command()
    async def lock(ctx, message):
        """Locks the specified or current channel"""
        everyone = discord.utils.find(lambda m: m.name.lower() == "@everyone", message.channel.guild.roles)
        perms = ctx.args.channel.overwrites_for(everyone)
        perms.send_messages = False
        await ctx.args.channel.set_permissions(everyone, overwrite=perms)
        await message.add_reaction("🔒")

    @bot.role("moderator")
    @bot.argument("channel*", discord.TextChannel, "here")
    @bot.command()
    async def unlock(ctx, message):
        """Unlocks the specified or current channel"""
        everyone = discord.utils.find(lambda m: m.name.lower() == "@everyone", message.channel.guild.roles)
        perms = ctx.args.channel.overwrites_for(everyone)
        perms.send_messages = None
        await ctx.args.channel.set_permissions(everyone, overwrite=perms)
        await message.add_reaction("🔓")

    @bot.role("manager")
    @bot.argument("count", int, 20)
    @bot.command()
    async def clear(ctx, message):
        """Clears the past n number of messages (Default: 20)"""
        messages = message.channel.history(limit=ctx.args.count + 1)
        await message.add_reaction(":eraser:495153237431943170")
        async for log in messages:
            if not log.pinned:
                try:
                    if log.id != message.id:
                        await log.delete()
                except discord.errors.NotFound:
                    logger.error("Failed to delete a message during clear.")
        await message.delete()

    @bot.role("moderator")
    @bot.argument("member", discord.Member)
    @bot.argument("command", bot.Command)
    @bot.argument("arguments+")
    @bot.command()
    async def runas(ctx, message):
        """Run a command as a member"""
        if bot.in_role_list(message.author, ctx.args.command.roles):
            message.author = ctx.args.member
            message.content = ctx.bot.profile.prefix + ctx.args.command.name + " " + ctx.args.arguments
            logger.debug(f"Running {message.content}")
            await ctx.bot.execute(message)
        else:
            await message.channel.send("You are not allowed to run that command.")
