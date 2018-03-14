# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-03-09 04:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lightcurve', '0003_lightcurve_ciband'),
        ('imageflow', '0003_imageanalysispair'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageanalysispair',
            name='lightcurve',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='lightcurve.LightCurve'),
            preserve_default=False,
        ),
    ]
