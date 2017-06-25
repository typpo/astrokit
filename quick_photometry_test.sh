#!/bin/bash -e

mkdir -p test_output

pushd test_output

if [[ ! -f ./coords.json ]]; then
  wget -O coords.json 'https://s3.amazonaws.com/astrokit-uploads/processed/1595354/1498414164-1595354_2088601_coords.json'
fi
if [[ ! -f ./corr.fits ]]; then
wget -O corr.fits 'https://s3.amazonaws.com/astrokit-uploads/processed/1595354/1498414156-1595354_2088601_corr.fits'
fi
if [[ ! -f ./image.fits ]]; then
  wget -O image.fits 'https://s3.amazonaws.com/astrokit-uploads/processed/1595354/1498414158-1595354_2088601_image.fits'
fi

# TODO(ian): This doesn't include the process_metadata step, which extracts datetime.

../point_source_extraction.py \
    --coords_json ./coords.json \
    ./image.fits

../compute_apparent_magnitudes.py \
    --corr_fits ./corr.fits \
    --point_source_json ./coords.json

popd
