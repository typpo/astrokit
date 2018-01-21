# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-01-21 22:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('imageflow', '0001_initial'),
        ('astrometry', '0001_initial'),
        ('photometry', '0001_initial'),
        ('lightcurve', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useruploadedimage',
            name='lightcurve',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lightcurve.LightCurve'),
        ),
        migrations.AddField(
            model_name='useruploadedimage',
            name='submission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='astrometry.AstrometrySubmission'),
        ),
        migrations.AddField(
            model_name='useruploadedimage',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reduction',
            name='analysis',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='imageflow.ImageAnalysis'),
        ),
        migrations.AddField(
            model_name='reduction',
            name='color_index_1',
            field=models.ForeignKey(default=17, on_delete=django.db.models.deletion.CASCADE, related_name='reduction_color_index_1_set', to='photometry.ImageFilter'),
        ),
        migrations.AddField(
            model_name='reduction',
            name='color_index_2',
            field=models.ForeignKey(default=18, on_delete=django.db.models.deletion.CASCADE, related_name='reduction_color_index_2_set', to='photometry.ImageFilter'),
        ),
        migrations.AddField(
            model_name='imageanalysis',
            name='astrometry_job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='astrometry.AstrometrySubmissionJob'),
        ),
        migrations.AddField(
            model_name='imageanalysis',
            name='image_filter',
            field=models.ForeignKey(default=17, on_delete=django.db.models.deletion.CASCADE, to='photometry.ImageFilter'),
        ),
        migrations.AddField(
            model_name='imageanalysis',
            name='lightcurve',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lightcurve.LightCurve'),
        ),
        migrations.AddField(
            model_name='imageanalysis',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
