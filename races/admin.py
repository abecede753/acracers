from django.contrib import admin

from races.models import RaceSetup, Race, Poll, Voting


class RaceAdmin(admin.ModelAdmin):
    pass


class RaceSetupAdmin(admin.ModelAdmin):
    fields = ('title', 'hidden', 'description', 'tgz', 'image',
              ('track_download_url', 'track_override'),
              ('car_download_url', 'car_override', 'fixed_cars'),
              'randomizable')
    list_display = ('title', 'id', 'hidden', 'randomizable', 'fixed_cars',
                    'car_override', 'track_override',
                    )
    ordering = ('title',)
    search_fields = ('title', 'description')
    pass


class PollAdmin(admin.ModelAdmin):
    pass


class VotingAdmin(admin.ModelAdmin):
    pass


admin.site.register(Race, RaceAdmin)
admin.site.register(RaceSetup, RaceSetupAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Voting, VotingAdmin)
