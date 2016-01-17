from __future__ import unicode_literals

from django.db import models

class AstrometrySubmission(models.Model):
    SUBMITTED = 'SUBMITTED'
    COMPLETE = 'COMPLETE'
    FAILED_TO_SUBMIT = 'FAILED_TO_SUBMIT'
    SUBMISSION_STATUSES = (
        (SUBMITTED, 'Submitted'),
        (COMPLETE, 'Complete'),
        (FAILED_TO_SUBMIT, 'Failed to submit'),
    )
    subid = models.IntegerField()
    status = models.CharField(
            max_length=50, choices=SUBMISSION_STATUSES, default=SUBMITTED)

class AstrometrySubmissionJob(models.Model):
    submission = models.ForeignKey(
            AstrometrySubmission, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
