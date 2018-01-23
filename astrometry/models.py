from __future__ import unicode_literals

import django
from django.contrib import admin
from django.db import models
from django.utils import timezone
from jsonfield import JSONField

from astrometry_client import Client

class AstrometrySubmission(models.Model):
    SUBMITTED = 'SUBMITTED'
    COMPLETE = 'COMPLETE'
    FAILED_TO_SUBMIT = 'FAILED_TO_SUBMIT'
    FAILED_TO_PROCESS = 'FAILED_TO_PROCESS'
    SUBMISSION_STATUSES = (
        (SUBMITTED, 'Submitted'),
        (COMPLETE, 'Complete'),
        (FAILED_TO_SUBMIT, 'Failed to submit'),
        (FAILED_TO_PROCESS, 'Failed to process'),
    )
    subid = models.IntegerField()
    upload_url = models.CharField(max_length=512)
    status = models.CharField(
            max_length=50, choices=SUBMISSION_STATUSES, default=SUBMITTED)
    created_at = models.DateTimeField(default=timezone.now)
    succeeded_at = models.DateTimeField(blank=True, null=True)

    def get_astrometry_net_url(self):
        return 'http://35.202.61.141/user_images/%d' % self.subid

    def is_done(self):
        return self.status != self.SUBMITTED

    def __str__(self):
        return 'Sub #%d - %s' % (self.subid, self.status)

class AstrometrySubmissionJob(models.Model):
    SUCCESS = 'SUCCESS'
    UNKNOWN = 'UNKNOWN'
    JOB_STATUSES = (
        (SUCCESS, 'Success'),
        (UNKNOWN, 'Unknown'),
    )

    jobid = models.IntegerField()
    submission = models.ForeignKey(
            AstrometrySubmission, on_delete=models.CASCADE)
    status = models.CharField(
            max_length=50, choices=JOB_STATUSES, default=UNKNOWN)
    created_at = models.DateTimeField(default=timezone.now)
    succeeded_at = models.DateTimeField(blank=True, null=True)

    # API results from astrometry.net.
    annotations = JSONField(blank=True, null=True)
    info = JSONField(blank=True, null=True)

    def __str__(self):
        return 'Job #%d for Sub #%d' % (self.jobid, self.submission.subid)

admin.site.register(AstrometrySubmission)
admin.site.register(AstrometrySubmissionJob)
