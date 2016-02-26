#!/usr/bin/env python

import json
import os
import sys

import django
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from astrometry.astrometry_client import Client

client = Client()
client.login(settings.ASTROKIT_ASTROMETRY_KEY)

pending_submissions = AstrometrySubmission.objects.all().filter(
        status=AstrometrySubmission.SUBMITTED)
for submission in pending_submissions:
    print 'Querying for submission %d...' % (submission.subid)
    substatus = client.sub_status(submission.subid, True)

    if substatus and 'processing_finished' in substatus:
        print '-> Submission is finished'

        job_ids = substatus['jobs']
        print 'Processing jobs: %s' % (job_ids)
        num_success = 0
        for job_id in job_ids:
            info = client.send_request('jobs/%d/info' % (job_id))
            status = info['status']
            if status == 'solving':
                print '-> Job %d is still solving' % (job_id)
                continue
            elif status == 'failure':
                print '-> Job %d has failed' % (job_id)
                submission.status = AstrometrySubmission.FAILED_TO_PROCESS
                submission.save()
                continue
            elif status != 'success':
                print '-> Warning: unknown status %s: job %d, submission %d' \
                        % (status, job_id, submission.subid)
                continue

            annotations = client.send_request('jobs/%d/annotations' % (job_id))

            # Save these results.
            job = AstrometrySubmissionJob.objects.create(
                    submission=submission,
                    jobid=job_id,
                    status=AstrometrySubmissionJob.SUCCESS,
                    annotations=annotations,
                    info=info)
            num_success += 1

        if num_success == len(job_ids):
            # Update submission.
            submission.succeeded_at = timezone.now()
            submission.status = AstrometrySubmission.COMPLETE
            submission.save()
