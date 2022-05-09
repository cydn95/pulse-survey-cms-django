# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-06-12 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0015_auto_20200611_0246'),
    ]

    operations = [
        migrations.AddField(
            model_name='tooltipguide',
            name='group',
            field=models.CharField(default='Test', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tooltipguide',
            name='content',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='tooltipguide',
            name='place',
            field=models.CharField(max_length=50),
        ),
    ]