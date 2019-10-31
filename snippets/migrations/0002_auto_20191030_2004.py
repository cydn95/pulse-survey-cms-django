# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-10-31 03:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snippets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteTopics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_position', models.CharField(max_length=64)),
                ('about_you', models.CharField(blank=True, default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=12)),
                ('description', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='snippet',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Snippet',
        ),
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together=set([('name',)]),
        ),
        migrations.AddField(
            model_name='profile',
            name='favorite_topics',
            field=models.ManyToManyField(to='snippets.Topic'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favoritetopics',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snippets.Profile'),
        ),
        migrations.AddField(
            model_name='favoritetopics',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snippets.Topic'),
        ),
    ]
