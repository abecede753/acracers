from django.conf import settings


def is_writeable_channel(ctx):
    """Decorator for generic server-based high permission test
    Passes found :class:`LocalServer` object as first arg,
    expects a :class:`Context`
    from above
    """
    if ctx.channel.id in settings.DISCORDCMDCHANNELS:
        return True
