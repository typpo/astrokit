# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-03-17 23:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0009_remove_imageanalysis_target_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageanalysis',
            name='image_jd',
            field=models.FloatField(null=True),
        ),
    ]
