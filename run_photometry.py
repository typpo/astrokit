#!/usr/bin/env python
import argparse
import logging
import os
import simplejson as json
import sys
import urllib

import django
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

import catalog
import imageflow.s3_util as s3_util
import point_source_extraction
from astrophot_util import get_fits_from_raw
from imageflow.models import ImageAnalysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhotometryRunner(object):
    def __init__(self, analysis, args):
        self.analysis = analysis
        self.image_fits_data = None

    def get_upload_key_prefix(self):
        # TODO(ian): Yuck. This is a really weird way to access submission id,
        # from its child...
        return 'processed/%d' % (self.analysis.astrometry_job.submission.subid)

    def run(self):
        self.load()

        # Point source extraction processing.
        self.process_point_sources()

        # Apparent magnitude processing.
        # TODO(ian): These inputs could be made more efficient by just passing
        # in the data from this function, rather than loading them again from
        # urls.
        self.process_magnitudes()

        # ID numbering may have changed.
        self.analysis.target_id = None

        # Done!
        self.analysis.status = ImageAnalysis.REVIEW_PENDING
        self.analysis.save()

    def load(self):
        # TODO(ian): Dedupe with astrometry step.
        job = self.analysis.astrometry_job
        new_image_fits_url = 'http://35.202.61.141/new_fits_file/%d' \
                % (job.jobid)
        self.image_fits_data = urllib.urlopen(new_image_fits_url).read()

    def process_point_sources(self):
        job = self.analysis.astrometry_job
        submission = job.submission

        logger.info('-> Processing fits image for analysis %d' % (analysis.id))

        fitsobj = get_fits_from_raw(self.image_fits_data)

        data = point_source_extraction.extract_image_data_from_fits(fitsobj)
        '''
        sources, residual_image, std = \
                point_source_extraction.compute_sextractor(self.analysis.get_or_create_photometry_settings(),
                                                           self.image_fits_data,
                                                           data)
        '''

        sources, residual_image, std = \
                point_source_extraction.compute_sextractor(self.analysis.get_or_create_photometry_settings(),
                                                           self.image_fits_data,
                                                           data)

        self.analysis.sigma_clipped_std = std

        # Unaltered image.
        image_path = '%d_%d_display_image.png' % (submission.subid, job.jobid)
        point_source_extraction.save_image(data, image_path);
        logger.info('  -> Uploading %s...' % image_path)
        if not args.dry_run:
            '''
            self.analysis.original_display_url = \
                    s3_util.upload_to_s3_via_file(image_path, \
                                                  self.get_upload_key_prefix())
            '''
            # Astrometry image looks much better.
            self.analysis.original_display_url = self.analysis.astrometry_original_display_url

        # Coords.
        '''
        coords_plot_path = '%d_%d_plot.png' % (submission.subid, job.jobid)
        point_source_extraction.plot(sources, data, coords_plot_path)
        logger.info('  -> Uploading %s...' % coords_plot_path)
        if not args.dry_run:
            self.analysis.coords_plot_url = \
                    s3_util.upload_to_s3_via_file(coords_plot_path, \
                                                  self.get_upload_key_prefix())
        '''

        coords_fits_path = '%d_%d_coords.fits' % (submission.subid, job.jobid)
        point_source_extraction.save_fits(sources, coords_fits_path)
        logger.info('  -> Uploading %s...' % coords_fits_path)
        if not args.dry_run:
            self.analysis.coords_fits_url = \
                    s3_util.upload_to_s3_via_file(coords_fits_path, \
                                                  self.get_upload_key_prefix())

        coords_json_path = '%d_%d_coords.json' % (submission.subid, job.jobid)
        point_source_extraction.save_json(sources, coords_json_path)
        logger.info('  -> Uploading %s...' % coords_json_path)
        if not args.dry_run:
            self.analysis.coords = point_source_extraction.format_for_json_export(sources)
            self.analysis.coords_json_url = \
                    s3_util.upload_to_s3_via_file(coords_json_path, \
                                                  self.get_upload_key_prefix())

        # PSF.
        psf_residual_path = '%d_%d_psf_residual.png' % (submission.subid, job.jobid)
        point_source_extraction.save_image(residual_image, psf_residual_path);
        logger.info('  -> Uploading %s' % psf_residual_path)
        if not args.dry_run:
            self.analysis.psf_residual_image_url = \
                    s3_util.upload_to_s3_via_file(psf_residual_path, \
                                                  self.get_upload_key_prefix())

        # TODO(ian): Should delete the files afterwards, or create them as
        # temporary files.

        logger.info('-> Processed fits image for submission %d' % (submission.subid))

    def process_magnitudes(self):
        job = self.analysis.astrometry_job
        submission = job.submission

        logger.info('-> Processing reference stars/magnitudes for submission %d' % \
                (submission.subid))

        coords = urllib.urlopen(self.analysis.coords_json_url).read()
        correlations = urllib.urlopen(self.analysis.astrometry_corr_fits_url).read()

        # Compute reference stars and their apparent magnitudes.
        ref_stars, unknown_stars = \
                catalog.choose_reference_stars(self.image_fits_data, correlations, coords)

        name = '%d_%d_image_reference_stars.json' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            self.analysis.image_reference_stars = ref_stars
            self.analysis.image_reference_stars_json_url = \
                    s3_util.upload_to_s3(json.dumps(ref_stars, indent=2, use_decimal=True), \
                                         self.get_upload_key_prefix(), name)

        logger.info('-> Uploaded reference stars for submission %d' % \
                (submission.subid))

        name = '%d_%d_image_unknown_stars.json' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            self.analysis.image_unknown_stars = unknown_stars
            self.analysis.image_unknown_stars_json_url = \
                    s3_util.upload_to_s3(json.dumps(unknown_stars, indent=2, use_decimal=True), \
                                         self.get_upload_key_prefix(), name)

        logger.info('-> Uploaded unknown stars for submission %d' % \
                (submission.subid))

        # Get reference star standard magnitudes.
        standard_mags = catalog.get_standard_magnitudes_urat1(ref_stars)
        name = '%d_%d_catalog_reference_stars.json' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            self.analysis.catalog_reference_stars = standard_mags
            self.analysis.catalog_reference_stars_json_url = \
                    s3_util.upload_to_s3(json.dumps(standard_mags, indent=2, use_decimal=True), \
                                         self.get_upload_key_prefix(), name)

        # Combine into single annotated point sources object.
        all_points = catalog.merge_known_with_unknown(standard_mags, unknown_stars)
        name = '%d_%d_annotated_point_sources.json' % (submission.subid, job.jobid)
        logger.info('  -> Uploading %s...' % name)
        if not args.dry_run:
            self.analysis.annotated_point_sources = all_points
            self.analysis.annotated_point_sources_json_url = \
                    s3_util.upload_to_s3(json.dumps(all_points, indent=2, use_decimal=True), \
                                         self.get_upload_key_prefix(), name)

        logger.info('-> Uploaded annotated point sources for submission %d' % \
                (submission.subid))

def process_pending(args):
    analyses = ImageAnalysis.objects.filter(status=ImageAnalysis.PHOTOMETRY_PENDING)
    for analysis in analyses:
        handler = PhotometryRunner(analysis, args)
        handler.run()

def get_args():
    parser = argparse.ArgumentParser('Process outstanding photometry jobs')
    parser.add_argument('--dry_run', help='don\'t actually do anything', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    process_pending(args)
    logger.info('Done.')
