# Generated by Django 5.2 on 2025-05-05 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeapp', '0004_userprofile_is_manager_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_salesagent_2',
            field=models.BooleanField(default=False),
        ),
    ]
