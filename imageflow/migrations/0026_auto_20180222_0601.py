# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-02-22 06:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0025_reduction_color_index_manual'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageanalysis',
            name='target_x',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='imageanalysis',
            name='target_y',
            field=models.IntegerField(default=-1),
        ),
    ]