from django.conf import settings


def is_writeable_channel(ctx):
    """checking for channel where the bot is supposed to answer"""
    if ctx.channel.id in settings.DISCORDCMDCHANNELS:
        return True


def is_elevated_role(ctx):
    """make sure user has correct permissions"""
    role_id = 815186444678070302
    if role_id in [r.id for r in ctx.author.roles]:
        return True
