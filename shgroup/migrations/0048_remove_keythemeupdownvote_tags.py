# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2022-05-15 13:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0047_keythemeupdownvote_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keythemeupdownvote',
            name='tags',
        ),
    ]
