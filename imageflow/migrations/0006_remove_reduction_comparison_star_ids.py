# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-03-11 19:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0005_auto_20180309_0624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reduction',
            name='comparison_star_ids',
        ),
    ]
