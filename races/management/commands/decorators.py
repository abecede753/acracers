from django.conf import settings


def is_writeable_channel(ctx):
    """checking for channel where the bot is supposed to answer"""
    if ctx.channel.id in settings.DISCORDCMDCHANNELS:
        return True


def is_elevated_role(ctx):
    """make sure user has correct permissions"""
    rolename = "AFTuesdays"
    if rolename in [r.name for r in ctx.author.roles]:
        return True
