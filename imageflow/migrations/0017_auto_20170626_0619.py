# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-06-26 06:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0016_auto_20170626_0612'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imagefilter',
            old_name='name',
            new_name='band',
        ),
        migrations.RenameField(
            model_name='imagefilter',
            old_name='survey',
            new_name='system',
        ),
    ]
