# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-08-28 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0021_auto_20200828_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='customGroup1',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='survey',
            name='customGroup2',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='survey',
            name='customGroup3',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
