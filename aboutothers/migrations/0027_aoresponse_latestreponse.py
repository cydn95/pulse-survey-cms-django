# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-04-02 02:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aboutothers', '0026_aoresponseacknowledgement'),
    ]

    operations = [
        migrations.AddField(
            model_name='aoresponse',
            name='latestReponse',
            field=models.BooleanField(default=False),
        ),
    ]
