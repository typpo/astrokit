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
from astrometry import astrometry_original_image_client
from astrometry.astrometry_client import Client
from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from astrometry.process import process_astrometry_online
from imageflow.models import ImageAnalysis, UserUploadedImage

import point_source_extraction
import catalog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubmissionHandler():
    def __init__(self, client, submission, args):
        self.client = client
        self.submission = submission
        self.args = args

    def run(self):
        self.handle_pending_submission()

    def handle_pending_submission(self):
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
            analysis = user_upload.analysis
        else:
            analysis = ImageAnalysis.objects.create(astrometry_job=job,
                                                    lightcurve=user_upload.lightcurve,
                                                    user=user_upload.user)
            user_upload.analysis = analysis

        logger.info('-> Submission %d, Job %d is complete' % (submission.subid, job.jobid))

        # Save results to S3.
        self.save_submission_results(job, analysis)

        # Update submission.
        submission.succeeded_at = timezone.now()
        submission.status = AstrometrySubmission.COMPLETE
        analysis.status = ImageAnalysis.REVIEW_PENDING
        if not args.dry_run:
            submission.save()
            analysis.save()
            user_upload.save()

    def save_submission_results(self, job, result):
        submission = self.submission

        logger.info('-> Uploading results for submission %d' % (submission.subid))

        original_display_url = astrometry_original_image_client.get_url(submission.subid)
        annotated_display_url = 'http://35.202.61.141/annotated_display/%d' \
                % (job.jobid)
        new_image_fits_url = 'http://35.202.61.141/new_fits_file/%d' \
                % (job.jobid)
        corr_url = 'http://35.202.61.141/corr_file/%d' \
                % (job.jobid)

        # Timestamp is added to name automatically.
        upload_key_prefix = 'processed/%d' % (submission.subid)

        # Original
        name = '%d_%d_original.jpg' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            result.astrometry_original_display_url = \
                    s3_util.upload_to_s3_via_url(original_display_url, \
                                                 upload_key_prefix, name)

        # Annotated jpg.
        name = '%d_%d_annotated.jpg' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            result.astrometry_annotated_display_url = \
                    s3_util.upload_to_s3_via_url(annotated_display_url, \
                                                 upload_key_prefix, name)

        # CORR.
        name = '%d_%d_corr.fits' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            result.astrometry_corr_fits_url = \
                    s3_util.upload_to_s3_via_url(corr_url, \
                                                 upload_key_prefix, name)

        # FITS.
        name = '%d_%d_image.fits' % (submission.subid, job.jobid)
        # TODO(ian): Process this raw fits data here using some util fn, rather
        # than processing it in point_source_extraction.
        image_fits_data = urllib.urlopen(new_image_fits_url).read()
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            result.astrometry_image_fits_url = \
                    s3_util.upload_to_s3(image_fits_data, \
                                         upload_key_prefix, name)

        logger.info('-> Uploaded results for submission %d' % (submission.subid))

        # Metadata processing.
        self.process_metadata(image_fits_data, result)

        # Point source extraction processing.
        self.process_point_sources(image_fits_data, job, result, upload_key_prefix)

        # Apparent magnitude processing.
        # TODO(ian): These inputs could be made more efficient by just passing
        # in the data from this function, rather than loading them again from
        # urls.
        self.process_magnitudes(image_fits_data, job, result, upload_key_prefix)

    def process_metadata(self, image_fits_data, result):
        fitsobj = point_source_extraction.get_fits_from_raw(image_fits_data)

        dateobs = fitsobj[0].header.get('DATE-OBS')
        if not dateobs:
            return None

        # TODO(ian): make this a util
        for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%y'):
            try:
                result.image_datetime = datetime.strptime(dateobs, fmt)
                break
            except ValueError:
                pass

    def process_point_sources(self, image_fits_data, job, result, upload_key_prefix):
        submission = self.submission

        logger.info('-> Processing fits image for submission %d' % (submission.subid))

        fitsobj = point_source_extraction.get_fits_from_raw(image_fits_data)

        data = point_source_extraction.extract_image_data_from_fits(fitsobj)
        sources, stats = point_source_extraction.compute(data)

        result.sigma_clipped_mean = stats[0]
        result.sigma_clipped_median = stats[1]
        result.sigma_clipped_std = stats[2]

        # Unaltered image.
        image_path = '%d_%d_display_image.png' % (submission.subid, job.jobid)
        point_source_extraction.save_image(data, image_path);
        logger.info('  -> Uploading %s...' % image_path)
        if not args.dry_run:
            '''
            result.original_display_url = \
                    s3_util.upload_to_s3_via_file(image_path, \
                                                  upload_key_prefix)
            '''
            # Astrometry image looks much better.
            result.original_display_url = result.astrometry_original_display_url

        # Coords.
        coords_plot_path = '%d_%d_plot.png' % (submission.subid, job.jobid)
        point_source_extraction.plot(sources, data, coords_plot_path)
        logger.info('  -> Uploading %s...' % coords_plot_path)
        if not args.dry_run:
            result.coords_plot_url = \
                    s3_util.upload_to_s3_via_file(coords_plot_path, \
                                                  upload_key_prefix)

        coords_fits_path = '%d_%d_coords.fits' % (submission.subid, job.jobid)
        point_source_extraction.save_fits(sources, coords_fits_path)
        logger.info('  -> Uploading %s...' % coords_fits_path)
        if not args.dry_run:
            result.coords_fits_url = \
                    s3_util.upload_to_s3_via_file(coords_fits_path, \
                                                  upload_key_prefix)

        coords_json_path = '%d_%d_coords.json' % (submission.subid, job.jobid)
        point_source_extraction.save_json(sources, coords_json_path)
        logger.info('  -> Uploading %s...' % coords_json_path)
        if not args.dry_run:
            result.coords = point_source_extraction.format_for_json_export(sources)
            result.coords_json_url = \
                    s3_util.upload_to_s3_via_file(coords_json_path, \
                                                  upload_key_prefix)

        # PSF.
        psf_scatter_path = '%d_%d_psf_scatter.png' % (submission.subid, job.jobid)
        psf_bar_path = '%d_%d_psf_bar.png' % (submission.subid, job.jobid)
        psf_hist_path = '%d_%d_psf_hist.png' % (submission.subid, job.jobid)
        psf_residual_path = '%d_%d_psf_residual.png' % (submission.subid, job.jobid)
        point_source_extraction.compute_psf_flux(data, sources, \
                psf_scatter_path, psf_bar_path, psf_hist_path, psf_residual_path)

        logger.info('  -> Uploading %s' % psf_scatter_path)
        logger.info('  -> Uploading %s' % psf_bar_path)
        logger.info('  -> Uploading %s' % psf_hist_path)
        logger.info('  -> Uploading %s' % psf_residual_path)
        if not args.dry_run:
            result.psf_scatter_url = \
                    s3_util.upload_to_s3_via_file(psf_scatter_path, \
                                                  upload_key_prefix)
            result.psf_bar_url = \
                    s3_util.upload_to_s3_via_file(psf_bar_path, \
                                                  upload_key_prefix)
            result.psf_hist_url = \
                    s3_util.upload_to_s3_via_file(psf_hist_path, \
                                                  upload_key_prefix)
            result.psf_residual_image_url = \
                    s3_util.upload_to_s3_via_file(psf_residual_path, \
                                                  upload_key_prefix)

        # TODO(ian): Should delete the files afterwards, or create them as
        # temporary files.

        logger.info('-> Processed fits image for submission %d' % (submission.subid))

    def process_magnitudes(self, image_fits_data, job, result, upload_key_prefix):
        submission = self.submission

        logger.info('-> Processing reference stars/magnitudes for submission %d' % \
                (submission.subid))

        coords = urllib.urlopen(result.coords_json_url).read()
        correlations = urllib.urlopen(result.astrometry_corr_fits_url).read()

        # Compute reference stars and their apparent magnitudes.
        ref_stars, unknown_stars = \
                catalog.choose_reference_stars(image_fits_data, correlations, coords)

        name = '%d_%d_image_reference_stars.json' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            result.image_reference_stars = ref_stars
            result.image_reference_stars_json_url = \
                    s3_util.upload_to_s3(json.dumps(ref_stars, indent=2, use_decimal=True), \
                                         upload_key_prefix, name)

        logger.info('-> Uploaded reference stars for submission %d' % \
                (submission.subid))

        name = '%d_%d_image_unknown_stars.json' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            result.image_unknown_stars = unknown_stars
            result.image_unknown_stars_json_url = \
                    s3_util.upload_to_s3(json.dumps(unknown_stars, indent=2, use_decimal=True), \
                                         upload_key_prefix, name)

        logger.info('-> Uploaded unknown stars for submission %d' % \
                (submission.subid))

        # Get reference star standard magnitudes.
        standard_mags = catalog.get_standard_magnitudes_urat1(ref_stars)
        name = '%d_%d_catalog_reference_stars.json' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            result.catalog_reference_stars = standard_mags
            result.catalog_reference_stars_json_url = \
                    s3_util.upload_to_s3(json.dumps(standard_mags, indent=2, use_decimal=True), \
                                         upload_key_prefix, name)

        # Combine into single annotated point sources object.
        all_points = catalog.merge_known_with_unknown(standard_mags, unknown_stars)
        name = '%d_%d_annotated_point_sources.json' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            result.annotated_point_sources = all_points
            result.annotated_point_sources_json_url = \
                    s3_util.upload_to_s3(json.dumps(all_points, indent=2, use_decimal=True), \
                                         upload_key_prefix, name)

        logger.info('-> Uploaded annotated point sources for submission %d' % \
                (submission.subid))

def process_pending_submissions(args):
    '''Turns submitted Astrometry jobs into ImageAnalyses
    '''
    # Set up astrometry.net client.
    client = Client('http://35.202.61.141/api/')
    client.login(settings.ASTROKIT_ASTROMETRY_KEY)

    pending_submissions = AstrometrySubmission.objects.all().filter(
            status=AstrometrySubmission.SUBMITTED)
    for submission in pending_submissions:
        handler = SubmissionHandler(client, submission, args)
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
    parser = argparse.ArgumentParser('Process outstanding jobs')
    parser.add_argument('--dry_run', help='don\'t actually do anything', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    process_pending_images(args)
    process_pending_submissions(args)
