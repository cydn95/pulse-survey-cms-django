# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-05-20 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0034_shgroup_responsepercent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectuser',
            name='isSuperUser',
            field=models.BooleanField(default=False, verbose_name='Reveal Dashboards'),
        ),
    ]
