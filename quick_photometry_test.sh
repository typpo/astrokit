#!/bin/bash -e

./point_source_extraction.py \
    --coords_json coords.json \
    'https://s3.amazonaws.com/astrokit-uploads/processed/1251219/1474609162-1251219_1738733_image.fits'

./compute_apparent_magnitudes.py \
    --corr_fits ~/Downloads/1474609156-1251219_1738733_corr.fits \
    --point_source_json ./coords.json

