# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-01-20 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='organization',
            field=models.CharField(max_length=200),
        ),
    ]
