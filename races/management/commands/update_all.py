from django.conf import settings
from django.core.management.base import BaseCommand

from races.models import RaceSetup


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for rs in RaceSetup.objects.all():
            rs.save()
        print("Done.")
