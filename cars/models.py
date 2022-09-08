from django.db import models


class Car(models.Model):
    title = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True)
    rsr_id = models.IntegerField(default=0)
    dlc_slug = models.CharField(max_length=128, blank=True, default='')
    download_url = models.URLField(max_length=2048, blank=True, default='')

    def __str__(self):
        return self.title


class Laptime(models.Model):
    car = models.ForeignKey('cars.Car', on_delete=models.CASCADE)
    track = models.ForeignKey('tracks.Track', on_delete=models.SET_NULL,
                              null=True)
    driver = models.ForeignKey('drivers.Driver', null=True,
                               on_delete=models.CASCADE)
    seconds = models.FloatField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    num_entries = models.IntegerField(null=True)
    best = models.FloatField(null=True)
    worst = models.FloatField(null=True)
    middle = models.FloatField(null=True)
