# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-05-29 21:37
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0007_analysisresult_catalog_reference_stars_json_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisresult',
            name='catalog_reference_stars',
            field=jsonfield.fields.JSONField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='analysisresult',
            name='coords',
            field=jsonfield.fields.JSONField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='analysisresult',
            name='reference_stars',
            field=jsonfield.fields.JSONField(default=''),
            preserve_default=False,
        ),
    ]
