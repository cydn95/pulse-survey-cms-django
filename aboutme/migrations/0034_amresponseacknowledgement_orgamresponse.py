# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2022-04-04 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aboutme', '0033_delete_emailrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='amresponseacknowledgement',
            name='orgAmResponse',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]