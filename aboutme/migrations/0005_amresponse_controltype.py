# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-01-15 02:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aboutme', '0004_amresponse_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='amresponse',
            name='controlType',
            field=models.CharField(default='exit', max_length=30),
            preserve_default=False,
        ),
    ]
