# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-03-09 04:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lightcurve', '0002_auto_20180309_0252'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightcurve',
            name='ciband',
            field=models.CharField(default='', max_length=50),
        ),
    ]
