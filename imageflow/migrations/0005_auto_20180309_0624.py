# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-03-09 06:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0004_imageanalysispair_lightcurve'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageanalysis',
            name='target_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
