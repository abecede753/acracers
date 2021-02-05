# from django.db import models


# class Car(models.Model):
#     title = models.CharField(max_length=32, unique=True)
#     uid = models.CharField(max_length=128, unique=True)
#     setup = models.TextField(blank=True, null=False, default='')
#     skinscsv = models.CharField(max_length=512, default='', blank=True)
#     downloadlink = models.URLField(blank=True, default='')
# 
#     def __str__(self):
#         return self.title
# 
#     @property
#     def skins(self):
#         return [x.strip()
#                 for x in self.skinscsv.split(',')
#                 if x.strip() != '']
