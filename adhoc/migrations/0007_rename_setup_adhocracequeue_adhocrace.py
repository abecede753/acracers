# Generated by Django 4.1 on 2022-08-26 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adhoc', '0006_remove_adhocracequeue_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adhocracequeue',
            old_name='setup',
            new_name='adhocrace',
        ),
    ]
