# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-02-09 03:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_convert', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spotify_user',
            name='added_songs',
        ),
        migrations.RemoveField(
            model_name='spotify_user',
            name='missed_songs',
        ),
        migrations.AddField(
            model_name='added_song',
            name='spotify_user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='spotify_convert.Spotify_User'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='missed_song',
            name='spotify_user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='spotify_convert.Spotify_User'),
            preserve_default=False,
        ),
    ]