# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-06-14 01:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0036_auto_20210525_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectuser',
            name='projectOrganization',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Project Organization'),
        ),
    ]