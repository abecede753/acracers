# Generated by Django 4.1 on 2022-08-27 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_props_admin_password_props_fixed_setups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='props',
            name='start_rule',
            field=models.IntegerField(choices=[(0, 'cars locked until start'), (1, 'teleport false starters to pits'), (2, 'false starters must do a pit drivethru')], default=0),
        ),
    ]
