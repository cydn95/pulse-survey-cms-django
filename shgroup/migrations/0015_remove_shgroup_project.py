# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-04-13 09:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0014_auto_20200413_0211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shgroup',
            name='project',
        ),
    ]
