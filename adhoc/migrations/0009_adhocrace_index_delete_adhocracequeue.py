# Generated by Django 4.1 on 2022-08-27 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adhoc', '0008_alter_adhocrace_start_ts'),
    ]

    operations = [
        migrations.AddField(
            model_name='adhocrace',
            name='index',
            field=models.IntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='AdhocRaceQueue',
        ),
    ]
