from django.db import models


class Track(models.Model):
    title = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=128, unique=True)
    layout = models.CharField(max_length=128, default='')
    rsr_id = models.IntegerField(default=0)
    dlc_slug = models.CharField(max_length=128, blank=True, default='')
    download_url = models.URLField(max_length=2048, blank=True, default='')

    def __str__(self):
        return self.title
