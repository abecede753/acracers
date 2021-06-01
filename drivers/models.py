from django.db import models


class Driver(models.Model):
    steam_guid = models.IntegerField(unique=True)
    discord_id = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return str(self.steam_guid)


class Factor(models.Model):
    driver = models.ForeignKey('drivers.Driver', on_delete=models.CASCADE)
    car = models.ForeignKey('cars.Car', on_delete=models.CASCADE)
    track = models.ForeignKey('tracks.Track', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    estimated_factor = models.FloatField()
    measured_factor = models.FloatField()
