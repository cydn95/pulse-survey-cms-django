# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-10-27 05:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0023_survey_anonymitythreshold'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='seatsPurchased',
            field=models.PositiveIntegerField(default=100),
        ),
    ]
