# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-08-28 06:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aboutothers', '0021_auto_20200827_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aoresponse',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='aoresponse',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='aoresponsetopic',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='aoresponsetopic',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]