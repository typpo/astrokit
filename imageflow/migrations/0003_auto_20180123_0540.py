# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-01-23 05:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0002_auto_20180121_2254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageanalysis',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('REVIEW_PENDING', 'Review pending'), ('REVIEW_PENDING', 'Review complete'), ('REDUCTION_COMPLETE', 'Reduction complete'), ('ADDED_TO_LIGHT_CURVE', 'Added to light curve'), ('FAILED', 'Failed')], default='PENDING', max_length=50),
        ),
    ]