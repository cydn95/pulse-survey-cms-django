# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-05-15 17:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aboutothers', '0010_remove_aoquestion_skipresponses'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aoquestion',
            options={'ordering': ['aoqOrder']},
        ),
        migrations.AddField(
            model_name='aoquestion',
            name='aoqOrder',
            field=models.PositiveIntegerField(default=0, verbose_name='Order'),
        ),
    ]
