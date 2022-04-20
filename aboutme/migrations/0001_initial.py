# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2022-03-02 07:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AMQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subdriver', models.CharField(blank=True, max_length=50)),
                ('questionText', models.CharField(max_length=1000)),
                ('questionSequence', models.PositiveIntegerField(default=5)),
                ('sliderTextLeft', models.CharField(blank=True, max_length=50)),
                ('sliderTextRight', models.CharField(blank=True, max_length=50)),
                ('skipOptionYN', models.BooleanField(default=True)),
                ('topicPrompt', models.CharField(blank=True, max_length=255)),
                ('commentPrompt', models.CharField(blank=True, max_length=255)),
                ('amqOrder', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('shortForm', models.BooleanField(default=False)),
                ('longForm', models.BooleanField(default=False)),
                ('isStandard', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['amqOrder'],
            },
        ),
        migrations.CreateModel(
            name='AMQuestionOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AMQuestionSHGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AMQuestionSkipOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AMResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('controlType', models.CharField(max_length=30)),
                ('integerValue', models.PositiveIntegerField(blank=True, verbose_name='Answer(Int)')),
                ('topicValue', models.TextField(blank=True, verbose_name='Answer(Text)')),
                ('commentValue', models.TextField(blank=True, verbose_name='Description')),
                ('skipValue', models.TextField(blank=True, verbose_name='Answer(Skip)')),
                ('topicTags', models.TextField(blank=True)),
                ('commentTags', models.TextField(blank=True)),
                ('latestResponse', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AMResponseAcknowledgement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likeStatus', models.PositiveIntegerField(default=0)),
                ('acknowledgeStatus', models.PositiveIntegerField(default=0)),
                ('flagStatus', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AMResponseTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topicName', models.CharField(blank=True, max_length=255)),
                ('topicComment', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PageAMQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amQuestion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aboutme.AMQuestion')),
            ],
        ),
    ]
