# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-05-29 23:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0008_auto_20170529_2137'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisresult',
            name='astrometry_original_display_url',
            field=models.CharField(default='', max_length=1024),
            preserve_default=False,
        ),
    ]
