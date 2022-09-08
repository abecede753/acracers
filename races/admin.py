from django.contrib import admin

from races.models import RaceSetup  # , Race, Poll, Voting


# class RaceAdmin(admin.ModelAdmin):
#     pass


class RaceSetupAdmin(admin.ModelAdmin):
    fields = (('title', 'tierdrop', 'hidden'), 'description', 'tgz', 'image',
              ('track_download_url', 'track_override'),
              ('car_download_url', 'car_override', 'fixed_cars'),
              'randomizable')
    list_display = ('title', 'id', 'hidden', 'randomizable', 'fixed_cars',
                    'car_override', 'track_override', 'date_modified'
                    )
    ordering = ('title',)
    search_fields = ('title', 'description')
    list_filter = ('date_modified', 'hidden')

    pass


# class PollAdmin(admin.ModelAdmin):
#     pass


# class VotingAdmin(admin.ModelAdmin):
#     pass


# admin.site.register(Race, RaceAdmin)
admin.site.register(RaceSetup, RaceSetupAdmin)
# admin.site.register(Poll, PollAdmin)
# admin.site.register(Voting, VotingAdmin)
