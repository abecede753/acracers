from django.contrib import admin

from races.models import RaceSetup, Race, Poll, Voting


class RaceAdmin(admin.ModelAdmin):
    pass


class RaceSetupAdmin(admin.ModelAdmin):
    pass


class PollAdmin(admin.ModelAdmin):
    pass


class VotingAdmin(admin.ModelAdmin):
    pass


admin.site.register(Race, RaceAdmin)
admin.site.register(RaceSetup, RaceSetupAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Voting, VotingAdmin)
