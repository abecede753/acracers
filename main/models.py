from django.contrib.auth.models import User
from django.db import models


class Props(models.Model):
    """extend user model."""
    START_RULES = [(0, 'cars locked until start'),
                   (1, 'teleport false starters to pits'),
                   (2, 'false starters must do a pit drivethru')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personaname = models.CharField(max_length=100)
    icon = models.URLField(null=True)
    practice_minutes = models.IntegerField(default=0, null=True, blank=True)
    qualifying_minutes = models.IntegerField(default=10, null=True, blank=True)
    race_minutes = models.IntegerField(default=15, null=True, blank=True)
    reverse_grid = models.IntegerField(default=0, null=True, blank=True)
    join_password = models.CharField(
        max_length=15, default='', blank=True, null=False)
    admin_password = models.CharField(
        max_length=15, default='', blank=True, null=False)
    fixed_setups = models.BooleanField(default=False)
    show_public = models.BooleanField(default=False)
    start_rule = models.IntegerField(default=0, choices=START_RULES)
