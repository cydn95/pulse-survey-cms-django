# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-05-15 14:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aboutme', '0011_remove_amquestion_skipresponses'),
    ]

    operations = [
        migrations.AddField(
            model_name='amquestion',
            name='amqOrder',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
