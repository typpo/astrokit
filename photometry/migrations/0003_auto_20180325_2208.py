# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-03-25 22:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photometry', '0002_photometrysettings_analysis'),
    ]

    operations = [
        migrations.AddField(
            model_name='photometrysettings',
            name='gain',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='photometrysettings',
            name='phot_apertures',
            field=models.FloatField(default=11.0),
        ),
        migrations.AddField(
            model_name='photometrysettings',
            name='pixel_scale',
            field=models.FloatField(default=2.5),
        ),
        migrations.AddField(
            model_name='photometrysettings',
            name='satur_level',
            field=models.FloatField(default=50000.0),
        ),
    ]