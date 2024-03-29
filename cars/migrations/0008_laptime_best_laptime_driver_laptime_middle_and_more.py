# Generated by Django 4.1 on 2022-08-20 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracks', '0005_alter_track_slug_alter_track_title'),
        ('drivers', '0001_initial'),
        ('cars', '0007_laptime_best_laptime_driver_laptime_middle_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='laptime',
            name='best',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='laptime',
            name='driver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='drivers.driver'),
        ),
        migrations.AddField(
            model_name='laptime',
            name='middle',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='laptime',
            name='num_entries',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='laptime',
            name='track',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tracks.track'),
        ),
        migrations.AddField(
            model_name='laptime',
            name='worst',
            field=models.FloatField(null=True),
        ),
    ]
