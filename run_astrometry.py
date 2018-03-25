#!/usr/bin/env python

import argparse
import logging
import os
import simplejson as json
import sys
import urllib

from datetime import datetime

import django
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

import imageflow.s3_util as s3_util
from accounts.models import UserUploadedImage
from astrometry import astrometry_original_image_client
from astrometry.astrometry_client import Client
from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from astrometry.process import process_astrometry_online
from astrophot_util import get_fits_from_raw
from imageflow.models import ImageAnalysis
from photometry.models import ImageFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AstrometryRunner(object):
    def __init__(self, client, submission, args):
        self.client = client
        self.submission = submission
        self.args = args

        self.image_fits_data = None
        self.analysis = None

    def get_upload_key_prefix(self):
        # Timestamp is added to name automatically.
        return 'processed/%d' % (self.submission.subid)

    def run(self):
        client = self.client
        submission = self.submission

        logger.info('Querying for submission %d...' % (submission.subid))
        substatus = client.sub_status(submission.subid, True)

        if not (substatus and 'processing_finished' in substatus):
            logger.info('Submission is not done submitting yet.')
            return False

        job_ids = substatus['jobs']
        if not job_ids:
            logger.info('Submission is not done submitting yet (job not created).')
            return False
        logger.info('Submission has processing jobs: %s' % (job_ids))
        num_success = 0
        for job_id in job_ids:
            if not job_id:
                continue
            info = client.send_request('jobs/%d/info' % (job_id))

            status = info['status']
            if status == 'solving' or status == 'processing':
                logger.info('-> Job %d is still solving' % (job_id))
                # TODO(ian): Sometimes an image can get stuck in this state; there
                # should be a maximum timeout.
                return False
            elif status == 'failure':
                logger.warn('-> Job %d has failed' % (job_id))
                submission.status = AstrometrySubmission.FAILED_TO_PROCESS
                submission.save()
                return False
            elif status != 'success':
                logger.warn('-> Warning: unknown status %s: job %d, submission %d' \
                        % (status, job_id, submission.subid))
                logger.warn('-> Got the following response: %s' % info)
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
            logger.info('-> Job %d was added' % (job_id))

        if num_success > 0 and num_success == len(job_ids):
            self.process_completed_submission(job)
            return True
        return False

    def process_completed_submission(self, job):
        submission = self.submission
        user_upload = UserUploadedImage.objects.get(submission=submission)
        if user_upload.analysis:
            self.analysis = user_upload.analysis
        else:
            self.analysis = ImageAnalysis.objects.create(astrometry_job=job,
                                                    lightcurve=user_upload.lightcurve,
                                                    user=user_upload.user)
            user_upload.analysis = self.analysis

        logger.info('-> Submission %d, Job %d is complete' % (submission.subid, job.jobid))

        # Save results to S3.
        self.process_submission(job)

        # Metadata processing.
        self.process_metadata()

        # Update submission.
        submission.succeeded_at = timezone.now()
        submission.status = AstrometrySubmission.COMPLETE
        # TODO(ian): It's a bit weird that ImageAnalyses are created with the
        # first state already complete. They should be created in the
        # beginning.
        self.analysis.status = ImageAnalysis.PHOTOMETRY_PENDING
        if not args.dry_run:
            self.analysis.save()
            submission.save()
            user_upload.save()

    def process_submission(self, job):
        submission = self.submission

        logger.info('-> Uploading analysis for submission %d' % (submission.subid))

        # TODO(ian): Move this to astrophot_util.py
        original_display_url = astrometry_original_image_client.get_url(submission.subid)
        annotated_display_url = 'http://35.202.61.141/annotated_display/%d' \
                % (job.jobid)
        new_image_fits_url = 'http://35.202.61.141/new_fits_file/%d' \
                % (job.jobid)
        corr_url = 'http://35.202.61.141/corr_file/%d' \
                % (job.jobid)

        # Original
        name = '%d_%d_original.jpg' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            self.analysis.astrometry_original_display_url = \
                    s3_util.upload_to_s3_via_url(original_display_url, \
                                                 self.get_upload_key_prefix(), name)

        # Annotated jpg.
        name = '%d_%d_annotated.jpg' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            self.analysis.astrometry_annotated_display_url = \
                    s3_util.upload_to_s3_via_url(annotated_display_url, \
                                                 self.get_upload_key_prefix(), name)

        # CORR.
        name = '%d_%d_corr.fits' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            self.analysis.astrometry_corr_fits_url = \
                    s3_util.upload_to_s3_via_url(corr_url, \
                                                 self.get_upload_key_prefix(), name)

        # FITS.
        name = '%d_%d_image.fits' % (submission.subid, job.jobid)
        # TODO(ian): Process this raw fits data here using some util fn, rather
        # than processing it in point_source_extraction.
        self.image_fits_data = urllib.urlopen(new_image_fits_url).read()
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            self.analysis.astrometry_image_fits_url = \
                    s3_util.upload_to_s3(self.image_fits_data, \
                                         self.get_upload_key_prefix(), name)

        logger.info('-> Uploaded analysis for submission %d' % (submission.subid))

    def process_metadata(self):
        fitsobj = get_fits_from_raw(self.image_fits_data)

        # Parse date
        dateobs = fitsobj[0].header.get('DATE-OBS')
        if dateobs:
            for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%y'):
                try:
                    # TODO(ian): Set timezone
                    self.analysis.image_datetime = datetime.strptime(dateobs, fmt)
                    break
                except ValueError:
                    logger.warning('Unable to parse DATE-OBS %s' % dateobs)

        # Parse latlng
        lat = fitsobj[0].header.get('OBSLAT')
        lng = fitsobj[0].header.get('OBSLON')
        if lat:
            try:
                self.analysis.image_latitude = float(lat)
            except ValueError:
                logger.warning('Unable to parse OBSLAT %s' % lat)
        if lng:
            try:
                self.analysis.image_longitude = float(lng)
            except ValueError:
                logger.warning('Unable to parse OBSLON %s' % lng)

        # Parse filter
        filterstr = fitsobj[0].header.get('FILTER')
        if filterstr:
            try:
                self.analysis.image_filter = ImageFilter.objects.get(band=filterstr)
            except ImageFilter.DoesNotExist:
                logger.warning('Unable to parse FILTER %s' % filterstr)

def process_pending_submissions(args):
    '''Turns submitted Astrometry jobs into ImageAnalyses
    '''
    # Set up astrometry.net client.
    client = Client('http://35.202.61.141/api/')
    client.login(settings.ASTROKIT_ASTROMETRY_KEY)

    pending_submissions = AstrometrySubmission.objects.all().filter(
            status=AstrometrySubmission.SUBMITTED)
    for submission in pending_submissions:
        handler = AstrometryRunner(client, submission, args)
        handler.run()

def process_pending_images(args):
    '''Takes uploaded images and sends them to astrometry.net service.
    '''

    images = UserUploadedImage.objects.all().filter(submission=None)
    for image in images:
        if hasattr(image, 'submission') and image.submission:
            continue
        image.submission = process_astrometry_online(image.image_url)
        image.save()

def get_args():
    parser = argparse.ArgumentParser('Process outstanding astrometry jobs')
    parser.add_argument('--dry_run', help='don\'t actually do anything', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    process_pending_images(args)
    process_pending_submissions(args)
