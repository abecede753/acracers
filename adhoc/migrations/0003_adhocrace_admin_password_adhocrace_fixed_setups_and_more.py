# Generated by Django 4.1 on 2022-08-20 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adhoc', '0002_adhocracequeue'),
    ]

    operations = [
        migrations.AddField(
            model_name='adhocrace',
            name='admin_password',
            field=models.CharField(default='kifflom', max_length=15),
        ),
        migrations.AddField(
            model_name='adhocrace',
            name='fixed_setups',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adhocrace',
            name='join_password',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AddField(
            model_name='adhocrace',
            name='reverse_grid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='adhocrace',
            name='show_public',
            field=models.BooleanField(default=False),
        ),
    ]
