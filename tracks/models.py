# from django.db import models


# class Track(models.Model):
#     title = models.CharField(max_length=32, unique=True)
#     uid = models.CharField(max_length=128, unique=True)
#     num_racers = models.PositiveSmallIntegerField()
#     variantscsv = models.CharField(max_length=512, default='', blank=True)
#     downloadlink = models.URLField(default='', blank=True)
# 
#     def __str__(self):
#         return self.title
# 
#     @property
#     def variants(self):
#         return [x.strip()
#                 for x in self.variantscsv.split(',')
#                 if x.strip() != '']
