# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-10-21 08:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0041_projectuser_sendemail'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectuser',
            name='projectAdmin',
            field=models.NullBooleanField(default=None, verbose_name='Project Admin'),
        ),
        migrations.AddField(
            model_name='projectuser',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
