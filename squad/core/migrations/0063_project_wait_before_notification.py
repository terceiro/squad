# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-20 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_project_allow_empty_enabled_plugin_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='wait_before_notification',
            field=models.IntegerField(help_text='Wait this many seconds before sending notifications', null=True),
        ),
    ]
