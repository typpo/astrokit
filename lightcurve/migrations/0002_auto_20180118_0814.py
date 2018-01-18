# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-01-18 08:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lightcurve', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lightcurve',
            name='image_filter',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='lightcurve_image_filter_set', to='photometry.ImageFilter'),
        ),
        migrations.AlterField(
            model_name='lightcurve',
            name='magband',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='lightcurve_magband_set', to='photometry.ImageFilter'),
        ),
    ]