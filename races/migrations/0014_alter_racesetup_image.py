# Generated by Django 4.1 on 2022-08-26 14:44

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0013_alter_racesetup_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='racesetup',
            name='image',
            field=easy_thumbnails.fields.ThumbnailerImageField(null=True, upload_to='images/'),
        ),
    ]
