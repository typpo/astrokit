# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-03-09 02:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imageflow', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageanalysis',
            name='image_filter',
            field=models.ForeignKey(default=17, on_delete=django.db.models.deletion.CASCADE, to='photometry.ImageFilter'),
        ),
        migrations.AlterField(
            model_name='reduction',
            name='color_index_1',
            field=models.ForeignKey(default=17, on_delete=django.db.models.deletion.CASCADE, related_name='reduction_color_index_1_set', to='photometry.ImageFilter'),
        ),
        migrations.AlterField(
            model_name='reduction',
            name='color_index_2',
            field=models.ForeignKey(default=18, on_delete=django.db.models.deletion.CASCADE, related_name='reduction_color_index_2_set', to='photometry.ImageFilter'),
        ),
    ]