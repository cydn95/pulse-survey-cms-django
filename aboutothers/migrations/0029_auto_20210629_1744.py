# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-06-29 09:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aboutothers', '0028_auto_20210402_1107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aoresponsesentiment',
            name='aoResponse',
        ),
        migrations.DeleteModel(
            name='AOResponseSentiment',
        ),
    ]