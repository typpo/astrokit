#!/bin/bash -e

mkdir -p test_output

pushd test_output

if [[ ! -f ./coords.json ]]; then
  wget -O coords.json 'https://s3.amazonaws.com/astrokit-uploads/processed/1078914/1464154928-1078914_1558980_coords.json'
fi
if [[ ! -f ./corr.fits ]]; then
wget -O corr.fits 'https://s3.amazonaws.com/astrokit-uploads/processed/1078914/1464154875-1078914_1558980_corr.fits'
fi
if [[ ! -f ./image.fits ]]; then
  wget -O image.fits 'https://s3.amazonaws.com/astrokit-uploads/processed/1078914/1464154893-1078914_1558980_image.fits'
fi

../point_source_extraction.py \
    --coords_json ./coords.json \
    ./image.fits

../compute_apparent_magnitudes.py \
    --corr_fits ./corr.fits \
    --point_source_json ./coords.json

popd
