from django.contrib import admin
from adhoc.models import AdhocRace


class AdhocRaceAdmin(admin.ModelAdmin):
#    fields = ('racesetup', 'practice_minutes', 'qualifying_minutes',
#              'race_minutes')
    list_display = ('racesetup', 'id')

admin.site.register(AdhocRace, AdhocRaceAdmin)
