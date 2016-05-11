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

def handle_pending_submission(client, submission):
    print 'Querying for submission %d...' % (submission.subid)
    substatus = client.sub_status(submission.subid, True)

    if not (substatus and 'processing_finished' in substatus):
        print 'Submission is not done submitting yet.'
        return False

    job_ids = substatus['jobs']
    print 'Submission has processing jobs: %s' % (job_ids)
    num_success = 0
    for job_id in job_ids:
        info = client.send_request('jobs/%d/info' % (job_id))

        status = info['status']
        if status == 'solving' or status == 'processing':
            print '-> Job %d is still solving' % (job_id)
            # TODO(ian): Sometimes an image can get stuck in this state; there
            # should be a maximum timeout.
            return False
        elif status == 'failure':
            print '-> Job %d has failed' % (job_id)
            submission.status = AstrometrySubmission.FAILED_TO_PROCESS
            submission.save()
            return False
        elif status != 'success':
            print '-> Warning: unknown status %s: job %d, submission %d' \
                    % (status, job_id, submission.subid)
            print '-> Got the following response:', info
            return False

        annotations = client.send_request('jobs/%d/annotations' % (job_id))

        # Save these results.
        job = AstrometrySubmissionJob.objects.create(
                submission=submission,
                jobid=job_id,
                status=AstrometrySubmissionJob.SUCCESS,
                annotations=annotations,
                info=info)
        num_success += 1
        print '-> Job %d was added' % (job_id)

    if num_success > 0 and num_success == len(job_ids):
        # Update submission.
        submission.succeeded_at = timezone.now()
        submission.status = AstrometrySubmission.COMPLETE
        submission.save()
        print '-> Submission %d is complete' % (job_id)
        return True
    return False

if __name__ == '__main__':
    # Set up astrometry.net client.
    client = Client()
    client.login(settings.ASTROKIT_ASTROMETRY_KEY)

    pending_submissions = AstrometrySubmission.objects.all().filter(
            status=AstrometrySubmission.SUBMITTED)
    for submission in pending_submissions:
        handle_pending_submission(client, submission)
